from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def assemble_videos(inputs: list[Path], output: Path) -> Path:
    if not inputs:
        raise ValueError("no videos to assemble")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
        list_path = Path(handle.name)
        for item in inputs:
            handle.write(f"file '{item.resolve()}'\n")
    try:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path), "-c", "copy", str(output)],
            check=True,
        )
    finally:
        list_path.unlink(missing_ok=True)
    return output


def extract_last_frame(video: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-sseof", "-0.1", "-i", str(video), "-frames:v", "1", str(output)],
        check=True,
    )
    return output


def probe(video: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)
