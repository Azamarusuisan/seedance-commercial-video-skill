# End-to-End Movie Pipeline (重量パス)

用途: 自然言語のブリーフだけから、Blenderプリビズ → GPT Image絵コンテ → Higgsfield ElevenLabsナレーション → Higgsfield Seedance → Palmier Pro仕上げまでを一気通貫で回す「重量パス」の定義。CM単発・素材差し替えだけで足りる案件は、このファイルを使わず既存の軽量パス(`seedance-cm-workflow.md` の Image-To-Video Route: 参照画像 → Seedance → Palmier Pro仕上げ)のままでよい。

## Routing: 軽量パス vs 重量パス

判定基準はどちらか一つでも当てはまるか:

- 複数ショットにわたって同じキャラクター/商品/空間が再登場する
- 起承転結など物語進行がある(短編映画、複数カットのCM)

両方NO → 軽量パス(このファイルは不要、既存フローのまま)
どちらかYES → 重量パス(このファイル)

迷う場合は一言ユーザーに確認する。CLIでもUIでもよい。

## 前提

- Blenderのシーン生成は完全自動。エージェントがブリーフからbpyスクリプトを書き、`blender --background --python` で無人実行する。自由な3D世界生成ではなく、手続き型プリミティブ(cube/cylinder/sphere)+マテリアル+カメラキーフレームの組み合わせに範囲を絞る。外部3Dアセットの読み込みは前提にしない。
- 絵コンテ生成(旧称 image2)は GPT Image (`gpt-image-2`) を使う。`workspace/scripts/gpt-image-reference.sh` が既に実装済み。Higgsfield独自の画像モデルではない。
- ElevenLabsはHiggsfield MCP経由で使う(`references/tiktok-story-cast-workflow.md` の "Higgsfield ElevenLabs" と同じ扱い)。ElevenLabsの直接APIキーは持たない、保存しない。
- セリフ(カメラ目線で喋るカット)の要否は、その都度ユーザーに自然言語で確認する。デフォルトはナレーション主体(セリフなし)。リップシンクはこのパイプラインのどのツールも解決しない。

## 重量パスのステップ

1. **ブリーフ確定**: 既存Workflowのbrief lock項目に加えて、キャラクター/商品の一貫性要件、想定ショット数、セリフ有無を確定する。
2. **Blenderプリビズ(完全自動)**:
   - `references/blender-3d-preview-workflow.md` のフォルダ規約に従う。
   - プロジェクトごとに `workspace/blender/<project>_previs.py` を、`workspace/blender/action_movie_previs.py` を土台として新規作成する。
   - Blender有無を先に確認する: `command -v blender`。
   - `blender --background --python workspace/blender/<project>_previs.py` で無人実行する。
   - この `.blend` をプロジェクトの正とする。以降の全ショットは同じシーンファイルから書き出し、キャラクター/商品/カメラの一貫性を担保する(AI動画生成単体の弱点である「ショットごとのブレ」をここで吸収する)。
3. **GPT Imageで絵コンテ化**: Blenderプリビズの構図を言語化したプロンプトを `workspace/scripts/gpt-image-reference.sh` に渡し、ショットごとの絵コンテ静止画を作る。
4. **承認ゲート1: 絵コンテ承認**。ここまでは低コストなので、修正はここで吸収する。ここより先に進めない。
5. **セリフ確認**: 「カメラ目線で喋るカットはありますか?」を一度確認する。
   - YES: リップシンクは未解決であることを明示し、(a) 顔アップを避ける演出にする、(b) 専用リップシンクツールを別途検討する、のどちらかをユーザーに選ばせる。
   - NO(デフォルト): ナレーション主体で進める。
6. **ナレーション確定**: `workspace/scripts/elevenlabs-narration.sh` でHiggsfield MCP経由のElevenLabsナレーションMCPリクエストを準備し、ホストのHiggsfield MCPツールで実行する。以降、映像側はこの音声の尺に合わせる(音声が主、映像が従)。
7. **Blender本アニメーション最終化**: 承認済みカットのみ、音声尺に合わせてカメラ・フレーム範囲を確定する。
8. **Higgsfield Seedanceで画づくり**: Blenderの最終レンダーを参照画像として渡すimage-to-video。既存の `workspace/scripts/seedance-cost.sh` / `seedance-generate.sh` をそのまま使う。ショットごとに同じ `.blend` 由来の参照画像を使うことで一貫性を保つ。
9. **承認ゲート2: 素材承認**(既存のHuman Gateと同じ位置、Seedance投入前。コスト承認・ログイン/クレジット確認を含む)。
10. **Palmier Proで最終仕上げ**: `sync_audio` → `add_captions` → `apply_color` → `upscale_media` → `export_project`。
11. **承認ゲート3: 最終書き出し前承認**。

## 一貫性ルール

- Blenderの `.blend` をプロジェクトの正とする。新規シーンを作らず、同じファイル内でオブジェクトを差し替える。
- 各ショットのSeedance参照画像は同じBlenderシーンから書き出す。

## 権利ゲートの拡張

`SKILL.md` の Rights Gate に加えて:

- Blenderの手続き生成物(プリミティブ+マテリアル)は権利リスクが低い。外部GLB/OBJ/HDRIを使う場合は既存のRights Gateと同じ基準を適用する。
- ElevenLabsで実在人物の声を複製する場合、本人の同意が必要。同意が取れない、または不明な場合は既定ライブラリボイスを使う。

## Known limitations(重量パス固有)

- リップシンクは未解決。カメラ目線の会話カットは演出で回避するか、別途専用ツールを検討する。
- 音声とBlender/Seedance映像のタイミング合わせは、Palmier Proの `sync_audio` と手動の速度調整に依存する。完全自動同期は保証しない。
- Blenderの自動生成シーンは手続き型プリミティブが中心。写実的な3Dアセットが必要な場合は別途モデリングが必要。
- 課金が発生するのはHiggsfield MCP(Seedance生成、ElevenLabsナレーション)とGPT Image APIのみ。Blenderはローカルのみで課金なし。
