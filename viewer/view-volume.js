import * as THREE from 'three';
import { horizontalDistance } from './spatial.js';

/** Camera frustum plus a nearby safety area, padded to prefetch at the edges. */
export function viewVolume(camera,radius,margin=0){
  camera.updateMatrixWorld(true);
  const frustum=new THREE.Frustum().setFromProjectionMatrix(
    new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse));
  const position=camera.position.toArray(),box=new THREE.Box3();
  const visible=bounds=>{
    box.min.fromArray(bounds[0]);box.max.fromArray(bounds[1]);
    return frustum.intersectsBox(box.expandByScalar(margin));
  };
  return {visible,includes:bounds=>visible(bounds)||horizontalDistance(bounds,position)<=radius+margin};
}
