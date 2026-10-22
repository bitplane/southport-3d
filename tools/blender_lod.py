"""Bake isolated component LODs; run through tools/project.py lod.

Never saves over the input master. Final manifests appear only after every target
passes checks. Geometry distance samples are evidence, not a Hausdorff bound.
"""
import argparse
import importlib
import json
import math
from pathlib import Path
import sys
import time

import bpy
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from southport3d.lod import file_record, load_recipe, sha256


def select(*objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[-1]


def triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def bounds(obj):
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


def evaluated_copy(source, name):
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(source.evaluated_get(dg), depsgraph=dg)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world = source.matrix_world.copy()
    return obj


def sample_error(high, low):
    """Both directions, local vertices and face centres, measured in world metres."""
    errors = []
    for source, target in ((high, low), (low, high)):
        world = [target.matrix_world @ v.co for v in target.data.vertices]
        tree = BVHTree.FromPolygons(world, [tuple(p.vertices) for p in target.data.polygons])
        verts = source.data.vertices
        points = [source.matrix_world @ v.co for v in (verts[i] for i in range(0, len(verts), max(1, len(verts)//4000)))]
        polys = source.data.polygons
        points += [source.matrix_world @ p.center for p in (polys[i] for i in range(0, len(polys), max(1, len(polys)//4000)))]
        distances = [tree.find_nearest(p)[3] for p in points]
        if any(d is None or not math.isfinite(d) for d in distances):
            raise ValueError('Surface sampling failed')
        errors.extend(distances)
    return {'samples': len(errors), 'rms_m': float(np.sqrt(np.mean(np.square(errors)))),
            'p99_m': float(np.percentile(errors, 99)), 'max_m': float(max(errors)),
            'interpretation': 'Bidirectional sampled surface distances; not a conservative geometric-error bound'}


def reduce(high, name, action, level, asset_dir):
    from southport3d.geometry import Mesh
    texture_size = level['texture_size']
    strategy = action['strategy']
    if strategy == 'replace':
        mesh = Mesh(name)
        if action['shape'] == 'lathe':
            mesh.lathe((0, 0), action['profile'], segments=action['segments'])
        else:
            lo = Vector([min(v.co[i] for v in high.data.vertices) for i in range(3)])
            hi = Vector([max(v.co[i] for v in high.data.vertices) for i in range(3)])
            if action['shape'] == 'box':
                mesh.box((lo+hi)*.5, hi-lo)
            else:
                # Front face of the local bounding volume, mounted against a wall.
                # Closed structures must use a closed proxy, not this adapter.
                mesh.add([(lo.x,lo.y,hi.z),(hi.x,lo.y,hi.z),(hi.x,hi.y,hi.z),(lo.x,hi.y,hi.z)], [(0,1,2,3)])
        obj = mesh.finish([])
    elif strategy == 'generator':
        if action['generator'] == 'heightfield':
            with np.load(asset_dir / action['source_npz'], allow_pickle=False) as data:
                z = data['z']; nx, ny = action['grid']
                # Bilinear resampling retains a single-valued, non-folded surface.
                xx = np.linspace(0, z.shape[1]-1, nx)
                yy = np.linspace(0, z.shape[0]-1, ny)
                horizontal = np.stack([np.interp(xx, np.arange(z.shape[1]), row) for row in z])
                heights = np.stack([np.interp(yy, np.arange(z.shape[0]), row) for row in horizontal.T]).T
                width, height, origin = float(data['width']), float(data['height']), float(data.get('origin_y', 0))
            verts = [(width*(i/(nx-1)-.5), origin+height*(1-j/(ny-1)), float(heights[j,i])) for j in range(ny) for i in range(nx)]
            faces = [(j*nx+i+nx,j*nx+i+nx+1,j*nx+i+1,j*nx+i) for j in range(ny-1) for i in range(nx-1)]
            mesh = Mesh(name); mesh.add(verts, faces)
            obj = mesh.finish([], smooth=True)
        else:
            sys.path.insert(0, str(asset_dir / 'scripts'))
            module, function = action['generator'].split(':')
            obj = getattr(importlib.import_module(module), function)(name, action['settings'], asset_dir)
    else:
        obj = high.copy()
        obj.data = high.data.copy()
        bpy.context.scene.collection.objects.link(obj)
        obj.name = name
        select(obj)
        mod = obj.modifiers.new('LOD collapse', 'DECIMATE')
        mod.ratio = action['ratio']
        mod.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.matrix_world = high.matrix_world.copy()
    select(obj)
    # Fix the diagonal BEFORE baking; glTF then sees the same tangent basis.
    mod = obj.modifiers.new('Bake triangulation', 'TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for layer in list(obj.data.uv_layers):
        obj.data.uv_layers.remove(layer)
    uv = obj.data.uv_layers.new(name='LOD atlas')
    method = action['uv']
    if method == 'planar-xy':
        coords = [v.co for v in obj.data.vertices]
        x0, x1 = min(p.x for p in coords), max(p.x for p in coords)
        y0, y1 = min(p.y for p in coords), max(p.y for p in coords)
        for poly in obj.data.polygons:
            if poly.normal.z <= 0:
                raise ValueError('Planar XY atlas requires a single front-facing heightfield')
            for i in poly.loop_indices:
                p = obj.data.vertices[obj.data.loops[i].vertex_index].co
                uv.data[i].uv = (.02 + .96 * (p.x-x0)/(x1-x0), .02 + .96 * (p.y-y0)/(y1-y0))
    elif method == 'lathe':
        radius = max(r for z, r in action['profile'])
        z0, z1 = action['profile'][0][0], action['profile'][-1][0]
        for poly in obj.data.polygons:
            points = [obj.data.vertices[obj.data.loops[i].vertex_index].co for i in poly.loop_indices]
            angles = [(math.atan2(p.y, p.x) / math.tau) % 1 for p in points]
            if max(angles)-min(angles) > .5:
                angles = [a+1 if a < .5 else a for a in angles]
            for i, p, angle in zip(poly.loop_indices, points, angles):
                if poly.normal.z > .99:
                    uv.data[i].uv = (.43 + .40*p.x/radius, .43 + .40*p.y/radius)
                elif poly.normal.z < -.99:
                    uv.data[i].uv = (.92 + .05*p.x/radius, .13 - .05*p.y/radius)
                else:
                    uv.data[i].uv = (.02 + .96*angle, .88 + .08*(p.z-z0)/(z1-z0))
    elif method == 'box':
        coordinates = [v.co for v in obj.data.vertices]
        lo = [min(p[i] for p in coordinates) for i in range(3)]
        hi = [max(p[i] for p in coordinates) for i in range(3)]
        for poly in obj.data.polygons:
            axis = max(range(3), key=lambda i: abs(poly.normal[i]))
            side = axis*2 + (1 if poly.normal[axis] < 0 else 0)
            a, b = [i for i in range(3) if i != axis]
            for i in poly.loop_indices:
                point = obj.data.vertices[obj.data.loops[i].vertex_index].co
                u = (point[a]-lo[a])/(hi[a]-lo[a])
                v = (point[b]-lo[b])/(hi[b]-lo[b])
                uv.data[i].uv = ((side%3+.05+.9*u)/3, (side//3+.05+.9*v)/2)
    else:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=8 / texture_size,
                                 margin_method='FRACTION', scale_to_bounds=True)
        bpy.ops.object.mode_set(mode='OBJECT')
    coords = np.array([tuple(x.uv) for x in obj.data.uv_layers.active.data])
    if not np.isfinite(coords).all() or coords.min() < -1e-5 or coords.max() > 1.00001:
        raise ValueError('Invalid atlas coordinates')
    return obj


def validate_materials(high):
    # This first adapter is deliberately explicit about what it can preserve.
    # Glass, metal and emissive fixtures require additional channels/adapters.
    for slot in high.material_slots:
        mat = slot.material
        if not mat or not mat.use_nodes:
            raise ValueError('LOD baker requires node-based opaque dielectric materials')
        outputs = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
        if len(outputs) != 1 or not outputs[0].inputs['Surface'].is_linked:
            raise ValueError('Unsupported material output')
        shader = outputs[0].inputs['Surface'].links[0].from_node
        if shader.type != 'BSDF_PRINCIPLED':
            raise ValueError('LOD baker currently requires direct Principled material outputs')
        for name, expected in [('Metallic', 0), ('Transmission Weight', 0), ('Alpha', 1), ('Emission Strength', 0)]:
            socket = shader.inputs[name]
            if socket.is_linked or abs(socket.default_value - expected) > 1e-6:
                raise ValueError(f'Unsupported {name} in {mat.name}; add a material adapter before baking')


def bake(high, low, target, level, dest):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.render.bake.use_selected_to_active = True
    scene.render.bake.use_cage = True
    scene.render.bake.cage_extrusion = target['cage_extrusion_m']
    scene.render.bake.max_ray_distance = target['cage_extrusion_m'] * 2
    scene.render.bake.margin = 4
    scene.render.bake.use_clear = True
    scene.render.bake.normal_space = 'TANGENT'
    scene.render.bake.normal_r = 'POS_X'
    scene.render.bake.normal_g = 'POS_Y'
    scene.render.bake.normal_b = 'POS_Z'
    scene.render.bake.use_pass_direct = False
    scene.render.bake.use_pass_indirect = False
    scene.render.bake.use_pass_color = True
    mat = bpy.data.materials.new(low.name + ' baked PBR')
    mat.use_nodes = True
    low.data.materials.clear()
    low.data.materials.append(mat)
    for poly in low.data.polygons:
        poly.material_index = 0
    nt = mat.node_tree
    shader = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Metallic'].default_value = 0
    images = {}
    image_stats = {}
    for channel, kind in [('base-color', 'DIFFUSE'), ('normal', 'NORMAL'), ('roughness', 'ROUGHNESS')]:
        image = bpy.data.images.new(low.name + '-' + channel, width=level['texture_size'],
                                    height=level['texture_size'], alpha=True)
        image.colorspace_settings.name = 'sRGB' if channel == 'base-color' else 'Non-Color'
        node = nt.nodes.new('ShaderNodeTexImage')
        node.image = image
        nt.nodes.active = node
        for other in nt.nodes:
            other.select = other == node
        # Do not connect any baked maps until all passes finish: avoids feedback.
        select(high, low)
        bpy.ops.object.bake(type=kind)
        pixels = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(pixels)
        rgba = pixels.reshape(-1, 4)
        if not np.isfinite(rgba).all():
            raise ValueError('Non-finite bake')
        covered = rgba[:, 3] > 0.5
        if not covered.any():
            raise ValueError('Empty bake')
        image_stats[channel] = {'covered_pixels': int(covered.sum()),
                                'rgb_min': float(rgba[covered, :3].min()),
                                'rgb_max': float(rgba[covered, :3].max())}
        if channel == 'normal':
            lengths = np.linalg.norm(rgba[covered, :3] * 2 - 1, axis=1)
            invalid = float(np.mean(abs(lengths - 1) > .2))
            image_stats[channel]['invalid_normal_fraction'] = invalid
            if invalid > .01:
                raise ValueError(f'Possible missed bake rays: {invalid:.2%} invalid normals')
        image.filepath_raw = str(dest / (channel + '.png'))
        image.file_format = 'PNG'
        image.save()
        images[channel] = node
    nt.links.new(images['base-color'].outputs['Color'], shader.inputs['Base Color'])
    nt.links.new(images['roughness'].outputs['Color'], shader.inputs['Roughness'])
    normal = nt.nodes.new('ShaderNodeNormalMap')
    normal.space = 'TANGENT'
    normal.uv_map = low.data.uv_layers.active.name
    nt.links.new(images['normal'].outputs['Color'], normal.inputs['Color'])
    nt.links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    # Opaque stone, even though bake alpha describes UV coverage.
    return mat, image_stats


def setup_camera(high, direction):
    scene = bpy.context.scene
    box = bounds(high)
    centre = (Vector(box[0]) + Vector(box[1])) * .5
    # Recipe directions are in object-local axes; preserve site placement in GLBs.
    direction = (high.matrix_world.to_3x3() @ Vector(direction)).normalized()
    extent = (Vector(box[1]) - Vector(box[0])).length
    data = bpy.data.cameras.new('LOD review camera')
    camera = bpy.data.objects.new('LOD review camera', data)
    scene.collection.objects.link(camera)
    camera.location = centre + direction * extent * 3
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.type = 'ORTHO'
    data.ortho_scale = extent * 1.10
    data.lens = 50
    scene.camera = camera
    lightdata = bpy.data.lights.new('LOD review key', 'AREA')
    light = bpy.data.objects.new('LOD review key', lightdata)
    scene.collection.objects.link(light)
    right = camera.rotation_euler.to_matrix() @ Vector((1, 0, 0))
    up = camera.rotation_euler.to_matrix() @ Vector((0, 1, 0))
    light.location = centre + direction * extent * 2 - right * extent + up * extent
    light.rotation_euler = (centre - light.location).to_track_quat('-Z', 'Y').to_euler()
    lightdata.energy = 150 * extent * extent
    lightdata.shape = 'DISK'
    lightdata.size = extent * .65
    scene.world = bpy.data.worlds.new('LOD review world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.24, .24, .24, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .4
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True


def render(obj, path):
    for other in bpy.context.scene.objects:
        if other.type in {'MESH', 'FONT', 'CURVE'}:
            other.hide_render = other != obj
    obj.hide_render = False
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)



def render_review(obj, path, reference):
    render(obj, path)
    camera = bpy.context.scene.camera
    saved_location, saved_rotation = camera.location.copy(), camera.rotation_euler.copy()
    box = bounds(reference)
    centre = (Vector(box[0]) + Vector(box[1])) * .5
    camera.location = centre + Quaternion((0, 0, 1), math.radians(25)) @ (saved_location - centre)
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    render(obj, path.with_name(path.stem + '-oblique.png'))
    camera.location, camera.rotation_euler = saved_location, saved_rotation


def inventory(scene):
    rows = []
    for obj in scene.objects:
        if obj.type not in {'MESH', 'FONT'} or not any(c.name[:2] in ('00', '01', '02', '03', '04') for c in obj.users_collection):
            continue
        dg = bpy.context.evaluated_depsgraph_get()
        evaluated = obj.evaluated_get(dg)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        rows.append({'name': obj.name, 'mesh': obj.data.name, 'triangles': len(mesh.loop_triangles),
                     'modifiers': [m.type for m in obj.modifiers]})
        evaluated.to_mesh_clear()
    return {'objects': rows, 'placed_triangles': sum(r['triangles'] for r in rows),
            'unique_mesh_triangles': sum(r['triangles'] for r in {r['mesh']: r for r in rows}.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--source-fingerprint', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    recipe = load_recipe(args.recipe)
    dest = Path(args.output).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 1, 'scope': recipe['scope'], 'status': 'experimental-requires-visual-review',
                'source_sha256': sha256(args.source), 'recipe_sha256': sha256(args.recipe),
                'source_fingerprint': args.source_fingerprint, 'baker_sha256': sha256(__file__), 'blender': bpy.app.version_string,
                'units': 'metres', 'bounds_coordinates': 'Blender world Z-up',
                'export_coordinates': 'glTF Y-up (x,z,-y); transforms retained',
                'levels': recipe['levels'], 'targets': []}
    started = time.monotonic()
    # Fail for any missing target before starting expensive bakes.
    bpy.ops.wm.open_mainfile(filepath=str(Path(args.source).resolve()))
    missing = [t['object'] for t in recipe['targets'] if t['object'] not in bpy.data.objects]
    if missing:
        raise ValueError(f'Missing source objects: {missing}')
    audit = inventory(bpy.context.scene)
    (dest / 'inventory.json').write_text(json.dumps(audit, indent=2) + '\n')
    if recipe['scope'] == 'asset' and {x['name'] for x in audit['objects']} != {x['object'] for x in recipe['targets']}:
        raise ValueError('Asset scope must cover every exportable object; use component-pilot for partial coverage')
    for target in recipe['targets']:
        # Reload for every component to isolate source materials, lights and visibility.
        bpy.ops.wm.open_mainfile(filepath=str(Path(args.source).resolve()))
        high = evaluated_copy(bpy.data.objects[target['object']], 'BAKE HIGH ' + target['id'])
        for obj in list(bpy.context.scene.objects):
            if obj != high:
                bpy.data.objects.remove(obj, do_unlink=True)
        high.hide_render = False
        high.hide_set(False)
        if any(a['strategy'] != 'omit' for a in target['actions'].values()):
            validate_materials(high)
        target_dir = dest / target['id']
        target_dir.mkdir()
        setup_camera(high, target['view_direction'])
        render_review(high, target_dir / 'master.png', high)
        report = {'id': target['id'], 'source_object': target['object'], 'source_triangles': triangles(high),
                  'source_bounds': bounds(high), 'lods': []}
        for level in recipe['levels']:
            print('LOD_START', target['id'], level['id'], flush=True)
            level_dir = target_dir / level['id']
            level_dir.mkdir()
            action = target['actions'][level['id']]
            if action['strategy'] == 'omit':
                report['lods'].append({'id': level['id'], 'strategy': 'omit', 'reason': action['reason'], 'triangles': 0})
                continue
            settings = dict(target, **action)
            high.hide_render = False
            low = reduce(high, target['id'] + '-' + level['id'], action, level, Path(args.recipe).parent)
            error = sample_error(high, low)
            if error['max_m'] > settings['max_sampled_error_m']:
                raise ValueError(f"{target['id']}: sampled error exceeds configured tolerance: {error}")
            if not 0 < triangles(low) < triangles(high):
                raise ValueError('LOD did not reduce geometry')
            mat, stats = bake(high, low, settings, level, level_dir)
            scene = bpy.context.scene
            scene.cycles.samples = 24
            render_review(low, level_dir / 'baked.png', high)
            shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            link = shader.inputs['Normal'].links[0]
            from_socket = link.from_socket
            mat.node_tree.links.remove(link)
            render_review(low, level_dir / 'without-normal.png', high)
            mat.node_tree.links.new(from_socket, shader.inputs['Normal'])
            select(low)
            glb = level_dir / 'model.glb'
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                                     export_apply=True, export_tangents=True, export_cameras=False,
                                     export_lights=False, export_extras=False)
            row = {'id': level['id'], 'strategy': action['strategy'], 'reason': action['reason'], 'max_sampled_error_m': settings['max_sampled_error_m'], 'triangles': triangles(low), 'bounds': bounds(low),
                   'sampled_surface_error': error, 'texture_size': level['texture_size'],
                   'bake_checks': stats, 'glb': file_record(glb, dest),
                   'textures': [file_record(level_dir / (key + '.png'), dest)
                                for key in ('base-color', 'normal', 'roughness')]}
            report['lods'].append(row)
            bpy.data.objects.remove(low, do_unlink=True)
        manifest['targets'].append(report)
    manifest['elapsed_seconds'] = round(time.monotonic() - started, 2)
    (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('LOD_COMPLETE', dest, flush=True)


if __name__ == '__main__':
    main()
