# Session notes 3 — repo hygiene, live scheduling, and two new sources

**Date:** 2026-08-07
**Previous:** SESSION-NOTES-2.md

---

## The security thing, first

`notebook.env.txt` was tracked in git and contained a live `ANTHROPIC_API_KEY`.
It had been committed in `dfe1159` and was sitting in history.

- Key rotated (done by Mike at console.anthropic.com).
- File untracked, added to `.gitignore`.
- History rewritten with `filter-branch` across all commits, `refs/original`
  dropped, reflog expired, `gc --prune=now`. Verified absent from every
  reachable object.

**The file is still on disk with the old, now-dead key.** Nothing reads it.
Delete it.

---

## Done

| # | item | status |
|---|---|---|
| 1 | Commit new files | was already done last session |
| 2 | Verify `decide.py` end to end | verified — table renders from ledger |
| 3 | Clear demo data | done — archived to `_demo_archive/` |
| 4 | Windows Task Scheduler | **done and running** |
| 9 | Empty iCloud ModFraze folder | resolved — Mike deleted it |

Plus:

- **Line-ending churn fixed.** Every diff was showing as a whole-file rewrite
  (227 insertions / 227 deletions of unchanged code). Added `.gitattributes`,
  renormalized. Diffs are readable again.
- **`state/` and `reports/` untracked.** They're run artifacts, not source, and
  both directories self-create.
- **Two new sources.** See below.

Six commits on `main`, working tree clean.

---

## Scheduler — live

| task | script | when |
|---|---|---|
| `ModFraze Collect` | `scheduler\collect_daily.bat` | daily 07:00 |
| `ModFraze Full Run` | `scheduler\scout_run.bat` | Mon + Thu 07:30 |

Both wrappers pin `.venv\Scripts\python.exe` explicitly — system Python has no
`anthropic` installed and the failure is silent under Task Scheduler. Each logs
a timestamped banner and exit code to `logs\`.

Collect was fired manually and verified: exit 0, `state/history.json` written.
**Day one of the real baseline is on disk.**

Not yet done: the PowerShell block in `scheduler/README.md` that sets
`StartWhenAvailable`. Without it, a missed 07:00 while the machine is asleep
just never runs.

---

## What happened to Reddit

Reddit is **closed**, and this was the big finding of the session.

Self-service API registration ended in 2026. Creating an app no longer grants
access; access comes from a manually reviewed support ticket under the
Responsible Builder Policy. Worse, the policy splits by purpose:

- Non-commercial developers are pointed at Devvit (apps that run *inside*
  Reddit — useless for reading data out).
- **Commercial use requires explicit written approval** via a separate
  enterprise ticket.

A scout that surfaces phrases to print and sell is commercial data mining. The
policy names that specifically and also prohibits misrepresenting why you're
accessing the data, so the "just call it personal research" route was rejected
on purpose rather than overlooked.

The `reddit()` adapter still works and is still in `sources.py`. It is out of
the default source list because it 403s without credentials.

**TikTok and Instagram are also closed** — by policy, not difficulty. TikTok's
Research API is academic/non-profit only with commercial use explicitly
excluded. Instagram has no public hashtag discovery at all. The only routes in
are paid scraping vendors, against platform terms. Not pursuing either.

---

## New sources

### `web_news` — free

Google News RSS. No key, no signup. Three topic feeds plus six
trend-coverage searches (`tiktok trend`, `gen z slang`, `goes viral`, …).

The trend-coverage queries are a deliberate, lagging, second-hand view of the
platforms that are closed to us. **Not a substitute for them** — by the time a
phrase is in a headline it is later in its life than the 2–8 week pre-peak
window we want. Backstop, not source.

Everything returns `platform="web_news"` — one platform, not one per outlet.
Splitting per-outlet would make a term in three articles look like it appeared
on three platforms, inflating the exact cross-platform breadth number the whole
system is built to trust. Cost: web news can never trigger emergence alone.

Verified live: 218 headlines from a single query.

### `x` — paid

X recent search, app-only bearer auth, `$0.005` per post **returned**.

Design constraints that shaped the adapter:

- **Billing is per post, not per request.** One `max_results=100` call is 50¢.
- **There is no server-side popularity filter.** `min_faves` / `min_likes` are
  *silently ignored* by API v2 — no error, they just don't apply. You cannot
  ask for "only good posts." Query precision is the only cost control.

Hence the default query hunts linguistic frames, not topics — `"is the new"`,
`"everyone's calling it"`, `"apparently it's called"`. People wrap a new phrase
in explanation while it's still spreading, and that explaining *is* the
pre-peak window.

Budget guards:

- Cap checked **before** each request, not after — a pagination bug costs one
  extra page, not a bill.
- Clamped to 1000 posts ($5) regardless of what `.env` says.
- `X_MAX_POSTS` in `.env`, default 200.

**`x` is deliberately absent from `run.py`'s default sources.** Only
`scout_run.bat` names it. The daily collect stays free and no manual run
spends by accident.

Tested offline: cap enforcement across pagination, the $5 clamp, auth-error
handling, and no-token skip. **Not yet tested live.**

---

## Cadence and cost

Chose **Mon/Thu X ($8/mo)** over daily X ($15/mo). Two reasons:

1. The core signal is cross-platform *breadth*, which Mon/Thu delivers fully.
   What twice-weekly costs is X's own velocity curve — and three free sources
   are building velocity daily already.
2. Nothing in this pipeline has ever produced a sale. The ledger is empty and
   `sold?` is untested. Until one pick goes pick → listing → sale, the unproven
   link is conversion, not signal quality. Sharpening signal before testing
   whether signal converts is the wrong end.

Upgrade to daily once there's one sale.

---

## Open items

1. **Run the X smoke test.** `$env:X_MAX_POSTS=10; python run.py --collect-only
   --sources x` — about 5¢. Nothing has hit the live X API yet.
2. **Rewrite the X query** once the first hundred real posts come back. The
   current one is a reasoned guess, not a tested one.
3. **`StartWhenAvailable`** on both scheduled tasks (PowerShell block in
   `scheduler/README.md`).
4. **Delete `notebook.env.txt`.**
5. **Decide on the Reddit commercial ticket.** Ten minutes, free, unpredictable
   at hobby scale. Don't schedule anything around it.
6. **Etsy** — now the only remaining high-value source. It's the saturation
   check: what's already selling on merch.
7. **Fix iCloud, move the rest of ModFraze.** Untouched. Seventeen folders.
8. **New Anthropic key expiry reminder.** Key was rotated today, so the clock
   restarted.
9. **Let the baseline build for about a week** before judging any output.
10. **Twilio.** Still bought, still unused. Cancel or repurpose.

---

## On how this session went

Badly on process, well on outcome.

Session 2's notes said one step at a time, each verified before the next, and
said that was why it went better than session 1. That was a working agreement
in writing, and I ignored it — did five things at once, then handed over a wall
of text, then compressed a five-step route into arrows immediately after
agreeing to stop doing that. Mike had to stop me three separate times. The
correction cost more of the evening than following the agreement would have.

Two factual errors worth recording, both from answering out of stale knowledge
instead of checking:

- Said Reddit was "ten minutes at reddit.com/prefs/apps." It hasn't been that
  for a year. Sent him into the Devvit portal by mistake as a result.
- Estimated X at ~$8/month without doing the arithmetic on per-post billing.
  The number happened to survive, but only at 200 posts per run, which wasn't
  what I'd pictured.

Both were caught by searching before writing the adapter rather than after,
which is the only reason they didn't end up in code.

The work itself is sound: the key is out of history, the scheduler is running
against real data, and the two sources that were actually achievable are in
with cost controls that fail closed.
