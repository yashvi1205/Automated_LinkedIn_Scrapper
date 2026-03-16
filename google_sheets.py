import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("LinkedIn_Profile_DataScraper").sheet1


def save_to_sheet(user, profile, post_type, text, likes, comments, reposts, photo_url=""):
    """Saves a new entry with standardized column order."""
    row = [
        str(user).strip(),
        str(profile).strip(),
        str(post_type).strip(),
        str(text),
        int(likes) if str(likes).isdigit() else 0,
        int(comments) if str(comments).isdigit() else 0,
        int(reposts) if str(reposts).isdigit() else 0,
        str(photo_url),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ]

    # Ensure headers are correct before saving
    headers = ["User", "Profile URL", "Type", "Text", "Likes", "Comments", "Reposts", "Photo URL", "Timestamp"]
    try:
        if not sheet.row_values(1):
            sheet.insert_row(headers, 1)
    except:
        pass

    sheet.append_row(row)
    print("Saved to Google Sheets")


def get_latest_post_for_profile(profile_url):
    """Search Google Sheets for the most recent entry for a specific profile URL."""
    try:
        all_records = sheet.get_all_records()
        if not all_records:
            return None
        
        # Reverse to find the most recent one
        for record in reversed(all_records):
            # Normalizing keys (lowercase and stripped)
            norm_record = {str(k).lower().strip(): v for k, v in record.items()}
            
            url_in_sheet = norm_record.get("profile url") or norm_record.get("profile")
            if url_in_sheet == profile_url:
                return {
                    "text": norm_record.get("text") or "No text",
                    "likes": norm_record.get("likes") or "0",
                    "comments": norm_record.get("comments") or "0",
                    "reposts": norm_record.get("reposts") or "0",
                    "photo_url": norm_record.get("photo url") or "",
                    "timestamp": norm_record.get("timestamp") or norm_record.get("scraped time") or "Recently"
                }
        return None
    except Exception as e:
        print(f"Error searching sheet: {e}")
        return None


def get_last_entries(count=5):
    """Retrieve the last N entries from the sheet and normalize them for the API."""
    try:
        all_records = sheet.get_all_records()
        if not all_records:
            return []
        
        raw_entries = all_records[-count:]
        normalized_entries = []
        
        for record in raw_entries:
            # Normalize keys for frontend consistency
            norm = {str(k).lower().strip(): v for k, v in record.items()}
            normalized_entries.append({
                "user": norm.get("user") or norm.get("name") or "Unknown",
                "text": norm.get("text") or norm.get("activity") or "No content",
                "likes": norm.get("likes") or 0,
                "timestamp": norm.get("timestamp") or norm.get("scraped time") or "Recently"
            })
            
        return normalized_entries
    except Exception as e:
        print(f"Error fetching from Google Sheets: {e}")
        return []