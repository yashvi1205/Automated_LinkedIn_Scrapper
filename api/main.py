from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import subprocess
import sys

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from google_sheets import get_last_entries, get_latest_post_for_profile

app = FastAPI(title="LinkedIn Scraper API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROFILES_FILE = os.path.join(os.path.dirname(__file__), "..", "profiles.txt")
LAST_POSTS_FILE = os.path.join(os.path.dirname(__file__), "..", "last_posts.json")
SCRAPER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scraper", "scrape_automation.py")

def read_profiles():
    if not os.path.exists(PROFILES_FILE):
        return []
    with open(PROFILES_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_last_posts():
    if not os.path.exists(LAST_POSTS_FILE):
        return {}
    with open(LAST_POSTS_FILE, "r") as f:
        return json.load(f)

def save_last_posts(data):
    with open(LAST_POSTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.get("/api/profiles")
def get_profiles():
    profiles = read_profiles()
    last_posts = load_last_posts()
    updated = False
    
    result = []
    for url in profiles:
        username = url.split("/in/")[1].split("/")[0].replace("-", " ").title() if "/in/" in url else url
        entry = last_posts.get(url)
        
        # Fallback to Google Sheets if local data is missing or incomplete
        if not entry or (isinstance(entry, str) and entry == "No activity tracked yet"):
            sheet_entry = get_latest_post_for_profile(url)
            if sheet_entry:
                entry = sheet_entry
                last_posts[url] = entry
                updated = True
            else:
                entry = "No activity tracked yet"

        # Handle both old string format and new object format
        if isinstance(entry, dict):
            post_text = entry.get("text", "No text found")
            photo_url = entry.get("photo_url", "")
            stats = {
                "likes": entry.get("likes", 0),
                "comments": entry.get("comments", 0),
                "reposts": entry.get("reposts", 0)
            }
        else:
            post_text = entry
            photo_url = ""
            stats = {"likes": 0, "comments": 0, "reposts": 0}

        result.append({
            "url": url,
            "username": username,
            "last_post": post_text,
            "photo_url": photo_url,
            "stats": stats
        })
    
    if updated:
        save_last_posts(last_posts)
        
    return result

@app.get("/api/activity")
def get_activity():
    return load_last_posts()

@app.get("/api/sheets-status")
def get_sheets_status():
    entries = get_last_entries(5)
    print(f"DEBUG: Fetched {len(entries)} entries from Sheet. Columns: {list(entries[0].keys()) if entries else 'None'}")
    return {"entries": entries, "count": len(entries)}

@app.post("/api/scrape")
def trigger_scrape():
    try:
        # Run scraper in the background
        subprocess.Popen([sys.executable, SCRAPER_SCRIPT])
        return {"status": "Scraper started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
