"""Procedural photoreal iced-latte scene for Blender (bpy). Import and call build()."""
import bpy, bmesh, math, random
from mathutils import Vector

def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links

def principled(m_nodes):
    return m_nodes.get('Principled BSDF')

def shadow_clear(m, n, l, amt=1.0):
    """Let shadow rays pass (fake caustics) so contents stay lit."""
    p = principled(n); out = n.get('Material Output')
    lp = n.new('ShaderNodeLightPath'); tr = n.new('ShaderNodeBsdfTransparent'); mx = n.new('ShaderNodeMixShader')
    mul = n.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = amt
    l.new(lp.outputs['Is Shadow Ray'], mul.inputs[0]); l.new(mul.outputs['Value'], mx.inputs['Fac'])
    l.new(p.outputs['BSDF'], mx.inputs[1]); l.new(tr.outputs['BSDF'], mx.inputs[2]); l.new(mx.outputs['Shader'], out.inputs['Surface'])

def m_glass(name, ior=1.46, rough=0.015, tint=(1, 1, 1, 1)):
    m, n, l = mat(name); p = principled(n)
    p.inputs['Base Color'].default_value = tint
    p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    p.inputs['IOR'].default_value = ior
    shadow_clear(m, n, l)
    return m

def m_ice():
    m, n, l = mat('ice'); p = principled(n)
    p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['IOR'].default_value = 1.31
    p.inputs['Roughness'].default_value = 0.02
    p.inputs['Base Color'].default_value = (0.97, 0.99, 1.0, 1)
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; nz.inputs['Detail'].default_value = 6
    bump = n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08
    l.new(nz.outputs['Fac'], bump.inputs['Height']); l.new(bump.outputs['Normal'], p.inputs['Normal'])
    shadow_clear(m, n, l, 0.95)
    return m

def m_latte(swirl_amt=1.0):
    """Milk at the bottom, espresso blooming down from the top, warped by noise."""
    m, n, l = mat('latte'); p = principled(n)
    p.inputs['Roughness'].default_value = 0.08
    p.inputs['Subsurface Weight'].default_value = 0.35
    p.inputs['Subsurface Radius'].default_value = (1.0, 0.7, 0.45)
    p.inputs['Subsurface Scale'].default_value = 0.004
    tc = n.new('ShaderNodeTexCoord')
    sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Object'], sep.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; nz.inputs['Detail'].default_value = 8; nz.inputs['Distortion'].default_value = 2.5
    l.new(tc.outputs['Object'], nz.inputs['Vector'])
    warp = n.new('ShaderNodeMath'); warp.operation = 'MULTIPLY_ADD'; warp.name = 'WARP'
    warp.inputs[1].default_value = 0.06 * swirl_amt
    l.new(nz.outputs['Fac'], warp.inputs[0]); l.new(sep.outputs['Z'], warp.inputs[2])
    mr = n.new('ShaderNodeMapRange'); mr.name = 'MR'; mr.inputs['From Min'].default_value = 0.07; mr.inputs['From Max'].default_value = 0.13
    l.new(warp.outputs['Value'], mr.inputs['Value'])
    ramp = n.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = (0.93, 0.88, 0.80, 1)   # milk
    cr.elements[1].position = 1.0; cr.elements[1].color = (0.16, 0.07, 0.03, 1)  # espresso
    e = cr.elements.new(0.45); e.color = (0.66, 0.46, 0.30, 1)
    e2 = cr.elements.new(0.78); e2.color = (0.36, 0.18, 0.08, 1)
    l.new(mr.outputs['Result'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m

def m_simple(name, col, rough=0.5, metal=0.0):
    m, n, l = mat(name); p = principled(n)
    p.inputs['Base Color'].default_value = col; p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    return m

def m_wood():
    m, n, l = mat('wood'); p = principled(n)
    p.inputs['Roughness'].default_value = 0.35
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 18, 1)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3; wv.inputs['Distortion'].default_value = 6; wv.inputs['Detail'].default_value = 6
    l.new(mp.outputs['Vector'], wv.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    cr.elements[0].color = (0.16, 0.07, 0.03, 1); cr.elements[1].color = (0.36, 0.18, 0.08, 1)
    l.new(wv.outputs['Fac'], ramp.inputs['Fac']); l.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m

def m_emit(name, col, strength):
    m, n, l = mat(name); n.clear()
    em = n.new('ShaderNodeEmission'); em.inputs['Color'].default_value = col; em.inputs['Strength'].default_value = strength
    out = n.new('ShaderNodeOutputMaterial'); l.new(em.outputs['Emission'], out.inputs['Surface'])
    return m

def frustum(name, r_bot, r_top, h, segs=96, cap_top=True, cap_bot=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r_bot, radius2=r_top, depth=h)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, h / 2))
    if not cap_top:
        top = [f for f in bm.faces if f.calc_center_median().z > h - 1e-5 and len(f.verts) > 4]
        bmesh.ops.delete(bm, geom=top, context='FACES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if not cap_top:
        for f in bm.faces:
            c = f.calc_center_median()
            if len(f.verts) > 4:  # bottom cap: normal must point down
                if f.normal.z > 0: f.normal_flip()
            elif Vector((c.x, c.y, 0)).dot(f.normal) < 0: f.normal_flip()
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    return ob

def ice_cube(name, size, loc, rot):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    ob = bpy.context.active_object; ob.name = name
    b = ob.modifiers.new('bev', 'BEVEL'); b.width = size * 0.18; b.segments = 4
    d = ob.modifiers.new('disp', 'DISPLACE'); tx = bpy.data.textures.new(name + 'tx', 'CLOUDS'); tx.noise_scale = size * 0.6
    d.texture = tx; d.strength = size * 0.04
    ob.modifiers.new('sub', 'SUBSURF').levels = 1
    bpy.ops.object.shade_smooth()
    return ob

H = 0.15; RB = 0.034; RT = 0.046
def r_at(z): return RB + (RT - RB) * z / H

def build_cup(fill=0.86, ice=True, straw=True, drops=True, seed=3):
    """Cup group under an empty 'cup' at origin (bottom centre)."""
    random.seed(seed)
    root = bpy.data.objects.new('cup', None); bpy.context.collection.objects.link(root)
    shell = frustum('shell', RB, RT, H, segs=160, cap_top=False)
    shell.data.materials.append(m_glass('plastic', 1.49, 0.02)); shell.parent = root
    # liquid
    lh = H * fill
    liq = frustum('liquid', RB - 0.0006, r_at(lh) - 0.0006, lh)
    liq.data.materials.append(m_latte()); liq.parent = root
    obs = {'root': root, 'shell': shell, 'liquid': liq, 'ice': [], 'drops': []}
    if ice:
        im = m_ice()
        spots = [(0.012, 0.010, lh - 0.004), (-0.016, -0.004, lh - 0.002), (0.004, -0.018, lh - 0.012),
                 (-0.010, 0.016, lh - 0.016), (0.018, -0.010, lh - 0.03), (-0.006, 0.002, lh - 0.045)]
        for i, (x, y, z) in enumerate(spots):
            c = ice_cube(f'ice{i}', 0.024, (x, y, z), (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 3)))
            c.data.materials.append(im); c.parent = root; obs['ice'].append(c)
    if straw:
        st = frustum('straw', 0.0042, 0.0042, 0.24, segs=32)
        st.location = (0.012, 0.006, 0.02); st.rotation_euler = (math.radians(-6), math.radians(11), 0)
        st.data.materials.append(m_simple('strawm', (0.06, 0.32, 0.18, 1), 0.25)); st.parent = root; obs['straw'] = st
    if drops:
        wm = m_glass('water', 1.33, 0.0)
        bm = bmesh.new()
        for i in range(260):
            z = random.uniform(0.01, lh - 0.004); a = random.uniform(0, 2 * math.pi)
            r = r_at(z) + 0.0013; rad = random.uniform(0.0006, 0.0018)
            g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=rad)
            v = g['verts']
            bmesh.ops.scale(bm, verts=v, vec=(1, 1, 1.25))
            bmesh.ops.scale(bm, verts=v, vec=(1, 0.45, 1))
            bmesh.ops.rotate(bm, verts=v, cent=(0, 0, 0), matrix=__import__('mathutils').Matrix.Rotation(a + math.pi / 2, 3, 'Z'))
            bmesh.ops.translate(bm, verts=v, vec=(r * math.cos(a), r * math.sin(a), z))
        me = bpy.data.meshes.new('drops'); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        dob = bpy.data.objects.new('drops', me); bpy.context.collection.objects.link(dob)
        dob.data.materials.append(wm); dob.parent = root; obs['drops_ob'] = dob
    return obs

def build_set(counter=True):
    """Counter + blurred cafe background (emissive bokeh + warm wall)."""
    if counter:
        bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0)); c = bpy.context.active_object; c.name = 'counter'
        c.data.materials.append(m_wood())
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 1.6, 1.0), rotation=(math.radians(90), 0, 0))
    w = bpy.context.active_object; w.name = 'wall'; w.data.materials.append(m_simple('wallm', (0.35, 0.22, 0.13, 1), 0.8))
    random.seed(9)
    for i in range(26):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.05), location=(random.uniform(-1.2, 1.2), random.uniform(1.0, 1.5), random.uniform(0.15, 1.3)))
        b = bpy.context.active_object
        b.data.materials.append(m_emit(f'bk{i}', (1.0, random.uniform(0.62, 0.8), random.uniform(0.35, 0.5), 1), random.uniform(6, 18)))

def lights():
    bpy.ops.object.light_add(type='AREA', location=(-0.55, 0.25, 0.45)); k = bpy.context.active_object
    k.data.energy = 70; k.data.size = 1.2; k.data.color = (1.0, 0.86, 0.7); k.rotation_euler = (math.radians(60), 0, math.radians(-120))
    bpy.ops.object.light_add(type='AREA', location=(0.6, 0.5, 0.5)); r = bpy.context.active_object
    r.data.energy = 45; r.data.size = 0.4; r.data.color = (1.0, 0.95, 0.9); r.rotation_euler = (math.radians(-60), 0, math.radians(130))
    bpy.ops.object.light_add(type='AREA', location=(0.0, -0.6, 0.3)); f = bpy.context.active_object
    f.data.energy = 7; f.data.size = 1.5; f.rotation_euler = (math.radians(80), 0, 0)
    w = bpy.data.worlds.new('w'); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.12, 0.08, 0.05, 1)

def camera(loc, target, lens=70, fstop=2.0, focus=None):
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    cam.dof.use_dof = True; cam.dof.aperture_fstop = fstop
    ob = bpy.data.objects.new('cam', cam); bpy.context.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.dof.focus_distance = focus or d.length
    bpy.context.scene.camera = ob
    return ob

def render_settings(w=540, h=960, samples=48):
    s = bpy.context.scene; s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'; s.cycles.samples = samples; s.cycles.use_denoising = True
    s.cycles.max_bounces = 10; s.cycles.transmission_bounces = 10; s.cycles.glossy_bounces = 4
    s.cycles.caustics_reflective = False; s.cycles.caustics_refractive = False
    s.render.resolution_x = w; s.render.resolution_y = h; s.render.resolution_percentage = 100
    s.view_settings.view_transform = 'AgX'; s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'PNG'
    s.render.threads_mode = 'FIXED'; s.render.threads = 4
    s.view_settings.exposure = -0.7


def m_splash():
    m, n, l = mat('splash'); p = principled(n)
    p.inputs['Base Color'].default_value = (0.40, 0.22, 0.11, 1)
    p.inputs['Roughness'].default_value = 0.05
    p.inputs['Subsurface Weight'].default_value = 0.3
    p.inputs['Subsurface Radius'].default_value = (1.0, 0.7, 0.45); p.inputs['Subsurface Scale'].default_value = 0.004
    p.inputs['Coat Weight'].default_value = 0.6
    return m

def build_splash(seed=4, amount=1.0):
    """Metaball splash leaving the rim (cup-local, rim at z=H), plus loose droplets and flying ice."""
    random.seed(seed)
    mb = bpy.data.metaballs.new('splashmb'); mb.resolution = 0.0016; mb.render_resolution = 0.0008; mb.threshold = 0.6
    ob = bpy.data.objects.new('splash', mb); bpy.context.collection.objects.link(ob)
    # fan of liquid sheets breaking up as they leave the rim
    for k, ang in enumerate([-44, -32, -22, -12, -3, 8, 18]):
        a = math.radians(ang + random.uniform(-4, 4)); L = random.uniform(0.07, 0.13)
        for i in range(26):
            u = i / 25
            if u > 0.45 and random.random() < 0.7: continue  # breakup into blobs near the tip
            r = (0.0085 * (1 - u) ** 1.5 + 0.0022) * amount
            x = math.sin(a) * L * u + random.uniform(-0.002, 0.002)
            z = H + 0.006 + math.cos(a) * L * u - 0.03 * u * u
            y = (k - 3) * 0.006 * u + random.uniform(-0.003, 0.003)
            el = mb.elements.new(); el.co = (x, y, z); el.radius = r
    for i in range(18):  # liquid bulging over the rim
        t = random.uniform(0, 2 * math.pi)
        el = mb.elements.new(); el.co = (0.035 * math.cos(t), 0.035 * math.sin(t), H + random.uniform(-0.004, 0.008)); el.radius = 0.013 * amount
    ob.data.materials.append(m_splash())
    drops = []
    sm = ob.data.materials[0]
    for i in range(34):
        a = math.radians(random.uniform(-60, 45)); d = random.uniform(0.12, 0.22)
        loc = (math.sin(a) * d, random.uniform(-0.04, 0.04), H + math.cos(a) * d - 0.02)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.0015, 0.0045), location=loc, segments=24, ring_count=12)
        dr = bpy.context.active_object; dr.scale = (1, 1, random.uniform(1.0, 1.6)); bpy.ops.object.shade_smooth()
        dr.data.materials.append(sm); drops.append(dr)
    im = bpy.data.materials.get('ice') or m_ice()
    flying = []
    for i, (x, z, r) in enumerate([(-0.07, H + 0.08, 0.4), (0.09, H + 0.12, 1.2), (0.03, H + 0.17, 2.0)]):
        c = ice_cube(f'fice{i}', 0.022, (x, random.uniform(-0.02, 0.02), z), (r, r * 0.7, r * 1.3)); c.data.materials.append(im); flying.append(c)
    return ob, drops, flying
