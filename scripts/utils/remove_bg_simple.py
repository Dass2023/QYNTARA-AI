from PIL import Image
import os

images = [
    r"C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_icon_3d_1765523450588.png",
    r"C:\Users\ArockiadassD_2j5cw54\.gemini\antigravity\brain\2f5a697b-41f7-4358-97c1-aa7390e017d4\qyntara_type_only_1765523113574.png"
]

for img_path in images:
    if not os.path.exists(img_path):
        print(f"MISSING: {img_path}")
        continue
        
    try:
        print(f"Processing {img_path}...")
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            # Simple threshold < 40
            if item[0] < 40 and item[1] < 40 and item[2] < 40:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        
        # Save to local dir e:\QYNTARA AI
        filename = os.path.basename(img_path).replace(".png", "_transparent.png")
        out_path = os.path.join(os.getcwd(), filename)
        img.save(out_path)
        print(f"Saved to {out_path}")
    except Exception as e:
        print(f"ERROR: {e}")
