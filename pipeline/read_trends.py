from db.database import SessionLocal
from db.models import Trend


def main():
    session = SessionLocal()
    try:
        rows = session.query(Trend).order_by(Trend.id.desc()).limit(5).all()

        if not rows:
            print("No trends found.")
            return

        print("Last 5 trends:")
        for r in rows:
            print(f"- id={r.id} source={r.source} platform_id={r.platform_id} score={r.virality_score} text={r.text[:60]!r}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
