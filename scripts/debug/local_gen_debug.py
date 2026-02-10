import sys
print("Starting diagnostic script...")
try:
    from PIL import Image
    print(f"PIL imported. Version: {Image.__version__}")
except ImportError as e:
    print(f"PIL Import Failed: {e}")
    sys.exit(1)

import os

# Input Paths (from artifacts)
images = [
    r"C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_icon_3d_1765523450588.png",
    r"C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_type_only_1765523113574.png"
]

for img_path in images:
    print(f"Checking {img_path}...")
    if not os.path.exists(img_path):
        print("  -> Does not exist!")
        continue
    
    try:
        print("  -> Opening...")
        img = Image.open(img_path).convert("RGBA")
        print(f"  -> Size: {img.size}")
        
        datas = img.getdata()
        newData = []
        print("  -> Processing pixels...")
        count = 0
        for item in datas:
            if item[0] < 40 and item[1] < 40 and item[2] < 40:
                newData.append((0, 0, 0, 0))
                count += 1
            else:
                newData.append(item)
        print(f"  -> Made {count} pixels transparent.")
        
        img.putdata(newData)
        
        # Save to Current Dir
        filename = "local_" + os.path.basename(img_path).replace(".png", "_transparent.png")
        out_path = os.path.join(os.getcwd(), filename)
        print(f"  -> Saving to {out_path}...")
        img.save(out_path)
        print("  -> Saved.")
        
    except Exception as e:
        print(f"  -> ERROR: {e}")

print("Diagnostic finished.")
