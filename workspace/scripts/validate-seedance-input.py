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
    "previs",
    "blockout",
)


def fail(reason: str) -> None:
    print(f"[ブロック] {reason}", file=sys.stderr)
    sys.exit(1)


def warn(reason: str) -> None:
    print(f"[警告] {reason}", file=sys.stderr)


def check_manifest(image_path: str, manifest: dict) -> None:
    asset_kind = manifest.get("asset_kind")
    role = manifest.get("role")
    seedance_input_allowed = manifest.get("seedance_input_allowed")
    approval_status = manifest.get("approval_status")
    rights_status = manifest.get("rights_status")

    if asset_kind in BLOCKED_ASSET_KINDS:
        fail(
            f"asset_kind='{asset_kind}' はSeedanceの主参照として使用禁止です。Blenderは構図参照"
            "(composition_only)専用で、写実キービジュアル生成(GPT Image等)を経由する必要があります"
            f"(references/known-failure-patterns.md FP-001)。画像: {image_path}"
        )
    if role == "composition_only":
        fail(f"role='composition_only' の素材はSeedanceの主参照にできません(構図参照専用): {image_path}")
    if seedance_input_allowed is not True:
        fail(
            f"seedance_input_allowed=true ではありません(現在値: {seedance_input_allowed!r})。"
            f"この素材はSeedanceに渡せません: {image_path}"
        )
    if approval_status != "approved":
        fail(f"approval_status='{approval_status}'。ユーザーによる明示承認(approved)が必要です: {image_path}")
    if rights_status == "unknown":
        fail(f"rights_status='unknown'。権利不明の素材はSeedanceの主参照にできません: {image_path}")
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
    parser.add_argument(
        "--allow-missing-image",
        action="store_true",
        help="Skip the image-file-exists check (for dry-run/test invocations against fixture paths).",
    )
    args = parser.parse_args()

    if not args.allow_missing_image and not Path(args.image).is_file():
        fail(f"画像ファイルが見つかりません: {args.image}")

    if args.asset_manifest:
        manifest_path = Path(args.asset_manifest)
        if not manifest_path.is_file():
            fail(f"アセットマニフェストが見つかりません: {manifest_path}")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"アセットマニフェストのJSONが壊れています: {manifest_path} ({exc})")
            return
        check_manifest(args.image, manifest)
    else:
        check_heuristic_only(args.image)

    sys.exit(0)


if __name__ == "__main__":
    main()
