from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from studio.providers.base import Estimate, Generation


class MockProvider:
    provider = "mock"
    model = "mock_video"

    def estimate(self, *, prompt: str, duration_sec: float = 0, kind: str = "video") -> Estimate:
        base = 0.05 if kind == "image" else 0.1
        return Estimate(self.provider, self.model, round(max(duration_sec, 1) * base, 2))

    def generate(self, *, prompt: str, output_dir: Path, duration_sec: float = 1, kind: str = "video") -> Generation:
        output_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:12]
        if kind == "image":
            out = output_dir / f"mock-{digest}.png"
            self._make_png(out)
        else:
            out = output_dir / f"mock-{digest}.mp4"
            self._make_mp4(out, duration_sec)
        return Generation(self.provider, self.model, f"mock_{digest}", out)

    def _make_png(self, out: Path) -> None:
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=white:s=640x360", "-frames:v", "1", str(out)],
            check=True,
        )

    def _make_mp4(self, out: Path, duration_sec: float) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=size=640x360:rate=24:duration={max(duration_sec, 1)}",
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=channel_layout=stereo:sample_rate=48000",
                "-shortest",
                "-pix_fmt",
                "yuv420p",
                str(out),
            ],
            check=True,
        )
