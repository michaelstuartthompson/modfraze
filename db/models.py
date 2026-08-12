"""
Database models for viral merch pipeline.
Extends existing Trend model with Design, Product, and Campaign models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class TrendStatus(enum.Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    DESIGN_PENDING = "design_pending"
    DESIGN_GENERATED = "design_generated"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DesignStatus(enum.Enum):
    GENERATED = "generated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PRODUCTION = "in_production"


class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    KILLED = "killed"
    COMPLETED = "completed"


class Trend(Base):
    """Social media trend signal"""
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)  # reddit, tiktok, x, etc
    platform_id = Column(String(255), nullable=False, unique=True)
    text = Column(Text, nullable=False)
    url = Column(String(512))
    raw_engagement = Column(Integer, default=0)
    sentiment = Column(Float, default=0.0)  # -1 to 1
    virality_score = Column(Float, default=0.0)
    status = Column(Enum(TrendStatus), default=TrendStatus.DETECTED)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    designs = relationship("Design", back_populates="trend", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trend(id={self.id}, source={self.source}, score={self.virality_score})>"


class Design(Base):
    """Generated design for a trend"""
    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trend_id = Column(Integer, ForeignKey("trends.id"), nullable=False, index=True)
    
    # Design details
    prompt = Column(Text, nullable=False)  # DALL-E prompt used
    image_url = Column(String(512))  # Local path or cloud URL
    mockup_url = Column(String(512))  # Product mockup image
    design_type = Column(String(50), default="graphic")  # graphic, text, hybrid
    
    # Metadata
    status = Column(Enum(DesignStatus), default=DesignStatus.GENERATED)
    approval_notes = Column(Text)  # User feedback/edits
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trend = relationship("Trend", back_populates="designs")
    products = relationship("Product", back_populates="design", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Design(id={self.id}, trend_id={self.trend_id}, status={self.status.value})>"


class Product(Base):
    """E-commerce product listing"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    design_id = Column(Integer, ForeignKey("designs.id"), nullable=False, index=True)
    
    # Product details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    product_type = Column(String(50), default="tshirt")  # tshirt, hoodie, mug, sticker
    price = Column(Float, nullable=False)
    
    # Platform IDs
    shopify_id = Column(String(100))
    shopify_variant_id = Column(String(100))
    printify_id = Column(String(100))
    etsy_id = Column(String(100))
    
    # Status
    is_listed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    listed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    design = relationship("Design", back_populates="products")
    campaigns = relationship("Campaign", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, title={self.title}, type={self.product_type})>"


class Campaign(Base):
    """Ad campaign for a product"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Campaign details
    platform = Column(String(50), nullable=False)  # meta, google, tiktok
    campaign_name = Column(String(255), nullable=False)
    ad_account_id = Column(String(100))
    campaign_id = Column(String(100))  # Platform campaign ID
    adset_id = Column(String(100))  # Platform adset ID
    ad_id = Column(String(100))  # Platform ad ID
    
    # Budget & targeting
    daily_budget = Column(Float, default=5.0)
    total_budget = Column(Float)
    target_audience = Column(Text)  # JSON string with targeting params
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    
    # Computed metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    roas = Column(Float, default=0.0)  # Return on ad spend
    
    # Status & lifecycle
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    kill_reason = Column(String(255))  # Why campaign was killed
    
    # Timestamps
    launched_at = Column(DateTime)
    paused_at = Column(DateTime)
    killed_at = Column(DateTime)
    last_synced_at = Column(DateTime)  # Last metrics sync from platform
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="campaigns")

    def __repr__(self):
        return f"<Campaign(id={self.id}, product_id={self.product_id}, status={self.status.value})>"

    def update_metrics(self, impressions=None, clicks=None, conversions=None, spend=None, revenue=None):
        """Update campaign metrics and calculate derived values"""
        if impressions is not None:
            self.impressions = impressions
        if clicks is not None:
            self.clicks = clicks
        if conversions is not None:
            self.conversions = conversions
        if spend is not None:
            self.spend = spend
        if revenue is not None:
            self.revenue = revenue
        
        # Calculate derived metrics
        self.ctr = (self.clicks / self.impressions * 100) if self.impressions > 0 else 0.0
        self.cpc = (self.spend / self.clicks) if self.clicks > 0 else 0.0
        self.roas = (self.revenue / self.spend) if self.spend > 0 else 0.0
        self.last_synced_at = datetime.utcnow()
