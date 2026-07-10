"""
Reactor Cleaning - Part 3: Water Boiling & Agitation
Run headless:
  blender -b -P configs/reactor_cleaning/part3_boil_agitate.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "components"))

import vessel
import scene_setup

scene_setup.clear_scene()
hdri_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "hdri", "studio.hdr")
scene_setup.setup_world_lighting(strength=1.0, hdri_path=hdri_path)
scene_setup.add_key_fill_lights()

reactor = vessel.build_vessel(radius=1.0, height=2.5, name="ReactorVessel")
liquid = vessel.build_liquid_fill(radius=0.92, height=2.5, fill_ratio=0.6, name="Water")
agitator = vessel.build_agitator(name="Agitator")

vessel.animate_fill_rise(liquid, start_frame=1, end_frame=60, start_z_scale=0.0, end_z_scale=1.0)
vessel.animate_rotation(agitator, start_frame=1, end_frame=120, revolutions=3)

scene_setup.setup_camera(location=(5, -5, 2.5), target=(0, 0, 1.2), dof_object=reactor)

output_path = os.path.join(os.path.dirname(__file__), "..", "..", "output", "part3_boil_agitate.mp4")
render_device = os.environ.get("BLENDER_DEVICE", "CPU")
scene_setup.setup_render(output_path, engine='CYCLES', frame_end=120, resolution=(1280, 720), samples=64, device=render_device)

import bpy
bpy.ops.render.render(animation=True)
print(f"Render complete: {output_path}")
