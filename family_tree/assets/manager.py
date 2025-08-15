"""
Asset management for family tree backgrounds and decorative elements.
"""
import os
from typing import List, Optional
from PIL import Image


class AssetManager:
    """Manages background images and other assets for family tree rendering."""
    
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = assets_dir
        self.ensure_assets_directory()
    
    def ensure_assets_directory(self):
        """Create assets directory if it doesn't exist."""
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)
    
    def get_background_path(self, background_name: str) -> Optional[str]:
        """Get full path to a background image."""
        path = os.path.join(self.assets_dir, "backgrounds", background_name)
        return path if os.path.exists(path) else None
    
    def list_backgrounds(self) -> List[str]:
        """List available background images."""
        backgrounds_dir = os.path.join(self.assets_dir, "backgrounds")
        if not os.path.exists(backgrounds_dir):
            return []
        
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        backgrounds = []
        
        for file in os.listdir(backgrounds_dir):
            if any(file.lower().endswith(fmt) for fmt in supported_formats):
                backgrounds.append(file)
        
        return sorted(backgrounds)
    
    def create_vintage_scroll_background(self, width: int = 2000, height: int = 1500) -> str:
        """Create a vintage scroll-like background image."""
        from PIL import ImageDraw, ImageFilter
        import random
        
        # Create a parchment-colored background
        background = Image.new('RGB', (width, height), color='#f4f1e8')
        draw = ImageDraw.Draw(background)
        
        # Add some texture with random spots and variations
        for _ in range(200):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 8)
            # Add brownish spots for aging effect
            color = (
                max(180, random.randint(200, 240)),
                max(160, random.randint(190, 220)),
                max(140, random.randint(170, 200))
            )
            draw.ellipse([x, y, x + size, y + size], fill=color)
        
        # Add subtle gradient from edges
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create vignette effect
        for i in range(50):
            alpha = int(i * 2)
            overlay_draw.rectangle(
                [i, i, width - i, height - i],
                outline=(139, 69, 19, alpha),  # Brown color
                width=1
            )
        
        # Composite the overlay
        background = Image.alpha_composite(background.convert('RGBA'), overlay)
        
        # Add decorative border
        border_width = 20
        border_color = '#8B4513'  # SaddleBrown
        draw = ImageDraw.Draw(background)
        
        # Outer border
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
        
        # Inner decorative border
        inner_margin = border_width + 10
        draw.rectangle([inner_margin, inner_margin, width-inner_margin-1, height-inner_margin-1], 
                      outline=border_color, width=3)
        
        # Add corner decorations (simple diamonds)
        corner_size = 30
        corners = [
            (border_width + 20, border_width + 20),  # Top-left
            (width - border_width - 50, border_width + 20),  # Top-right
            (border_width + 20, height - border_width - 50),  # Bottom-left
            (width - border_width - 50, height - border_width - 50)  # Bottom-right
        ]
        
        for cx, cy in corners:
            # Draw diamond shape
            points = [
                (cx, cy - corner_size//2),
                (cx + corner_size//2, cy),
                (cx, cy + corner_size//2),
                (cx - corner_size//2, cy)
            ]
            draw.polygon(points, outline=border_color, width=2)
        
        backgrounds_dir = os.path.join(self.assets_dir, "backgrounds")
        os.makedirs(backgrounds_dir, exist_ok=True)
        
        output_path = os.path.join(backgrounds_dir, "vintage_scroll.png")
        background.convert('RGB').save(output_path)
        
        return output_path
    
    def create_classic_paper_background(self, width: int = 2000, height: int = 1500) -> str:
        """Create a classic paper background."""
        # Create an off-white paper-like background
        background = Image.new('RGB', (width, height), color='#faf8f3')
        
        backgrounds_dir = os.path.join(self.assets_dir, "backgrounds")
        os.makedirs(backgrounds_dir, exist_ok=True)
        
        output_path = os.path.join(backgrounds_dir, "classic_paper.png")
        background.save(output_path)
        
        return output_path