"""
agent.py -- THE LOOP. This is the file worth reading twice.

Everything before this was normal Python: fetch, count, sort. Deterministic.
You could have written it in 2015.

This file is the part that makes it an agent. The structure is only:

    while True:
        response = model(conversation, tools)
        if response has no tool calls:
            break                       # model decided it's done
        for each tool call:
            result = run_that_python_function(**args)
            append result to conversation

That is the entire idea. Every framework you'll encounter -- LangGraph,
CrewAI, the Claude Agent SDK, OpenAI's Agents SDK -- is this loop plus
convenience. Once you've written it by hand you can evaluate those tools
instead of being sold them, which is most of what "senior" means here.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
MODEL = os.environ.get("MODFRAZE_MODEL", "claude-sonnet-5")
MAX_TURNS = 12          # hard stop. an agent without one WILL bill you $300.


# ===========================================================================
# 1. TOOLS
# ===========================================================================
# A tool is two things stapled together:
#   (a) a normal Python function
#   (b) a JSON-schema description the model reads to decide when to call it
#
# The description is PROMPT ENGINEERING, not documentation. It's the only
# thing standing between the model and misuse of your function. Most agent
# bugs that look like "the model is dumb" are actually vague tool descriptions.

class ToolBox:
    """Holds the run's data so tools can close over it instead of using globals."""

    def __init__(self, candidates: list[dict], history: dict):
        self.by_term = {c["term"]: c for c in candidates}
        self.candidates = candidates
        self.history = history
        self.shortlist: list[dict] | None = None

    # --- tool implementations -------------------------------------------

    def inspect_candidate(self, term: str) -> dict:
        """Full evidence for one term."""
        c = self.by_term.get(term)
        if not c:
            near = [t for t in self.by_term if term.lower() in t][:5]
            return {"error": f"'{term}' is not in this run's candidates",
                    "did_you_mean": near}
        return {
            "term": c["term"],
            "platforms": c["platforms"],
            "mentions_today": c["mentions_today"],
            "recent_daily_average": c["baseline"],
            "days_ever_observed": c["days_seen"],
            "etsy_listings_seen": c.get("etsy_listings", 0),
            "example_posts": c["examples"],
        }

    def trend_history(self, term: str) -> dict:
        """Day-by-day mention counts, so the model can see the shape of the curve."""
        entry = self.history.get(term)
        if not entry:
            return {"term": term, "history": {}, "note": "never seen before today"}
        days = dict(sorted(entry["days"].items()))
        counts = list(days.values())
        if len(counts) < 2:
            note = "first observation -- no trend direction yet"
        elif counts[-1] > counts[0]:
            note = "rising"
        elif counts[-1] < counts[0]:
            note = "falling"
        else:
            note = "flat"
        return {
            "term": term,
            "history": days,
            "days_of_history": len(counts),
            "first_seen": next(iter(days), None),
            "note": note,
        }

    def find_related_terms(self, substring: str) -> dict:
        """Other candidates containing a word -- helps spot a cluster."""
        hits = [
            {"term": c["term"], "score": c["score"], "breadth": c["breadth"]}
            for c in self.candidates if substring.lower() in c["term"]
        ][:15]
        return {"substring": substring, "matches": hits}

    def save_shortlist(self, picks: list) -> dict:
        """Terminal tool. Recording the answer is what ends the run."""
        self.shortlist = picks
        return {"saved": len(picks)}

    # --- schemas the model sees -----------------------------------------

    SCHEMAS = [
        {
            "name": "inspect_candidate",
            "description": (
                "Get the full evidence behind one candidate term: which platforms "
                "mentioned it, how many times today, its recent daily average, "
                "how many Etsy listings already use the phrase, and "
                "up to four real example post titles with links. Call this before "
                "shortlisting anything -- the summary table alone is not enough to "
                "judge whether a term is a real social phrase or a coincidence of "
                "common words."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"term": {"type": "string",
                    "description": "Exact term string from the candidate table."}},
                "required": ["term"],
            },
        },
        {
            "name": "trend_history",
            "description": (
                "Get day-by-day mention counts for a term across all previous runs. "
                "Use this to distinguish a term that is ACCELERATING (few days of "
                "history, rising counts -- what we want) from one that has been "
                "steady for weeks (established, too late to design for)."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"term": {"type": "string"}},
                "required": ["term"],
            },
        },
        {
            "name": "find_related_terms",
            "description": (
                "Find other candidate terms containing a given word. Use when you "
                "suspect several candidates are facets of one larger trend, so you "
                "can shortlist the trend once with its strongest phrasing instead "
                "of three times."
            ),
            "input_schema": {
                "type": "object",
                "properties": {"substring": {"type": "string"}},
                "required": ["substring"],
            },
        },
        {
            "name": "save_shortlist",
            "description": (
                "Record your final ranked shortlist and END the run. Call this "
                "exactly once, only after you have inspected the evidence for every "
                "term you are including. Include 3-7 items. If nothing today meets "
                "the ModFraze criteria, call it with an empty list -- an honest "
                "empty result is far more valuable than a padded one."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "picks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "term": {"type": "string"},
                                "confidence": {"type": "string",
                                    "enum": ["high", "medium", "low"]},
                                "why_now": {"type": "string",
                                    "description": "The emergence evidence, citing platforms and counts."},
                                "hypothesis": {"type": "string",
                                    "enum": ["H1", "H2", "H3", "H4", "H5"],
                                    "description": "Which brand hypothesis from brand.md this item tests."},
                                "modfraze_angle": {"type": "string",
                                    "description": "Why this could work for ModFraze, stated as a testable bet rather than a certainty."},
                                "design_direction": {"type": "string",
                                    "description": "One concrete visual/typographic idea for the merch."},
                                "risk": {"type": "string",
                                    "description": "Trademark, tone, saturation, or timing risk. Say 'none obvious' if none."},
                                "weeks_to_peak_estimate": {"type": "integer"},
                            },
                            "required": ["term", "confidence", "hypothesis", "why_now",
                                         "modfraze_angle", "design_direction", "risk"],
                        },
                    }
                },
                "required": ["picks"],
            },
        },
    ]


SYSTEM_PROMPT = """You are the ModFraze Trend Scout.

Your job is to find emerging social phrases EARLY -- while they are crossing
between platforms but before mainstream media names them -- so Michael has time
to design merchandise around them before they peak.

You are given a pre-scored candidate table. The scoring is mechanical: it
measures cross-platform breadth, acceleration, and newness. It has NO taste.
Plenty of high-scoring rows will be coincidental word overlap, platform
artifacts, or news. Your job is the judgment the scoring cannot do.

DEMAND vs SUPPLY. Most sources here (x, google_trends, hackernews, web_news)
tell you people are SAYING something. Etsy tells you sellers are already
PRINTING it. The two mean opposite things, and Etsy counts are reported
separately from breadth for that reason. Read `etsy_listings_seen` as a
lateness warning:

  0            nobody has made this yet -- the position we want
  1-3          one or two sellers are testing it; still early, move fast
  4 or more    the merch market has already noticed; you would be
               competing on execution rather than on timing

A term that is loud on the demand platforms and ABSENT from Etsy is the most
valuable thing this system can find. Say so explicitly in `why_now` when you
see that gap, and treat heavy Etsy presence as a reason to downgrade
confidence rather than a reason to feel reassured.

Method:
1. Read the candidate table.
2. Use inspect_candidate on anything plausible. Read the actual example posts.
   A term is only real if the example posts show people using it as a PHRASE,
   not as unrelated words that happen to co-occur.
3. Use trend_history to check whether it is accelerating or already flat.
4. Use find_related_terms when several rows look like one trend.
5. Call save_shortlist once with your ranked picks.

Be harsh about EMERGENCE evidence -- a false positive there costs Michael a
week of design work on a dead trend. A short honest list beats a long hopeful
one, and an empty list is an acceptable answer on a slow day.

But be GENEROUS about brand fit. Michael has not settled on a niche yet, and
brand.md lists five untested hypotheses. Deliberately include at least one pick
per run that does not resemble the existing catalog, and tag every pick with
the hypothesis it tests. Your job right now is as much to help him discover the
niche as to serve it."""


# ===========================================================================
# 2. THE LOOP
# ===========================================================================

def run_agent(candidates: list[dict], history: dict, verbose: bool = True) -> dict:
    try:
        import anthropic
    except ImportError:
        sys.exit("Missing dependency. Run:  pip install anthropic")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        # try once more in case run_agent was imported directly, not via run.py
        from env_loader import load_env
        load_env()

    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "  Add it to C:\\Users\\miket\\iCloudDrive\\04_Projects\\ModFraze\\.env as:\n"
            "    ANTHROPIC_API_KEY=sk-ant-...\n"
            "  or for one session:  $env:ANTHROPIC_API_KEY = \"sk-ant-...\""
        )
    if not key.startswith("sk-ant-"):
        sys.exit(
            f"ANTHROPIC_API_KEY is set but starts with {key[:8]!r}.\n"
            "  That looks like an OpenAI key. This agent needs an Anthropic key\n"
            "  (sk-ant-...) from console.anthropic.com."
        )

    client = anthropic.Anthropic()
    box = ToolBox(candidates, history)
    brand = (HERE / "brand.md").read_text(encoding="utf-8")

    import decisions
    calibration = decisions.load_calibration()
    # Compact table -- one line per candidate. Tokens are money; don't send
    # the example posts up front, make the model ASK for them via a tool.
    table = "\n".join(
        f"{i+1:2d}. {c['term']!r} | score {c['score']} | "
        f"{c['breadth']} platforms ({', '.join(c['platforms'])}) | "
        f"{c['mentions_today']} today vs {c['baseline']} avg | "
        f"seen {c['days_seen']}d | "
        f"etsy {c.get('etsy_listings', 0)}"
        for i, c in enumerate(candidates)
    )

    messages = [{
        "role": "user",
        "content": (
            f"# ModFraze brand criteria\n\n{brand}\n\n"
            f"{calibration}\n\n"
            f"# Candidate table for {date.today().isoformat()}\n\n{table}\n\n"
            "Investigate and produce today's shortlist."
        ),
    }]

    # ---- the loop ----
    for turn in range(1, MAX_TURNS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=ToolBox.SCHEMAS,
            messages=messages,
        )

        if verbose:
            print(f"\n{'='*68}\nTURN {turn}  (stop_reason: {response.stop_reason})\n{'='*68}")
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(f"[thinking] {block.text.strip()[:600]}")

        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        # NO TOOL CALLS => the model is done talking. Exit the loop.
        if not tool_uses:
            break

        results = []
        for tu in tool_uses:
            fn = getattr(box, tu.name, None)
            if fn is None:
                out = {"error": f"no such tool: {tu.name}"}
            else:
                try:
                    out = fn(**tu.input)
                except Exception as e:            # tools must never crash the loop
                    out = {"error": f"{type(e).__name__}: {e}"}

            if verbose:
                preview = json.dumps(out)[:220]
                print(f"[tool] {tu.name}({json.dumps(tu.input)[:90]}) -> {preview}")

            results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": json.dumps(out, default=str),
            })

        messages.append({"role": "user", "content": results})

        # terminal tool was called -- stop even if the model wants to keep going
        if box.shortlist is not None:
            if verbose:
                print("\n[loop] save_shortlist called; ending run.")
            break
    else:
        print(f"\n[loop] hit MAX_TURNS={MAX_TURNS} without a shortlist.")

    return {
        "date": date.today().isoformat(),
        "model": MODEL,
        "turns_used": turn,
        "shortlist": box.shortlist or [],
    }
