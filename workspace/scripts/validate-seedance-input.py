#!/usr/bin/env python3
"""Blocks disallowed assets (Blender previs, viewport screenshots, unapproved/rights-unknown
material) from becoming a Seedance primary image (start_image/end_image). See
references/known-failure-patterns.md FP-001. Never runs generation itself; exits 0/1 only."""

import argparse
import json
import sys
from pathlib import Path

ALLOWED_ASSET_KINDS = {
    "approved_storyboard_frame",
    "photoreal_key_visual",
    "rights_confirmed_user_asset",
    "approved_product_reference",
}

BLOCKED_ASSET_KINDS = {"blender_previs", "viewport_screenshot", "blender_render"}

# Heuristic fallback when no --asset-manifest is given (older/lighter projects that
# predate this gate). Never trust an image at these paths as a Seedance primary input,
# manifest or not.
BLOCKED_PATH_HINTS = (
    "workspace/assets/3d/renders/",
    "workspace/assets/3d/blend/",
    "workspace/assets/3d/live/",
    "blender",
    "viewport",
    "previs",
    "blockout",
    "panel_",
)


def fail(reason: str) -> None:
    print(f"[ブロック] {reason}", file=sys.stderr)
    sys.exit(1)


def warn(reason: str) -> None:
    print(f"[警告] {reason}", file=sys.stderr)


def load_json(path: str, label: str) -> dict:
    if not path:
        fail(f"{label} が指定されていません。Seedance前にはmanifest/preflight/permissionが必須です。")
    p = Path(path)
    if not p.is_file():
        fail(f"{label} が見つかりません: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{label} のJSONが壊れています: {path} ({exc})")
        return {}


def parse_preflight(path: str) -> None:
    if not path:
        fail("learning_preflight が指定されていません。pre-generation-learning-check.pyを先に実行してください。")
    p = Path(path)
    if not p.is_file():
        fail(f"learning_preflight が見つかりません: {path}")
    text = p.read_text(encoding="utf-8")
    if "can_prepare_seedance_request: true" not in text:
        fail(f"learning_preflight がSeedance準備を許可していません: {path}")


def check_permission(permission: dict, require_generation: bool) -> None:
    actions = permission.get("allowed_actions", {})
    asset_rules = permission.get("asset_rules", {})
    if asset_rules.get("allow_blender_as_seedance_input") is not False:
        fail("permission manifestで allow_blender_as_seedance_input=false が確認できません。")
    if asset_rules.get("require_approved_storyboard_frame") is not True:
        fail("permission manifestで require_approved_storyboard_frame=true が確認できません。")
    if actions.get("prepare_seedance_cost_request") is not True and actions.get("prepare_seedance_generation_request") is not True:
        fail("permission manifestでSeedance request preparationが許可されていません。")
    if require_generation and actions.get("execute_paid_generation") is not True:
        fail("permission manifestで execute_paid_generation=true が確認できません。")


def check_manifest(image_path: str, manifest: dict, learning_preflight: str) -> None:
    manifest_image = manifest.get("path") or manifest.get("source_path")
    asset_kind = manifest.get("asset_kind")
    role = manifest.get("role")
    seedance_input_allowed = manifest.get("seedance_input_allowed")
    approval_status = manifest.get("approval_status")
    rights_status = manifest.get("rights_status")
    known_failure_checked_at = manifest.get("known_failure_checked_at")
    learning_preflight = learning_preflight or manifest.get("learning_preflight") or manifest.get("learning_preflight_path")

    if manifest_image and Path(manifest_image).as_posix() != Path(image_path).as_posix():
        fail(f"asset manifestの画像パスと --image が一致しません: manifest={manifest_image} image={image_path}")
    if asset_kind in BLOCKED_ASSET_KINDS:
        fail(
            f"asset_kind='{asset_kind}' はSeedanceの主参照として使用禁止です。Blenderは構図参照"
            "(composition_only)専用で、写実キービジュアル生成(GPT Image等)を経由する必要があります"
            f"(references/known-failure-patterns.md FP-001)。画像: {image_path}"
        )
    if role == "composition_only":
        fail(f"role='composition_only' の素材はSeedanceの主参照にできません(構図参照専用): {image_path}")
    if role != "visual_truth":
        fail(f"role='{role}'。Seedanceの主参照には role='visual_truth' が必要です: {image_path}")
    if seedance_input_allowed is not True:
        fail(
            f"seedance_input_allowed=true ではありません(現在値: {seedance_input_allowed!r})。"
            f"この素材はSeedanceに渡せません: {image_path}"
        )
    if approval_status != "approved":
        fail(f"approval_status='{approval_status}'。ユーザーによる明示承認(approved)が必要です: {image_path}")
    if rights_status == "unknown" or not rights_status:
        fail(f"rights_status='unknown'。権利不明の素材はSeedanceの主参照にできません: {image_path}")
    if not known_failure_checked_at:
        fail(f"known_failure_checked_at がありません。known-failure-patterns.md確認後にmanifestへ記録してください: {image_path}")
    parse_preflight(learning_preflight)
    if asset_kind not in ALLOWED_ASSET_KINDS:
        fail(
            f"asset_kind='{asset_kind}' は許可リストにありません。許可されているのは: "
            f"{', '.join(sorted(ALLOWED_ASSET_KINDS))} / 画像: {image_path}"
        )
    print(
        f"[許可] {image_path} はSeedanceの主参照として使用できます "
        f"(asset_kind={asset_kind}, rights_status={rights_status})。"
    )


def check_heuristic_only(image_path: str) -> None:
    """No asset-manifest was given. Fall back to a path heuristic so Blender renders can
    never slip through silently, but don't hard-block unrelated images from projects that
    predate this gate."""
    normalized = image_path.replace("\\", "/").lower()
    for hint in BLOCKED_PATH_HINTS:
        if hint in normalized:
            fail(
                f"アセットマニフェストがなく、パスがBlenderプリビズ/レンダーらしき場所を指しています: "
                f"{image_path}。写実キービジュアルを生成・承認してから、そのファイルを"
                f"asset_kind='photoreal_key_visual' のasset-manifest付きで渡してください"
                "(references/known-failure-patterns.md FP-001)。"
            )
    warn(
        f"アセットマニフェストが指定されていません: {image_path}。"
        "後方互換のため許可しますが、今後は --asset-manifest を用意することを推奨します"
        "(workspace/schemas/asset-manifest.schema.json)。"
    )
    print(f"[許可・マニフェストなし] {image_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--asset-manifest", default="")
    parser.add_argument("--learning-preflight", default="")
    parser.add_argument("--permission-manifest", default="")
    parser.add_argument("--require-paid-generation-permission", action="store_true")
    parser.add_argument(
        "--allow-missing-image",
        action="store_true",
        help="Skip the image-file-exists check (for dry-run/test invocations against fixture paths).",
    )
    args = parser.parse_args()

    if not args.allow_missing_image and not Path(args.image).is_file():
        fail(f"画像ファイルが見つかりません: {args.image}")

    if args.asset_manifest:
        manifest = load_json(args.asset_manifest, "asset manifest")
        check_manifest(args.image, manifest, args.learning_preflight)
        if args.permission_manifest or args.require_paid_generation_permission:
            permission = load_json(args.permission_manifest, "permission manifest")
            check_permission(permission, args.require_paid_generation_permission)
    else:
        check_heuristic_only(args.image)

    sys.exit(0)


if __name__ == "__main__":
    main()
