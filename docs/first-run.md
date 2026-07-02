# Studio v2 First Run

Codexでは有料生成・MCP実行・外部投稿をしない。初回スモークは人間が最小条件で実行する。

1. `bash studio/tests/self_audit.sh` を実行し、`SELF-AUDIT: ALL GREEN` を確認する。
2. 人間が `studio/memory/seeds/provider_pricing.json` の `higgsfield_seedance_video` を確認済み単価に更新する。
   - `status: "active"`
   - `usd_per_second: <Higgsfieldで確認した値>`
   - `verified_at: <確認日>`
   - `source: <確認先>`
3. 人間が対象プロジェクトの `permission.json` を編集する。
   - `seedance_generate: true`
   - `cap_usd: <最小額>`
   - `daily_cap_usd: <最小額>`
   - `max_takes_per_shot: 1`
4. **1ショット・4〜5秒・最低解像度**の契約1本だけでrequestを発行する。

```bash
python3 -m studio generate \
  --root <project-root> \
  --contract <shot-contract.json> \
  --provider higgsfield \
  --take take_001
```

5. 出力された `requests/*.request.json` を人間が目視確認する。
   - prompt
   - references
   - estimate
   - execution_token
6. 人間がHiggsfield MCPでrequestどおりに実行し、成果物をローカル保存する。
7. 実行結果をrecordする。

```bash
python3 -m studio record \
  --root <project-root> \
  --request <requests/...request.json> \
  --output <downloaded-output.mp4> \
  --cost <actual-usd>
```

8. 結果を `python3 -m studio review ...` で記録する。
   - 成功/失敗
   - `failure_tag`
   - コスト
9. 終了後、人間が `permission.json` の `seedance_generate` を `false` に戻す。

**execution_tokenの無いrequestをMCPで実行しない。request JSONに無いパラメータを実行時に足さない。**

完成CMをいきなり作らない。初回はStudio v2のゲート、予算、記録が動くかだけを見る。
