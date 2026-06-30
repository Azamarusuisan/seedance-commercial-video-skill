import json
import math
import time
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
ASSET_3D_DIR = ROOT / "workspace" / "assets" / "3d"
RENDER_DIR = ASSET_3D_DIR / "renders"
BLEND_DIR = ASSET_3D_DIR / "blend"
MANIFEST_DIR = ASSET_3D_DIR / "manifests"
LIVE_DIR = ASSET_3D_DIR / "live"

for path in [RENDER_DIR, BLEND_DIR, MANIFEST_DIR, LIVE_DIR]:
    path.mkdir(parents=True, exist_ok=True)


def make_mat(name, color, emission=0.0, roughness=0.42, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emission
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return material


def cube(name, location, scale, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def cylinder(name, location, radius, depth, material, rotation=(0, 0, 0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def sphere(name, location, radius, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def aim_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

dark = make_mat("action_asphalt_dark", (0.006, 0.009, 0.018, 1), 0.0, 0.58)
steel = make_mat("action_gunmetal", (0.03, 0.045, 0.06, 1), 0.0, 0.36, 0.5)
cyan = make_mat("action_cyan_neon", (0.0, 0.78, 1.0, 1), 3.0, 0.18)
magenta = make_mat("action_magenta_neon", (1.0, 0.02, 0.72, 1), 2.7, 0.2)
amber = make_mat("action_amber_blast", (1.0, 0.52, 0.05, 1), 4.6, 0.25)
red = make_mat("action_warning_red", (1.0, 0.03, 0.05, 1), 3.2, 0.2)
hero_mat = make_mat("action_hero_black_suit", (0.01, 0.015, 0.022, 1), 0.0, 0.26, 0.35)
visor_mat = make_mat("action_hero_blue_visor", (0.08, 0.9, 1.0, 1), 2.5, 0.15)

# City base and road lanes.
cube("雨上がりの高速道路", (0, 0, -0.08), (11.5, 5.2, 0.08), dark)
for y in [-1.15, 0, 1.15]:
    cube(f"ネオン車線_{y}", (0, y, 0.015), (10.8, 0.035, 0.012), cyan if y else magenta)
for x in [-4.8, -3.4, -2.0, -0.6, 0.8, 2.2, 3.6, 5.0]:
    cube(f"反射マーカー_{x}", (x, -0.02, 0.04), (0.22, 0.035, 0.018), amber)

# Skyscraper silhouettes.
for index, x in enumerate([-5.2, -4.0, -2.8, -1.6, 1.8, 3.0, 4.2, 5.4]):
    height = 1.8 + (index % 4) * 0.55
    y = 2.45 if index < 4 else -2.55
    building = cube(f"都市ビル_{index+1:02d}", (x, y, height / 2), (0.48, 0.32, height / 2), steel)
    for floor in range(3, int(height * 4)):
        if floor % 2 == index % 2:
            cube(f"ビル窓_{index+1:02d}_{floor:02d}", (x, y + (0.34 if y < 0 else -0.34), floor * 0.22), (0.18, 0.015, 0.018), cyan if index % 2 else magenta)

# Hero, enemy vehicle, drones, blast.
hero_body = cylinder("主役スタント_黒い戦闘スーツ", (-1.25, -0.05, 0.64), 0.14, 0.72, hero_mat)
hero_body.rotation_euler[1] = math.radians(18)
hero_head = sphere("主役_ヘルメット", (-1.42, -0.06, 1.08), 0.18, hero_mat)
cube("主役_青いバイザー", (-1.57, -0.06, 1.11), (0.035, 0.18, 0.045), visor_mat)
cube("主役_伸びる左腕", (-1.14, -0.43, 0.76), (0.42, 0.04, 0.04), hero_mat, rotation=(0, 0, math.radians(-28)))
cube("主役_伸びる右腕", (-1.04, 0.26, 0.78), (0.38, 0.04, 0.04), hero_mat, rotation=(0, 0, math.radians(24)))
cube("主役_ジャンプ軌道ライト", (-1.02, -0.02, 0.26), (0.82, 0.025, 0.025), cyan, rotation=(0, math.radians(10), math.radians(8)))

cube("追跡車_装甲バイク本体", (1.3, 0.42, 0.36), (0.72, 0.24, 0.18), steel, rotation=(0, 0, math.radians(-8)))
cylinder("追跡車_前輪", (0.78, 0.50, 0.2), 0.16, 0.08, red, rotation=(math.radians(90), 0, 0))
cylinder("追跡車_後輪", (1.86, 0.34, 0.2), 0.16, 0.08, red, rotation=(math.radians(90), 0, 0))
cube("追跡車_赤いライト", (0.67, 0.51, 0.39), (0.08, 0.14, 0.03), red)

for index, (x, y, z) in enumerate([(-2.55, 0.72, 1.55), (0.25, -1.35, 1.35), (2.75, 1.08, 1.62)]):
    drone = cube(f"追跡ドローン_{index+1:02d}", (x, y, z), (0.18, 0.18, 0.06), steel)
    cube(f"ドローン発光_{index+1:02d}", (x, y, z + 0.07), (0.13, 0.13, 0.018), magenta if index == 1 else cyan)
    for arm_x, arm_y in [(0.24, 0.24), (-0.24, 0.24), (0.24, -0.24), (-0.24, -0.24)]:
        cylinder(f"ドローンローター_{index+1:02d}_{arm_x}_{arm_y}", (x + arm_x, y + arm_y, z), 0.08, 0.018, cyan, vertices=20)

sphere("爆発の芯", (2.78, -0.92, 0.44), 0.16, amber)
for angle in range(0, 360, 30):
    cube(f"爆発スパーク_{angle}", (2.78, -0.92, 0.44), (0.025, 0.025, 0.42), amber, rotation=(math.radians(82), 0, math.radians(angle)))

# Camera and lighting.
bpy.ops.object.light_add(type="AREA", location=(0.0, -3.4, 4.6))
softbox = bpy.context.object
softbox.name = "巨大ソフトボックス_夜景反射"
softbox.data.energy = 520
softbox.data.size = 5.8

for name, location, color, energy in [
    ("青い追跡ライト", (-3.4, -1.5, 2.4), (0.0, 0.8, 1.0), 450),
    ("赤い警告ライト", (2.9, 1.2, 1.9), (1.0, 0.05, 0.04), 260),
    ("爆発ライト", (2.55, -0.82, 0.8), (1.0, 0.42, 0.05), 620),
]:
    bpy.ops.object.light_add(type="POINT", location=location)
    light = bpy.context.object
    light.name = name
    light.data.color = color
    light.data.energy = energy

bpy.ops.object.camera_add(location=(6.8, -5.6, 3.35))
camera = bpy.context.object
camera.name = "手持ち風アクションカメラ"
aim_at(camera, (0.25, -0.08, 0.62))
bpy.context.scene.camera = camera

available_engines = {item.identifier for item in bpy.context.scene.render.bl_rna.properties["engine"].enum_items}
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
if hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 32
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.view_settings.view_transform = "Filmic"
bpy.context.scene.view_settings.look = "High Contrast"

# Add simple animation keyframes so the open Blender file visibly has action timing.
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 96
for frame, x in [(1, -1.6), (48, -0.6), (96, 0.85)]:
    bpy.context.scene.frame_set(frame)
    hero_body.location.x = x
    hero_body.keyframe_insert(data_path="location")
for frame, x in [(1, 2.3), (48, 1.25), (96, -0.15)]:
    bpy.context.scene.frame_set(frame)
    bpy.data.objects["追跡車_装甲バイク本体"].location.x = x
    bpy.data.objects["追跡車_装甲バイク本体"].keyframe_insert(data_path="location")
for frame, loc in [(1, (6.8, -5.6, 3.35)), (48, (5.25, -4.35, 2.75)), (96, (3.7, -3.4, 2.15))]:
    bpy.context.scene.frame_set(frame)
    camera.location = loc
    aim_at(camera, (0.25, -0.08, 0.62))
    camera.keyframe_insert(data_path="location")
    camera.keyframe_insert(data_path="rotation_euler")

bpy.context.scene.frame_set(36)
render_path = RENDER_DIR / "action_movie_previs.png"
bpy.context.scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

blend_path = BLEND_DIR / "action_movie_previs.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

manifest = {
    "id": "action_movie_previs",
    "title": "3Dアクション映画プリビズ",
    "status": "ready",
    "local_only": True,
    "paid_generation_executed": False,
    "blend_path": str(blend_path.relative_to(ROOT)),
    "render_path": str(render_path.relative_to(ROOT)),
    "scene": "Night cyber city chase, hero stunt, drones, armored bike, explosion light.",
    "use_scope": "Seedance/Higgsfield visual reference and local Factory UI preview only.",
    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
manifest_path = MANIFEST_DIR / "action_movie_previs.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

live_state_path = LIVE_DIR / "live-state.json"
live_state_path.write_text(json.dumps({
    "id": "action_movie_previs",
    "name": "3Dアクション映画プリビズ",
    "status": "ready",
    "latest_frame": str(render_path.relative_to(ROOT)),
    "updated_at": manifest["updated_at"],
    "rights_status": "generated_local",
    "use_scope": manifest["use_scope"],
    "notes": "Local Blender preview. No paid generation, no external API, no publishing.",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
