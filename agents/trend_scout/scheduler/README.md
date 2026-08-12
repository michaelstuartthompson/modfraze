# Scheduling the scout

Two tasks, two different reasons.

| task | what runs | when | cost |
|---|---|---|---|
| `ModFraze Trend Scout - Collect` | `collect_daily.bat` | every day, 07:00 | free |
| `ModFraze Trend Scout - Full Run` | `scout_run.bat` | Mon + Thu, 07:30 | ~4¢ per run |

Collect is daily because velocity is measured against a term's own history, and
history only exists if something writes it down. The agent stage is the only
part that costs money, so it runs twice a week against a real curve instead of
day-one noise where every term looks like it's exploding.

Both scripts call `.venv\Scripts\python.exe` directly. **Do not point Task
Scheduler at `python.exe` on PATH** — that's system Python, which does not have
`anthropic` installed, and the failure is silent in a scheduled context.

---

## Register the tasks

Open PowerShell **as Administrator** and paste:

```powershell
schtasks /Create /TN "ModFraze Trend Scout - Collect" `
  /TR "C:\Users\miket\Desktop\trend_scout\scheduler\collect_daily.bat" `
  /SC DAILY /ST 07:00 /RL LIMITED /F

schtasks /Create /TN "ModFraze Trend Scout - Full Run" `
  /TR "C:\Users\miket\Desktop\trend_scout\scheduler\scout_run.bat" `
  /SC WEEKLY /D MON,THU /ST 07:30 /RL LIMITED /F
```

Then make both tasks run even if the machine was asleep at the scheduled time —
this is the single most common reason a scheduled scout quietly never runs:

```powershell
foreach ($t in "ModFraze Trend Scout - Collect","ModFraze Trend Scout - Full Run") {
  $task = Get-ScheduledTask -TaskName $t
  $task.Settings.StartWhenAvailable = $true
  $task.Settings.DisallowStartIfOnBatteries = $false
  $task.Settings.StopIfGoingOnBatteries = $false
  Set-ScheduledTask -InputObject $task
}
```

## Verify before trusting it

```powershell
# fire them by hand right now
schtasks /Run /TN "ModFraze Trend Scout - Collect"

# did it work?
schtasks /Query /TN "ModFraze Trend Scout - Collect" /V /FO LIST | Select-String "Last Result","Last Run"
```

`Last Result: 0` is success. Anything else, read the log.

## Logs

Both scripts append to `logs\` in the project root, with a timestamp banner and
an exit code per run:

- `logs\collect.log`
- `logs\scout.log`

`logs\` is gitignored. Nothing is rotated — if it gets big, delete it, the
files are disposable.

## Removing the tasks

```powershell
schtasks /Delete /TN "ModFraze Trend Scout - Collect" /F
schtasks /Delete /TN "ModFraze Trend Scout - Full Run" /F
```

---

## Note on failure modes

A scheduled job that fails is worse than one that never ran, because you assume
it ran. The two guards worth knowing:

1. **Dead API key.** The full run exits non-zero and `logs\scout.log` shows the
   auth error, but nothing tells you — no email arrives, and no email is also
   what a quiet trend week looks like. Check `Last Result` occasionally, or set
   the key-expiry reminder (open item #6).
2. **Missing `.env`.** `scout_run.bat` checks for it up front and fails loudly
   in the log rather than letting `run.py` get halfway through a live fetch
   before discovering it can't do the paid stage.
