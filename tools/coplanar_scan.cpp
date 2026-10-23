// Native broad phase for the published-map audit. Inputs: packed float64 triangles.
// Outputs: uint32 triangle IDs, float64 positive overlap area (16-byte records).
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <numeric>
#include <vector>
using V=std::array<double,3>;
struct Tri { V p[3],lo,hi,n; };
struct Node {V lo,hi; uint32_t begin,end,left=0,right=0;};
std::vector<Tri> ts; std::vector<uint32_t> ids; std::vector<Node> ns;
double tol=2e-5, minarea=1e-6; FILE* output;
V sub(V a,V b){return {a[0]-b[0],a[1]-b[1],a[2]-b[2]};}
double dot(V a,V b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
V cross(V a,V b){return {a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};}
bool boxes(V al,V ah,V bl,V bh){for(int k=0;k<3;k++)if(ah[k]+tol<bl[k]||bh[k]+tol<al[k])return false;return true;}
uint32_t build(uint32_t begin,uint32_t end){
 Node n;n.begin=begin;n.end=end;n.lo=ts[ids[begin]].lo;n.hi=ts[ids[begin]].hi;
 for(uint32_t i=begin+1;i<end;i++)for(int k=0;k<3;k++){n.lo[k]=std::min(n.lo[k],ts[ids[i]].lo[k]);n.hi[k]=std::max(n.hi[k],ts[ids[i]].hi[k]);}
 uint32_t id=ns.size();ns.push_back(n);
 if(end-begin>8){int axis=0;for(int k=1;k<3;k++)if(n.hi[k]-n.lo[k]>n.hi[axis]-n.lo[axis])axis=k;
 uint32_t mid=(begin+end)/2;std::nth_element(ids.begin()+begin,ids.begin()+mid,ids.begin()+end,[axis](uint32_t a,uint32_t b){return ts[a].lo[axis]+ts[a].hi[axis]<ts[b].lo[axis]+ts[b].hi[axis];});
 auto l=build(begin,mid),r=build(mid,end);ns[id].left=l;ns[id].right=r;}
 return id;
}
using P=std::array<double,2>;
double side(P a,P b,P p){return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);}
void check(uint32_t i,uint32_t j){
 auto &a=ts[i],&b=ts[j];if(!boxes(a.lo,a.hi,b.lo,b.hi)||dot(a.n,b.n)<1-1e-8)return;
 for(int k=0;k<3;k++)if(std::abs(dot(sub(b.p[k],a.p[0]),a.n))>tol||std::abs(dot(sub(a.p[k],b.p[0]),b.n))>tol)return;
 int axis=0;for(int k=1;k<3;k++)if(std::abs(a.n[k])>std::abs(a.n[axis]))axis=k;
 int x=(axis+1)%3,y=(axis+2)%3;std::vector<P> poly;P clip[3];
 // Translate near the origin to avoid area cancellation at large map coordinates.
 for(int k=0;k<3;k++){poly.push_back({a.p[k][x]-a.p[0][x],a.p[k][y]-a.p[0][y]});clip[k]={b.p[k][x]-a.p[0][x],b.p[k][y]-a.p[0][y]};}
 if(side(clip[0],clip[1],clip[2])<0)std::swap(clip[0],clip[2]);
 for(int k=0;k<3&&!poly.empty();k++){std::vector<P> next;auto p=clip[k],q=clip[(k+1)%3];
 for(size_t h=0;h<poly.size();h++){auto s=poly[h],t=poly[(h+1)%poly.size()];double ds=side(p,q,s),dt=side(p,q,t);
 if(ds>=-1e-10)next.push_back(s);
 if((ds>0&&dt<0)||(ds<0&&dt>0)){double f=ds/(ds-dt);next.push_back({s[0]+(t[0]-s[0])*f,s[1]+(t[1]-s[1])*f});}}
 poly=std::move(next);}
 double area=0;for(size_t k=0;k<poly.size();k++){auto p=poly[k],q=poly[(k+1)%poly.size()];area+=p[0]*q[1]-p[1]*q[0];}
 area=std::abs(area)/2/std::abs(a.n[axis]);if(area<=minarea)return;
 if(i>j)std::swap(i,j);fwrite(&i,4,1,output);fwrite(&j,4,1,output);fwrite(&area,8,1,output);
}
void visit(uint32_t ia,uint32_t ib){
 auto &a=ns[ia],&b=ns[ib];if(!boxes(a.lo,a.hi,b.lo,b.hi))return;
 if(!a.left&&!b.left){for(uint32_t i=a.begin;i<a.end;i++)for(uint32_t j=b.begin;j<b.end;j++)if(ia!=ib||i<j)check(ids[i],ids[j]);return;}
 if(ia==ib){visit(a.left,a.left);visit(a.left,a.right);visit(a.right,a.right);}
 else if(a.left&&(!b.left||a.end-a.begin>=b.end-b.begin)){visit(a.left,ib);visit(a.right,ib);}
 else {visit(ia,b.left);visit(ia,b.right);}
}
int main(int argc,char**argv){
 if(argc!=3)return 2;std::ifstream in(argv[1],std::ios::binary);if(!in)return 3;
 Tri t;while(in.read(reinterpret_cast<char*>(t.p),72)){
 t.lo=t.hi=t.p[0];for(int j=1;j<3;j++)for(int k=0;k<3;k++){t.lo[k]=std::min(t.lo[k],t.p[j][k]);t.hi[k]=std::max(t.hi[k],t.p[j][k]);}
 t.n=cross(sub(t.p[1],t.p[0]),sub(t.p[2],t.p[0]));double len=std::sqrt(dot(t.n,t.n));
 if(len>minarea*2){for(double &v:t.n)v/=len;ids.push_back(ts.size());}ts.push_back(t);}
 output=fopen(argv[2],"wb");if(!output)return 4;
 if(!ids.empty()){build(0,ids.size());visit(0,0);}fclose(output);
 fprintf(stderr,"Scanned %zu triangles (%zu above area threshold)\n",ts.size(),ids.size());
}
