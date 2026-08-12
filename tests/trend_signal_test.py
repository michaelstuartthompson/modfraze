from datetime import datetime
from schemas.trend import TrendSignal


def main():
    demo = TrendSignal(
        source="tiktok",
        platform_id="123",
        text="Demo trend signal",
        url="https://example.com",
        raw_engagement=42,
        sentiment=0.1,
        virality_score=0.5,
        detected_at=datetime.utcnow(),
    )

    print("TrendSignal import OK ✅")
    print(demo)


if __name__ == "__main__":
    main()
