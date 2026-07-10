"""
Reusable pharmaceutical vessel/reactor builder.
Parametric: change radius/height/ports to reuse across reactor, GC oven, etc.
"""
import bpy
import math


def add_bolt_ring(center, radius, bolt_count=16, bolt_radius=0.025, bolt_height=0.04, mat=None):
    """Ring of small bolt heads around a flange, arranged in a circle."""
    bolts = []
    for i in range(bolt_count):
        angle = (2 * math.pi / bolt_count) * i
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=bolt_radius, depth=bolt_height, vertices=6,
            location=(x, y, center[2])
        )
        bolt = bpy.context.active_object
        bolt.name = f"Bolt_{i}"
        if mat:
            bolt.data.materials.append(mat)
        bolts.append(bolt)
    return bolts


def add_flange(location, outer_radius, thickness=0.06, bolt_count=16, name="Flange"):
    """A flat ring flange with a bolt circle, e.g. at vessel top or a port base."""
    mat = create_steel_material(name + "_Mat")
    bpy.ops.mesh.primitive_torus_add(
        location=location, major_radius=outer_radius * 0.85,
        minor_radius=thickness, major_segments=32, minor_segments=12
    )
    flange = bpy.context.active_object
    flange.name = name
    flange.scale.z = 0.5
    flange.data.materials.append(mat)
    add_bolt_ring(location, outer_radius, bolt_count=bolt_count, mat=mat)
    return flange


def add_top_port(location, port_radius=0.12, port_height=0.25, name="Port"):
    """A pipe nozzle sticking up from the vessel top, with a small flange cap."""
    mat = create_steel_material(name + "_Mat")
    x, y, z = location
    bpy.ops.mesh.primitive_cylinder_add(
        radius=port_radius, depth=port_height, location=(x, y, z + port_height / 2)
    )
    port = bpy.context.active_object
    port.name = name
    port.data.materials.append(mat)
    add_flange((x, y, z + port_height), port_radius * 1.6, thickness=0.03, bolt_count=8, name=name + "_Flange")
    return port


def create_steel_material(name="SteelPolished"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.55, 0.57, 0.6, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.15
    return mat


def create_liquid_material(name="Liquid", color=(0.15, 0.45, 0.75, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Transmission Weight"].default_value = 0.6
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["IOR"].default_value = 1.33
    bsdf.inputs["Alpha"].default_value = 0.85
    mat.blend_method = 'BLEND'
    return mat


def build_vessel(radius=1.0, height=2.5, wall_thickness=0.05, name="Vessel", cutaway=True, with_details=True):
    """Creates a hollow cylindrical vessel. If cutaway=True, removes a quarter
    wedge of the wall so the interior (liquid, agitator) is visible to camera.
    If with_details=True, adds a top flange with bolt ring and nozzle ports."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=height, location=(0, 0, height / 2)
    )
    vessel = bpy.context.active_object
    vessel.name = name

    solidify = vessel.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = wall_thickness
    solidify.offset = -1

    if cutaway:
        # Cutting wedge: a large box rotated to slice out a quarter of the cylinder,
        # positioned toward the camera side so the cut faces the viewer.
        cut_size = radius * 4
        bpy.ops.mesh.primitive_cube_add(size=cut_size, location=(radius, -radius, height / 2))
        cutter = bpy.context.active_object
        cutter.name = name + "_Cutter"
        cutter.rotation_euler[2] = 0.785398  # 45 degrees

        boolean = vessel.modifiers.new(name="Cutaway", type='BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = cutter
        cutter.hide_render = True
        cutter.hide_viewport = True

    vessel.data.materials.append(create_steel_material())

    if with_details:
        add_flange((0, 0, height), radius, bolt_count=20, name=name + "_TopFlange")
        add_top_port((radius * 0.4, radius * 0.4, height), port_radius=0.08, name=name + "_Port1")
        add_top_port((-radius * 0.4, radius * 0.4, height), port_radius=0.06, name=name + "_Port2")
        add_top_port((0, -radius * 0.5, height), port_radius=0.1, name=name + "_Port3")

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


def create_agitator_material(name="SteelShaft"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.75, 0.78, 0.8, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.25
    return mat


def build_agitator(shaft_radius=0.05, blade_length=0.35, shaft_height=2.2, blade_count=4, name="Agitator"):
    """Creates a rotating shaft + hub + pitched turbine blades, parented for easy keyframing."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    agitator_root = bpy.context.active_object
    agitator_root.name = name + "_Root"

    agitator_mat = create_agitator_material()

    # Shaft running down from the top of the vessel
    bpy.ops.mesh.primitive_cylinder_add(
        radius=shaft_radius, depth=shaft_height, location=(0, 0, shaft_height / 2)
    )
    shaft = bpy.context.active_object
    shaft.name = name + "_Shaft"
    shaft.data.materials.append(agitator_mat)
    shaft.parent = agitator_root

    # Hub where blades attach, positioned near the bottom of the shaft
    hub_z = 0.35
    bpy.ops.mesh.primitive_cylinder_add(
        radius=shaft_radius * 2.2, depth=0.18, location=(0, 0, hub_z)
    )
    hub = bpy.context.active_object
    hub.name = name + "_Hub"
    hub.data.materials.append(agitator_mat)
    hub.parent = agitator_root

    # Pitched turbine blades: angled rectangles radiating from the hub, tilted
    # like a real Rushton/pitched-blade turbine so they read as functional, not flat.
    for i in range(blade_count):
        angle = (2 * math.pi / blade_count) * i
        bx = (blade_length / 2 + shaft_radius * 2.2) * math.cos(angle)
        by = (blade_length / 2 + shaft_radius * 2.2) * math.sin(angle)

        bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, hub_z))
        blade = bpy.context.active_object
        blade.scale = (blade_length / 2, 0.14, 0.02)
        blade.rotation_euler[2] = angle
        blade.rotation_euler[1] = 0.5  # ~28 degree pitch for realistic turbine angle
        blade.name = f"{name}_Blade_{i}"
        blade.data.materials.append(agitator_mat)
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
