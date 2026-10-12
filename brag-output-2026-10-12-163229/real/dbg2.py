import sys; sys.path.insert(0, sys.argv[1])
import bpy, scene as S
mode=sys.argv[2]
S.clear(); S.render_settings(270,480,8)
S.build_set(); S.lights(); o=S.build_cup(drops=False)
sh=o['shell']
if mode=='nosolid': sh.modifiers.clear()
if mode=='ior1': sh.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.0
if mode=='bounces': bpy.context.scene.cycles.max_bounces=32; bpy.context.scene.cycles.transmission_bounces=32; bpy.context.scene.cycles.transparent_max_bounces=32
S.camera((0.0, -0.40, 0.24), (0, 0, 0.08), lens=55, fstop=2.8)
bpy.context.scene.render.filepath=f'{sys.argv[1]}/dbg_{mode}.png'; bpy.ops.render.render(write_still=True)
