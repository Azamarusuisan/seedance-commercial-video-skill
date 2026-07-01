# Brand Assets (自社素材ライブラリ)

自社所有のロゴ・商品写真・過去のキャンペーン素材・ブランドガイドをここに置く。**ローカルのみ。外部クラウドDB(Supabase等)には接続しない。** セキュリティ上、素材の実体は常にこのリポジトリのローカルファイルシステム上に留める。

`workspace/assets/cast/`(TikTok/劇場キャスト用)と同じマニフェスト方式を、会社の素材全般に一般化したもの。

## フォルダ構成

```text
workspace/assets/brand/
  logos/           ロゴ
  products/        商品写真
  campaigns/       過去の承認済みキャンペーン素材(スチール/映像)
  guidelines/      ブランドガイド(色・フォント・トーン。テキスト/PDF/画像)
  brand-manifest.json
```

画像/動画ファイル(png/jpg/jpeg/webp/mp4/mov)は`.gitignore`でデフォルト除外される(このリポジトリのGit履歴には乗らない、ローカルのみ)。`.md`/`.json`/`.gitkeep`は追跡対象。

## マニフェスト

`brand-manifest.example.json`を土台に、プロジェクト固有の`brand-manifest.json`を作る。

## rights_status について

自社所有素材は`rights_status: "company_owned"`を使う。これは第三者権利の懸念がない最優先の参照元であることを示す。他の値(`generated`/`user_provided`/`unknown`)との違い:

- `company_owned`: 自社が権利を持つ素材。Rights Gateを気にせず最優先で使える。
- `generated`: AIが生成した素材。権利リスクは低いが自社所有ではない。
- `user_provided`: ユーザーがその場で提供した素材。都度の権利確認が必要。
- `unknown`: 権利不明。内部ドラフト用途に限定する。

## 使い方

ブリーフロック時の「参照素材の有無」確認では、まずこのフォルダの`brand-manifest.json`を見に行く。ロゴ・商品写真・過去のキャンペーン素材があれば、生成した参照画像より優先して使う(実在の自社資産のほうが権利面・ブランド一貫性の両方で望ましい)。
