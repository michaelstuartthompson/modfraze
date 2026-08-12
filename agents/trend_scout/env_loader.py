"""
env_loader.py -- find and load the project's .env, using only the stdlib.

WHY NOT python-dotenv
---------------------
It's a fine library. But this is 30 lines, has no install step, and removes a
thing that can go wrong on someone else's machine. For a dependency this small,
owning it is cheaper than depending on it.

Searches this folder and every parent, so it finds ModFraze/.env no matter
which directory you run from.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env(start: Path | None = None, verbose: bool = False) -> Path | None:
    """
    Walk up from `start` looking for a .env file. Load the first one found.

    Existing environment variables WIN -- a value you exported in your shell
    overrides the file. That ordering matters: it lets you temporarily test a
    different key without editing (and later forgetting you edited) the file.
    """
    here = (start or Path(__file__).parent).resolve()

    for folder in [here, *here.parents]:
        candidate = folder / ".env"
        if not candidate.is_file():
            continue

        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as e:
            if verbose:
                print(f"  [warn] found {candidate} but could not read it: {e}")
            return None

        loaded = 0
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip().removeprefix("export ").strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded += 1

        if verbose:
            print(f"  loaded {loaded} vars from {candidate}")
        return candidate

    if verbose:
        print("  [warn] no .env found in this folder or any parent")
    return None
