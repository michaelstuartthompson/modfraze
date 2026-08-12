"""
Campaign management pipeline for Meta Ads.
Monitors performance and automatically kills/boosts campaigns.
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from db.database import SessionLocal
from db.models import Campaign, Product, Design, CampaignStatus
from tools.meta_ads_client import MetaAdsClient, create_basic_targeting

load_dotenv()


class CampaignManager:
    """Manages ad campaigns lifecycle"""
    
    # Performance thresholds
    MIN_CTR = 0.5  # Kill if CTR < 0.5% after 12 hours
    GOOD_CTR = 2.0  # Boost if CTR > 2%
    MIN_RUNTIME_HOURS = 12  # Minimum hours before killing
    BOOST_MULTIPLIER = 1.5  # Budget multiplier for winners
    
    def __init__(self):
        self.meta_client = MetaAdsClient()
    
    def create_campaign_for_product(
        self,
        product_id: int,
        daily_budget: float = 5.0,
        target_audience: Optional[Dict] = None
    ) -> int:
        """
        Create and launch a Meta Ads campaign for a product.
        
        Args:
            product_id: Product database ID
            daily_budget: Daily ad budget in dollars
            target_audience: Custom targeting (uses defaults if None)
            
        Returns:
            Campaign database ID
        """
        
        session = SessionLocal()
        
        try:
            # Get product
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError(f"Product {product_id} not found")
            
            design = product.design
            trend = design.trend
            
            print(f"\n🚀 Creating campaign for product: {product.title}")
            
            # Create campaign
            campaign_name = f"Viral: {product.title[:40]}"
            meta_campaign = self.meta_client.create_campaign(
                name=campaign_name,
                daily_budget=daily_budget,
                status="PAUSED"  # Start paused, activate after setup
            )
            
            # Create targeting if not provided
            if target_audience is None:
                target_audience = create_basic_targeting(
                    age_min=18,
                    age_max=45,
                    countries=["US"]
                )
            
            # Create ad set
            meta_adset = self.meta_client.create_adset(
                campaign_id=meta_campaign["id"],
                name=f"{campaign_name} - AdSet",
                daily_budget=daily_budget,
                targeting=target_audience
            )
            
            # Create ad creative
            # TODO: Upload product image to Meta or use public URL
            product_url = os.getenv("SHOPIFY_STORE_URL", "https://yourstore.com")
            product_link = f"{product_url}/products/{product.shopify_id}"
            
            meta_creative = self.meta_client.create_ad_creative(
                name=f"{campaign_name} - Creative",
                image_url=design.image_url,  # Must be public URL for Meta
                link_url=product_link,
                message=f"Get your {product.title}! Limited edition merch. 🔥"
            )
            
            # Create ad
            meta_ad = self.meta_client.create_ad(
                name=f"{campaign_name} - Ad",
                adset_id=meta_adset["id"],
                creative_id=meta_creative["id"],
                status="PAUSED"
            )
            
            # Store campaign in database
            campaign = Campaign(
                product_id=product_id,
                platform="meta",
                campaign_name=campaign_name,
                campaign_id=meta_campaign["id"],
                adset_id=meta_adset["id"],
                ad_id=meta_ad["id"],
                daily_budget=daily_budget,
                target_audience=str(target_audience),
                status=CampaignStatus.DRAFT,
                created_at=datetime.utcnow()
            )
            
            session.add(campaign)
            session.commit()
            session.refresh(campaign)
            
            print(f"✅ Campaign created: DB ID {campaign.id}, Meta ID {meta_campaign['id']}")
            
            return campaign.id
            
        finally:
            session.close()
    
    def activate_campaign(self, campaign_id: int) -> bool:
        """Activate a campaign to start running ads"""
        
        session = SessionLocal()
        
        try:
            campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Activate on Meta
            self.meta_client.update_campaign_status(
                campaign.campaign_id,
                "ACTIVE"
            )
            
            # Update database
            campaign.status = CampaignStatus.ACTIVE
            campaign.launched_at = datetime.utcnow()
            session.commit()
            
            print(f"✅ Campaign {campaign_id} activated")
            return True
            
        finally:
            session.close()
    
    def sync_campaign_metrics(self, campaign_id: int) -> Dict[str, Any]:
        """
        Sync performance metrics from Meta Ads API.
        
        Args:
            campaign_id: Campaign database ID
            
        Returns:
            Updated metrics
        """
        
        session = SessionLocal()
        
        try:
            campaign = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Get insights from Meta
            insights = self.meta_client.get_campaign_insights(
                campaign.campaign_id,
                date_preset="lifetime"
            )
            
            if insights:
                # Update metrics
                campaign.update_metrics(
                    impressions=int(insights.get("impressions", 0)),
                    clicks=int(insights.get("clicks", 0)),
                    spend=float(insights.get("spend", 0)),
                    # TODO: Track conversions if pixel is set up
                )
                
                session.commit()
                
                print(f"✅ Synced metrics for campaign {campaign_id}")
                print(f"   Impressions: {campaign.impressions}")
                print(f"   Clicks: {campaign.clicks}")
                print(f"   CTR: {campaign.ctr:.2f}%")
                print(f"   Spend: ${campaign.spend:.2f}")
            
            return {
                "impressions": campaign.impressions,
                "clicks": campaign.clicks,
                "ctr": campaign.ctr,
                "spend": campaign.spend
            }
            
        finally:
            session.close()
    
    def monitor_and_optimize_campaigns(self) -> Dict[str, List[int]]:
        """
        Monitor all active campaigns and apply kill/boost logic.
        
        Returns:
            Dict with lists of killed and boosted campaign IDs
        """
        
        session = SessionLocal()
        results = {
            "killed": [],
            "boosted": [],
            "monitored": 0
        }
        
        try:
            # Get all active campaigns
            campaigns = (
                session.query(Campaign)
                .filter(Campaign.status == CampaignStatus.ACTIVE)
                .all()
            )
            
            print(f"\n🔍 Monitoring {len(campaigns)} active campaigns")
            
            for campaign in campaigns:
                results["monitored"] += 1
                
                # Sync latest metrics
                self.sync_campaign_metrics(campaign.id)
                session.refresh(campaign)
                
                # Check if campaign has run long enough
                if not campaign.launched_at:
                    continue
                
                hours_running = (datetime.utcnow() - campaign.launched_at).total_seconds() / 3600
                
                print(f"\nCampaign {campaign.id}: {campaign.campaign_name}")
                print(f"  Runtime: {hours_running:.1f}h")
                print(f"  CTR: {campaign.ctr:.2f}%")
                print(f"  Clicks: {campaign.clicks}")
                print(f"  Spend: ${campaign.spend:.2f}")
                
                # KILL LOGIC: No clicks after minimum runtime
                if hours_running >= self.MIN_RUNTIME_HOURS and campaign.clicks == 0:
                    print(f"  🔪 KILL: No clicks after {self.MIN_RUNTIME_HOURS}h")
                    self._kill_campaign(campaign, "No clicks after 12 hours")
                    results["killed"].append(campaign.id)
                    continue
                
                # KILL LOGIC: Low CTR after minimum runtime
                if hours_running >= self.MIN_RUNTIME_HOURS and campaign.ctr < self.MIN_CTR:
                    print(f"  🔪 KILL: CTR {campaign.ctr:.2f}% < {self.MIN_CTR}%")
                    self._kill_campaign(campaign, f"Low CTR: {campaign.ctr:.2f}%")
                    results["killed"].append(campaign.id)
                    continue
                
                # BOOST LOGIC: High CTR
                if campaign.ctr > self.GOOD_CTR and hours_running >= 6:
                    print(f"  🚀 BOOST: CTR {campaign.ctr:.2f}% > {self.GOOD_CTR}%")
                    self._boost_campaign(campaign)
                    results["boosted"].append(campaign.id)
                    continue
                
                print(f"  ✅ Continue monitoring")
            
            session.commit()
            
            print(f"\n{'='*60}")
            print(f"📊 MONITORING SUMMARY:")
            print(f"   Monitored: {results['monitored']}")
            print(f"   Killed: {len(results['killed'])}")
            print(f"   Boosted: {len(results['boosted'])}")
            
        finally:
            session.close()
        
        return results
    
    def _kill_campaign(self, campaign: Campaign, reason: str):
        """Pause campaign and mark as killed"""
        
        # Pause on Meta
        self.meta_client.update_campaign_status(
            campaign.campaign_id,
            "PAUSED"
        )
        
        # Update database
        campaign.status = CampaignStatus.KILLED
        campaign.kill_reason = reason
        campaign.killed_at = datetime.utcnow()
    
    def _boost_campaign(self, campaign: Campaign):
        """Increase budget for well-performing campaign"""
        
        new_budget = campaign.daily_budget * self.BOOST_MULTIPLIER
        
        # Update budget on Meta
        self.meta_client.update_adset_budget(
            campaign.adset_id,
            new_budget
        )
        
        # Update database
        campaign.daily_budget = new_budget


# Command-line interface
if __name__ == "__main__":
    import sys
    
    manager = CampaignManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_campaigns.py create <product_id> [budget]")
        print("  python manage_campaigns.py activate <campaign_id>")
        print("  python manage_campaigns.py monitor")
        print("  python manage_campaigns.py sync <campaign_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Error: product_id required")
            sys.exit(1)
        
        product_id = int(sys.argv[2])
        budget = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
        
        campaign_id = manager.create_campaign_for_product(product_id, daily_budget=budget)
        print(f"\n✅ Campaign created: {campaign_id}")
        print(f"Next step: python manage_campaigns.py activate {campaign_id}")
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Error: campaign_id required")
            sys.exit(1)
        
        campaign_id = int(sys.argv[2])
        manager.activate_campaign(campaign_id)
    
    elif command == "monitor":
        results = manager.monitor_and_optimize_campaigns()
    
    elif command == "sync":
        if len(sys.argv) < 3:
            print("Error: campaign_id required")
            sys.exit(1)
        
        campaign_id = int(sys.argv[2])
        metrics = manager.sync_campaign_metrics(campaign_id)
        print(f"\nMetrics: {metrics}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
