import os
import platform
import subprocess
import requests
import zipfile
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_file(url, output_path):
    print(f"📥 Downloading: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))

        with open(output_path, "wb") as file, tqdm(
            desc=f"⬇️ {os.path.basename(output_path)}",
            total=total, unit="B", unit_scale=True, unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))
        return output_path
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        return None

def extract_zip(zip_path, extract_to=DOWNLOAD_DIR):
    print(f"\n📦 Extracting {zip_path} ...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ Extracted to {extract_to}")
        return os.listdir(extract_to)
    except Exception as e:
        print(f"❌ Failed to extract: {e}")
        return []

def open_file(file_path):
    print(f"📂 Opening {file_path} ...")
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", file_path])
        else:
            subprocess.run(["xdg-open", file_path])
    except Exception as e:
        print(f"❌ Failed to open file: {e}")

def download_m3u8(url, output_path):
    print(f"🎞️ Downloading M3U8 video: {url}")
    try:
        cmd = ["ffmpeg", "-y", "-i", url, "-c", "copy", output_path]
        subprocess.run(cmd, check=True)
        print(f"✅ M3U8 video saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ M3U8 download failed: {e}")
        return None

def send_to_telegram(file_path, caption=""):
    print(f"🚀 [TELEGRAM] Would send: {file_path} with caption: {caption}")

def process_url(url):
    filename = url.split("/")[-1].split("?")[0]
    file_ext = os.path.splitext(filename)[-1].lower()

    if ".m3u8" in url or file_ext == ".m3u8":
        output_path = os.path.join(DOWNLOAD_DIR, filename.replace(".m3u8", ".mp4"))
        result = download_m3u8(url, output_path)
        if result:
            open_file(result)
            send_to_telegram(result)
    else:
        download_path = os.path.join(DOWNLOAD_DIR, filename)
        downloaded = download_file(url, download_path)
        if downloaded and file_ext == ".zip":
            for f in extract_zip(downloaded):
                if f.endswith(('.mp4', '.pdf')):
                    fp = os.path.join(DOWNLOAD_DIR, f)
                    open_file(fp)
                    send_to_telegram(fp)
        elif downloaded and file_ext in ('.mp4', '.pdf'):
            open_file(download_path)
            send_to_telegram(download_path)
        else:
            print("📎 File downloaded, no automatic action.")

def main():
    urls = [
        "https://transcoded-videos-v2.classx.co.in/videos/gyanbindu-data/342818-1747564844/encrypted-ff5de0/720p.zip",
    ]
    for url in urls:
        process_url(url)

if __name__ == "__main__":
    main()
