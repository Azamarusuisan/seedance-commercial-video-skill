import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET_3D_DIR = ROOT / "workspace" / "assets" / "3d"
RENDER_DIR = ASSET_3D_DIR / "renders"
BLEND_DIR = ASSET_3D_DIR / "blend"
MANIFEST_DIR = ASSET_3D_DIR / "manifests"
for directory in (RENDER_DIR, BLEND_DIR, MANIFEST_DIR):
    directory.mkdir(parents=True, exist_ok=True)


def mat(name, color, emission=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emission
        bsdf.inputs["Roughness"].default_value = 0.36
    return material


def cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

dark = mat("mat_dark_factory_floor", (0.01, 0.018, 0.032, 1), 0.0)
cyan = mat("mat_cyan_light_lane", (0.0, 0.9, 1.0, 1), 2.5)
green = mat("mat_green_status", (0.1, 1.0, 0.55, 1), 1.6)
magenta = mat("mat_magenta_monitor", (1.0, 0.05, 0.85, 1), 1.9)
amber = mat("mat_amber_gate", (1.0, 0.6, 0.05, 1), 1.4)
metal = mat("mat_blue_black_metal", (0.02, 0.08, 0.12, 1), 0.0)

cube("factory_floor", (0, 0, -0.08), (8, 5, 0.08), dark)
cube("main_conveyor_lane", (0, 0, 0.08), (6.8, 0.45, 0.08), metal)
cube("left_machine_bay", (-3.7, 0, 0.7), (0.25, 1.3, 0.8), metal)
cube("right_machine_bay", (3.7, 0, 0.7), (0.25, 1.3, 0.8), metal)

for index, x in enumerate([-2.4, -1.2, 0, 1.2, 2.4]):
    material = [cyan, green, magenta, amber, cyan][index]
    cube(f"video_cube_{index + 1:02d}", (x, 0, 0.42 + index * 0.03), (0.32, 0.32, 0.32), material)
    cube(f"status_light_{index + 1:02d}", (x, -0.7, 0.12), (0.28, 0.04, 0.025), material)

for x in [-3.0, -1.5, 0.0, 1.5, 3.0]:
    cube(f"cyan_rail_{x}", (x, 0.53, 0.22), (0.42, 0.025, 0.025), cyan)
    cube(f"cyan_rail_back_{x}", (x, -0.53, 0.22), (0.42, 0.025, 0.025), cyan)

cube("central_render_core_04", (0, 1.15, 1.25), (1.1, 0.06, 0.46), cyan)
cube("subtitle_gate", (1.45, 1.15, 1.05), (0.62, 0.06, 0.32), magenta)
cube("voice_lane", (-1.45, 1.15, 1.05), (0.62, 0.06, 0.32), green)

bpy.ops.object.light_add(type="AREA", location=(0, -2.4, 4.2))
bpy.context.object.name = "large_softbox"
bpy.context.object.data.energy = 450
bpy.context.object.data.size = 5

for name, location, color in [
    ("cyan_beam", (-3, 0, 2.5), (0.0, 0.8, 1.0)),
    ("magenta_beam", (2.6, 1.4, 2.2), (1.0, 0.05, 0.8)),
    ("amber_gate_light", (0.8, -1.6, 1.8), (1.0, 0.55, 0.05)),
]:
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = 120
    light.data.color = color

bpy.ops.object.camera_add(location=(4.6, -4.0, 2.6), rotation=(math.radians(62), 0, math.radians(43)))
bpy.context.scene.camera = bpy.context.object

available_engines = {item.identifier for item in bpy.context.scene.render.bl_rna.properties["engine"].enum_items}
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
if hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 32
bpy.context.scene.render.resolution_x = 1600
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.view_settings.view_transform = "Filmic"
bpy.context.scene.view_settings.look = "High Contrast"
bpy.context.scene.render.filepath = str(RENDER_DIR / "codex_factory_demo.png")

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_DIR / "codex_factory_demo.blend"))
bpy.ops.render.render(write_still=True)
