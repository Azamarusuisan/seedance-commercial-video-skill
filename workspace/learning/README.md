# Learning Layer

This folder is the production memory for prompts, gates, reviews, and failure patterns.
It does not fine-tune third-party models.

Before Seedance request preparation, agents read:

- `references/known-failure-patterns.md`
- `workspace/learning/prompt-rules.md`
- `workspace/learning/pattern-memory.jsonl`
- `references/public-demand-short-video-patterns.md`
- the project brief
- the shot `visual-handoff.json`
- the Seedance prompt

After review, agents write:

- `workspace/learning/pattern-memory.jsonl`
- `workspace/learning/iteration-log.csv`
- `workspace/learning/failure-candidates.md`

`known-failure-patterns.md` is only changed by explicit human/agent decision, or by
`post-generation-learning-update.py --apply`.
