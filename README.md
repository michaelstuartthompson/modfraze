# ModFraze

Canonical working folder. Everything that matters from three earlier build attempts
now lives here. Consolidated 2026-08-10.

---

## What's where

| Folder | What it is | Provenance |
|---|---|---|
| `agents/trend_scout/` | **The live agent.** Collect → score → LLM tool loop → shortlist → decision ledger. This is the newest and most complete code. | August build (`Desktop\trend_scout`) |
| `pipeline/` | SQLite ingestion + dedupe + `run_daily.py` orchestration. The plumbing the agent still lacks. | January build |
| `db/` | SQLAlchemy models, init script, and `modfraze.db` — **real collected data, do not delete** | January build |
| `schemas/` | `trend.py`, `design.py`, `product.py` — the object model, incl. the 2.5× pricing floor | January build |
| `integrations/` | Printify, Shopify, Meta Ads, DALL·E, TikTok (Apify) API clients | January build |
| `ui/` | Streamlit approval dashboard | January build |
| `workflows/` | Prefect flow definitions | January build |
| `dashboard/` | Ops workbook + the openpyxl script that builds it | August build |
| `docs/` | Session notes 1–6, MVP Operating System, architecture prompt, TikTok research | mixed |
| `assets/` | Product images, logos, Etsy banner | January build |
| `_archive/` | Dead code kept for the record — nothing here is imported | all eras |
| `_secrets_DO_NOT_COMMIT/` | Old `.env` files and recovery codes, quarantined and gitignored | all eras |

**Deliberately not copied:** every `.venv/`, every `__pycache__/`, and the `xdk` repo
(that's X's public SDK generator — use `pip install xdk`, don't vendor it).

---

## Run the agent

```powershell
cd C:\Users\miket\Desktop\ModFraze
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install anthropic
copy .env.example .env      # then paste your ANTHROPIC_API_KEY into it

cd agents\trend_scout
python run.py --demo        # no network, no keys — proves the pipeline works
python run.py               # real sources
```

`--demo` uses the fixture data in `sources.py`. Always run it first after a move:
if demo works and live doesn't, the problem is network or keys, not your logic.

---

## Sources

| Source | Status | Notes |
|---|---|---|
| `google_trends`, `hackernews`, `web_news` | live | free, no key |
| `x` | live | paid per post read, hard budget cap in `sources.py` |
| `etsy` | **built, needs a key** | free API, but requires an approved Personal App — human review, days to months. Apply early. |
| `tiktok` | closed | Research API is academic/non-profit only. Apify is the only route and it's against TikTok's ToS. |
| `reddit` | removed | self-service API registration closed; commercial use needs written approval |

Etsy is the only source that measures **supply** (what sellers already print)
rather than **demand** (what people say). It is therefore excluded from the
breadth score and reported separately as `etsy_listings` — a lateness warning,
not a point in a term's favour. `MARKET_PLATFORMS` in `scoring.py` is where any
future marketplace source belongs.

`sources.etsy_saturation(term)` exists but is not wired in yet — it's designed to
become an agent tool so the model can ask "how crowded is this already?" about a
specific candidate.

## The merge that's still outstanding

The January and August builds are complementary halves of one system, and joining
them is mostly file moves, not new code:

1. `integrations/tiktok_adapter.py` fills the `tiktok()` stub in
   `agents/trend_scout/sources.py`
2. `TrendSignal` (January) maps onto `Signal` (August) with field renames
3. SQLite (`db/`) replaces `agents/trend_scout/state/history.json` as the store
4. `pipeline/run_daily.py` becomes the single scheduled entry point

Do these in that order. Each one is independently testable with `--demo`.

---

## Known gaps

- **Five files were iCloud-online-only and did not transfer.** Open each once in
  Explorer (or right-click → *Always keep on this device*) to force a download,
  then re-copy. From `iCloudDrive\04_Projects\ModFraze\`:
  - `Pipeline\manage_campaigns.py` (12.7 KB) → `pipeline\`
  - `Library\modfraze logo.png`, `modfraze logo 2.png`, `Logo green on blue.PNG` → `assets\brand\`
  - (`Library\Etsy Codes*.png` are 2FA backup-code screenshots — deliberately
    **not** copied and gitignored. Leave them out of this folder entirely.)
- The ChatGPT Operating Guidebook and original Prompt document are not yet
  integrated. They contain a named niche umbrella, hard production specs
  (DPI/canvas/exports), and the **3 concepts → 1 winner** choice-limiting gate.
- Brand palette still unlocked — two candidates. One palette per asset until it is.
- Dead on arrival, archived not deleted: `x_scraper.py` (snscrape broke in 2023),
  `tiktok_trends.py` (music-ID endpoint answers the wrong question).

---

## Before the first commit

`git log --all --oneline -- .env` on the old `trend_scout` repo returned nothing —
**`.env` was never committed.** The `.gitignore` here covers secrets, generated
output, venvs, and the DB. Safe to `git init` fresh.

The old `Desktop\trend_scout\.git` history was intentionally left behind rather than
moved. If you want that history, `git init` here and add the old repo as a remote —
don't copy `.git` over the top.

---

## Originals

Nothing was deleted. Sources still sit at `Desktop\trend_scout` and
`iCloudDrive\04_Projects\ModFraze`. Verify this folder runs, then remove them.
