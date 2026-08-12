"""
Meta (Facebook/Instagram) Ads API client for campaign management.
"""
import os
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


class MetaAdsClient:
    """Client for Meta (Facebook/Instagram) Ads API"""
    
    API_VERSION = "v19.0"
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        ad_account_id: Optional[str] = None
    ):
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN")
        self.ad_account_id = ad_account_id or os.getenv("META_AD_ACCOUNT_ID")
        
        if not self.access_token:
            raise ValueError("META_ACCESS_TOKEN is required")
        if not self.ad_account_id:
            raise ValueError("META_AD_ACCOUNT_ID is required (format: act_123456789)")
        
        # Ensure ad_account_id has correct format
        if not self.ad_account_id.startswith("act_"):
            self.ad_account_id = f"act_{self.ad_account_id}"
        
        self.base_url = f"https://graph.facebook.com/{self.API_VERSION}"
        self.default_params = {"access_token": self.access_token}
    
    def create_campaign(
        self,
        name: str,
        objective: str = "OUTCOME_TRAFFIC",
        status: str = "PAUSED",
        daily_budget: Optional[float] = None,
        lifetime_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create an ad campaign.
        
        Args:
            name: Campaign name
            objective: Campaign objective (OUTCOME_TRAFFIC, OUTCOME_SALES, etc.)
            status: ACTIVE or PAUSED
            daily_budget: Daily budget in dollars (converted to cents)
            lifetime_budget: Lifetime budget in dollars
            
        Returns:
            Campaign data with campaign_id
        """
        
        campaign_data = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": []  # Required field
        }
        
        if daily_budget:
            campaign_data["daily_budget"] = int(daily_budget * 100)  # Convert to cents
        elif lifetime_budget:
            campaign_data["lifetime_budget"] = int(lifetime_budget * 100)
        
        response = requests.post(
            f"{self.base_url}/{self.ad_account_id}/campaigns",
            params={**self.default_params, **campaign_data}
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Created campaign: {result['id']} - {name}")
        return result
    
    def create_adset(
        self,
        campaign_id: str,
        name: str,
        daily_budget: float,
        targeting: Dict[str, Any],
        optimization_goal: str = "LINK_CLICKS",
        billing_event: str = "IMPRESSIONS",
        bid_strategy: str = "LOWEST_COST_WITHOUT_CAP"
    ) -> Dict[str, Any]:
        """
        Create an ad set within a campaign.
        
        Args:
            campaign_id: Parent campaign ID
            name: Ad set name
            daily_budget: Daily budget in dollars
            targeting: Targeting specification (age, gender, interests, etc.)
            optimization_goal: What to optimize for
            billing_event: What you're charged for
            bid_strategy: Bidding strategy
            
        Returns:
            Ad set data with adset_id
        """
        
        # Set schedule (start now, run indefinitely)
        start_time = datetime.utcnow().isoformat()
        
        adset_data = {
            "name": name,
            "campaign_id": campaign_id,
            "daily_budget": int(daily_budget * 100),
            "billing_event": billing_event,
            "optimization_goal": optimization_goal,
            "bid_strategy": bid_strategy,
            "targeting": targeting,
            "status": "PAUSED",
            "start_time": start_time,
        }
        
        response = requests.post(
            f"{self.base_url}/{self.ad_account_id}/adsets",
            params={**self.default_params, **adset_data}
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Created ad set: {result['id']} - {name}")
        return result
    
    def create_ad_creative(
        self,
        name: str,
        image_url: str,
        link_url: str,
        message: str,
        call_to_action: str = "SHOP_NOW"
    ) -> Dict[str, Any]:
        """
        Create ad creative (the actual ad content).
        
        Args:
            name: Creative name
            image_url: URL to ad image
            link_url: Destination URL (your product page)
            message: Ad copy/text
            call_to_action: CTA button type
            
        Returns:
            Creative data with creative_id
        """
        
        creative_data = {
            "name": name,
            "object_story_spec": {
                "page_id": os.getenv("META_PAGE_ID"),  # Your Facebook Page ID
                "link_data": {
                    "image_url": image_url,
                    "link": link_url,
                    "message": message,
                    "call_to_action": {
                        "type": call_to_action
                    }
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/{self.ad_account_id}/adcreatives",
            params=self.default_params,
            json=creative_data
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Created ad creative: {result['id']}")
        return result
    
    def create_ad(
        self,
        name: str,
        adset_id: str,
        creative_id: str,
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Create an ad using existing ad set and creative.
        
        Args:
            name: Ad name
            adset_id: Parent ad set ID
            creative_id: Ad creative ID
            status: ACTIVE or PAUSED
            
        Returns:
            Ad data with ad_id
        """
        
        ad_data = {
            "name": name,
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "status": status
        }
        
        response = requests.post(
            f"{self.base_url}/{self.ad_account_id}/ads",
            params={**self.default_params, **ad_data}
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Created ad: {result['id']} - {name}")
        return result
    
    def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "today"
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a campaign.
        
        Args:
            campaign_id: Campaign ID
            date_preset: Time range (today, yesterday, last_7d, etc.)
            
        Returns:
            Insights data with impressions, clicks, spend, etc.
        """
        
        fields = [
            "impressions",
            "clicks",
            "spend",
            "reach",
            "ctr",
            "cpc",
            "cpp",
            "actions",  # Conversions
            "cost_per_action_type"
        ]
        
        params = {
            **self.default_params,
            "fields": ",".join(fields),
            "date_preset": date_preset
        }
        
        response = requests.get(
            f"{self.base_url}/{campaign_id}/insights",
            params=params
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("data"):
            return result["data"][0]
        return {}
    
    def update_campaign_status(
        self,
        campaign_id: str,
        status: str
    ) -> bool:
        """
        Update campaign status (activate, pause, or archive).
        
        Args:
            campaign_id: Campaign ID
            status: ACTIVE, PAUSED, or ARCHIVED
            
        Returns:
            True if successful
        """
        
        update_data = {"status": status}
        
        response = requests.post(
            f"{self.base_url}/{campaign_id}",
            params={**self.default_params, **update_data}
        )
        
        response.raise_for_status()
        print(f"✅ Updated campaign {campaign_id} status to {status}")
        return True
    
    def update_adset_budget(
        self,
        adset_id: str,
        daily_budget: float
    ) -> bool:
        """
        Update ad set daily budget.
        
        Args:
            adset_id: Ad set ID
            daily_budget: New daily budget in dollars
            
        Returns:
            True if successful
        """
        
        update_data = {"daily_budget": int(daily_budget * 100)}
        
        response = requests.post(
            f"{self.base_url}/{adset_id}",
            params={**self.default_params, **update_data}
        )
        
        response.raise_for_status()
        print(f"✅ Updated ad set {adset_id} budget to ${daily_budget}")
        return True


def create_basic_targeting(
    age_min: int = 18,
    age_max: int = 65,
    genders: Optional[List[int]] = None,
    countries: Optional[List[str]] = None,
    interests: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Helper to create basic targeting spec.
    
    Args:
        age_min: Minimum age
        age_max: Maximum age
        genders: [1] for male, [2] for female, [1,2] for all
        countries: List of country codes (e.g., ["US", "CA"])
        interests: List of interest dictionaries
        
    Returns:
        Targeting specification dict
    """
    
    targeting = {
        "age_min": age_min,
        "age_max": age_max,
        "genders": genders or [1, 2],
        "geo_locations": {
            "countries": countries or ["US"]
        }
    }
    
    if interests:
        targeting["flexible_spec"] = [{"interests": interests}]
    
    return targeting


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    client = MetaAdsClient()
    
    # Example: Create a complete campaign structure
    # NOTE: This is example code - don't run without proper setup
    
    # 1. Create campaign
    campaign = client.create_campaign(
        name="Test Viral Merch Campaign",
        daily_budget=10.0
    )
    
    # 2. Create targeting
    targeting = create_basic_targeting(
        age_min=18,
        age_max=34,
        countries=["US"],
        interests=[
            {"id": "6003139266461", "name": "Online shopping"}
        ]
    )
    
    # 3. Create ad set
    adset = client.create_adset(
        campaign_id=campaign["id"],
        name="Test Ad Set",
        daily_budget=10.0,
        targeting=targeting
    )
    
    print("\n✅ Campaign structure created successfully")
    print(f"Campaign ID: {campaign['id']}")
    print(f"Ad Set ID: {adset['id']}")
