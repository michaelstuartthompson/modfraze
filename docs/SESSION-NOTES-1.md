# Session notes — trend scout build

**Date:** 2026-08-05

---

## What this session produced

A working trend-spotting agent at `ModFraze/agents/trend_scout/`. It finds
words and phrases surfacing on more than one platform at once and reports
candidates worth designing merch around.

### Files

| file | what it is |
|---|---|
| `signals.py` | The `Signal` shape every data source is converted into, plus n-gram term extraction |
| `sources.py` | One adapter per platform. Google Trends + Hacker News work with no API key. Reddit works from a home IP. Etsy/X/TikTok/Amazon are stubs |
| `scoring.py` | Pure-Python scoring. No LLM. Ranks terms by cross-platform breadth, acceleration, and newness |
| `agent.py` | The agent loop. Tools + schemas + the model call |
| `run.py` | Entry point, wires the stages together, writes reports |
| `env_loader.py` | Finds and loads `ModFraze/.env` using only the stdlib |
| `brand.md` | The agent's taste — five untested niche hypotheses. Edit this, not the code |
| `TUTORIAL.md` | Full written walkthrough |

### Architecture

Three stages: **collect → score → agent.**

~1,500 items become ~40 by ordinary Python counting, then the model turns ~40
into ~5. The reason for the split: deterministic code handles anything with a
right answer (counting, comparing to yesterday), the model handles only
judgment (is this a real phrase, is it early, does it fit the brand).

Sending all 1,500 to the model is the common beginner approach. It's expensive
and it can't measure change over time, because a model handed one day of data
has no yesterday.

---

## Current state

**Works, verified:**

- `python run.py --demo --collect-only` — fixtures, no network, no key
- `python run.py --collect-only` — live collection + scoring
- Google Trends and Hacker News adapters
- Report writing to `reports/`

**Not yet run:** the actual agent stage. Blocked on the environment, not the
code.

---

## Open items

1. **Set up git.** Not done. Start here.
2. **Fix iCloud.** iCloud Drive on Windows is not hydrating files — every file
   older than this session returns "RPC server is unavailable" on read.
   `notepad .env` failed for this reason. Try: quit iCloud from system tray and
   reopen, then reboot if that fails.
3. **Move the project out of iCloud.** A live code directory in a
   sync-on-demand folder causes intermittent import errors that look like code
   bugs. Local folder + git is the normal arrangement.
4. **Add the Anthropic key.** Either into `ModFraze/.env` as
   `ANTHROPIC_API_KEY=sk-ant-...`, or per-session in PowerShell with
   `$env:ANTHROPIC_API_KEY = "sk-ant-..."`. Key was created but not yet placed.
5. **`pip install anthropic`** in the project venv. Not yet done.
6. **Confirm `.env` is gitignored** before any push.
7. **Run `--collect-only` daily for about a week** before judging output.
   Velocity is measured against a term's own history, and on day one there is
   none, so everything looks like it's exploding.
8. **Add Reddit, then Etsy.** Only two sources currently work, and
   cross-platform breadth is the core signal — two is weak. Etsy matters
   because it shows what's already selling on merch, which is the saturation
   check.

---

## Things established about ModFraze

- The existing product names (*Passive Aggression*, *Regret Concierge*, etc.)
  came from an AI-generated phrase exercise for design practice. They are not
  evidence of a niche.
- Niche is undetermined. `brand.md` holds five hypotheses (H1 social friction,
  H2 internet moments, H3 work/money, H4 subculture identity, H5 pure visual
  trend) and the agent tags each pick with which one it tests.
- H5 is the only hypothesis where the trend is visual rather than verbal, and
  it's the one that plays to the actual art skill.
- There's a decision log table at the bottom of `brand.md`. After ~30 entries
  it should show real patterns.

---

## Note on how this session went

Too much output, too fast, and it created a backlog of untracked tasks instead
of understanding. If picking this back up: **one step at a time, stop and wait.**
Start with git.
