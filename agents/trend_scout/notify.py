"""
notify.py -- email the day's shortlist report.

WHY SMTP AND NOT AN API
-----------------------
Same reasoning as env_loader.py: smtplib is in the stdlib, so there's no install
step and nothing to break on a machine that hasn't been touched in a month. A
transactional email service would be more robust at volume. This sends at most
one message a day to one recipient.

CREDENTIALS
-----------
Reads three vars, all from .env:

    SMTP_USER           your gmail address
    SMTP_APP_PASSWORD   a Google *app password*, not your account password
    NOTIFY_TO           where to send (optional, defaults to SMTP_USER)

If the first two are missing this does nothing and says so. A missing email
config should never take down a scout run that otherwise succeeded -- the
report is already on disk either way.
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def _subject(picks: list[dict], stamp: str) -> str:
    """A subject line you can triage without opening the mail."""
    if not picks:
        return f"Trend Scout {stamp} -- nothing met the bar"

    top = picks[0]
    term = top.get("term", "?")
    conf = top.get("confidence", "?")
    n = len(picks)
    plural = "pick" if n == 1 else "picks"
    return f"Trend Scout {stamp} -- {n} {plural}, top: {term} ({conf})"


def send_report(report_path: str | Path, picks: list[dict] | None = None) -> bool:
    """
    Email the markdown report as the message body. Returns True on success.

    Never raises. A failed send prints and returns False, because the caller
    has already written the report and there's nothing to roll back.
    """
    picks = picks or []
    path = Path(report_path)

    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_APP_PASSWORD")
    recipient = os.environ.get("NOTIFY_TO") or user

    if not user or not password:
        print("  [notify] SMTP_USER / SMTP_APP_PASSWORD not set -- skipping email")
        return False

    if not path.is_file():
        print(f"  [notify] no report at {path} -- skipping email")
        return False

    body = path.read_text(encoding="utf-8")
    stamp = path.stem.replace("-shortlist", "")

    msg = EmailMessage()
    msg["Subject"] = _subject(picks, stamp)
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content(body)

    # Attach the markdown as well, so it can be filed or opened in an editor
    # without copy-pasting out of the mail body.
    msg.add_attachment(
        body.encode("utf-8"),
        maintype="text",
        subtype="markdown",
        filename=path.name,
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(user, password)
            server.send_message(msg)
    except Exception as e:  # noqa: BLE001 -- notification must never break the run
        print(f"  [notify] send failed: {type(e).__name__}: {e}")
        return False

    print(f"  [notify] emailed report to {recipient}")
    return True


if __name__ == "__main__":
    # Smoke test: python notify.py  -- sends the most recent report.
    import sys

    from env_loader import load_env

    load_env(verbose=True)

    reports = sorted(Path(__file__).parent.joinpath("reports").glob("*-shortlist.md"))
    if not reports:
        print("No reports found. Run run.py first.")
        sys.exit(1)

    print(f"Sending {reports[-1].name} ...")
    ok = send_report(reports[-1], [])
    sys.exit(0 if ok else 1)
