import sys; sys.path.insert(0, sys.argv[1])
import bpy, scene as S
mode=sys.argv[2]
S.clear(); S.render_settings(270,480,8)
S.build_set(); S.lights(); o=S.build_cup(drops=False)
if mode=='noshell': o['shell'].hide_render=True
if mode=='noice':
    for c in o['ice']: c.hide_render=True
if mode=='flat':
    o['liquid'].data.materials[0]=S.m_simple('x',(0.8,0.6,0.4,1))
S.camera((0.0, -0.40, 0.24), (0, 0, 0.08), lens=55, fstop=2.8)
bpy.context.scene.render.filepath=f'{sys.argv[1]}/dbg_{mode}.png'; bpy.ops.render.render(write_still=True)
