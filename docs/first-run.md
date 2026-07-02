# Studio v2 First Run

Codexでは有料生成・MCP実行・外部投稿をしない。初回スモークは人間が最小条件で実行する。

1. `bash studio/tests/self_audit.sh` を実行し、`SELF-AUDIT: ALL GREEN` を確認する。
2. 人間が対象プロジェクトの `permission.json` を編集する。
   - `seedance_generate: true`
   - `cap_usd: <最小額>`
   - `max_takes_per_shot: 1`
3. **1ショット・4〜5秒・最低解像度**の契約1本だけで `python3 -m studio generate ...` を実行する。
   - 冪等キー
   - 予算計上
   - QC
   - take記録
   を確認する。
4. 結果を `python3 -m studio review ...` で記録する。
   - 成功/失敗
   - `failure_tag`
   - コスト
   これをProduction Memoryの初レコードにする。
5. 終了後、人間が `permission.json` の `seedance_generate` を `false` に戻す。
6. 15秒CM本番は T13〜T15 がマージされた後に行う。

完成CMをいきなり作らない。初回はStudio v2のゲート、予算、記録が動くかだけを見る。
