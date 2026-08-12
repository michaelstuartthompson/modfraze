# Session notes 2 — getting it out of iCloud, running it, wiring the loop

**Date:** 2026-08-05 (evening)
**Previous:** SESSION-NOTES.md

---

## What changed

The project moved off iCloud, got version control, and ran end to end for the
first time. The agent stage — never executed before tonight — works.

### Location

`C:\Users\miket\Desktop\trend_scout`

Copied out of `iCloudDrive\04_Projects\ModFraze\agents\trend_scout`. The
original is untouched; nothing was deleted.

### Why the move was only partial

The full-project copy failed: 1,092 files, 48.8 MB, and robocopy transferred
exactly **one** of them before stalling. That confirmed the diagnosis in the
previous session's notes — iCloud is refusing to hydrate, and no copy tool
gets around it.

The trend_scout subfolder copied cleanly because those files were touched
today and are still local. The other seventeen ModFraze folders remain stuck
in iCloud and still need the reboot fix.

`.env` and `.venv` were deliberately excluded from the copy.

---

## Done

| # | item | status |
|---|---|---|
| 1 | Set up git | done — `main`, initial commit, 13 files |
| 4 | Anthropic key | done — new key, `.env` at `trend_scout\.env` |
| 5 | `pip install anthropic` | done — fresh `.venv` |
| 6 | Confirm `.env` gitignored | done — ignored *before* the first commit |

Plus, not on the original list:

- **Email delivery.** `notify.py`, stdlib `smtplib` over Gmail SMTP. Sends the
  markdown report as both body and attachment. Fails soft — a broken mail
  config prints a warning and never takes down a run that otherwise worked.
- **Decision ledger.** `decisions.py` + `decide.py`.
- **First full agent run.** `python run.py --demo` produced a shortlist with
  art direction and a weeks-to-peak estimate.

### Note on the first run

Given two candidates with nearly identical scores — `quiet cracking` 12.22 and
`loud budgeting` 11.77, both 3 platforms, both day-one — the agent approved one
and rejected the other on the *content of the example posts*, not the numbers.
That is the collect/score/agent split doing exactly the thing it was built for.
Mechanical scoring could not have made that call.

---

## New files

| file | what it is |
|---|---|
| `notify.py` | Emails the report. Reads `SMTP_USER`, `SMTP_APP_PASSWORD`, `NOTIFY_TO` from `.env` |
| `decisions.py` | The ledger. `state/decisions.jsonl` is source of truth; the brand.md table is rendered from it |
| `decide.py` | CLI for approve / deny / sold |

Edits to existing files:

- `run.py` — added `--notify`; logs every pick to the ledger as `pending`
- `agent.py` — loads `decisions.load_calibration()` into the prompt

---

## How the decision loop works

**Every pick is logged automatically as `pending`** the moment a report is
written, before you look at anything. Picks you ignore stay pending forever,
on purpose. "Surfaced, ignored" is the most common outcome and the one most
worth counting — a ledger that only records decisions you bothered to make
will flatter the agent.

```
python decide.py list
python decide.py approve "quiet cracking" -n "strong H1 fit, phrase stands alone"
python decide.py deny    "loud budgeting"  -n "already on Etsy, we're late"
python decide.py sold    "quiet cracking"  --yes
python decide.py status
```

The `-n` note is optional and is the entire point. Bare approve/deny teaches
nothing; the reason is the payload.

**Calibration is gated at 10 decisions.** `load_calibration()` returns an empty
string until then, so `agent.py` needs no conditional — the feature switches
itself on once the evidence exists. Two data points is not taste, and an agent
shown two rejections will overcorrect into refusing anything that rhymes with
them.

`sold?` is tracked separately from `designed?`. Approving costs nothing;
selling is the only field that actually tests H1–H5.

---

## Cadence decision

**Collect daily, agent twice weekly (Mon + Thu).**

The reasoning: velocity is measured against a term's own history, and history
comes from the *collect* stage, which is free. Only the agent stage costs
money. So daily `--collect-only` builds the baseline at zero cost, and the
paid stage runs against a real curve instead of day-one noise where everything
looks like it's exploding.

Roughly 30¢/month against $25 of credit.

Neither task is scheduled yet.

---

## Open items

1. **Commit the new files.** `notify.py`, `decisions.py`, `decide.py`, and the
   `run.py` / `agent.py` edits are all untracked. Do this first.
2. **Verify `decide.py` end to end.** Approve or deny the `quiet cracking`
   pick and confirm the table at the bottom of `brand.md` fills in.
3. **Clear the demo data.** The ledger and `state/history.json` currently hold
   fixture terms from `--demo` runs. Decide whether to wipe before real
   collection starts, or the baseline is polluted with fake history.
4. **Windows Task Scheduler, two tasks.** Daily `--collect-only`; Mon/Thu
   `run.py --notify`. Both need the venv Python, not system Python.
5. **Fix iCloud, then move the rest of ModFraze.** Quit from the system tray,
   reopen, reboot if that fails.
6. **API key expiry.** Set a reminder before it lapses — a scheduled scout
   fails silently on a dead key.
7. **Add Reddit, then Etsy.** Still the highest-value code change. Two working
   sources is weak when cross-platform breadth is the core signal, and Etsy is
   the saturation check — it shows what's already selling on merch.
8. **Run live `--collect-only` for about a week** before judging output.
9. **Second, empty `ModFraze` folder** at `iCloudDrive\02_Business & Tech\`
   reported 0 files. Either a stale duplicate or more dehydration. Check after
   the iCloud fix.
10. **Twilio.** Bought, then not used — email won on content shape. Decide
    whether to keep the subscription for something else or cancel it.

---

## On how this session went

Better than the last one. One step at a time, each verified before the next,
and the two failures that came up — the iCloud stall and the `agent.py`
indentation — were caught immediately because nothing was stacked on top of
unverified work.

The one thing that got ahead of itself: `notify.py`, `decisions.py`, and
`decide.py` all arrived before any of them was tested, which is why the missing
`decisions.py` and the bad indent surfaced together instead of separately.
