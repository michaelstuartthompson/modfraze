import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv()


def _run_step(name, func):
    start = datetime.utcnow()
    print(f"[{start.isoformat()}] start {name}")
    try:
        func()
        end = datetime.utcnow()
        print(f"[{end.isoformat()}] ok {name}")
        return True
    except Exception as exc:
        end = datetime.utcnow()
        print(f"[{end.isoformat()}] fail {name}: {exc}")
        return False


def main():
    from pipeline.ingest_tiktok import main as ingest_tiktok

    steps = []

    run_tiktok = os.getenv("RUN_TIKTOK", "1").lower() in {"1", "true", "yes", "y"}
    if run_tiktok:
        steps.append(("tiktok", ingest_tiktok))

    run_demo = os.getenv("RUN_DEMO", "0").lower() in {"1", "true", "yes", "y"}
    if run_demo:
        from pipeline.ingest_one_demo import main as ingest_demo

        steps.append(("demo", ingest_demo))

    if not steps:
        print("No sources enabled. Set RUN_TIKTOK=1 or other source flags.")
        return

    total = len(steps)
    successes = 0
    for name, func in steps:
        if _run_step(name, func):
            successes += 1

    print(f"Completed {successes}/{total} sources.")


if __name__ == "__main__":
    main()
