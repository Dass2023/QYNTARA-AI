from PIL import Image
from collections import Counter
import sys

def get_dominant_colors(image_path, num_colors=3):
    try:
        image = Image.open(image_path)
        image = image.convert('RGB')
        
        # Resize for faster processing
        image = image.resize((150, 150))
        
        pixels = list(image.getdata())
        
        # Remove white/near-white/transparent background pixels if possible
        # Simple filter: skip very light pixels
        filtered_pixels = [p for p in pixels if not (p[0] > 240 and p[1] > 240 and p[2] > 240)]
        
        if not filtered_pixels:
            print("Image is mostly white. Returning fallback.")
            return [(0, 0, 0)]

        counts = Counter(filtered_pixels)
        dominant = counts.most_common(num_colors)
        
        return [color for color, count in dominant]
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    logo_path = r"e:\QYNTARA AI\Qyntara_Logo_Final.png"
    colors = get_dominant_colors(logo_path)
    print("Found Colors (RGB):")
    for c in colors:
        print(c)
