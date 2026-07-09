"""
Reusable pharmaceutical vessel/reactor builder.
Parametric: change radius/height/ports to reuse across reactor, GC oven, etc.
"""
import bpy
import math


def create_steel_material(name="SteelPolished"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.55, 0.57, 0.6, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.15
    return mat


def create_liquid_material(name="Liquid", color=(0.6, 0.75, 0.9, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Transmission Weight"].default_value = 0.9
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.33
    return mat


def build_vessel(radius=1.0, height=2.5, wall_thickness=0.05, name="Vessel"):
    """Creates a hollow cylindrical vessel (outer minus inner via solidify)."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=height, location=(0, 0, height / 2)
    )
    vessel = bpy.context.active_object
    vessel.name = name

    solidify = vessel.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = wall_thickness
    solidify.offset = -1

    vessel.data.materials.append(create_steel_material())
    return vessel


def build_liquid_fill(radius=0.92, height=2.5, fill_ratio=0.3, name="Liquid"):
    """Creates a liquid cylinder inside the vessel, sized by fill_ratio (0-1)."""
    fill_height = height * fill_ratio
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=fill_height, location=(0, 0, fill_height / 2)
    )
    liquid = bpy.context.active_object
    liquid.name = name
    liquid.data.materials.append(create_liquid_material())
    return liquid


def build_agitator(shaft_radius=0.05, blade_length=0.7, shaft_height=2.2, name="Agitator"):
    """Creates a rotating shaft + blades assembly, parented for easy keyframing."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    agitator_root = bpy.context.active_object
    agitator_root.name = name + "_Root"

    bpy.ops.mesh.primitive_cylinder_add(
        radius=shaft_radius, depth=shaft_height, location=(0, 0, shaft_height / 2)
    )
    shaft = bpy.context.active_object
    shaft.name = name + "_Shaft"
    shaft.data.materials.append(create_steel_material("SteelShaft"))
    shaft.parent = agitator_root

    for i in range(2):
        angle = i * math.pi
        bpy.ops.mesh.primitive_cube_add(
            size=1, location=(blade_length / 2 * math.cos(angle), blade_length / 2 * math.sin(angle), 0.15)
        )
        blade = bpy.context.active_object
        blade.scale = (blade_length / 2, 0.05, 0.15)
        blade.name = f"{name}_Blade_{i}"
        blade.data.materials.append(create_steel_material("SteelShaft"))
        blade.parent = agitator_root

    return agitator_root


def animate_rotation(obj, start_frame=1, end_frame=120, revolutions=2):
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=start_frame)
    obj.rotation_euler = (0, 0, revolutions * 2 * math.pi)
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=end_frame)
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'


def animate_fill_rise(obj, start_frame=1, end_frame=90, start_z_scale=0.0, end_z_scale=1.0):
    obj.scale.z = start_z_scale
    obj.keyframe_insert(data_path="scale", index=2, frame=start_frame)
    obj.scale.z = end_z_scale
    obj.keyframe_insert(data_path="scale", index=2, frame=end_frame)
