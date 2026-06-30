# Blender / 3D Preview Lane

用途: Seedance / Higgsfield の生成前後に、ローカルBlenderで3Dプレビュー、工場フロア風の背景、GLB/OBJ素材、カメラパス、ライティング、簡易レンダーを扱うための参照。

## Scope

扱うこと:

- ローカルBlenderを使った3Dプレビュー
- 生成工場UIや説明動画用の3D風背景素材
- GLB / OBJ / FBX / USDZ などの読み込み確認
- カメラパス、ライト、マテリアル、簡易レンダー
- Seedanceへ渡すための静止画参照や背景plateの作成
- Higgsfieldのimage-to-3D / multi-image-to-3D成果物をローカル確認する導線

扱わないこと:

- Blender未インストール環境での実レンダー
- 外部3D素材の権利確認なし利用
- 課金生成や外部API実行
- 最終広告公開判断

## Activation

ユーザーが次を言ったらこのレーンを検討する。

- Blenderかける
- Blenderで回す
- 3Dで確認
- GLBにする
- 工場フロアを3Dっぽくしたい
- 生成前にカメラやライティングを見たい
- Higgsfieldの3D素材を確認したい
- Seedanceに渡す背景plateをBlenderで作りたい

## Preflight

必ず確認する。

```bash
command -v blender
ls /Applications | rg -i '^Blender'
```

Blenderがなければ実行せず、次のどちらかにする。

- CSS/HTML/SVG/Three.jsでプレビュー
- Higgsfield 3D生成や画像生成で参照素材を作る

## Folder Rules

Blender関連は以下に保存する。

```text
workspace/assets/3d/
workspace/assets/3d/source/
workspace/assets/3d/renders/
workspace/assets/3d/blend/
workspace/assets/3d/manifests/
```

推奨manifest:

```json
{
  "id": "",
  "name": "",
  "type": "blend | glb | render | plate | camera_path",
  "path": "",
  "thumbnail_path": "",
  "source_asset": "",
  "rights_status": "generated | user_provided | internal_draft | blocked",
  "use_scope": "",
  "created_at": "",
  "review_status": "pending | approved | blocked",
  "notes": ""
}
```

## Workflow

1. 目的を決める。
   - UI背景
   - Seedance参照plate
   - 生成物レビュー
   - 説明動画用素材
   - 商品/キャラ/空間の3D確認
2. 権利と利用範囲を確認する。
3. Blender有無を確認する。
4. 入力素材を `workspace/assets/3d/source/` に置く。
5. `.blend` は `workspace/assets/3d/blend/` に保存する。
6. プレビュー画像/動画は `workspace/assets/3d/renders/` に保存する。
7. `workspace/assets/3d/manifests/` に登録する。
8. 生成工場UIの asset library に source capture / 3D render として登録する。

## Generation Factory UIへの反映

Blender laneを使う場合、UIでは次のように出す。

- `BLENDER LANE: available / unavailable`
- `3D Preview: pending / rendering / ready / blocked`
- `Local render only`
- `No paid generation executed`

Blenderがない場合も、UIには `Blender unavailable` と出し、代替のCSS/Three.js/Higgsfield 3D案を提示する。

## Safety

- Blender処理はローカルのみ。
- 外部APIや課金生成はしない。
- 権利不明の3D素材を本番広告素材にしない。
- 実在ブランド、人物、施設、キャラクターに似せた3D素材は権利確認に止める。
- レンダー完了と動画生成完了を混同しない。
