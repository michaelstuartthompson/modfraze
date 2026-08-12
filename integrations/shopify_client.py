"""
Shopify API client for product management.
"""
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class ShopifyClient:
    """Client for Shopify Admin API"""
    
    def __init__(
        self,
        shop_name: Optional[str] = None,
        access_token: Optional[str] = None,
        api_version: str = "2024-01"
    ):
        self.shop_name = shop_name or os.getenv("SHOPIFY_SHOP_NAME")
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if not self.shop_name or not self.access_token:
            raise ValueError("SHOPIFY_SHOP_NAME and SHOPIFY_ACCESS_TOKEN are required")
        
        self.api_version = api_version
        self.base_url = f"https://{self.shop_name}.myshopify.com/admin/api/{api_version}"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
    
    def create_product(
        self,
        title: str,
        description: str,
        price: float,
        image_url: str,
        product_type: str = "T-Shirt",
        vendor: str = "Viral Merch Co",
        tags: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new product on Shopify.
        
        Args:
            title: Product title
            description: Product description (supports HTML)
            price: Product price
            image_url: URL or local path to product image
            product_type: Product category
            vendor: Brand/vendor name
            tags: List of tags for product
            
        Returns:
            Dict with product data including product_id
        """
        
        product_data = {
            "product": {
                "title": title,
                "body_html": description,
                "vendor": vendor,
                "product_type": product_type,
                "tags": ", ".join(tags) if tags else "",
                "status": "draft",  # Start as draft for review
                "variants": [
                    {
                        "price": str(price),
                        "inventory_management": None,  # POD doesn't track inventory
                    }
                ],
                "images": [
                    {
                        "src": image_url
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{self.base_url}/products.json",
            headers=self.headers,
            json=product_data
        )
        
        response.raise_for_status()
        result = response.json()
        
        product = result["product"]
        print(f"✅ Created Shopify product: {product['id']} - {title}")
        
        return {
            "product_id": str(product["id"]),
            "variant_id": str(product["variants"][0]["id"]),
            "admin_url": f"https://{self.shop_name}.myshopify.com/admin/products/{product['id']}",
            "status": product["status"]
        }
    
    def publish_product(self, product_id: str) -> bool:
        """
        Publish a draft product to make it live.
        
        Args:
            product_id: Shopify product ID
            
        Returns:
            True if successful
        """
        
        update_data = {
            "product": {
                "id": product_id,
                "status": "active"
            }
        }
        
        response = requests.put(
            f"{self.base_url}/products/{product_id}.json",
            headers=self.headers,
            json=update_data
        )
        
        response.raise_for_status()
        print(f"✅ Published product {product_id}")
        return True
    
    def update_product_image(self, product_id: str, image_url: str) -> bool:
        """
        Update product's main image.
        
        Args:
            product_id: Shopify product ID
            image_url: New image URL
            
        Returns:
            True if successful
        """
        
        image_data = {
            "image": {
                "product_id": product_id,
                "src": image_url
            }
        }
        
        response = requests.post(
            f"{self.base_url}/products/{product_id}/images.json",
            headers=self.headers,
            json=image_data
        )
        
        response.raise_for_status()
        print(f"✅ Updated image for product {product_id}")
        return True
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        
        response = requests.get(
            f"{self.base_url}/products/{product_id}.json",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()["product"]
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product (use sparingly)"""
        
        response = requests.delete(
            f"{self.base_url}/products/{product_id}.json",
            headers=self.headers
        )
        
        response.raise_for_status()
        print(f"✅ Deleted product {product_id}")
        return True
    
    def create_product_variant(
        self,
        product_id: str,
        option: str,
        price: float
    ) -> Dict[str, Any]:
        """
        Create a product variant (e.g., different sizes/colors).
        
        Args:
            product_id: Parent product ID
            option: Variant option (e.g., "Large", "Red")
            price: Variant price
            
        Returns:
            Variant data
        """
        
        variant_data = {
            "variant": {
                "product_id": product_id,
                "option1": option,
                "price": str(price)
            }
        }
        
        response = requests.post(
            f"{self.base_url}/products/{product_id}/variants.json",
            headers=self.headers,
            json=variant_data
        )
        
        response.raise_for_status()
        return response.json()["variant"]


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    client = ShopifyClient()
    
    # Test product creation
    result = client.create_product(
        title="Test Viral Trend T-Shirt",
        description="<p>This is a test product from the viral merch pipeline.</p>",
        price=24.99,
        image_url="https://cdn.shopify.com/test-image.png",
        product_type="T-Shirt",
        tags=["viral", "trending", "meme"]
    )
    
    print(f"\nProduct created: {result['product_id']}")
    print(f"Admin URL: {result['admin_url']}")
