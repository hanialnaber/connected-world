"""Small, dependency-free HTTP helpers: retries with backoff, atomic writes, checksums."""
from __future__ import annotations

import hashlib
import logging
import time
import urllib.error
import urllib.request
from pathlib import Path

log = logging.getLogger("connected_world")
USER_AGENT = "connected-world/1.0 (+https://hani-alnaber.com/connected)"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, dest: Path, *, retries: int = 4, backoff: float = 2.0, timeout: int = 120) -> Path:
    """Download ``url`` to ``dest`` atomically. Retries transient failures with exponential backoff."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp, tmp.open("wb") as out:
                while chunk := resp.read(1 << 20):
                    out.write(chunk)
            tmp.replace(dest)
            return dest
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == retries:
                raise
            wait = backoff ** attempt
            log.warning("fetch %s failed (%s), retry %d/%d in %.0fs", url, exc, attempt, retries, wait)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def cached_fetch(url: str, dest: Path, *, expected_sha256: str | None = None, refresh: bool = False) -> Path:
    """Reuse a cached raw file unless ``refresh``; always verify the checksum when one is published."""
    if refresh or not dest.exists():
        log.info("downloading %s", url)
        fetch(url, dest)
    if expected_sha256:
        actual = sha256(dest)
        if actual != expected_sha256:
            raise ValueError(f"checksum mismatch for {dest.name}: {actual} != {expected_sha256}")
    return dest
