# Session Notes 7

ModFraze session summary — Aug 10–12, 2026

## What we set out to do

Consolidate three scattered build attempts into one folder, then keep building
the agents.

## Consolidation

`trendscout` and `trendmerch_ai` turned out to be:

- **`Desktop\trend_scout`** — the August build, and newer than the copy buried
  in iCloud. Had `decide.py`, `notify.py`, the scheduler, and reports through
  08-07.
- **`iCloudDrive\04_Projects\ModFraze`** — the January build, plus a literal
  `trendmerch_ai\` subfolder holding the empty agent stubs from the earliest
  era. It was renamed to `ModFraze_project` partway through the session, which
  briefly looked like a different folder.

Result: **`Desktop\ModFraze`**, one tree.

| Folder | Contents | Era |
|---|---|---|
| `agents/trend_scout/` | the live agent — collect → score → tool loop → shortlist | August |
| `pipeline/` `db/` `schemas/` `integrations/` `ui/` `workflows/` | the plumbing | January |
| `docs/` `assets/` `dashboard/` | notes, art, ops workbook | mixed |
| `_archive/` | dead code, kept for the record | all |
| `_secrets_DO_NOT_COMMIT/` | quarantined `.env` files, gitignored | all |

Excluded deliberately: every `.venv`, every `__pycache__`, and the `xdk` repo
(X's public SDK generator — `pip install xdk`, don't vendor it).

## The iCloud failure

Error `0x800701AA`, then "The RPC server is unavailable" — iCloud's sync engine
was wedged, not the files. Placeholder hydration was failing system-wide; even
listing the folder hung. Reboot and app repair are the fixes; the workaround
that actually unblocked us was downloading through iCloud.com in a browser,
which bypasses the local provider entirely.

Retrieving `setup_check.py` paid for itself immediately: running it showed the
January code reads `SHOPIFY_ACCESS_TOKEN`, `PRINTIFY_API_KEY` and
`APIFY_API_KEY` — not the names guessed in `.env.example` — plus eight
variables that had been missed entirely. All corrected.

Full audit before deleting the source: 51 of 57 files accounted for, the
remaining six trivial dotfiles that iCloud.com doesn't display. Etsy 2FA backup
codes confirmed stored elsewhere; they were never copied into the repo by
design.

**Standing recommendation:** keep code off iCloud. Thousands of small files
behind a sync engine means slow imports, failed builds, and git operations that
hang. Assets and docs are fine there.

## Etsy adapter

TikTok was already a documented dead end in the newer `sources.py` — the
Research API is academic/non-profit only, and Apify is the only other route and
violates TikTok's ToS. Etsy was chosen instead: free official API, no ToS
problem, and it measures what actually sells rather than what gets views.

Built two functions, verified against Etsy's real OpenAPI spec rather than the
docs site:

- **`etsy()`** — newest active listings, sorted by `created` rather than
  relevance. Relevance surfaces what sells *well*, which is by definition
  established and too late. New listings are sellers placing bets.
- **`etsy_saturation(term)`** — how crowded a phrase already is, with a
  plain-English verdict. Not wired in yet; shaped to become an agent tool.

### The bug it exposed

Adding Etsy rows to the demo fixture pushed "loud budgeting" to the top of the
rankings — **because three sellers had already printed it.**

`breadth = len(per_platform)` was counting Etsy as one more platform saying the
phrase. But Etsy is the one source that measures SUPPLY; every other source
measures DEMAND. The scoring was rewarding terms for being crowded, which is
exactly backwards.

Fixed: `MARKET_PLATFORMS` set in `scoring.py`, Etsy excluded from breadth and
carried separately as `etsy_listings`. The agent's system prompt now reads a
high count as a lateness warning — 0 is the position we want, 4+ means
competing on execution rather than timing.

### Rate limit

An unapproved Etsy app gets **5 requests per day**. The original default of 500
listings was 5 requests — the entire daily quota in one 6am scheduled run,
leaving every later call to fail. Rebudgeted in requests rather than listings:
`ETSY_MAX_REQUESTS=1`, checked before each call, clamping the listing cap to
match. Raise to ~5 / 500 after approval.

## Also fixed

Both scheduler `.bat` files hardcoded `C:\Users\miket\Desktop\trend_scout` and
fail fast when the venv is missing — so the **daily collect has been silently
dead since the move.** Last reports are 08-06 and 08-07. Five days of velocity
baseline lost, and velocity is most of what makes the scout work. Both files
repointed at the new layout, where the venv and `.env` live at the ModFraze
root and `run.py` lives in the scout folder.

## Git

Discarded the local `trend_scout` repo (9 commits, never pushed, didn't match
how the project is thought about). Connected to
`michaelstuartthompson/modfraze` — public, one placeholder commit — adopted
that commit as the base rather than overwriting, and committed 101 files.
A second commit removed five duplicated assets and a 0-byte `setup_check.py`
husk left over from the iCloud failure.

Secrets verified absent from the staged set before pushing, which mattered
because the repo is public.

## Still open

- venv and `.env` at the ModFraze root; restart the daily collect and confirm a
  line lands in `logs\collect.log`
- `git push` for the cleanup commit
- Etsy Personal App pending human review — days to months. Use
  `tools/etsy_probe.py` to test the key; do **not** add `etsy` to
  `scout_run.bat` yet, or the 6am job spends the one useful daily request on
  data nobody reads
- Next build: wire `etsy_saturation` in as an agent tool, then the SQLite
  migration to replace `state/history.json`
- Still unintegrated from the ChatGPT documents: the named niche umbrella, hard
  production specs (DPI, canvas, exports), and the **3 concepts → 1 winner**
  choice-limiting gate
- Brand palette still unlocked — one palette per asset until it is
