"""NEW420 rigid sectional-door illustration rig. Run this text after opening rig blend.
Bounded controller['opening'] 0..1. No physics/spring force certification.
"""
import bpy, math
from mathutils import Vector
H=2.1336; L=.5334; R=.3048; BASE=.025; ARC=H+R*math.pi/2

def path(s):
    if s<=H:return Vector((0,0,s))
    if s<ARC:
        a=(s-H)/R;return Vector((0,R*(1-math.cos(a)),H+R*math.sin(a)))
    return Vector((0,R+s-ARC,H+R))

def stations(opening):
    s=BASE+max(0.,min(1.,opening))*(ARC-BASE)
    ss=[s]
    for j in range(4):
        a=path(s);lo=s;hi=s+L*2
        for k in range(60):
            mid=(lo+hi)/2
            if (path(mid)-a).length<L:lo=mid
            else:hi=mid
        s=(lo+hi)/2;ss.append(s)
    return ss

def cable_tangent(a):
    # Exact analytic external tangent to illustrative cylindrical drum in YZ plane.
    c=Vector((a.x,-.085,2.68));v=a-c;d2=v.y*v.y+v.z*v.z;r=.0548
    if d2<=r*r:raise ValueError('Bottom anchor inside drum tangent circle')
    q=r*r/d2;t=r*math.sqrt(d2-r*r)/d2
    return c+Vector((0,q*v.y-t*v.z,q*v.z+t*v.y))

def bottom_anchor(ps,side):
    d=ps[1]-ps[0];theta=-math.atan2(d.y,d.z)
    return ps[0]+Vector((side*1.383,-.03*math.cos(theta),-.03*math.sin(theta)))

def pose(opening):
    ss=stations(opening);ps=[path(s) for s in ss]
    for i in range(4):
        ob=bpy.data.objects.get('Section_%d'%i)
        if ob:
            d=ps[i+1]-ps[i];ob.location=ps[i];ob.rotation_euler=(-math.atan2(d.y,d.z),0,0)
    for i,p in enumerate(ps):
        ob=bpy.data.objects.get('Station_%d'%i)
        if ob:ob.location=p
    for side in (-1,1):
        ob=bpy.data.objects.get('LiftCable_%s'%side)
        if ob:
            a=bottom_anchor(ps,side);b=cable_tangent(a);d=b-a
            ob.location=(a+b)/2;ob.rotation_mode='QUATERNION';theta=-math.atan2(d.y,d.z);ob.rotation_quaternion=(math.cos(theta/2),math.sin(theta/2),0,0);ob.scale=(1,1,d.length)
    drum=bpy.data.objects.get('ShaftRotation')
    if drum:
        # Cable take-up is measured from actual endpoints, not assumed linear door lift.
        a=bottom_anchor(ps,0);b=cable_tangent(a)
        drum.rotation_euler.x=(math.sqrt((2.68-BASE)**2+.055**2-.0548**2)-(b-a).length)/.0548
    bpy.context.view_layer.update()
    return ss

_busy=False
_last=None
def update(scene,*args):
    global _busy,_last
    c=bpy.data.objects.get('Door_Controller')
    if _busy or c is None:return
    v=max(0.,min(1.,float(c.get('opening',0))))
    if _last==v:return
    _busy=True
    try:pose(v);_last=v
    finally:_busy=False

def register():
    for h in list(bpy.app.handlers.depsgraph_update_post):
        if getattr(h,'__name__','')=='update' and getattr(h,'__module__','')==__name__:bpy.app.handlers.depsgraph_update_post.remove(h)
    bpy.app.handlers.depsgraph_update_post.append(update)
    update(bpy.context.scene)
if __name__=='__main__':register()
