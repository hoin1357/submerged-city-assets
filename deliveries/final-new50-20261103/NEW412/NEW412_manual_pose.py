"""Manual pose helper for NEW412, supplemental support only.

Open NEW412_LOD0.blend in Blender, run this script, then call
set_manual_yaw(-12), set_manual_yaw(0), or set_manual_yaw(12).
The reviewed samples are -12, 0 and +12 degrees, not a continuous
collision or physics certification. Rotating the front object alone
DOES NOT retarget the cylinder: call this helper to update both parts.
There are no automatic drivers, constraints, actions or powertrain.
This helper changes the current in-memory scene only; it saves nothing.
"""
import math
import bpy
from mathutils import Vector, Matrix

def set_manual_yaw(degrees=0):
    degrees=float(degrees)
    if not math.isfinite(degrees) or not -12 <= degrees <= 12:
        raise ValueError('Manual review scope is -12 to +12 degrees; only endpoints and zero were sampled.')
    names=('FRONT_ARTICULATION_manual_yaw','steering_hydraulic_barrel','steering_hydraulic_rod')
    missing=[name for name in names if name not in bpy.data.objects]
    if missing:
        raise ValueError('Open the complete neutral NEW412 scene first. Missing: '+', '.join(missing))
    front,barrel,rod=(bpy.data.objects[name] for name in names)
    A=Vector((-.24,-.32,.60))
    B0=Vector((.25,-.32,.60))
    axis=Vector((1,0,0))
    angle=math.radians(degrees)
    B=Matrix.Rotation(angle,4,'Z') @ B0
    direction=(B-A).normalized()
    rotation=axis.rotation_difference(direction).to_matrix().to_4x4()
    front.rotation_euler=(0,0,angle)
    for obj,old_center,old_length,start,end in (
        (barrel,A+axis*.145,.29,A,A+direction*.29),
        (rod,A+axis*.36,.26,A+direction*.23,B),
    ):
        scale=Matrix.Diagonal(((end-start).length/old_length,1,1,1))
        obj.matrix_basis=Matrix.Translation((start+end)/2) @ rotation @ scale @ Matrix.Translation(-old_center)
    bpy.context.view_layer.update()
    return {'manual_yaw_degrees':degrees,'actuator_anchor_distance_metres':(B-A).length,
            'scope':'Manual/script-coupled pose, not autonomous animation or physics'}

if __name__=='__main__':
    set_manual_yaw(0)
