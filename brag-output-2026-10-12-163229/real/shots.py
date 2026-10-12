"""Render every shot. usage: python shots.py <dir> <shot> [quality]"""
import sys, time, math, json, random
sys.path.insert(0, sys.argv[1])
import bpy, scene as S
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT = sys.argv[1] + '/out'; shot = sys.argv[2]
import os; OUT = OUT + ('_q' if os.environ.get('QUICK') else ''); os.makedirs(OUT, exist_ok=True)

QUICK = os.environ.get('QUICK')
def base(w, h, spp):
    if QUICK: w, h, spp = w // 4, h // 4, 4
    S.clear(); S.render_settings(w, h, spp); S.build_set(); S.lights()

def rend(path):
    bpy.context.scene.render.filepath = path; t = time.time(); bpy.ops.render.render(write_still=True)
    print('done', path, round(time.time() - t, 1), flush=True)

def set_latte(mat, top, depth, warp):
    n = mat.node_tree.nodes
    n['MR'].inputs['From Max'].default_value = top
    n['MR'].inputs['From Min'].default_value = top - max(depth, 1e-4)
    n['WARP'].inputs[1].default_value = warp

def make_liquid(o, lh):
    old = o.get('liquid')
    mat = old.data.materials[0]
    bpy.data.objects.remove(old, do_unlink=True)
    liq = S.frustum('liquid', S.RB - 0.0006, S.r_at(lh) - 0.0006, lh); liq.data.materials.append(mat); liq.parent = o['root']
    o['liquid'] = liq; return liq

def air_rig(o, sp, drops, fl):
    air = bpy.data.objects.new('air', None); bpy.context.collection.objects.link(air)
    for ob in [o['root'], sp] + drops + fl: ob.parent = air
    return air

if shot == 'freeze':  # hook still + orbit start frame
    base(1080, 1920, 96)
    o = S.build_cup(fill=0.78); sp, drops, fl = S.build_splash(); air = air_rig(o, sp, drops, fl)
    air.location = (0, 0, 0.18); air.rotation_euler = (0, math.radians(-28), 0)
    S.camera((-0.02, -0.66, 0.40), (-0.04, 0, 0.33), lens=50, fstop=3.2)
    rend(OUT + '/freeze.png')

elif shot == 'orbit':
    base(720, 1280, 20)
    o = S.build_cup(fill=0.78); sp, drops, fl = S.build_splash(); air = air_rig(o, sp, drops, fl)
    air.location = (0, 0, 0.18); air.rotation_euler = (0, math.radians(-28), 0)
    cam = S.camera((-0.02, -0.66, 0.40), (-0.04, 0, 0.33), lens=50, fstop=3.2)
    sc = bpy.context.scene; pts = []
    lh = S.H * 0.78
    def wp(local, ob=None):
        ob = ob or o['root']; return ob.matrix_world @ Vector(local)
    N = 60
    if QUICK: N = 6
    for f in range(N):
        a = math.radians(-14 + 34 * (f / (N - 1)))  # orbit angle
        piv = Vector((-0.04, 0, 0.30)); r = 0.68
        cam.location = piv + Vector((math.sin(a) * r, -math.cos(a) * r, 0.10 - 0.05 * f / (N - 1)))
        d = piv - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.data.dof.focus_distance = d.length
        bpy.context.view_layer.update()
        def proj(v):
            c = world_to_camera_view(sc, cam, v); return [round(c.x, 4), round(1 - c.y, 4)]
        # front-facing points on the cup toward camera
        toc = (cam.location - wp((0, 0, lh / 2))); toc_local = o['root'].matrix_world.inverted().to_3x3() @ toc; ang = math.atan2(toc_local.y, toc_local.x)
        front = lambda z, k=1.0: wp((math.cos(ang) * S.r_at(z) * k, math.sin(ang) * S.r_at(z) * k, z))
        pts.append({'espresso': proj(front(lh * 0.88)), 'ice': proj(fl[1].matrix_world.translation), 'swirl': proj(front(lh * 0.62)),
                    'condensation': proj(wp((math.cos(ang + 0.7) * S.r_at(lh * 0.4), math.sin(ang + 0.7) * S.r_at(lh * 0.4), lh * 0.4))),
                    'milk': proj(front(lh * 0.22))})
        rend(OUT + f'/orbit_{f:03d}.png')
    json.dump(pts, open(OUT + '/orbit_pts.json', 'w'))

elif shot == 'build':
    base(720, 1280, 20)
    o = S.build_cup(fill=0.86, drops=False)
    mat = o['liquid'].data.materials[0]
    S.camera((0.0, -0.40, 0.24), (0, 0, 0.085), lens=55, fstop=2.8)
    milkm = S.m_simple('stream_milk', (0.93, 0.89, 0.82, 1), 0.1); espm = S.m_simple('stream_esp', (0.16, 0.07, 0.03, 1), 0.08)
    def stream(name, r, m):
        s = S.frustum(name, r, r * 0.8, 0.5, segs=24); s.data.materials.append(m); return s
    ms = stream('ms', 0.0045, milkm); es = stream('es', 0.0028, espm)
    N = 60
    if QUICK: N = 6
    for f in range(N):
        u = f / (N - 1)
        mk = min(1, u / 0.5); ek = max(0, (u - 0.5) / 0.5)
        lh = max(0.002, S.H * (0.70 * (1 - (1 - mk) ** 2) + 0.16 * min(1, ek * 1.5)))
        make_liquid(o, lh)
        set_latte(o['liquid'].data.materials[0], lh, 0.002 + 0.075 * ek ** 0.8, 0.06 * ek)
        o['liquid'].hide_render = lh < 0.008
        ms.hide_render = not (0.0 < u < 0.5); ms.location = (0.006, 0, lh); ms.scale = (1, 1, 1)
        es.hide_render = not (0.52 < u < 0.86); es.location = (-0.004, 0.002, lh)
        o['straw'].hide_render = u < 0.9
        rend(OUT + f'/build_{f:03d}.png')

elif shot == 'land':
    base(720, 1280, 20)
    o = S.build_cup(fill=0.78); sp, drops, fl = S.build_splash(); air = air_rig(o, sp, drops, fl)
    cam = S.camera((0.02, -0.62, 0.26), (0.0, 0, 0.14), lens=50, fstop=3.2)
    mb = sp.data; R0 = [e.radius for e in mb.elements]; C0 = [Vector(e.co) for e in mb.elements]
    D0 = [Vector(d.location) for d in drops]; F0 = [Vector(c.location) for c in fl]
    rim = Vector((0, 0, S.H))
    N = 24
    if QUICK: N = 6
    for f in range(N):
        u = f / (N - 1); e = u * u
        air.location = (0, 0, 0.18 * (1 - e)); air.rotation_euler = (0, math.radians(-28) * (1 - min(1, u * 1.15)), 0)
        k = max(0.0, 1 - u * 1.4)
        for el, r0, c0 in zip(mb.elements, R0, C0): el.radius = r0 * k; el.co = rim + (c0 - rim) * k
        for d, p0 in zip(drops, D0): d.location = rim + (p0 - rim) * k; d.hide_render = k < 0.05
        for c, p0 in zip(fl, F0): c.location = rim + (p0 - rim) * k + Vector((0, 0, -0.02 * (1 - k))); c.hide_render = k < 0.08
        sp.hide_render = k < 0.03
        rend(OUT + f'/land_{f:03d}.png')

elif shot == 'order':
    base(1080, 1920, 64)
    o = S.build_cup(fill=0.86, drops=False); o['liquid'].hide_render = True; o['straw'].hide_render = True
    for i, c in enumerate(o['ice']): c.location.z = 0.012 + 0.02 * (i % 3) + 0.006 * i
    S.camera((0.0, -0.40, 0.24), (0, 0, 0.085), lens=55, fstop=2.8)
    rend(OUT + '/order.png')

elif shot == 'hero':
    base(1080, 1920, 96)
    o = S.build_cup(fill=0.86)
    S.camera((0.0, -0.46, 0.10), (0, 0, 0.12), lens=60, fstop=2.4)
    rend(OUT + '/hero.png')
