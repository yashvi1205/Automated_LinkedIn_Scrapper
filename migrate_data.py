import json
import os

LAST_POST_FILE = "last_posts.json"

if os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "r") as f:
        data = json.load(f)
    
    new_data = {}
    for url, content in data.items():
        if isinstance(content, str):
            new_data[url] = {
                "text": content,
                "likes": "0",
                "comments": "0",
                "reposts": "0",
                "timestamp": "Pre-migration"
            }
        else:
            new_data[url] = content
            
    with open(LAST_POST_FILE, "w") as f:
        json.dump(new_data, f, indent=4)
    print("Migration complete.")
else:
    print("File not found.")
