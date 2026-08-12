"""
Schema for product creation and management.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProductRequest:
    """Request to create a product from an approved design"""
    design_id: int
    title: str
    description: str
    product_type: str = "tshirt"  # tshirt, hoodie, mug, sticker
    price: float = 24.99
    

@dataclass
class ProductListing:
    """Product listing details for e-commerce platforms"""
    product_id: int
    platform: str  # shopify, etsy, printify
    platform_product_id: str
    listing_url: Optional[str] = None
    listed_at: datetime = None
    
    def __post_init__(self):
        if self.listed_at is None:
            self.listed_at = datetime.utcnow()


@dataclass
class CampaignRequest:
    """Request to launch an ad campaign"""
    product_id: int
    platform: str = "meta"  # meta, google, tiktok
    daily_budget: float = 5.0
    target_audience: Optional[dict] = None
