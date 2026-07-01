# End-to-End Movie Pipeline (重量パス)

用途: 自然言語のブリーフだけから、Blenderプリビズ -> Higgsfield MCP画像絵コンテ -> Higgsfield MCP ElevenLabsナレーション -> Higgsfield MCP Seedance -> Palmier Pro仕上げまでを一気通貫で回す「重量パス」の定義。CM単発・素材差し替えだけで足りる案件は、このファイルを使わず既存の軽量パス(`seedance-cm-workflow.md` の Image-To-Video Route: 参照画像 -> Seedance -> Palmier Pro仕上げ)のままでよい。

## Routing: 軽量パス vs 重量パス

判定基準はどちらか一つでも当てはまるか:

- 複数ショットにわたって同じキャラクター/商品/空間が再登場する
- 起承転結など物語進行がある(短編映画、複数カットのCM)

両方NO -> 軽量パス(このファイルは不要、既存フローのまま)
どちらかYES -> 重量パス(このファイル)

迷う場合は一言ユーザーに確認する。CLIでもUIでもよい。

## 前提

- Blenderのシーン生成は完全自動。エージェントがブリーフからbpyスクリプトを書き、`blender --background --python` で無人実行する。自由な3D世界生成ではなく、手続き型プリミティブ(cube/cylinder/sphere)+マテリアル+カメラキーフレームの組み合わせに範囲を絞る。外部3Dアセットの読み込みは前提にしない。
- 画像生成(絵コンテ)、音声生成(ElevenLabsナレーション)、動画生成(Seedance)はすべてHiggsfield MCP経由。`OPENAI_API_KEY` など個別APIキーは重量パスでは使わない。
- 絵コンテ生成は `workspace/scripts/higgsfield-image.sh` でHiggsfield MCP画像生成リクエストを準備する。モデル名(暫定 `image2`)とBlenderレンダー画像入力(img2img相当)の可否は、Higgsfield MCP接続環境で確認して確定する。
- ナレーションは `workspace/scripts/elevenlabs-narration.sh` でHiggsfield MCP ElevenLabsリクエストを準備する。
- Palmier Proは仕上げ工程に使う。生成系は原則使わないが、`upscale_media` だけは仕上げで使う可能性があるため、呼び出し前にモデル仕様と実行内容を提示してユーザー承認を取る。
- セリフ(カメラ目線で喋るカット)の要否は、その都度ユーザーに自然言語で確認する。デフォルトはナレーション主体(セリフなし)。リップシンクはこのパイプラインのどのツールも解決しない。

## フォルダ規約

重量パスでは、ショットごとに成果物を分ける。軽量パスの既存 `*-v1` 命名は変更しない。

```text
workspace/projects/<project_id>/
  brief.md
  shots/
    <shot_id>/
      previs.blend
      previs.png
      storyboard.png
      narration.mp3
      seedance_prompt.txt
      seedance_output.mp4
      review.json
```

`<project_id>` は英数字、ハイフン、アンダースコアだけにする。`<shot_id>` は `shot_01` のように固定幅で並べる。

## 課金生成ゲート

- Higgsfield画像/音声/Seedance: 既存通り `APPROVED=1`、コスト見積またはモデル確認、ログイン/クレジット確認、ユーザー承認が必要。
- Palmier Pro `upscale_media`: 呼ぶ前に必ず `list_models` で対象モデルの仕様を確認し、対象クリップ、出力品質、費用が発生しうることを自然言語で提示してユーザー承認を取る。
- Palmier Pro `import_media`、`sync_audio`、字幕配置、色調整、`export_project` は生成課金ではないが、公開/書き出し前の人間確認は必要。

## 重量パスのステップ

1. **ブリーフ確定**: 既存Workflowのbrief lock項目に加えて、キャラクター/商品の一貫性要件、想定ショット数、セリフ有無、プロジェクトID、ショットIDを確定する。
2. **Blenderプリビズ(完全自動)**:
   - `references/blender-3d-preview-workflow.md` のフォルダ規約と、このファイルの `workspace/projects/<project_id>/shots/<shot_id>/` 規約に従う。
   - プロジェクトごとに `workspace/blender/<project>_previs.py` を、`workspace/blender/action_movie_previs.py` を土台として新規作成する。
   - Blender有無を先に確認する: `command -v blender`。
   - `blender --background --python workspace/blender/<project>_previs.py` で無人実行する。
   - この `.blend` をプロジェクトの正とする。以降の全ショットは同じシーンファイルから書き出し、キャラクター/商品/カメラの一貫性を担保する。
3. **Higgsfield MCP画像生成で絵コンテ化**: `workspace/scripts/higgsfield-image.sh` を使い、ショットごとのBlenderレンダーpngを `IMAGE_FILE` として渡せるかをMCP側で確認する。入力画像が使えない場合はBlender構図をプロンプトに明記し、結果は内部レビュー用ドラフトとして扱う。
4. **承認ゲート1: 絵コンテ承認**。ここより先に進めない。
5. **セリフ確認**: 「カメラ目線で喋るカットはありますか?」を一度確認する。
   - YES: リップシンクは未解決であることを明示し、(a) 顔アップを避ける演出にする、(b) 専用リップシンクツールを別途検討する、のどちらかをユーザーに選ばせる。
   - NO(デフォルト): ナレーション主体で進める。
6. **ナレーション確定**: `workspace/scripts/elevenlabs-narration.sh` でHiggsfield MCP経由のElevenLabsナレーションMCPリクエストを準備し、ホストのHiggsfield MCPツールで実行する。以降、映像側はこの音声の尺に合わせる(音声が主、映像が従)。
7. **Blender本アニメーション最終化**: 承認済みカットのみ、音声尺に合わせてカメラ・フレーム範囲を確定する。
8. **Higgsfield Seedanceで画づくり**: Blenderの最終レンダーを参照画像として渡すimage-to-video。既存の `workspace/scripts/seedance-cost.sh` / `seedance-generate.sh` を使う。ショットごとに同じ `.blend` 由来の参照画像を使うことで一貫性を保つ。
9. **承認ゲート2: 素材承認**。Seedance投入前に、コスト承認、ログイン/クレジット確認、参照画像、プロンプト、出力先を確認する。
10. **Palmier Proで最終仕上げ**: `import_media` -> `sync_audio` -> 字幕/テロップ配置 -> 色調整 -> 必要なら承認後に `upscale_media` -> `export_project`。
11. **承認ゲート3: 最終書き出し前承認**。

## 一貫性ルール

- Blenderの `.blend` をプロジェクトの正とする。新規シーンを作らず、同じファイル内でオブジェクトを差し替える。
- 各ショットの絵コンテ/Seedance参照画像は同じBlenderシーンから書き出す。
- 画像生成がBlenderレンダーを入力として受けられない場合は、その制限をログに残し、プロンプトで構図を固定する。

## 権利ゲートの拡張

`SKILL.md` の Rights Gate に加えて:

- Blenderの手続き生成物(プリミティブ+マテリアル)は権利リスクが低い。外部GLB/OBJ/HDRIを使う場合は既存のRights Gateと同じ基準を適用する。
- ElevenLabsで実在人物の声を複製する場合、本人の同意が必要。同意が取れない、または不明な場合は既定ライブラリボイスを使う。

## Known limitations(重量パス固有)

- Higgsfield MCPの画像生成モデル名とimg2img対応は未検証。接続環境で最初に確認する。
- リップシンクは未解決。カメラ目線の会話カットは演出で回避するか、別途専用ツールを検討する。
- 音声とBlender/Seedance映像のタイミング合わせは、Palmier Proの `sync_audio` と速度調整に依存する。完全自動同期は保証しない。
- Blenderの自動生成シーンは手続き型プリミティブが中心。写実的な3Dアセットが必要な場合は別途モデリングが必要。
- 課金が発生するのはHiggsfield MCP(画像生成、ElevenLabsナレーション、Seedance生成)とPalmier Proの`upscale_media`。Blenderはローカルのみで課金なし。
