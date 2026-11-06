"""CLI: python -m pipeline [extract|transform|export|all] [--refresh]"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time

from . import export, extract
from .config import BRONZE, ROOT, WAREHOUSE


def transform() -> None:
    """dbt build = run every model, seed and data test in dependency order; fail fast on a broken test."""
    env = dict(
        os.environ,
        CONNECTED_WORLD_BRONZE=str(BRONZE),
        CONNECTED_WORLD_WAREHOUSE=str(WAREHOUSE),
        DBT_SEND_ANONYMOUS_USAGE_STATS="False",
    )
    cmd = ["dbt", "build", "--project-dir", str(ROOT / "dbt"), "--profiles-dir", str(ROOT / "dbt")]
    subprocess.run(cmd, check=True, cwd=ROOT / "dbt", env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pipeline", description="Connected World data pipeline")
    parser.add_argument("step", choices=["extract", "transform", "export", "all"])
    parser.add_argument("--refresh", action="store_true", help="re-download sources instead of using the raw cache")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    started = time.perf_counter()
    if args.step in ("extract", "all"):
        extract.run(refresh=args.refresh)
    if args.step in ("transform", "all"):
        transform()
    if args.step in ("export", "all"):
        export.run(runtime_s=time.perf_counter() - started)
    logging.getLogger("connected_world").info("done in %.1fs", time.perf_counter() - started)
    return 0


if __name__ == "__main__":
    sys.exit(main())
