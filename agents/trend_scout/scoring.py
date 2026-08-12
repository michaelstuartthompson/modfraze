"""
scoring.py -- deterministic pre-filter. NO LLM IN THIS FILE.

THE MOST IMPORTANT ARCHITECTURAL IDEA IN THE PROJECT
----------------------------------------------------
A naive build sends all ~1,500 collected headlines to the model and asks
"what's trending?" That costs real money per run, is slow, and the model
will confidently invent patterns because it has no memory of yesterday.

Instead: cheap deterministic code does the counting, and the expensive
model only ever sees the ~40 survivors. Counting is something Python is
better at than any LLM. Judgment is something the LLM is better at than
any regex. Put each where it belongs.

WHAT WE ACTUALLY MEASURE
------------------------
You said the target is a fad *just before* it peaks. That is NOT the same
as "most popular," which is why raw volume is the wrong metric -- "nfl
scores" wins every day and is useless to you. Three components instead:

  Platforms are split into two kinds. DEMAND platforms (X, Google Trends,
  Hacker News, news) tell you people are saying a thing. MARKET platforms
  (Etsy) tell you people are already selling it. Only demand counts toward
  breadth; market presence is reported separately as a saturation warning.

  breadth   how many DIFFERENT platforms mention it. A phrase on Reddit
            only is a subculture. The same phrase on Reddit + Google
            Trends + HN is crossing over. Crossover is the buy signal.

  velocity  today's mentions vs. this term's own recent average. Catches
            acceleration rather than size.

  novelty   how many days we've ever seen it. Something we first saw
            three days ago and is accelerating is the sweet spot.
            Something we've logged for 90 days is furniture, not a fad.

The weights below are guesses. They are SUPPOSED to be tuned by you after
you watch a few weeks of output. Tuning them is the actual craft.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

from signals import Signal, terms_by_platform

STATE_DIR = Path(__file__).parent / "state"
HISTORY_PATH = STATE_DIR / "history.json"

# --- tunable weights ---
W_BREADTH = 3.0     # reward cross-platform appearance heavily
W_VELOCITY = 2.0    # reward acceleration
W_NOVELTY = 1.5     # reward newness
W_PHRASE = 1.5      # prefer "quiet cracking" over the bare word "quiet"
MIN_TOTAL_MENTIONS = 3      # ignore one-off noise
MAX_DAYS_SEEN = 21          # older than this = established, not a fad

# Platforms that report SUPPLY rather than DEMAND. These are excluded from
# the breadth count -- see the note in score_terms(). Add any future
# marketplace source (Amazon, Redbubble, TeePublic) here, not to breadth.
MARKET_PLATFORMS = {"etsy"}
SHORTLIST_SIZE = 40         # how many candidates the agent gets to see

# Platform furniture. These recur forever and are never a trend. Cheap to
# filter here; expensive to filter with an LLM. Add to this list every time
# you see junk in a report -- this file is where you tune out noise.
NOISE_TERMS = {
    "show hn", "ask hn", "tell hn", "launch hn", "hacker news",
    "weekly discussion", "discussion thread", "daily thread", "megathread",
    "reddit", "tiktok", "youtube", "twitter", "instagram", "facebook",
    "github", "google", "apple", "microsoft", "amazon", "openai", "meta",
    "update", "release", "version", "announcement", "trailer", "episode",
    "score", "scores", "game", "games", "vs", "live stream", "highlights",
}


def is_noise(term: str) -> bool:
    if term in NOISE_TERMS:
        return True
    # a phrase built entirely from noise words is also noise
    words = term.split()
    return len(words) > 1 and all(w in NOISE_TERMS for w in words)


def load_history() -> dict:
    """history = {term: {"days": {"2026-08-05": 7, ...}}}"""
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text())
    return {}


def save_history(history: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def prune_history(history: dict, keep_days: int = 60) -> dict:
    """Keep the file from growing forever."""
    cutoff = sorted({d for t in history.values() for d in t["days"]})[-keep_days:]
    cutoff_set = set(cutoff)
    for term in list(history):
        history[term]["days"] = {
            d: c for d, c in history[term]["days"].items() if d in cutoff_set
        }
        if not history[term]["days"]:
            del history[term]
    return history


def score_candidates(
    signals: list[Signal],
    history: dict | None = None,
    today: str | None = None,
) -> tuple[list[dict], dict]:
    """
    Returns (ranked_candidates, updated_history).

    Each candidate dict is exactly what the agent will later see. Keep it
    small and human-readable -- if YOU can't tell why something scored
    high by reading the dict, the model can't either.
    """
    history = history if history is not None else load_history()
    today = today or date.today().isoformat()

    index = terms_by_platform(signals)

    # keep a couple of example headlines per term for evidence
    examples: dict[str, list[dict]] = defaultdict(list)
    from signals import extract_terms
    for sig in signals:
        for term in extract_terms(sig.text):
            if len(examples[term]) < 4:
                examples[term].append(
                    {"platform": sig.platform, "text": sig.text,
                     "url": sig.url, "score": sig.score}
                )

    candidates = []
    for term, per_platform in index.items():
        total = sum(per_platform.values())
        if total < MIN_TOTAL_MENTIONS:
            continue
        if is_noise(term):
            continue

        # --- record today's count into history ---
        entry = history.setdefault(term, {"days": {}})
        entry["days"][today] = total

        # --- breadth ---
        # Etsy is deliberately excluded from the breadth count. Every other
        # platform here measures DEMAND -- people saying a thing. Etsy measures
        # SUPPLY -- sellers already printing it. Counting it as breadth means a
        # phrase gets rewarded for being crowded, which is exactly backwards:
        # the first live demo of this ranked "loud budgeting" above "quiet
        # cracking" purely because three sellers had beaten us to it.
        #
        # So Etsy hits are carried as a separate number, and a high one is a
        # warning, not a score. The agent is told how to read it.
        demand = {p: c for p, c in per_platform.items() if p not in MARKET_PLATFORMS}
        breadth = len(demand)
        if breadth == 0:
            continue                       # listings only, nobody talking. skip.
        etsy_listings = per_platform.get("etsy", 0)

        # --- velocity: today vs. mean of prior days ---
        prior = [c for d, c in entry["days"].items() if d != today]
        baseline = (sum(prior) / len(prior)) if prior else 0.0
        velocity = math.log1p(total) - math.log1p(baseline)

        # --- novelty: fewer observed days = newer ---
        days_seen = len(entry["days"])
        if days_seen > MAX_DAYS_SEEN:
            continue  # established, not a fad
        novelty = 1.0 / days_seen

        # multi-word phrases are far more useful to you than bare words --
        # "quiet cracking" is a design brief, "quiet" is not.
        n_words = term.count(" ") + 1

        score = (
            W_BREADTH * (breadth - 1)      # 1 platform earns nothing
            + W_VELOCITY * velocity
            + W_NOVELTY * novelty
            + W_PHRASE * (n_words - 1)
        )

        candidates.append({
            "term": term,
            "score": round(score, 3),
            "breadth": breadth,
            "platforms": per_platform,
            # supply-side, kept separate from breadth on purpose
            "etsy_listings": etsy_listings,
            "mentions_today": total,
            "baseline": round(baseline, 2),
            "days_seen": days_seen,
            "examples": examples[term][:4],
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates, history


def dedupe_overlapping(candidates: list[dict], limit: int) -> list[dict]:
    """
    "quiet cracking", "quiet", and "cracking" will all rank. Keep the
    longest phrase and drop its own substrings so the agent isn't shown
    the same idea three times. Context window is a budget -- spend it on
    distinct ideas.
    """
    kept: list[dict] = []
    for cand in candidates:
        t = cand["term"]
        if any(t in k["term"] or k["term"] in t for k in kept):
            continue
        kept.append(cand)
        if len(kept) >= limit:
            break
    return kept
