from playwright.sync_api import sync_playwright
from backend.database.crud import get_all_users
import time
import random


def scrape_profile(page, url):

    print("Opening profile:", url)

    page.goto(url)

    page.wait_for_timeout(5000)

    try:
        name = page.locator("h1").first.inner_text()
    except:
        name = "Unknown"

    try:
        headline = page.locator(".text-body-medium").first.inner_text()
    except:
        headline = "Unknown"

    try:
        location = page.locator(".text-body-small").first.inner_text()
    except:
        location = "Unknown"

    print(name, headline, location)


def run_profile_scraper():

    users = get_all_users()

    with sync_playwright() as p:

        browser = p.chromium.launch_persistent_context(
            user_data_dir="backend/session",
            headless=False
        )

        page = browser.new_page()

        for user in users:

            scrape_profile(page, user.profile_url)

            time.sleep(random.uniform(3,6))

        input("Press ENTER to close")

        browser.close()


run_profile_scraper()