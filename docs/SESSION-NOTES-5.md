# Session notes 5 — X goes live, first pick logged

**Date:** 2026-08-08 **Previous:** SESSION-NOTES-4.md

---

## The headline

X is live, and the pipeline produced its first real pick — though not the way
it was designed to. Mike found the phrase by reading ten tweets, not by the
scout scoring it. That distinction is now recorded rather than smoothed over,
because it is the most interesting open question in the project.

Total spend this session: **$0.20** (four X probes at 10 posts each).

---

## Done

| # | item | status |
| :---- | :---- | :---- |
| 1 | Run the X smoke test | **done** — auth, cap, billing all verified live |
| 2 | Rewrite the X query | diagnosed, not yet rewritten — see below |
| — | Strip URLs from tokenizer | **done and verified** |
| — | Remove Reddit from the code | **done** |
| — | Log first pick + fill dashboard | **done** |

---

## The X smoke test

First live call: 10 posts, exit clean, `[cost] x: 10 posts read ~ $0.05`.
Cap enforcement, app-only bearer auth and per-post billing all behave as the
offline tests predicted.

One immediate finding: the single highest-scoring candidate was **`https t co`**.
Every X post carrying a link tokenizes to `["https", "t", "co", <hash>]`, and
since most posts carry links, the trigram appeared everywhere. Fixed by
stripping whole URLs *before* tokenizing rather than filtering terms after —
the artifact is now dead at the source. Verified.

---

## What the query frames actually return

The default query OR's six frames together. Nine of the first ten posts came
back on `"is the new"`, so the other frames were never really tested. Probed
two of them in isolation (`tools/query_probe.py`, added this session).

**`is the new`** — wrong frame. It is a *comparison* template, not a naming
one: "Iglesias is the new Will Smith", "X is the new Instagram", "Privacy is
the new utility". Sports analogies and crypto marketing. Almost never names
anything new.

**`apparently it's called`** — 10/10 posts named something, so structurally it
is exactly right: the phrase reliably follows the frame. But it surfaces things
the *speaker* didn't know the name of, not things that are new — gaslighting,
nested mapping, the wicker man, rain. Personal ignorance, not emergence.

**`everyone's calling it`** — semantically the best of the three, because
collective naming *is* adoption. But it attracts finance and engagement-bait
threads where "it" resolves to an evaluative label rather than a name: a heist,
a disaster, an opportunity, reliability. One genuine hit in ten — **"AI brain
fry"**.

### Two structural findings, more important than the query itself

1. **The frame words win the term count.** `apparently`, `called`, `it's called`
   top every probe. The system is measuring its own query. Query terms need
   stripping the same way URLs did.

2. **Bag-of-n-grams is the wrong extractor for X.** The phrase always sits
   *immediately after* the frame. `everyone's calling it ___` is a capture
   group, not a trigram problem. A positional extractor would have caught
   "AI brain fry" automatically instead of Mike catching it by eye. This is
   probably the real fix — not a better query, a different extractor for
   frame-matched sources. Not yet built.

---

## Reddit, removed

The `reddit()` adapter, its `SOURCES` entry, and its demo fixtures are gone.
Demo signals reattributed to `x` and `web_news` so the fixture still exercises
cross-platform breadth. The adapter is in git history if the policy ever
changes; it is not carried in the tree as dead weight.

Two mentions were **kept deliberately**: `scoring.py` and `signals.py` both
list "reddit" as a noise word to ignore *in text*. Removing those would let
"reddit" become a candidate term from news headlines.

This also explains the six `403`s per run in `logs/collect.log` — Reddit was
out of `run.py`'s defaults but `collect()` falls back to all of `SOURCES` when
passed nothing. Fixed by removal.

---

## First pick: AI Brain Fry

Logged to `state/decisions.jsonl` as **pending**, and written into
`ModFraze_Dashboard.xlsx` (backup saved alongside):

| tab | row |
| :---- | :---- |
| Designs | `MF-DES-20260808-AIBrainFry-V01`, status `concept` |
| Products | `MF-AIBRAINFRY-TEE`, `draft`, $29.99 / $11.50 |
| Content Calendar | three organic posts, Aug 11 / 13 / 15 |
| Ads | `MF-AD-TT-202608-Conversions-02`, **planned, not active** |
| Experiments | `MF-EXP-20260808-01` |

Two judgment calls worth recording:

**The ad campaign is staged, not running.** $5/day, $35 cap, Aug 24. There is
no artwork yet, so there is nothing to advertise. The organic posts run first
and cost nothing; if the phrase gets no traction there, the $35 is saved and
the lesson is identical.

**It is logged as an instinct pick, n=1.** One post, no baseline, never scored
by the scout. That is not a knock — it reads better than anything the scout has
produced in two weeks. But the Experiments row now tests exactly that: whether
Mike's instinct outperforms the scoring. If it does, that finding is worth more
than any query rewrite, and it changes what this system should be.

---

## A caught mistake

While writing dashboard rows, formulas were copied from the template row using
a blind string replace of the row number. That turned `$F2*2.5` into `$F3*3.5`
— silently changing the price-floor rule on the new product. Caught on
verification, fixed with a proper column-anchored regex, and 281 formulas across
`Designs` and `Products` were re-derived correctly.

Worth recording because it is the same class of bug as `https t co`: a
transformation applied one level too broadly, producing output that looks
plausible and is wrong.

---

## Open items

1. **Strip query frame terms** from extraction, as URLs now are.
2. **Build the positional extractor** for frame-matched X posts. Highest-value
   code change available.
3. **Rewrite the X default query** — but only after 1 and 2, since both change
   what a "good" query looks like.
4. **`StartWhenAvailable`** on both scheduled tasks. Carried from session 4.
5. **Delete `notebook.env.txt`.** Carried from session 4.
6. **Etsy** — the saturation check, and the only remaining high-value source.
7. **Fix iCloud, move the rest of ModFraze.** Seventeen folders, untouched.
8. **Let the baseline build.** Both scheduled runs still return zero picks for
   the correct reason: `days_ever_observed: 1`, `recent_daily_average: 0.0`.
   Nothing can look like emergence yet. Roughly a week to go.
9. **Twilio.** Still bought, still unused.
10. **Reddit commercial ticket.** Now a clean yes/no — the code no longer
    assumes either answer.

---

## Next

The image-generation agent. Blocked on aesthetic direction: it needs training
on what Mike actually wants before it can be useful. Starting point is
reference images, not code.

---

## On how this session went

Better on process. One command at a time, each verified before the next, which
is what sessions 2 and 4 both said to do.

The schema-guessing stretch was the weak part — four commands spent probing
`history.json` and `raw.json` structure one blind one-liner at a time, when
requesting folder access at the start would have answered all of it in a single
read. Getting file access earlier is the lesson.

The X finding is the substantive outcome. The query was a reasoned guess that
turned out to be wrong in an informative way: not "bad results" but the wrong
*kind* of frame, which is only visible by reading actual posts. $0.20 well
spent.
