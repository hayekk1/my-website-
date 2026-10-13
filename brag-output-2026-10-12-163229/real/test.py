import sys, time, math
sys.path.insert(0, sys.argv[1])
import bpy, scene as S
S.clear(); S.render_settings(540, 960, int(sys.argv[3]) if len(sys.argv) > 3 else 48)
S.build_set(); S.lights(); S.build_cup()
S.camera((0.0, -0.40, 0.24), (0, 0, 0.08), lens=55, fstop=2.8)
bpy.context.scene.render.filepath = sys.argv[2]
t = time.time(); bpy.ops.render.render(write_still=True); print('RENDER_SECONDS', round(time.time() - t, 1))
