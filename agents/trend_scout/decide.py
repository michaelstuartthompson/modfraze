"""
decide.py -- tell the scout what you thought of its picks.

    python decide.py list
    python decide.py list --all

    python decide.py approve "quiet cracking" -n "strong H1 fit, phrase stands alone"
    python decide.py deny    "loud budgeting" -n "already on Etsy, we're late"

    python decide.py sold    "quiet cracking" --yes
    python decide.py sold    "quiet cracking" --no  -n "2 orders in 3 weeks"

    python decide.py status

Terms are matched case-insensitively and you can pass a unique prefix, so
`decide.py approve quiet` works when only one pending term starts that way.

ON THE -n FLAG
--------------
It's optional and you should use it anyway. A log of bare approve/deny teaches
neither you nor the agent anything -- the reason is the entire payload. Once
about ten decisions exist, these notes get fed back into the agent's prompt.
"""

from __future__ import annotations

import argparse
import sys

import decisions


def _resolve(term: str, entries: list[dict]) -> str | None:
    """Exact match, else unique case-insensitive prefix, else None."""
    t = term.strip().lower()
    exact = [e["term"] for e in entries if e["term"].lower() == t]
    if exact:
        return exact[0]

    hits = [e["term"] for e in entries if e["term"].lower().startswith(t)]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        print(f"'{term}' is ambiguous. Matches: {', '.join(hits)}")
        return None

    contains = [e["term"] for e in entries if t in e["term"].lower()]
    if len(contains) == 1:
        return contains[0]
    if len(contains) > 1:
        print(f"'{term}' is ambiguous. Matches: {', '.join(contains)}")
        return None

    print(f"No logged pick matches '{term}'. Try:  python decide.py list --all")
    return None


def cmd_list(args) -> int:
    entries = decisions.load()
    if not args.all:
        entries = [e for e in entries if e["status"] == "pending"]

    if not entries:
        print("Nothing pending." if not args.all else "Ledger is empty.")
        return 0

    for e in entries:
        sold = "" if e.get("sold") is None else ("  [sold]" if e["sold"] else "  [no sales]")
        mark = {"pending": "?", "approved": "+", "denied": "-"}.get(e["status"], "?")
        print(f"  {mark} {e['term']}  ({e.get('hypothesis','?')}, "
              f"{e.get('confidence','?')} conf, first seen {e['first_surfaced']}){sold}")
        if e.get("reason"):
            print(f"      {e['reason']}")
    return 0


def cmd_decide(args, status: str) -> int:
    entries = decisions.load()
    term = _resolve(args.term, entries)
    if term is None:
        return 1

    updated = decisions.set_decision(term, status, args.note or "")
    verb = "Approved" if status == "approved" else "Denied"
    print(f"{verb}: {updated['term']}")
    if not args.note:
        print("  (no reason recorded -- the reason is the part that teaches)")

    s = decisions.summary()
    if s["decided"] < s["needed_for_calibration"]:
        left = s["needed_for_calibration"] - s["decided"]
        print(f"  {s['decided']} decisions logged; {left} more before the agent sees them.")
    return 0


def cmd_sold(args) -> int:
    entries = decisions.load()
    term = _resolve(args.term, entries)
    if term is None:
        return 1
    if args.yes == args.no:
        print("Pass exactly one of --yes / --no")
        return 1

    updated = decisions.set_sold(term, bool(args.yes), args.note or "")
    print(f"Recorded: {updated['term']} {'sold' if args.yes else 'did not sell'}")
    return 0


def cmd_status(args) -> int:
    s = decisions.summary()
    print(f"  total logged   {s['total']}")
    print(f"  pending        {s['pending']}")
    print(f"  approved       {s['approved']}")
    print(f"  denied         {s['denied']}")
    print(f"  sold           {s['sold']}")
    print()
    if s["decided"] >= s["needed_for_calibration"]:
        print(f"  Calibration ACTIVE -- the agent sees your last "
              f"{decisions.CALIBRATION_WINDOW} decisions.")
    else:
        left = s["needed_for_calibration"] - s["decided"]
        print(f"  Calibration off -- {left} more decisions needed.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="show pending picks")
    p.add_argument("--all", action="store_true", help="include already-decided picks")
    p.set_defaults(fn=cmd_list)

    for name, status in (("approve", "approved"), ("deny", "denied")):
        p = sub.add_parser(name, help=f"mark a pick {status}")
        p.add_argument("term")
        p.add_argument("-n", "--note", default="", help="why -- the important part")
        p.set_defaults(fn=lambda a, s=status: cmd_decide(a, s))

    p = sub.add_parser("sold", help="record the outcome")
    p.add_argument("term")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--no", action="store_true")
    p.add_argument("-n", "--note", default="")
    p.set_defaults(fn=cmd_sold)

    p = sub.add_parser("status", help="ledger counts and calibration state")
    p.set_defaults(fn=cmd_status)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
