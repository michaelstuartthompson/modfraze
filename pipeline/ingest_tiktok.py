import os
from dotenv import load_dotenv

from db.database import SessionLocal
from db.models import Trend
from tools.tiktok_adapter import fetch_tiktok_apify_trends

load_dotenv()


def main():
    apify_key = os.getenv("APIFY_API_KEY")
    if not apify_key:
        print("Missing APIFY_API_KEY in .env")
        raise SystemExit

    search_query = os.getenv("APIFY_TIKTOK_QUERY", "tiktok trends")
    max_items = int(os.getenv("APIFY_TIKTOK_MAX_ITEMS", "5"))
    actor = os.getenv("APIFY_TIKTOK_ACTOR", "clockworks/tiktok-scraper")

    signals = fetch_tiktok_apify_trends(
        api_key=apify_key,
        search_queries=[search_query],
        max_items=max_items,
        actor=actor,
    )
    print(f"Fetched {len(signals)} TikTok signals")

    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        for s in signals:
            exists = (
                session.query(Trend)
                .filter(Trend.source == s.source, Trend.platform_id == s.platform_id)
                .first()
            )
            if exists:
                skipped += 1
                continue

            session.add(Trend(**s.__dict__))
            inserted += 1

        session.commit()

    finally:
        session.close()

    print(f"Inserted {inserted} | Skipped {skipped}")


if __name__ == "__main__":
    main()
