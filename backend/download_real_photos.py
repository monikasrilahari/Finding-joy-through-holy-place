"""Download distinct place photographs from Wikimedia Commons with retry/backoff.
Run from the project folder: python download_real_photos.py
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json, sqlite3, time, re, csv

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "static" / "images"
DB = ROOT / "finding_joy.db"
API = "https://commons.wikimedia.org/w/api.php"
UA = "FindingJoyHolyPlacesStudentProject/2.0 (educational website; contact: project-maintainer@example.com)"
PLACES = [
("Tirumala Venkateswara Temple", "Tirumala Venkateswara Temple India"),
("Kashi Vishwanath Temple", "Kashi Vishwanath Temple Varanasi India"),
("Golden Temple", "Golden Temple Harmandir Sahib Amritsar India"),
("Meenakshi Amman Temple", "Meenakshi Amman Temple Madurai India"),
("Jagannath Temple", "Jagannath Temple Puri India"),
("Somnath Temple", "Somnath Temple Gujarat India"),
("Brihadeeswarar Temple", "Brihadeeswarar Temple Thanjavur India"),
("Kedarnath Temple", "Kedarnath Temple Uttarakhand India"),
("Vaishno Devi", "Vaishno Devi temple Katra India"),
("Akshardham Temple", "Akshardham Temple Delhi India"),
("Ramanathaswamy Temple", "Ramanathaswamy Temple Rameswaram India"),
("Siddhivinayak Temple", "Siddhivinayak Temple Mumbai India"),
("Haji Ali Dargah", "Haji Ali Dargah Mumbai India"),
("Jama Masjid", "Jama Masjid Delhi India"),
("Charminar Mosque", "Charminar Hyderabad mosque India"),
("Basilica of Bom Jesus", "Basilica of Bom Jesus Goa India"),
("San Thome Basilica", "San Thome Basilica Chennai India"),
("Velankanni Basilica", "Velankanni Basilica Tamil Nadu India"),
("Tawang Monastery", "Tawang Monastery Arunachal Pradesh India"),
("Mahabodhi Temple", "Mahabodhi Temple Bodh Gaya India"),
]

def api(params, attempts=5):
    url = API + "?" + urlencode(params)
    for attempt in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urlopen(req, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                raise
            wait = min(90, 8 * (2 ** attempt))
            print(f"  Wikimedia busy (HTTP {e.code}); retrying in {wait}s...")
            time.sleep(wait)
        except (URLError, TimeoutError) as e:
            if attempt == attempts - 1:
                raise
            wait = min(60, 5 * (2 ** attempt))
            print(f"  Network issue; retrying in {wait}s...")
            time.sleep(wait)

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def download(url, dest):
    for attempt in range(5):
        try:
            req = Request(url, headers={"User-Agent": UA})
            with urlopen(req, timeout=60) as response:
                data = response.read()
            if len(data) < 12000 or not (data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG\r\n\x1a\n")):
                raise ValueError("Not a usable JPEG photo")
            dest.write_bytes(data)
            return
        except Exception:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    used_titles, credits = set(), []
    success = 0
    for index, (name, query) in enumerate(PLACES, 1):
        dest = IMG / f"{slug(name)}.jpg"
        print(f"[{index}/20] {name}")
        existing_png = dest.with_suffix(".png")
        if (dest.exists() and dest.stat().st_size > 12000) or (existing_png.exists() and existing_png.stat().st_size > 12000):
            print("  Existing photo kept")
            success += 1
            continue
        try:
            result = api({"action":"query", "format":"json", "list":"search", "srnamespace":6,
                          "srlimit":12, "srsearch":query})
            candidates = result.get("query", {}).get("search", [])
            # Prefer a unique file whose title contains a useful part of the place name.
            chosen = None
            terms = [w.lower() for w in re.findall(r"[a-zA-Z]+", name) if len(w) > 3]
            ranked = sorted(candidates, key=lambda x: sum(t in x.get("title", "").lower() for t in terms), reverse=True)
            for item in ranked:
                title = item.get("title", "")
                if title in used_titles:
                    continue
                info = api({"action":"query", "format":"json", "titles":title,
                            "prop":"imageinfo", "iiprop":"url|mime|extmetadata", "iiurlwidth":1200})
                pages = info.get("query", {}).get("pages", {})
                page = next(iter(pages.values()), {})
                ii = (page.get("imageinfo") or [{}])[0]
                mime = ii.get("mime", "")
                image_url = ii.get("thumburl") or ii.get("url")
                if mime not in ("image/jpeg", "image/png") or not image_url:
                    continue
                chosen = (title, image_url, ii.get("extmetadata", {}))
                break
            if not chosen:
                raise RuntimeError("No distinct JPEG/PNG photo was found in Wikimedia Commons search results")
            title, image_url, metadata = chosen
            # JPG files are used by the existing site; PNGs are stored with their correct extension.
            if image_url.lower().split("?")[0].endswith(".png"):
                dest = dest.with_suffix(".png")
            download(image_url, dest)
            used_titles.add(title)
            artist = metadata.get("Artist", {}).get("value", "Unknown author")
            license_name = metadata.get("LicenseShortName", {}).get("value", "See Wikimedia Commons file page")
            page_url = "https://commons.wikimedia.org/wiki/" + title.replace(" ", "_")
            credits.append([name, dest.name, title, artist, license_name, page_url])
            print(f"  Downloaded: {dest.name} ({dest.stat().st_size // 1024} KB)")
            success += 1
        except Exception as exc:
            print(f"  Could not download: {exc}")
        # Keep requests gentle to avoid Wikimedia rate limits.
        time.sleep(3.0)

    with (ROOT / "WIKIMEDIA_IMAGE_CREDITS.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Place", "Local file", "Wikimedia file", "Author", "License", "Source URL"])
        writer.writerows(credits)

    if DB.exists():
        with sqlite3.connect(DB) as con:
            for name, _ in PLACES:
                jpg = IMG / f"{slug(name)}.jpg"
                png = IMG / f"{slug(name)}.png"
                chosen = jpg if jpg.exists() else png if png.exists() else None
                if chosen:
                    con.execute("UPDATE places SET image=? WHERE name=?", (f"/static/images/{chosen.name}", name))
    print(f"\nFinished: {success}/20 places have local photos.")
    print("Photo credits: WIKIMEDIA_IMAGE_CREDITS.csv")
    if success < 20:
        print("Some images may need another run later; downloaded photos are kept and will not be downloaded again.")

if __name__ == "__main__":
    main()
