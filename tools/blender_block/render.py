"""Render a built .blend headless and log the real time per frame.

    blender -b scene.blend -P render.py -- OUT_DIR [--frames 1,60,120 | --range 1 240] [--pct 100] [--samples 96]
                                           [--device OPTIX|CUDA|CPU] [--nomb]
Writes OUT_DIR/####.png and OUT_DIR/render_log.json (seconds per frame, device, samples, resolution).
"""
import json
import os
import sys
import time

import bpy

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = os.path.abspath(argv[0])
os.makedirs(out, exist_ok=True)
opt = dict(view=None, look=None, engine='CYCLES', denoiser=None, nobump=False, thr=None, nosss=False, pct=100, samples=None, device='OPTIX', frames=None, range=None, nomb=False, hide=[], bounces=None)
i = 1
while i < len(argv):
    a = argv[i]
    if a == '--frames':
        opt['frames'] = [int(x) for x in argv[i + 1].split(',')]; i += 2
    elif a == '--range':
        opt['range'] = (int(argv[i + 1]), int(argv[i + 2])); i += 3
    elif a in ('--pct', '--samples'):
        opt[a[2:]] = int(argv[i + 1]); i += 2
    elif a == '--device':
        opt['device'] = argv[i + 1]; i += 2
    elif a == '--nomb':
        opt['nomb'] = True; i += 1
    elif a == '--view':
        opt['view'] = argv[i + 1]; i += 2
    elif a == '--look':
        opt['look'] = argv[i + 1]; i += 2
    elif a == '--engine':
        opt['engine'] = argv[i + 1]; i += 2
    elif a == '--denoiser':
        opt['denoiser'] = argv[i + 1]; i += 2
    elif a == '--nobump':
        opt['nobump'] = True; i += 1
    elif a == '--thr':
        opt['thr'] = float(argv[i + 1]); i += 2
    elif a == '--nosss':
        opt['nosss'] = True; i += 1
    elif a == '--hide':
        opt['hide'].append(argv[i + 1]); i += 2
    elif a == '--bounces':
        opt['bounces'] = int(argv[i + 1]); i += 2
    else:
        i += 1

sc = bpy.context.scene
cy = sc.cycles
if opt['device'] != 'CPU':
    pr = bpy.context.preferences.addons['cycles'].preferences
    pr.compute_device_type = opt['device']
    pr.get_devices()
    for d in pr.devices:
        d.use = d.type == opt['device']
    cy.device = 'GPU'
    print('DEVICES::' + ';'.join(f'{d.name}|{d.type}|{d.use}' for d in pr.devices), flush=True)
else:
    cy.device = 'CPU'
cy.denoising_use_gpu = True             # OIDN on the GPU: 38 s -> 13.6 s per 1080p frame (measured)
if opt['engine'] == 'EEVEE':
    sc.render.engine = 'BLENDER_EEVEE'
    ee = sc.eevee
    ee.taa_render_samples = opt['samples'] or 64
    for k_, v_ in (('use_raytracing', True), ('use_shadows', True), ('use_volumetric_shadows', True)):
        if hasattr(ee, k_):
            setattr(ee, k_, v_)
if opt['view']:
    sc.view_settings.view_transform = opt['view']
if opt['look']:
    sc.view_settings.look = opt['look']
sc.render.use_persistent_data = True   # keep BVH/textures between frames
if opt['samples']:
    cy.samples = opt['samples']
sc.render.resolution_percentage = opt['pct']
if opt['nomb']:
    sc.render.use_motion_blur = False
for name in opt['hide']:
    ob = bpy.data.objects.get(name)
    if ob:
        ob.animation_data_clear() if name == 'steam' else None
        ob.hide_render = True
if opt['nosss']:
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.bl_idname == 'ShaderNodeBsdfPrincipled':
                    n.inputs['Subsurface Weight'].default_value = 0
if opt['nobump']:
    for m in bpy.data.materials:
        if m.node_tree:
            for l in list(m.node_tree.links):
                if l.to_socket.name == 'Normal':
                    m.node_tree.links.remove(l)
if opt['denoiser'] == 'NONE':
    cy.use_denoising = False
elif opt['denoiser'] == 'OPTIX':
    cy.denoiser = 'OPTIX'
elif opt['denoiser'] == 'OIDN_FAST':
    cy.denoiser = 'OPENIMAGEDENOISE'
    cy.denoising_prefilter = 'FAST'
elif opt['denoiser'] == 'OIDN_GPU':
    cy.denoiser = 'OPENIMAGEDENOISE'
    cy.denoising_use_gpu = True
if opt['thr']:
    cy.adaptive_threshold = opt['thr']
if opt['bounces']:
    cy.max_bounces = opt['bounces']
    cy.diffuse_bounces = min(cy.diffuse_bounces, opt['bounces'])
    cy.glossy_bounces = min(cy.glossy_bounces, opt['bounces'])
if opt['frames']:
    frames = opt['frames']
elif opt['range']:
    frames = list(range(opt['range'][0], opt['range'][1] + 1))
else:
    frames = list(range(sc.frame_start, sc.frame_end + 1))
log = dict(view=[sc.view_settings.view_transform, sc.view_settings.look], engine=sc.render.engine, denoise=[cy.use_denoising, cy.denoiser, cy.denoising_prefilter, getattr(cy, 'denoising_use_gpu', None)], nobump=opt['nobump'], thr=cy.adaptive_threshold, nosss=opt['nosss'], device=opt['device'], samples=cy.samples, hidden=opt['hide'], bounces=cy.max_bounces, res=[sc.render.resolution_x * opt['pct'] // 100,
           sc.render.resolution_y * opt['pct'] // 100], motion_blur=sc.render.use_motion_blur, frames={})
t_all = time.time()
for f in frames:
    path = os.path.join(out, f'{f:04d}.png')
    if os.path.exists(path):
        continue
    sc.frame_set(f)
    sc.render.filepath = path
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    log['frames'][f] = round(time.time() - t0, 2)
    log['total_s'] = round(time.time() - t_all, 1)
    json.dump(log, open(os.path.join(out, 'render_log.json'), 'w'), indent=1)
    print(f'RENDER_FRAME::{f}::{log["frames"][f]}s', flush=True)
done = log['frames'].values()
log['mean_s'] = round(sum(done) / max(1, len(done)), 2)
json.dump(log, open(os.path.join(out, 'render_log.json'), 'w'), indent=1)
print('RENDER_OK::' + json.dumps({k: v for k, v in log.items() if k != 'frames'}))
