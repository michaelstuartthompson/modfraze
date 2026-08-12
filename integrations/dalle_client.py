"""
DALL-E 3 client for generating merch designs.
"""
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional
from openai import OpenAI


class DALLEClient:
    """Client for DALL-E 3 image generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = Path(os.getenv("DESIGN_OUTPUT_DIR", "./generated_designs"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_merch_design(
        self,
        trend_text: str,
        design_type: str = "graphic",
        style: str = "bold",
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> tuple[str, str]:
        """
        Generate a merchandise design based on a trend.
        
        Args:
            trend_text: The trending topic/meme/phrase
            design_type: graphic, text, hybrid
            style: bold, minimalist, retro, modern
            size: 1024x1024 (standard) or 1024x1792 (HD)
            quality: standard or hd
            
        Returns:
            (prompt, local_file_path)
        """
        # Build prompt based on design type
        prompt = self._build_prompt(trend_text, design_type, style)
        
        # Generate image
        print(f"🎨 Generating design with DALL-E 3...")
        print(f"Prompt: {prompt[:100]}...")
        
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # Download and save image
        local_path = self._download_image(image_url, trend_text)
        
        print(f"✅ Design generated: {local_path}")
        return revised_prompt, str(local_path)
    
    def _build_prompt(self, trend_text: str, design_type: str, style: str) -> str:
        """Build DALL-E prompt optimized for merch designs"""
        
        base_instructions = (
            "Create a print-on-demand merchandise design suitable for t-shirts. "
            "The design should be eye-catching, trendy, and commercially viable. "
            "Use bold colors and clear imagery. "
            "NO BACKGROUND - transparent or single color background. "
        )
        
        style_modifiers = {
            "bold": "Use thick lines, high contrast, and vibrant colors. Modern graphic design style.",
            "minimalist": "Clean, simple design with minimal elements. Scandinavian aesthetic.",
            "retro": "Vintage 80s/90s aesthetic with nostalgic vibes. Retro color palette.",
            "modern": "Contemporary graphic design with trendy aesthetics. Clean and professional.",
        }
        
        type_instructions = {
            "graphic": f"Create an illustration or graphic design representing: {trend_text}",
            "text": f"Create a typographic design with the text: '{trend_text}'. Make the typography creative and engaging.",
            "hybrid": f"Combine illustration and typography for: {trend_text}",
        }
        
        prompt = (
            f"{base_instructions} "
            f"{style_modifiers.get(style, style_modifiers['bold'])} "
            f"{type_instructions.get(design_type, type_instructions['graphic'])}"
        )
        
        return prompt
    
    def _download_image(self, url: str, trend_text: str) -> Path:
        """Download generated image to local storage"""
        
        # Create safe filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in trend_text)
        safe_name = safe_name[:50].strip().replace(' ', '_')
        filename = f"{timestamp}_{safe_name}.png"
        
        filepath = self.output_dir / filename
        
        # Download image
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return filepath
    
    def generate_variations(
        self,
        original_image_path: str,
        n: int = 2,
        size: str = "1024x1024"
    ) -> list[str]:
        """
        Generate variations of an existing design.
        Useful for A/B testing different versions.
        
        Args:
            original_image_path: Path to original image
            n: Number of variations (1-4)
            size: Image size
            
        Returns:
            List of local file paths to variations
        """
        print(f"🔄 Generating {n} variations...")
        
        with open(original_image_path, 'rb') as image_file:
            response = self.client.images.create_variation(
                image=image_file,
                n=min(n, 4),  # DALL-E max is 4
                size=size,
            )
        
        variation_paths = []
        for i, image_data in enumerate(response.data):
            image_url = image_data.url
            local_path = self._download_image(image_url, f"variation_{i}")
            variation_paths.append(str(local_path))
        
        print(f"✅ Generated {len(variation_paths)} variations")
        return variation_paths


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    client = DALLEClient()
    
    # Test design generation
    test_trend = "Cats wearing tiny hats"
    prompt, image_path = client.generate_merch_design(
        trend_text=test_trend,
        design_type="graphic",
        style="bold"
    )
    
    print(f"\nPrompt used: {prompt}")
    print(f"Image saved: {image_path}")
