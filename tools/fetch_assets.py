"""Download the site images listed in tools/assets.json and prepare web-sized copies.

Run by the "Fetch assets" GitHub Action. Safe to re-run: existing files are skipped.
"""
import io, json, os, sys, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX = {"making": 1800, "story": 2000}
THUMB = 480
failed = []

def save_webp(img, path, max_side, quality=82):
    img = ImageOps.exif_transpose(img)
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.LANCZOS)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    img.save(path, "WEBP", quality=quality, method=6)

for item in json.load(open(os.path.join(ROOT, "tools", "assets.json"))):
    dest = os.path.join(ROOT, item["dest"])
    kind = item["kind"]
    thumb = os.path.join(os.path.dirname(dest), "thumb", os.path.basename(dest))
    if os.path.exists(dest) and (kind != "making" or os.path.exists(thumb)):
        continue
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        if kind == "keep":
            open(dest, "wb").write(data)
        else:
            img = Image.open(io.BytesIO(data))
            save_webp(img, dest, MAX[kind])
            if kind == "making":
                os.makedirs(os.path.dirname(thumb), exist_ok=True)
                save_webp(Image.open(io.BytesIO(data)), thumb, THUMB, quality=78)
        print("ok  ", item["dest"])
    except Exception as e:  # keep going, report at the end
        failed.append((item["dest"], str(e)))
        print("FAIL", item["dest"], e)

if failed:
    sys.exit(f"{len(failed)} asset(s) failed")
