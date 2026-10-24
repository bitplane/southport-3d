"""Small GEOS bridge for this corridor's planar ownership and triangulation.

Requires libgeos_c (GEOS >=3.10), supplied by Debian's libgeos-c1t64 package.
Overlay arithmetic uses a micrometre grid, substantially finer than the reference uncertainty.
No image/OSM download or third-party Python wheel is needed during a build.
"""
import ctypes as C
from ctypes.util import find_library
class Plan:
 def __init__(self):
  name=find_library('geos_c')
  if not name:raise RuntimeError('Lord Street ground requires libgeos_c (GEOS >=3.10); see docs/LORD-STREET-BLOCK-PLAN.md')
  self.lib=C.CDLL(name);self.owned=[]
  def api(name,result,*args):
   f=getattr(self.lib,name);f.restype=result;f.argtypes=list(args);return f
  P=C.c_void_p;I=C.c_int;U=C.c_uint;D=C.c_double
  self.context=api('GEOS_init_r',P)();ctx=P
  self.finish=api('GEOS_finish_r',None,ctx)
  self.destroy=api('GEOSGeom_destroy_r',None,ctx,P)
  self.reader=api('GEOSWKTReader_create_r',P,ctx)(self.context)
  self.read=api('GEOSWKTReader_read_r',P,ctx,P,C.c_char_p)
  self.reader_destroy=api('GEOSWKTReader_destroy_r',None,ctx,P)
  self.unary=api('GEOSUnaryUnionPrec_r',P,ctx,P,D)
  self.diff=api('GEOSDifferencePrec_r',P,ctx,P,P,D)
  self.inter=api('GEOSIntersectionPrec_r',P,ctx,P,P,D)
  self.cdt=api('GEOSConstrainedDelaunayTriangulation_r',P,ctx,P)
  self.kind=api('GEOSGeomTypeId_r',I,ctx,P)
  self.count=api('GEOSGetNumGeometries_r',I,ctx,P)
  self.child=api('GEOSGetGeometryN_r',P,ctx,P,I)
  self.exterior=api('GEOSGetExteriorRing_r',P,ctx,P)
  self.seq=api('GEOSGeom_getCoordSeq_r',P,ctx,P)
  self.size=api('GEOSCoordSeq_getSize_r',I,ctx,P,C.POINTER(U))
  self.x=api('GEOSCoordSeq_getX_r',I,ctx,P,U,C.POINTER(D))
  self.y=api('GEOSCoordSeq_getY_r',I,ctx,P,U,C.POINTER(D))
 def own(self,g):
  if not g:raise RuntimeError('GEOS operation failed; invalid corridor source geometry')
  self.owned.append(g);return g
 def polygons(self,polys):
  rings=[]
  for p in polys:
   if len(p)<3:continue
   rings.append('POLYGON (('+','.join(f'{float(x):.9f} {float(y):.9f}' for x,y in list(p)+[p[0]])+'))')
  wkt='GEOMETRYCOLLECTION ('+','.join(rings)+')' if rings else 'GEOMETRYCOLLECTION EMPTY'
  g=self.own(self.read(self.context,self.reader,wkt.encode()))
  return self.own(self.unary(self.context,g,.000001))
 def difference(self,a,b):return self.own(self.diff(self.context,a,b,.000001))
 def intersection(self,a,b):return self.own(self.inter(self.context,a,b,.000001))
 def triangles(self,g):
  out=[];g=self.own(self.cdt(self.context,g))
  def visit(o):
   if self.kind(self.context,o)==3:
    ring=self.exterior(self.context,o);seq=self.seq(self.context,ring);n=C.c_uint();self.size(self.context,seq,C.byref(n));p=[]
    for i in range(n.value-1):
     x=C.c_double();y=C.c_double();self.x(self.context,seq,i,C.byref(x));self.y(self.context,seq,i,C.byref(y));p.append((x.value,y.value))
    if len(p)!=3:raise RuntimeError('GEOS constrained triangulation returned a non-triangle')
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))<0:p.reverse()
    out.append(p)
   else:
    for i in range(self.count(self.context,o)):visit(self.child(self.context,o,i))
  visit(g);return out
 def close(self):
  for g in reversed(self.owned):self.destroy(self.context,g)
  self.reader_destroy(self.context,self.reader);self.finish(self.context)
