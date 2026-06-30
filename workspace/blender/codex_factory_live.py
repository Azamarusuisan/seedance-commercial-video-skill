import json
import math
import time
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
ASSET_3D_DIR = ROOT / "workspace" / "assets" / "3d"
LIVE_DIR = ASSET_3D_DIR / "live"
LIVE_DIR.mkdir(parents=True, exist_ok=True)

FRAME_COUNT = 18
STATE_PATH = LIVE_DIR / "live-state.json"


def write_state(frame_index, latest_path, status):
    payload = {
        "id": "codex_factory_live_viewport",
        "name": "Codex Factory Live Viewport",
        "status": status,
        "frame": frame_index,
        "frame_count": FRAME_COUNT,
        "progress": round((frame_index / FRAME_COUNT) * 100, 1) if FRAME_COUNT else 0,
        "latest_frame": latest_path,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rights_status": "generated",
        "use_scope": "local factory UI, live Blender viewport projection, internal docs",
        "notes": "Local Blender live frame sequence. No paid generation, no external API, no publishing.",
    }
    STATE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mat(name, color, emission=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emission
        bsdf.inputs["Roughness"].default_value = 0.34
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

dark = mat("viewport_floor_dark", (0.01, 0.018, 0.032, 1), 0.0)
cyan = mat("viewport_cyan_emitter", (0.0, 0.9, 1.0, 1), 2.6)
green = mat("viewport_green_status", (0.12, 1.0, 0.55, 1), 1.6)
magenta = mat("viewport_magenta_clip", (1.0, 0.04, 0.86, 1), 1.9)
amber = mat("viewport_amber_gate", (1.0, 0.62, 0.05, 1), 1.4)
metal = mat("viewport_metal_lane", (0.02, 0.08, 0.12, 1), 0.0)

cube("live_floor_grid", (0, 0, -0.08), (8.6, 5.2, 0.08), dark)
cube("live_main_lane", (0, 0, 0.08), (7.2, 0.48, 0.08), metal)
cube("live_blender_screen_left", (-3.8, 0.85, 0.8), (0.14, 1.0, 0.75), cyan)
cube("live_blender_screen_right", (3.8, -0.85, 0.8), (0.14, 1.0, 0.75), magenta)

video_cubes = []
materials = [cyan, green, magenta, amber, cyan]
for index, x in enumerate([-2.8, -1.4, 0, 1.4, 2.8]):
    obj = cube(f"live_video_cube_{index + 1:02d}", (x, 0, 0.46), (0.34, 0.34, 0.34), materials[index])
    video_cubes.append(obj)

rails = []
for x in [-3.2, -1.6, 0.0, 1.6, 3.2]:
    rails.append(cube(f"live_rail_front_{x}", (x, -0.57, 0.2), (0.46, 0.025, 0.025), cyan))
    rails.append(cube(f"live_rail_back_{x}", (x, 0.57, 0.2), (0.46, 0.025, 0.025), cyan))

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0.25))
target = bpy.context.object
target.name = "live_camera_target"

bpy.ops.object.light_add(type="AREA", location=(0, -2.4, 4.2))
bpy.context.object.name = "live_large_softbox"
bpy.context.object.data.energy = 420
bpy.context.object.data.size = 5

for name, location, color in [
    ("live_cyan_beam", (-3.0, 0.0, 2.3), (0.0, 0.8, 1.0)),
    ("live_magenta_beam", (2.7, 1.4, 2.1), (1.0, 0.05, 0.8)),
    ("live_amber_gate", (0.6, -1.6, 1.7), (1.0, 0.55, 0.05)),
]:
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = 140
    light.data.color = color

bpy.ops.object.camera_add(location=(4.7, -4.0, 2.7), rotation=(math.radians(62), 0, math.radians(43)))
camera = bpy.context.object
bpy.context.scene.camera = camera

available_engines = {item.identifier for item in bpy.context.scene.render.bl_rna.properties["engine"].enum_items}
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
if hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 16
bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.view_settings.view_transform = "Filmic"
bpy.context.scene.view_settings.look = "High Contrast"

write_state(0, "", "rendering")

for frame in range(1, FRAME_COUNT + 1):
    phase = frame / FRAME_COUNT
    for index, obj in enumerate(video_cubes):
        obj.location.x = -3.2 + ((index * 1.32 + phase * 4.6) % 6.4)
        obj.location.z = 0.42 + math.sin(phase * math.tau + index) * 0.08
        obj.rotation_euler.z = phase * math.tau + index * 0.32
    for index, rail in enumerate(rails):
        rail.scale.x = 0.28 + 0.22 * (0.5 + 0.5 * math.sin(phase * math.tau * 2 + index))

    camera.location.x = 4.7 + math.sin(phase * math.tau) * 0.34
    camera.location.y = -4.0 + math.cos(phase * math.tau) * 0.28
    camera.rotation_euler = (math.radians(62), 0, math.radians(43 + math.sin(phase * math.tau) * 3.0))

    filename = f"blender_live_{frame:04d}.png"
    output_path = LIVE_DIR / filename
    rel_output_path = output_path.relative_to(ROOT).as_posix()
    bpy.context.scene.render.filepath = str(output_path)
    write_state(frame, rel_output_path, "rendering")
    bpy.ops.render.render(write_still=True)
    write_state(frame, rel_output_path, "rendering" if frame < FRAME_COUNT else "ready")

bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_3D_DIR / "blend" / "codex_factory_live.blend"))
