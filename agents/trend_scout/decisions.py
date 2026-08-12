"""
decisions.py -- the record of what you actually did with each pick.

WHY THIS FILE EXISTS
--------------------
scoring.py measures the world. brand.md states a guess about your taste. This
file is the only place that holds *evidence* about your taste, and it is the
thing that eventually lets brand.md be rewritten from fact instead of
assumption.

TWO STORES, ON PURPOSE
----------------------
    state/decisions.jsonl   machine-readable, one JSON object per line
    brand.md decision log   human-readable table, regenerated from the jsonl

The jsonl is the source of truth. The markdown table is a rendering of it, so
editing the table by hand does nothing -- edit via decide.py instead. Keeping
one canonical store avoids the classic failure where two logs disagree and you
no longer trust either.

EVERY PICK IS LOGGED, IMMEDIATELY
---------------------------------
run.py calls log_pending() the moment a report is written, before you have
looked at anything. Picks you never act on stay 'pending' forever, and that is
deliberate: "surfaced, ignored" is the most common outcome and the one most
worth counting. A log that only records decisions you bothered to make will
flatter the agent.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent
STATE = HERE / "state"
LEDGER = STATE / "decisions.jsonl"
BRAND = HERE / "brand.md"

STATUSES = ("pending", "approved", "denied")

# Below this many *decided* entries, calibration is withheld from the agent.
# Two data points is not taste, it's noise, and an agent shown two rejections
# will overcorrect into refusing everything that rhymes with them.
MIN_FOR_CALIBRATION = 10

# How many recent decided entries to show the agent. Enough for a pattern,
# small enough to stay cheap.
CALIBRATION_WINDOW = 25

TABLE_HEADER = "| date | term | hypothesis | designed? | sold? | notes |"
TABLE_RULE = "|---|---|---|---|---|---|"


# ---------------------------------------------------------------------------
# storage
# ---------------------------------------------------------------------------

def load() -> list[dict]:
    """Every entry, oldest first. Missing or corrupt lines are skipped, not fatal."""
    if not LEDGER.is_file():
        return []
    out = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def save(entries: list[dict]) -> None:
    STATE.mkdir(exist_ok=True)
    body = "\n".join(json.dumps(e, default=str) for e in entries)
    LEDGER.write_text(body + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# writing
# ---------------------------------------------------------------------------

def log_pending(picks: list[dict], run_date: str | None = None) -> int:
    """
    Record today's shortlist as pending. Returns how many NEW rows were added.

    Re-surfaced terms are not duplicated -- if the scout finds 'quiet cracking'
    again next week and you already denied it, the original decision stands and
    the times_surfaced counter increments. That counter is useful on its own: a
    term the scout keeps pushing that you keep refusing is a brand.md bug.
    """
    stamp = run_date or date.today().isoformat()
    entries = load()
    by_term = {e["term"]: e for e in entries}
    added = 0

    for p in picks or []:
        term = p.get("term")
        if not term:
            continue

        if term in by_term:
            e = by_term[term]
            e["times_surfaced"] = e.get("times_surfaced", 1) + 1
            e["last_surfaced"] = stamp
            continue

        entries.append({
            "term": term,
            "first_surfaced": stamp,
            "last_surfaced": stamp,
            "times_surfaced": 1,
            "hypothesis": p.get("hypothesis", "?"),
            "confidence": p.get("confidence", "?"),
            "why_now": p.get("why_now", ""),
            "status": "pending",
            "reason": "",
            "sold": None,
            "decided_at": None,
        })
        added += 1

    save(entries)
    render_brand_table()
    return added


def set_decision(term: str, status: str, reason: str = "") -> dict | None:
    """Flip a pending row to approved/denied. Returns the updated entry, or None."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")

    entries = load()
    for e in entries:
        if e["term"].lower() == term.lower():
            e["status"] = status
            e["reason"] = reason or e.get("reason", "")
            e["decided_at"] = datetime.now().isoformat(timespec="seconds")
            save(entries)
            render_brand_table()
            return e
    return None


def set_sold(term: str, sold: bool, reason: str = "") -> dict | None:
    """
    Record the outcome. This is the field that actually tests H1-H5 --
    approving a pick costs nothing, selling one is evidence.
    """
    entries = load()
    for e in entries:
        if e["term"].lower() == term.lower():
            e["sold"] = sold
            if reason:
                e["reason"] = reason
            save(entries)
            render_brand_table()
            return e
    return None


# ---------------------------------------------------------------------------
# rendering into brand.md
# ---------------------------------------------------------------------------

def render_brand_table() -> None:
    """
    Rewrite the decision-log table at the bottom of brand.md from the ledger.

    Everything above the table header is left untouched, so your hand-written
    criteria are safe. If the header is missing the function does nothing
    rather than guessing where to write.
    """
    if not BRAND.is_file():
        return

    text = BRAND.read_text(encoding="utf-8")
    if TABLE_HEADER not in text:
        return

    head = text.split(TABLE_HEADER)[0]
    rows = []
    for e in load():
        designed = {"approved": "yes", "denied": "no", "pending": "—"}.get(e["status"], "—")
        sold = "—" if e.get("sold") is None else ("yes" if e["sold"] else "no")
        note = (e.get("reason") or "").replace("|", "/").replace("\n", " ")
        if e.get("times_surfaced", 1) > 1:
            note = f"{note} (surfaced {e['times_surfaced']}×)".strip()
        rows.append(
            f"| {e['first_surfaced']} | {e['term']} | {e.get('hypothesis','?')} "
            f"| {designed} | {sold} | {note} |"
        )

    BRAND.write_text(
        head + TABLE_HEADER + "\n" + TABLE_RULE + "\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# feeding it back to the agent
# ---------------------------------------------------------------------------

def load_calibration() -> str:
    """
    A prompt fragment describing past decisions, or "" if there aren't enough.

    Returning "" below the threshold means agent.py needs no conditional logic:
    it appends whatever this returns, and the feature switches itself on once
    the evidence exists.
    """
    decided = [e for e in load() if e["status"] in ("approved", "denied")]
    if len(decided) < MIN_FOR_CALIBRATION:
        return ""

    decided = decided[-CALIBRATION_WINDOW:]
    approved = [e for e in decided if e["status"] == "approved"]
    denied = [e for e in decided if e["status"] == "denied"]

    def fmt(e: dict) -> str:
        why = f" -- {e['reason']}" if e.get("reason") else ""
        sold = ""
        if e.get("sold") is True:
            sold = " [SOLD]"
        elif e.get("sold") is False:
            sold = " [did not sell]"
        return f"- {e['term']} ({e.get('hypothesis','?')}){sold}{why}"

    parts = [
        "# Michael's past decisions on your picks",
        "",
        "These are real outcomes, not hypotheses. Where this evidence conflicts",
        "with brand.md, trust this -- brand.md is a guess and this is a record.",
        "Do not simply avoid anything resembling a denial; look for the REASON",
        "behind the pattern and apply that.",
        "",
    ]
    if approved:
        parts += [f"## Approved ({len(approved)})", ""] + [fmt(e) for e in approved] + [""]
    if denied:
        parts += [f"## Denied ({len(denied)})", ""] + [fmt(e) for e in denied] + [""]

    return "\n".join(parts)


def summary() -> dict:
    entries = load()
    return {
        "total": len(entries),
        "pending": sum(1 for e in entries if e["status"] == "pending"),
        "approved": sum(1 for e in entries if e["status"] == "approved"),
        "denied": sum(1 for e in entries if e["status"] == "denied"),
        "sold": sum(1 for e in entries if e.get("sold") is True),
        "decided": sum(1 for e in entries if e["status"] in ("approved", "denied")),
        "needed_for_calibration": MIN_FOR_CALIBRATION,
    }
