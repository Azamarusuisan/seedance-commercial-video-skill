from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class ProductionMemory:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                create table if not exists generations (
                  project text not null,
                  take text not null,
                  verdict text not null,
                  failure_tag text not null default '',
                  cost_usd real not null default 0,
                  note text not null default '',
                  unique(project, take)
                );
                create table if not exists failure_patterns (
                  fp_id text primary key,
                  title text not null,
                  source_path text not null,
                  source_sha256 text not null
                );
                create table if not exists playbooks (
                  tag text primary key,
                  recipe text not null,
                  source text not null
                );
                """
            )

    def record_generation(self, *, project: str, take: str, verdict: str, failure_tag: str = "", cost_usd: float = 0, note: str = "") -> None:
        with self._connect() as db:
            db.execute(
                """
                insert into generations(project, take, verdict, failure_tag, cost_usd, note)
                values(?, ?, ?, ?, ?, ?)
                on conflict(project, take) do update set
                  verdict=excluded.verdict,
                  failure_tag=excluded.failure_tag,
                  cost_usd=excluded.cost_usd,
                  note=excluded.note
                """,
                (project, take, verdict, failure_tag, cost_usd, note),
            )

    def upsert_failure_pattern(self, *, fp_id: str, title: str, source_path: str, source_sha256: str) -> None:
        with self._connect() as db:
            db.execute(
                """
                insert into failure_patterns(fp_id, title, source_path, source_sha256)
                values(?, ?, ?, ?)
                on conflict(fp_id) do update set
                  title=excluded.title,
                  source_path=excluded.source_path,
                  source_sha256=excluded.source_sha256
                """,
                (fp_id, title, source_path, source_sha256),
            )

    def upsert_playbook(self, *, tag: str, recipe: str, source: str) -> None:
        with self._connect() as db:
            db.execute(
                """
                insert into playbooks(tag, recipe, source)
                values(?, ?, ?)
                on conflict(tag) do update set recipe=excluded.recipe, source=excluded.source
                """,
                (tag, recipe, source),
            )

    def counts(self) -> dict[str, int]:
        with self._connect() as db:
            return {
                table: db.execute(f"select count(*) from {table}").fetchone()[0]
                for table in ("generations", "failure_patterns", "playbooks")
            }

    def failure_ids(self) -> set[str]:
        with self._connect() as db:
            return {row[0] for row in db.execute("select fp_id from failure_patterns")}

    def rows(self, table: str) -> list[tuple[Any, ...]]:
        with self._connect() as db:
            return list(db.execute(f"select * from {table}"))

