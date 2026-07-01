# Failure Pattern Candidates

New review-derived failures go here first. Move them to `references/known-failure-patterns.md`
only after human review or `post-generation-learning-update.py --apply`.

## FP-CANDIDATE-007: 生成条件だけ先に固め、台本・セリフ・配役・字幕・音声方針の確認が後回しになる

- **症状**: 生成直前または生成後に、台本、セリフ有無、起用人物、字幕、音声、編集方針が未決だと判明する。
- **原因**: cost/generation条件の確認を優先し、制作意図のチェックリストを前段ゲートにしていなかった。
- **修正候補**: `pre-generation-learning-check.py` と `project-state.json.pre_generation_checklist` で、script/cast/dialogue/audio/subtitle/final titleを必須確認にする。
- **今回の学習**: MacNeo PC CMで、PC素材とSeedance条件は揃ったが、ユーザーが確認したかった「誰を起用するか」「セリフはあるか」「字幕/音声はどうするか」がUIに十分出ていなかった。
