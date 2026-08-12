"""
signals.py -- the common shape every data source gets flattened into.

WHY THIS EXISTS
---------------
Reddit, Google Trends, TikTok and Etsy all return wildly different JSON.
If every part of the system had to know each API's quirks, adding a source
would mean touching five files. Instead each source adapter converts its
own mess into ONE dataclass: Signal.

This is the single most valuable habit in agent engineering. The model
should never see raw API responses. It sees a clean, uniform shape you
control -- so its behavior stays stable when a source changes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Iterable


@dataclass
class Signal:
    """One observed thing on one platform at one moment."""

    platform: str            # "x", "google_trends", "hackernews", ...
    text: str                # headline / post title / query string
    url: str = ""            # where a human can go look at it
    score: float = 0.0       # platform-native popularity (upvotes, etc.)
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Term extraction
# ---------------------------------------------------------------------------
# We need to turn free text into countable "terms" so the same idea appearing
# on Reddit AND Google Trends AND Hacker News can be recognized as the SAME
# thing. This is deliberately dumb n-gram counting -- no ML, no embeddings.
#
# Dumb and predictable beats clever and opaque here, because this stage runs
# on thousands of items and you want it fast, free, and debuggable. The smart
# judgment happens later, in the agent, on ~40 survivors.

STOPWORDS = set("""
a an the and or but if then than that this these those of in on at to for from
by with without about into over under again further once here there when where
why how all any both each few more most other some such no nor not only own
same so too very can will just dont should now is are was were be been being
have has had do does did doing i you he she it we they me him her us them my
your his its our their what which who whom as up down out off above below new
best top get gets got make makes made says said just like really need needs
after before while because during vs via amp reddit tiktok video post thread
today year day week month time people thing things way ways
""".split())

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'\-]*")

# URLs must be removed BEFORE tokenizing, not filtered after. A t.co link
# tokenizes to ["https", "t", "co", <hash>], and the trigram "https t co"
# then appears in every post carrying any link -- which on X is most of
# them. That made it the single highest-scoring candidate in the first
# live X run. Stripping whole URLs kills the artifact at the source.
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(URL_RE.sub(" ", text).lower())


def extract_terms(text: str, max_n: int = 3) -> set[str]:
    """
    Return the set of candidate terms in a piece of text.

    Produces unigrams, bigrams and trigrams. A term is kept only if it
    contains at least one non-stopword, so "of the" is dropped but
    "regret concierge" survives.
    """
    tokens = tokenize(text)
    terms: set[str] = set()

    for n in range(1, max_n + 1):
        for i in range(len(tokens) - n + 1):
            gram = tokens[i : i + n]

            # skip grams that start or end on a stopword -- those are
            # almost always sentence glue, not concepts
            if gram[0] in STOPWORDS or gram[-1] in STOPWORDS:
                continue
            # skip pure-stopword and pure-numeric grams
            if all(t in STOPWORDS for t in gram):
                continue
            if all(t.isdigit() for t in gram):
                continue
            # single tokens must be substantial
            if n == 1 and (len(gram[0]) < 4 or gram[0] in STOPWORDS):
                continue

            terms.add(" ".join(gram))

    return terms


def terms_by_platform(signals: Iterable[Signal]) -> dict[str, dict[str, int]]:
    """
    Invert the signal list into: term -> {platform: count}.

    This is the data structure the whole "is it cross-platform?" question
    is answered from.
    """
    index: dict[str, dict[str, int]] = {}
    for sig in signals:
        for term in extract_terms(sig.text):
            index.setdefault(term, {})
            index[term][sig.platform] = index[term].get(sig.platform, 0) + 1
    return index
