"""
Shared scene setup: lighting (HDRI), camera, render settings.
Import into every part script to keep visual consistency across all categories.
"""
import bpy


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def setup_world_lighting(strength=1.2):
    """Simple studio-style world lighting. Swap for an HDRI file later by
    setting world.node_tree.nodes['Environment Texture'].image = bpy.data.images.load(path)."""
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.05, 0.06, 0.09, 1.0)
    bg.inputs["Strength"].default_value = strength


def add_key_fill_lights():
    bpy.ops.object.light_add(type='AREA', radius=3, location=(4, -4, 5))
    key = bpy.context.active_object
    key.data.energy = 1500
    key.data.color = (1.0, 0.98, 0.95)

    bpy.ops.object.light_add(type='AREA', radius=4, location=(-5, 3, 3))
    fill = bpy.context.active_object
    fill.data.energy = 600
    fill.data.color = (0.85, 0.9, 1.0)

    bpy.ops.object.light_add(type='POINT', location=(1.5, -1.5, 1.5))
    interior = bpy.context.active_object
    interior.data.energy = 200
    interior.data.color = (1.0, 1.0, 1.0)


def setup_camera(location=(6, -6, 3), target=(0, 0, 1.5), dof_object=None):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    constraint = cam.constraints.new(type='TRACK_TO')
    bpy.ops.object.empty_add(location=target)
    empty = bpy.context.active_object
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    if dof_object:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_object = dof_object
        cam.data.dof.aperture_fstop = 2.8

    return cam


def setup_render(output_path, engine='CYCLES', frame_end=120, resolution=(1280, 720), samples=64):
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.frame_start = 1
    scene.frame_end = frame_end
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'

    if engine == 'CYCLES':
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        try:
            bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'NONE'
        except Exception:
            pass
