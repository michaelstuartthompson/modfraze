"""
etsy_probe.py -- does the Etsy key work yet?

Etsy issues a keystring the moment you create an app, but the app is not
usable until a human approves it, and reports differ on whether the key
returns data in the meantime. Rather than guess, ask.

Reads ETSY_KEYSTRING from .env. Never prints the key.

    python tools/etsy_probe.py
    python tools/etsy_probe.py "quiet cracking"     # saturation check
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from env_loader import load_env          # noqa: E402
import sources                            # noqa: E402


def main() -> int:
    load_env()

    key = os.environ.get("ETSY_KEYSTRING", "").strip()
    if not key:
        print("ETSY_KEYSTRING is not set in .env -- nothing to test.")
        return 1

    # Confirm which credential shape is in play without revealing it.
    shape = "keystring:shared_secret" if ":" in key else "keystring only"
    print(f"key present ({len(key)} chars, {shape})\n")

    term = sys.argv[1] if len(sys.argv) > 1 else None

    if term:
        print(f"saturation check: {term!r}")
        result = sources.etsy_saturation(term)
        if result.get("error"):
            print(f"  FAILED: {result['error']}")
            return 2
        print(f"  active listings : {result['active_listings']}")
        print(f"  verdict         : {result['verdict']}")
        for row in result["top_listings"]:
            print(f"    {row['favorers']:>5} favs  {row['title']}")
        return 0

    print("discovery check: newest 10 active listings")
    signals = sources.etsy(max_listings=10)

    if not signals:
        print("\n  No listings returned.")
        print("  Either the key is not approved yet, or the request failed.")
        print("  A [warn] line above will say which. 401/403 = not approved yet;")
        print("  anything else is a real bug worth reporting.")
        return 2

    print(f"\n  OK -- {len(signals)} listings came back. The key is live.\n")
    for s in signals[:10]:
        tags = ", ".join((s.meta.get("tags") or [])[:4])
        print(f"    {s.score:>4.0f} favs  {s.text[:62]}")
        if tags:
            print(f"                 tags: {tags}")

    print("\nNext: add 'etsy' to the --sources list in scheduler/scout_run.bat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
