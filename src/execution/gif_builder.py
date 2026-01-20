import os
import imageio
import numpy as np
from PIL import Image, ImageDraw

class GIFBuilder:
    """
    A lightweight utility for creating animated GIFs optimized for Slack/Social.
    Ported concepts from slack-gif-creator skill.
    """
    def __init__(self, width=480, height=480, fps=12):
        self.width = width
        self.height = height
        self.fps = fps
        self.frames = []

    def add_frame(self, pil_image):
        """Adds a PIL image as a frame."""
        # Ensure correct size
        if pil_image.size != (self.width, self.height):
            pil_image = pil_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if it's RGBA
        if pil_image.mode == 'RGBA':
            background = Image.new('RGB', pil_image.size, (255, 255, 255))
            background.paste(pil_image, mask=pil_image.split()[3])
            pil_image = background
            
        self.frames.append(np.array(pil_image))

    def save(self, output_path, loop=0):
        """Saves the accumulated frames as a GIF."""
        if not self.frames:
            raise ValueError("No frames added to GIFBuilder.")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        imageio.mimsave(output_path, self.frames, fps=self.fps, loop=loop)
        return output_path

def create_pulsing_animation(text, brand_color=(0, 102, 204), bg_color=(240, 240, 240)):
    """A helper to create a simple branded pulsing GIF."""
    builder = GIFBuilder(width=480, height=128, fps=15)
    
    for i in range(20):
        # Pulse factor using sine wave
        pulse = 1.0 + 0.1 * np.sin(i * (2 * np.pi / 20))
        
        frame = Image.new('RGB', (480, 128), bg_color)
        draw = ImageDraw.Draw(frame)
        
        # We'll use a simple rectangle as a placeholder for text/logo pulse
        center_x, center_y = 240, 64
        rw, rh = 200 * pulse, 40 * pulse
        
        draw.rectangle(
            [center_x - rw/2, center_y - rh/2, center_x + rw/2, center_y + rh/2],
            fill=brand_color,
            outline=(255, 255, 255),
            width=3
        )
        
        builder.add_frame(frame)
    
    return builder
