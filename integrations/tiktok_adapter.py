from datetime import datetime
from typing import List, Optional

import requests

from schemas.trend import TrendSignal


def fetch_tiktok_signals(url: str, headers: dict, querystring: dict) -> List[TrendSignal]:
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()

    data = response.json()
    posts = data.get("itemList", []) or []

    signals: List[TrendSignal] = []
    now = datetime.utcnow()

    for item in posts:
        author = (item.get("author") or {}).get("uniqueId", "unknown")
        caption = item.get("desc", "") or ""
        platform_id = item.get("id") or item.get("aweme_id") or caption[:40] or "unknown"

        url_guess: Optional[str] = None
        share = item.get("share_info") or item.get("shareInfo") or {}
        if isinstance(share, dict):
            url_guess = share.get("share_url") or share.get("url")

        stats = item.get("stats") or {}
        raw_engagement = 0
        if isinstance(stats, dict):
            raw_engagement = (
                int(stats.get("diggCount", 0) or 0)
                + int(stats.get("commentCount", 0) or 0)
                + int(stats.get("shareCount", 0) or 0)
            )

        signals.append(
            TrendSignal(
                source="tiktok",
                platform_id=str(platform_id),
                text=f"@{author} {caption}".strip(),
                url=url_guess,
                raw_engagement=raw_engagement,
                sentiment=0.0,
                virality_score=0.0,
                detected_at=now,
            )
        )

    return signals


def fetch_tiktok_apify_trends(
    api_key: str,
    search_queries: List[str],
    max_items: int = 10,
    actor: str = "clockworks/tiktok-scraper",
    wait_for_finish: int = 120,
) -> List[TrendSignal]:
    headers = {"Authorization": f"Bearer {api_key}"}
    actor_id = actor.replace("/", "~")
    run_response = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        params={"waitForFinish": wait_for_finish},
        headers=headers,
        json={"searchQueries": search_queries, "maxItems": max_items},
    )
    run_response.raise_for_status()
    run_data = (run_response.json() or {}).get("data", {}) or {}

    status = run_data.get("status")
    dataset_id = run_data.get("defaultDatasetId")
    if status != "SUCCEEDED" or not dataset_id:
        raise RuntimeError("Apify run failed or did not return a dataset.")

    items_response = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        headers=headers,
        params={"limit": max_items},
    )
    items_response.raise_for_status()
    items = items_response.json() or []

    signals: List[TrendSignal] = []
    now = datetime.utcnow()
    for item in items:
        author_meta = item.get("authorMeta") or {}
        author = (
            author_meta.get("name")
            or author_meta.get("nickName")
            or author_meta.get("uniqueId")
            or "unknown"
        )
        caption = item.get("text") or item.get("desc") or ""
        platform_id = item.get("id") or item.get("aweme_id") or caption[:40] or "unknown"
        url_guess = item.get("webVideoUrl") or item.get("videoUrl")

        raw_engagement = (
            int(item.get("diggCount", 0) or 0)
            + int(item.get("commentCount", 0) or 0)
            + int(item.get("shareCount", 0) or 0)
        )

        signals.append(
            TrendSignal(
                source="tiktok",
                platform_id=str(platform_id),
                text=f"@{author} {caption}".strip(),
                url=url_guess,
                raw_engagement=raw_engagement,
                sentiment=0.0,
                virality_score=0.0,
                detected_at=now,
            )
        )

    return signals
