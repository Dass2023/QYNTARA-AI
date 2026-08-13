from PIL import Image
import sys
import os

def remove_background(image_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        datas = img.getdata()
        
        newData = []
        # Target background is roughly #1a1a1a (26, 26, 26) or just black/dark
        # We will filter out dark pixels.
        
        for item in datas:
            # item is (r,g,b,a)
            # Calculate luminance or just sum
            # If it's very dark, make it transparent
            # Let's say anything darker than (40, 40, 40) is background?
            # Or use specific color distance to #1a1a1a
            
            # Simple threshold:
            if item[0] < 40 and item[1] < 40 and item[2] < 40:
                newData.append((0, 0, 0, 0))
            else:
                # For a better look, we can scale alpha based on brightness for the 'glow' edge?
                # But simple Hard Key is safer to avoid semi-transparent artifacts in the UI.
                newData.append(item)
                
        img.putdata(newData)
        
        # Save as _transparent.png
        base, ext = os.path.splitext(image_path)
        out_path = base + "_transparent.png"
        img.save(out_path, "PNG")
        print(f"Saved: {out_path}")
        
    except Exception as e:
        with open("e:/QYNTARA AI/bg_error.log", "w") as f:
            f.write(f"Failed to process {image_path}: {e}")
        print(f"Failed to process {image_path}: {e}")

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("No args")
        for arg in sys.argv[1:]:
            remove_background(arg)
    except Exception as e:
        with open("e:/QYNTARA AI/bg_error.log", "w") as f:
            f.write(f"Main Error: {e}")
