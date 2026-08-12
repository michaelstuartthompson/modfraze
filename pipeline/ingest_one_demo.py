from datetime import datetime

from db.database import SessionLocal
from db.models import Trend
from schemas.trend import TrendSignal


def main():
    demo = TrendSignal(
        source="demo",
        platform_id="demo-001",
        text="This is a demo trend signal to prove DB insert works.",
        url="https://example.com/demo",
        raw_engagement=123,
        sentiment=0.2,
        virality_score=0.6,
        detected_at=datetime.utcnow(),
    )

    session = SessionLocal()
    try:
        exists = (
            session.query(Trend)
            .filter(Trend.source == demo.source, Trend.platform_id == demo.platform_id)
            .first()
        )

        if exists:
            print("Already exists ✅ (no insert):", exists.id)
            return

        row = Trend(**demo.__dict__)
        session.add(row)
        session.commit()
        session.refresh(row)
        print("Inserted ✅ Trend id:", row.id)

    finally:
        session.close()


if __name__ == "__main__":
    main()
