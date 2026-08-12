from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TrendSignal:
    source: str              # reddit | tiktok | x | etc
    platform_id: str         # post_id / video_id / tweet_id
    text: str                # title + caption + summary
    url: Optional[str]
    raw_engagement: int      # likes + shares + comments (rough for now)
    sentiment: float         # -1 to 1
    virality_score: float    # computed
    detected_at: datetime
