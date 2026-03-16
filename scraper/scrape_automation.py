import sys
import os
import time
import random
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from session import get_driver, human_delay
from google_sheets import save_to_sheet


LAST_POST_FILE = "last_posts.json"


def read_profiles():

    with open("profiles.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def load_last_posts():

    if not os.path.exists(LAST_POST_FILE):
        return {}

    with open(LAST_POST_FILE, "r") as f:
        return json.load(f)


def save_last_posts(data):

    with open(LAST_POST_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_username(profile_url):

    slug = profile_url.split("/in/")[1].split("/")[0]
    return slug.replace("-", " ").title()

def get_latest_post(driver):

    try:

        post = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.feed-shared-update-v2")
            )
        )

        text = post.find_element(
            By.CSS_SELECTOR,
            "div.update-components-text"
        ).text

        def extract_number(text):
            if not text: return "0"
            numbers = "".join(filter(str.isdigit, text))
            return numbers if numbers else "0"

        try:
            # Likes: Try multiple common LinkedIn classes
            likes_selectors = [
                ".social-details-social-counts__reactions-count",
                ".social-details-social-counts__social-text",
                "span[class*='reactions-count']"
            ]
            likes_text = ""
            for selector in likes_selectors:
                elements = post.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    likes_text = elements[0].text
                    if likes_text: break
            
            print(f"DEBUG: Found likes text: '{likes_text}'")
            likes = extract_number(likes_text)
        except:
            pass

        try:
            # Comments: Look for aria-label or text
            comments_selectors = [
                "button[aria-label*='comment']",
                ".social-details-social-counts__comments",
                "span[class*='comments-count']"
            ]
            comments_text = ""
            for selector in comments_selectors:
                elements = post.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    el = elements[0]
                    comments_text = el.get_attribute("aria-label") or el.text
                    if comments_text: break

            print(f"DEBUG: Found comments text: '{comments_text}'")
            comments = extract_number(comments_text)
        except:
            pass

        try:
            # Reposts: Look for aria-label or text
            reposts_selectors = [
                "button[aria-label*='repost']",
                "button[aria-label*='Repost']",
                ".social-details-social-counts__reposts"
            ]
            reposts_text = ""
            for selector in reposts_selectors:
                elements = post.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    el = elements[0]
                    reposts_text = el.get_attribute("aria-label") or el.text
                    if reposts_text: break

            print(f"DEBUG: Found reposts text: '{reposts_text}'")
            reposts = extract_number(reposts_text)
        except:
            pass

        try:
            # Profile Photo: Look for the image associated with the post author
            photo_element = post.find_element(By.CSS_SELECTOR, "img.update-components-actor__avatar-image")
            photo_url = photo_element.get_attribute("src")
            print(f"DEBUG: Found photo URL: '{photo_url}'")
        except:
            print("DEBUG: Photo element not found")
            photo_url = ""

        return text, likes, comments, reposts, photo_url

    except Exception as e:
        print("Could not fetch post:", e)
        return None, "0", "0", "0", ""

def send_notification(user, profile, post):
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    url = "http://localhost:5678/webhook/linkedin-activity" # Default
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                url = config.get("n8n_webhook_url", url)
        except:
            pass

    payload = {
        "user": user,
        "profile": profile,
        "post": post,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Notification sent to n8n ({url})")
    except Exception as e:
        print("Webhook error:", e)

def scrape_profile(driver, profile_url, last_posts):
    username = get_username(profile_url)
    print(f"\n--- Checking Profile: {username} ---")
    
    activity_url = profile_url.rstrip("/") + "/recent-activity/all/"
    print("URL:", activity_url)
    
    try:
        driver.get(activity_url)
        time.sleep(5) # Wait for page load
        
        post_text, likes, comments, reposts, photo_url = get_latest_post(driver)
        
        if not post_text:
            print(f"No posts found for {username}")
            return

        last_entry = last_posts.get(profile_url)
        
        if isinstance(last_entry, dict):
            last_text = last_entry.get("text", "")
            last_likes = str(last_entry.get("likes", "0"))
            last_comments = str(last_entry.get("comments", "0"))
            last_reposts = str(last_entry.get("reposts", "0"))
            last_photo = last_entry.get("photo_url", "")
        else:
            last_text = last_entry
            last_likes = last_comments = last_reposts = "0"
            last_photo = ""

        # Check for change
        if last_text == post_text and last_likes == likes and last_comments == comments and last_reposts == reposts and last_photo == photo_url:
            print(f"No changes detected for {username}")
        else:
            print(f"Result: NEW ACTIVITY DETECTED for {username}!")
            save_to_sheet(username, profile_url, "Post", post_text, likes, comments, reposts, photo_url)
            
            last_posts[profile_url] = {
                "text": post_text,
                "likes": likes,
                "comments": comments,
                "reposts": reposts,
                "photo_url": photo_url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            send_notification(username, profile_url, post_text)
            
    except Exception as e:
        print(f"Error while scraping {username}: {e}")

def start_scraper():
    driver = None
    try:
        driver = get_driver()
        profiles = read_profiles()
        last_posts = load_last_posts()

        for profile in profiles:
            scrape_profile(driver, profile, last_posts)
            save_last_posts(last_posts) # Save progress after each profile
            
            wait_time = random.randint(15, 30)
            print(f"Waiting {wait_time}s before next profile...")
            time.sleep(wait_time)
            
    finally:
        if driver:
            print("Finished all profiles. Closing browser...")
            driver.quit()


if __name__ == "__main__":
    start_scraper()