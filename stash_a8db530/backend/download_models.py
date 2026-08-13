import os
import requests
import sys
from tqdm import tqdm

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
SAM_CHECKPOINT_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
SAM_CHECKPOINT_FILENAME = "sam_vit_h_4b8939.pth"

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
        return False
    return True

def main():
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        print(f"Created directory: {MODELS_DIR}")
        
    filepath = os.path.join(MODELS_DIR, SAM_CHECKPOINT_FILENAME)
    
    if os.path.exists(filepath):
        print(f"Model already exists at: {filepath}")
        # Optional: Check size or hash to verify integrity
        return

    print(f"Downloading SAM ViT-H checkpoint to {filepath}...")
    try:
        success = download_file(SAM_CHECKPOINT_URL, filepath)
        if success:
            print("Download complete!")
        else:
            print("Download failed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
