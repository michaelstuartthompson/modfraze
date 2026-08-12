"""
Printify API client for print-on-demand product creation.
"""
import os
import requests
from typing import Optional, Dict, Any, List


class PrintifyClient:
    """Client for Printify API"""
    
    # Common product blueprints (Printify IDs)
    BLUEPRINTS = {
        "tshirt": 6,           # Bella+Canvas 3001 Unisex T-Shirt
        "hoodie": 77,          # Gildan 18500 Unisex Hoodie
        "mug": 26,             # White Glossy Mug
        "sticker": 301,        # Kiss Cut Stickers
        "tank_top": 7,         # Bella+Canvas Tank
        "tote_bag": 71,        # Tote Bag
    }
    
    def __init__(self, api_key: Optional[str] = None, shop_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("PRINTIFY_API_KEY")
        self.shop_id = shop_id or os.getenv("PRINTIFY_SHOP_ID")
        
        if not self.api_key:
            raise ValueError("PRINTIFY_API_KEY is required")
        
        self.base_url = "https://api.printify.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_shops(self) -> List[Dict[str, Any]]:
        """Get all connected shops"""
        
        response = requests.get(
            f"{self.base_url}/shops.json",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def upload_image(self, image_path: str, file_name: str) -> str:
        """
        Upload an image to Printify.
        
        Args:
            image_path: Local path to image file
            file_name: Name for the uploaded file
            
        Returns:
            Printify image ID
        """
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Upload to Printify
        upload_data = {
            "file_name": file_name,
            "contents": image_data.hex()  # Printify expects hex-encoded binary
        }
        
        response = requests.post(
            f"{self.base_url}/uploads/images.json",
            headers=self.headers,
            json=upload_data
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Uploaded image to Printify: {result['id']}")
        return result['id']
    
    def create_product(
        self,
        title: str,
        description: str,
        blueprint_id: int,
        print_provider_id: int,
        design_image_id: str,
        variants: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Create a product on Printify.
        
        Args:
            title: Product title
            description: Product description
            blueprint_id: Printify blueprint ID (product type)
            print_provider_id: Print provider ID (use get_print_providers)
            design_image_id: Uploaded image ID from upload_image()
            variants: List of variant configurations
            
        Returns:
            Product data including product ID
        """
        
        if not self.shop_id:
            raise ValueError("PRINTIFY_SHOP_ID is required")
        
        # Default variants if not specified (basic t-shirt example)
        if variants is None:
            variants = [
                {
                    "id": 17390,  # Example variant ID - needs to match blueprint
                    "price": 2499,  # Price in cents
                    "is_enabled": True
                }
            ]
        
        product_data = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": print_provider_id,
            "variants": variants,
            "print_areas": [
                {
                    "variant_ids": [v["id"] for v in variants],
                    "placeholders": [
                        {
                            "position": "front",
                            "images": [
                                {
                                    "id": design_image_id,
                                    "x": 0.5,  # Center X
                                    "y": 0.5,  # Center Y
                                    "scale": 1.0,
                                    "angle": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/shops/{self.shop_id}/products.json",
            headers=self.headers,
            json=product_data
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Created Printify product: {result['id']} - {title}")
        return result
    
    def publish_product(self, product_id: str) -> Dict[str, Any]:
        """
        Publish a product to connected sales channel (Shopify/Etsy).
        
        Args:
            product_id: Printify product ID
            
        Returns:
            Publishing status
        """
        
        if not self.shop_id:
            raise ValueError("PRINTIFY_SHOP_ID is required")
        
        publish_data = {
            "title": True,
            "description": True,
            "images": True,
            "variants": True,
            "tags": True
        }
        
        response = requests.post(
            f"{self.base_url}/shops/{self.shop_id}/products/{product_id}/publish.json",
            headers=self.headers,
            json=publish_data
        )
        
        response.raise_for_status()
        print(f"✅ Published Printify product {product_id}")
        return response.json()
    
    def get_print_providers(self, blueprint_id: int) -> List[Dict[str, Any]]:
        """
        Get available print providers for a blueprint.
        
        Args:
            blueprint_id: Printify blueprint ID
            
        Returns:
            List of print providers with pricing
        """
        
        response = requests.get(
            f"{self.base_url}/catalog/blueprints/{blueprint_id}/print_providers.json",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_variants(self, blueprint_id: int, print_provider_id: int) -> List[Dict[str, Any]]:
        """
        Get available variants (sizes/colors) for a blueprint.
        
        Args:
            blueprint_id: Printify blueprint ID
            print_provider_id: Print provider ID
            
        Returns:
            List of variants with IDs and options
        """
        
        response = requests.get(
            f"{self.base_url}/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json",
            headers=self.headers
        )
        
        response.raise_for_status()
        return response.json()["variants"]


# Helper function for easy product creation
def create_simple_tshirt(
    client: PrintifyClient,
    title: str,
    description: str,
    image_path: str,
    price: float = 24.99
) -> Dict[str, Any]:
    """
    Quick helper to create a basic t-shirt product.
    
    Args:
        client: PrintifyClient instance
        title: Product title
        description: Product description
        image_path: Path to design image
        price: Retail price (converted to cents)
        
    Returns:
        Product data
    """
    
    # Upload image
    image_id = client.upload_image(image_path, f"{title}.png")
    
    # Get print providers for t-shirt
    providers = client.get_print_providers(PrintifyClient.BLUEPRINTS["tshirt"])
    provider_id = providers[0]["id"]  # Use first available provider
    
    # Get variants for t-shirt
    variants = client.get_variants(PrintifyClient.BLUEPRINTS["tshirt"], provider_id)
    
    # Enable all sizes, set pricing
    variant_config = [
        {
            "id": v["id"],
            "price": int(price * 100),  # Convert to cents
            "is_enabled": True
        }
        for v in variants[:5]  # First 5 sizes (S-XL typically)
    ]
    
    # Create product
    product = client.create_product(
        title=title,
        description=description,
        blueprint_id=PrintifyClient.BLUEPRINTS["tshirt"],
        print_provider_id=provider_id,
        design_image_id=image_id,
        variants=variant_config
    )
    
    return product


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    client = PrintifyClient()
    
    # List shops
    shops = client.get_shops()
    print(f"Connected shops: {len(shops)}")
    for shop in shops:
        print(f"  - {shop['title']} (ID: {shop['id']})")
