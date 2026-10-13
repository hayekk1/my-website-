import sys, time, math; sys.path.insert(0, sys.argv[1])
import bpy, scene as S
S.clear(); S.render_settings(int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
S.build_set(); S.lights()
o = S.build_cup(fill=0.78)
sp, drops, fl = S.build_splash()
air = bpy.data.objects.new('air', None); bpy.context.collection.objects.link(air)
for ob in [o['root'], sp] + drops + fl: ob.parent = air
air.location = (0, 0, 0.18); air.rotation_euler = (0, math.radians(-28), 0)
S.camera((-0.02, -0.66, 0.40), (-0.04, 0, 0.33), lens=50, fstop=3.2)
bpy.context.scene.render.filepath = sys.argv[2]
t = time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS', round(time.time() - t, 1))
