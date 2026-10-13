import sys, math, json, os, time
sys.path.insert(0, sys.argv[1] + '/../real')
import bpy, scene as S
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT = sys.argv[1] + '/assets'; os.makedirs(OUT, exist_ok=True); what = sys.argv[2]
Q = os.environ.get('QUICK')
def setup(w, h, spp, transparent=True, cream=True):
    if Q: w, h, spp = w // 3, h // 3, 6
    S.clear(); S.render_settings(w, h, spp)
    sc = bpy.context.scene; sc.render.film_transparent = transparent; sc.view_settings.exposure = -0.3
    sc.render.image_settings.color_mode = 'RGBA'
    S.lights()
    if cream: bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.68, 0.58, 1)
def rend(name):
    bpy.context.scene.render.filepath = f'{OUT}/{name}.png'; t = time.time(); bpy.ops.render.render(write_still=True); print('done', name, round(time.time() - t, 1), flush=True)

if what == 'cup':
    setup(1000, 1400, 96); S.build_cup(fill=0.86)
    S.camera((0, -0.55, 0.16), (0, 0, 0.10), lens=60, fstop=16); rend('cup')
elif what == 'ice':
    for i, rot in enumerate([(0.3, 0.5, 0.2), (1.0, 0.2, 0.7), (0.4, 1.2, 1.4), (0.9, 0.8, 2.2)]):
        setup(600, 600, 64); im = S.m_ice()
        c = S.ice_cube('c', 0.024, (0, 0, 0), rot); c.data.materials.append(im)
        S.camera((0, -0.16, 0.05), (0, 0, 0), lens=70, fstop=16); rend(f'ice{i}')
elif what == 'macro':
    setup(1440, 900, 96, transparent=False)
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0.4, 0.5), rotation=(math.radians(90), 0, 0))
    bpy.context.active_object.data.materials.append(S.m_simple('bd', (0.78, 0.70, 0.60, 1), 0.9))
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0)); bpy.context.active_object.data.materials.append(S.m_simple('fl', (0.78, 0.70, 0.60, 1), 0.9))
    S.build_cup(fill=0.86)
    S.camera((0.0, -0.26, 0.13), (0, 0, 0.10), lens=60, fstop=5.6); rend('macro')
elif what == 'laptop':
    setup(1080, 1920, 64, transparent=False, cream=False)
    for ob in [o for o in bpy.data.objects if o.type == 'LIGHT']: bpy.data.objects.remove(ob)
    bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.004, 0.004, 0.005, 1)
    alu = S.m_simple('alu', (0.035, 0.037, 0.04, 1), 0.4, 1.0); keym = S.m_simple('key', (0.015, 0.015, 0.016, 1), 0.6)
    desk = S.m_simple('desk', (0.05, 0.045, 0.04, 1), 0.7)
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -0.001)); bpy.context.active_object.data.materials.append(desk)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.0075)); base = bpy.context.active_object; base.scale = (0.155, 0.108, 0.0075); base.data.materials.append(alu)
    bv = base.modifiers.new('b', 'BEVEL'); bv.width = 0.004; bv.segments = 3
    for r in range(6):
        for c in range(13):
            w = 0.0155
            bpy.ops.mesh.primitive_cube_add(location=(-0.122 + c * 0.0203, 0.025 - r * 0.0195 + 0.03, 0.0155)); k = bpy.context.active_object
            k.scale = (w / 2, 0.0078, 0.0012); k.data.materials.append(keym)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.07, 0.0151)); tp = bpy.context.active_object; tp.scale = (0.06, 0.03, 0.0002); tp.data.materials.append(S.m_simple('tp', (0.06, 0.065, 0.07, 1), 0.25, 1.0))
    # lid hinged at back edge, opened ~105deg
    lid = bpy.data.objects.new('lid', None); bpy.context.collection.objects.link(lid); lid.location = (0, 0.108, 0.015); lid.rotation_euler = (math.radians(-15), 0, 0)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.004, 0.105)); shell = bpy.context.active_object; shell.scale = (0.155, 0.0025, 0.105); shell.data.materials.append(alu); shell.parent = lid
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.0002, 0.108), rotation=(math.radians(90), 0, 0)); scr = bpy.context.active_object
    scr.scale = (0.145, 0.0906, 1); scr.data.materials.append(S.m_simple('glassblack', (0.0, 0.0, 0.0, 1), 0.08)); scr.parent = lid
    # screen glow (content gets composited later) + dim room light
    bpy.ops.object.light_add(type='AREA', location=(0, 0.0, 0.11)); gl = bpy.context.active_object; gl.data.shape = 'RECTANGLE'; gl.data.size = 0.29; gl.data.size_y = 0.18
    gl.data.energy = 9; gl.data.color = (1.0, 0.92, 0.82); gl.rotation_euler = (math.radians(90 - 15 + 180), 0, 0); gl.parent = lid; gl.location = (0, -0.01, 0.108)
    bpy.ops.object.light_add(type='AREA', location=(0, 0.6, 0.9)); top = bpy.context.active_object; top.data.size = 1.5; top.data.energy = 8; top.rotation_euler = (math.radians(30), 0, math.radians(180))
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0.9, 0.6), rotation=(math.radians(80), 0, 0)); wall = bpy.context.active_object; wall.data.materials.append(S.m_simple('wall', (0.10, 0.10, 0.11, 1), 0.8))
    cam = S.camera((0.0, -0.20, 0.215), (0, 0.07, 0.10), lens=22, fstop=5)
    bpy.context.view_layer.update(); sc = bpy.context.scene
    corners = [scr.matrix_world @ Vector(v) for v in [(-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0)]]
    pts = [[round(world_to_camera_view(sc, cam, c).x * 1080, 1), round((1 - world_to_camera_view(sc, cam, c).y) * 1920, 1)] for c in corners]
    json.dump({'screen': pts}, open(OUT + '/laptop.json', 'w')); print('screen', pts)
    rend('laptop')
