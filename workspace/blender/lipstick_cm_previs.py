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

for path in [RENDER_DIR, BLEND_DIR, MANIFEST_DIR]:
    path.mkdir(parents=True, exist_ok=True)


def set_input(node, name, value):
    if node and name in node.inputs:
        node.inputs[name].default_value = value


def make_mat(name, color, emission=0.0, roughness=0.34, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Emission Color", color)
    set_input(bsdf, "Emission Strength", emission)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Metallic", metallic)
    return material


def cylinder(name, location, radius, depth, material, rotation=(0, 0, 0), vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def cone(name, location, radius1, radius2, depth, material, rotation=(0, 0, 0), vertices=96):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def cube(name, location, scale, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def sphere(name, location, radius, material, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=12, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def torus(name, location, major_radius, minor_radius, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=128,
        minor_segments=12,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def aim_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(name, location, target, lens):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = name
    camera.data.lens = lens
    aim_at(camera, target)
    return camera


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

black_lacquer = make_mat("lipstick_black_lacquer", (0.004, 0.003, 0.006, 1), 0.0, 0.18, 0.2)
deep_red = make_mat("lipstick_deep_noir_red", (0.33, 0.0, 0.035, 1), 0.0, 0.22, 0.0)
gold = make_mat("lipstick_champagne_gold", (1.0, 0.68, 0.28, 1), 0.0, 0.2, 0.85)
dark = make_mat("lipstick_dark_background", (0.002, 0.002, 0.006, 1), 0.0, 0.62, 0.0)
soft_gold = make_mat("lipstick_soft_gold_glow", (1.0, 0.72, 0.33, 1), 5.0, 0.26, 0.0)
hot_red = make_mat("lipstick_red_energy_glow", (1.0, 0.0, 0.12, 1), 2.8, 0.16, 0.0)
soft_white = make_mat("lipstick_softbox_reflection", (1.0, 0.82, 0.66, 1), 4.0, 0.18, 0.0)

# Minimal premium product-previs: primitive geometry only, no external assets.
cylinder("ROUGE_NOIR_body_black_lacquer", (0, 0, 1.0), 0.34, 1.8, black_lacquer)
cylinder("ROUGE_NOIR_gold_ring_lower", (0, 0, 1.86), 0.355, 0.12, gold)
cylinder("ROUGE_NOIR_gold_ring_upper", (0, 0, 2.02), 0.31, 0.16, gold)
cylinder("ROUGE_NOIR_inner_tube_gold", (0, 0, 2.38), 0.24, 0.78, gold)
cone("ROUGE_NOIR_lip_color_bullet", (0, 0, 3.0), 0.22, 0.08, 0.74, deep_red)

cap = cylinder("ROUGE_NOIR_cap_lifted_black_lacquer", (-0.52, 0.05, 2.88), 0.36, 1.35, black_lacquer, rotation=(0, math.radians(12), math.radians(-8)))
cylinder("ROUGE_NOIR_cap_gold_edge", (-0.52, 0.05, 2.18), 0.365, 0.08, gold, rotation=(0, math.radians(12), math.radians(-8)))

cube("matte_black_plinth", (0, 0, -0.08), (1.2, 1.2, 0.08), dark)
cube("champagne_reflection_line", (0, -0.47, 0.04), (1.0, 0.018, 0.012), soft_gold)
cube("vertical_shadow_panel", (0, 0.48, 1.5), (1.6, 0.035, 1.6), dark)
cube("deep_black_background_wall", (0, 0.9, 1.8), (3.4, 0.05, 2.4), dark)
cube("cinema_floor_reflection", (0, -0.05, -0.13), (2.3, 2.2, 0.02), black_lacquer)

for angle, radius, height in [(18, 1.0, 1.0), (42, 1.28, 1.5), (-24, 1.08, 0.76)]:
    x = math.sin(math.radians(angle)) * radius
    y = -0.68 - math.cos(math.radians(angle)) * 0.12
    cube(f"soft_gold_specular_card_{angle}", (x, y, height), (0.012, 0.02, 0.52), soft_gold, rotation=(0, 0, math.radians(angle)))

for index in range(44):
    angle = index * 137.5
    radius = 0.55 + (index % 9) * 0.05
    z = 0.45 + (index % 13) * 0.18
    x = math.sin(math.radians(angle)) * radius
    y = -0.2 + math.cos(math.radians(angle)) * 0.42
    mat = soft_gold if index % 3 else hot_red
    sphere(f"floating_luxury_particle_{index:02d}", (x, y, z), 0.012 + (index % 3) * 0.004, mat, segments=12)

for index, z in enumerate([0.88, 1.38, 2.08]):
    ring = torus(
        f"cinematic_orbit_light_ring_{index+1}",
        (0, -0.04, z),
        0.58 + index * 0.08,
        0.006,
        soft_gold if index != 1 else hot_red,
        rotation=(math.radians(78), math.radians(index * 7), math.radians(18 + index * 35)),
    )
    ring.scale.x = 0.72

for index, x in enumerate([-0.74, 0.72]):
    cube(f"anamorphic_vertical_light_blade_{index+1}", (x, -0.58, 1.15), (0.015, 0.012, 0.78), soft_gold)

bpy.ops.object.light_add(type="AREA", location=(0.8, -2.4, 4.1))
key = bpy.context.object
key.name = "large_softbox_champagne_key"
key.data.energy = 780
key.data.size = 4.4
key.data.color = (1.0, 0.82, 0.58)

bpy.ops.object.light_add(type="AREA", location=(-1.7, -1.4, 2.3))
rim = bpy.context.object
rim.name = "gold_rim_light"
rim.data.energy = 900
rim.data.size = 1.6
rim.data.color = (1.0, 0.63, 0.22)

camera = add_camera("camera_03_hero_vfx_packshot", (1.55, -7.2, 2.15), (0, 0, 1.72), 52)
bpy.context.scene.camera = camera
shot_cameras = [
    ("panel_01_silhouette", add_camera("camera_01_silhouette_hook", (-0.95, -5.3, 1.48), (0, 0, 1.45), 76), 1),
    ("panel_02_cap_macro", add_camera("camera_02_cap_macro_reveal", (0.58, -4.25, 2.42), (-0.16, 0.0, 2.32), 92), 42),
    ("panel_03_hero_vfx", camera, 66),
    ("panel_04_negative_space_tag", add_camera("camera_04_final_negative_space", (-1.8, -6.6, 1.72), (0, 0, 1.55), 48), 96),
]

available_engines = {item.identifier for item in bpy.context.scene.render.bl_rna.properties["engine"].enum_items}
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in available_engines else "BLENDER_EEVEE"
if hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 64

bpy.context.scene.render.resolution_x = 1080
bpy.context.scene.render.resolution_y = 1920
bpy.context.scene.view_settings.view_transform = "Filmic"
bpy.context.scene.view_settings.look = "High Contrast"
bpy.context.scene.world.color = (0.0, 0.0, 0.0)

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 96
for frame, z in [(1, 2.35), (48, 2.72), (96, 3.04)]:
    bpy.context.scene.frame_set(frame)
    cap.location.z = z
    cap.keyframe_insert(data_path="location")
for frame, z_rot in [(1, 0), (48, math.radians(8)), (96, math.radians(16))]:
    bpy.context.scene.frame_set(frame)
    bpy.data.objects["ROUGE_NOIR_body_black_lacquer"].rotation_euler[2] = z_rot
    bpy.data.objects["ROUGE_NOIR_body_black_lacquer"].keyframe_insert(data_path="rotation_euler")

panel_paths = []
for panel_name, panel_camera, panel_frame in shot_cameras:
    bpy.context.scene.frame_set(panel_frame)
    bpy.context.scene.camera = panel_camera
    panel_path = RENDER_DIR / f"lipstick_cm_{panel_name}.png"
    bpy.context.scene.render.filepath = str(panel_path)
    bpy.ops.render.render(write_still=True)
    panel_paths.append(panel_path)

bpy.context.scene.frame_set(66)
bpy.context.scene.camera = camera
render_path = RENDER_DIR / "lipstick_cm_previs.png"
bpy.context.scene.render.filepath = str(render_path)
bpy.ops.render.render(write_still=True)

blend_path = BLEND_DIR / "lipstick_cm_previs.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

manifest = {
    "id": "lipstick_cm_previs",
    "title": "新作リップCM Blenderプリビズ",
    "status": "ready",
    "local_only": True,
    "paid_generation_executed": False,
    "blend_path": str(blend_path.relative_to(ROOT)),
    "render_path": str(render_path.relative_to(ROOT)),
    "storyboard_panels": [str(path.relative_to(ROOT)) for path in panel_paths],
    "scene": "Premium lipstick product-previs with black lacquer, champagne gold rim light, deep red bullet, floating particles, anamorphic light blades, orbit glow rings, and four camera cuts.",
    "use_scope": "Seedance image-to-video reference plate and local Factory UI review only.",
    "rights_status": "generated_local",
    "source_brief": "workspace/briefs/lipstick-cm-30s-script.md",
    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}
manifest_path = MANIFEST_DIR / "lipstick_cm_previs.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
