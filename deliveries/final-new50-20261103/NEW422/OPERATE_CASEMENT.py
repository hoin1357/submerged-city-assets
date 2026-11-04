import bpy, math
from mathutils import Vector, Quaternion

def set_casement_pose(degrees=50):
    # explicit finite bounded helper; rigid frame; no solver / weather / load certification
    if not math.isfinite(float(degrees)): raise ValueError("Finite degrees required")
    a=math.radians(max(0.0,min(65.0,float(degrees))))
    d=.485-.205*math.cos(a)-math.sqrt(.280**2-(.205*math.sin(a))**2)
    # x=.050 at closed up to represented arithmetic; .485 = support length .280 + sash lever .205
    s=.050+d
    def endpoint(x,y): return (s+x*math.cos(a)-y*math.sin(a),.035+x*math.sin(a)+y*math.cos(a))
    for o in bpy.data.objects:
      g=o.get('assembly_group','')
      if g=='sash':
        r=o['rest_location'];p=endpoint(r[0],r[1]);o.location=(p[0],p[1],r[2]);o.rotation_euler=(0,0,a)
      elif g=='shoe':o.location.x=s;o.location.y=.035
    for tag in ['Bottom','Top']:
      o=bpy.data.objects[tag+' constant length support arm'];p=endpoint(.205,0);o.location.x=.535;o.location.y=.035;o.rotation_euler.z=math.atan2(p[1]-.035,p[0]-.535)
    # unequal constant .245/.120 m links fold inside the closed depth; monotonic primary drive
    p=Vector((.522,.035));q=Vector(endpoint(.345,.020));delta=q-p;dist=delta.length
    if not .125 < dist < .365:raise ValueError('Operator linkage unreachable')
    unit=delta/dist;along=(.245**2-.120**2+dist**2)/(2*dist);perp=Vector((-unit.y,unit.x));e=p+along*unit+math.sqrt(.245**2-along**2)*perp
    for n,start,end in [('Operator primary arm',p,e),('Operator split arm',e,q)]:
      o=bpy.data.objects[n];o.location.x=start.x;o.location.y=start.y;o.rotation_euler.z=math.atan2(end.y-start.y,end.x-start.x)
    for n in ['Operator elbow rivet','Operator elbow lower flange','Operator elbow retaining head']:
      o=bpy.data.objects[n];o.location.x=e.x;o.location.y=e.y
    # inferred 38.48:1 crank-to-primary gear ratio; this is a visual geared relation, not measured gear internals
    primary=math.atan2(e.y-p.y,e.x-p.x);primary=primary if primary>0 else primary+2*math.pi;turn=(math.radians(180.433906)-primary)*38.48;o=bpy.data.objects['Crank offset handle'];o.location=(.522,-.145,.061);o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion((0,1,0),turn) @ Quaternion((1,0,0),math.pi/2)
    # handle lies in interior XZ plane, grip is at actual transformed endpoint
    bpy.context.view_layer.update();p=o.matrix_world@Vector((.075,0,0));gr=bpy.data.objects['Crank rotating grip'];gr.location=(p.x,p.y-.030,p.z)
    gp=bpy.data.objects['Crank grip pin'];gp.location=(p.x,p.y-.008,p.z)
    gh=bpy.data.objects['Crank grip retaining head'];gh.location=(p.x,p.y+.0074,p.z)
    bpy.data.objects['Lock vertical linkage'].location.z=.620+(0 if a==0 else .028)
    # automatic release lifts lock hooks before sash opening; no closed latch while opening
    for i in range(2):bpy.data.objects['Lock '+str(i)+' hook'].location.z=(.270 if i==0 else .970)+.005+(0 if a==0 else .028)
    lever=bpy.data.objects['Lock release lever'];lever.rotation_euler.y=0 if a==0 else math.pi/2;lever.location=(.586 if a==0 else .566,-.084,.640 if a==0 else .620)
    bpy.context.scene['casement_open_degrees']=math.degrees(a)
    bpy.context.view_layer.update()
set_casement_pose(50)
