"""
Probe individual X query frames in isolation.

The first live X run used all six frames OR'd together, and 9 of 10 posts
came back on "is the new" -- which turned out to be a comparison template
("X is the new Instagram"), not a naming one. This runs each frame on its
own so you can see which frames actually surface a NEW phrase before
committing to a rewritten default query.

Usage:
    .venv\\Scripts\\python.exe tools\\query_probe.py "apparently it's called"
    .venv\\Scripts\\python.exe tools\\query_probe.py "everyone's calling it" --n 10

Cost: $0.005 per post returned. Default 10 posts = $0.05 per frame.
"""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def load_env() -> None:
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip().strip("'\""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("frame", help="exact phrase to probe, without quotes")
    ap.add_argument("--n", type=int, default=10, help="max posts (default 10)")
    args = ap.parse_args()

    load_env()
    os.environ["X_MAX_POSTS"] = str(args.n)

    import signals
    import sources

    query = f'"{args.frame}" -is:retweet -is:reply -is:quote lang:en'
    print(f"query: {query}")
    print(f"budget: {args.n} posts ~ ${args.n * sources.X_COST_PER_POST:.2f}\n")

    posts = sources.x_search(query=query, max_posts=args.n)
    if not posts:
        print("no posts returned (check X_BEARER_TOKEN, or the frame is rare)")
        return 1

    for i, s in enumerate(posts, 1):
        text = " ".join(getattr(s, "text", str(s)).split())
        print(f"{i:>2}. {text[:280]}")

    # what the scorer would actually pull out of this batch, post-URL-strip
    counts: dict[str, int] = {}
    for s in posts:
        for term in signals.extract_terms(getattr(s, "text", "")):
            counts[term] = counts.get(term, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]

    print(f"\nterms seen in 2+ posts ({len(posts)} posts):")
    for term, n in top:
        if n >= 2:
            print(f"  {n:>2}x  {term}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
