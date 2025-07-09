import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
avatars_dir = os.path.join(BASE_DIR, "assets", "avatars")

# تأكد أن المجلد موجود
os.makedirs(avatars_dir, exist_ok=True)

# هنجرب نحمل 20 صورة بنات من randomuser
for i in range(20):
    index = i + 1
    url = f"https://randomuser.me/api/portraits/women/{index}.jpg"
    file_path = os.path.join(avatars_dir, f"avatar{index}.jpg")
    
    try:
        print(f"Downloading {url} ...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Saved {file_path}")
        else:
            print(f"❌ Failed to get image {url} (status {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {url} -> {e}")
