"""
run.py -- entry point. Wires the three stages together.

    collect  ->  score  ->  agent  ->  report

Usage:
    python run.py --demo              # fixtures, no network, no API key
    python run.py --collect-only      # live fetch + scoring, still no API key
    python run.py                     # the whole thing
    python run.py --sources google_trends,hackernews
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import scoring
import sources
from env_loader import load_env

HERE = Path(__file__).parent
REPORTS = HERE / "reports"


def write_report(result: dict, candidates: list[dict]) -> Path:
    REPORTS.mkdir(exist_ok=True)
    stamp = date.today().isoformat()

    (REPORTS / f"{stamp}-raw.json").write_text(
        json.dumps({"candidates": candidates, "result": result}, indent=2, default=str)
    )

    lines = [f"# ModFraze Trend Scout -- {stamp}", ""]
    picks = result.get("shortlist") or []
    if not picks:
        lines += ["_Nothing met the criteria today._", ""]
    for i, p in enumerate(picks, 1):
        lines += [
            f"## {i}. {p['term']}  ({p.get('confidence','?')} confidence, {p.get('hypothesis','?')})",
            "",
            f"**Why now** — {p.get('why_now','')}",
            "",
            f"**ModFraze angle** — {p.get('modfraze_angle','')}",
            "",
            f"**Design direction** — {p.get('design_direction','')}",
            "",
            f"**Risk** — {p.get('risk','')}",
            "",
            f"**Est. weeks to peak** — {p.get('weeks_to_peak_estimate','?')}",
            "",
        ]

    lines += ["---", "", "## Top mechanical candidates (pre-agent)", ""]
    lines += ["| term | score | platforms | today | avg | days |",
              "|---|---|---|---|---|---|"]
    for c in candidates[:20]:
        lines.append(
            f"| {c['term']} | {c['score']} | {', '.join(c['platforms'])} | "
            f"{c['mentions_today']} | {c['baseline']} | {c['days_seen']} |"
        )

    path = REPORTS / f"{stamp}-shortlist.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true", help="use fixtures, no network")
    ap.add_argument("--collect-only", action="store_true", help="skip the LLM stage")
    # Free sources only. 'x' costs money per post read, so it is opt-in via
    # --sources and never runs by accident. Only scout_run.bat asks for it.
    ap.add_argument("--sources", default="google_trends,hackernews,web_news")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--notify", action="store_true", help="email the report when done")
    args = ap.parse_args()

    # Load .env before anything reads os.environ. Walks up to ModFraze/.env.
    load_env(verbose=not args.quiet)

    # ---- stage 1: collect -------------------------------------------------
    print("[1/3] collecting signals")
    if args.demo:
        signals = sources.demo_signals()
        print(f"  demo fixtures    {len(signals):4d} signals")
    else:
        signals = sources.collect(args.sources.split(","))
    print(f"  total            {len(signals):4d}\n")

    if not signals:
        print("No signals collected. Check your network or try --demo.")
        return

    # ---- stage 2: score (deterministic, free) -----------------------------
    print("[2/3] scoring for cross-platform emergence")
    history = {} if args.demo else scoring.load_history()
    candidates, history = scoring.score_candidates(signals, history)
    candidates = scoring.dedupe_overlapping(candidates, scoring.SHORTLIST_SIZE)
    if not args.demo:
        scoring.save_history(scoring.prune_history(history))

    print(f"  {len(candidates)} candidates survived. Top 10:")
    for c in candidates[:10]:
        print(f"    {c['score']:6.2f}  {c['breadth']}p  {c['term']}")
    print()

    if args.collect_only:
        print("--collect-only: stopping before the LLM stage.")
        return

    # ---- stage 3: agent (the expensive part, on ~40 rows) -----------------
    print("[3/3] running the agent")
    from agent import run_agent
    result = run_agent(candidates, history, verbose=not args.quiet)

    path = write_report(result, candidates)
    print(f"\nReport written: {path}")

    import decisions
    n = decisions.log_pending(result.get("shortlist") or [])
    print(f"  logged {n} new pick(s) to the decision ledger")

    if args.notify:
        from notify import send_report
        send_report(path, result.get("shortlist") or [])

    for p in result.get("shortlist") or []:
        print(f"  - {p['term']} ({p.get('confidence')})")


if __name__ == "__main__":
    main()
