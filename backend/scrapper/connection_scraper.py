from playwright.sync_api import sync_playwright
from database.crud import save_user
import time
import random


def auto_scroll(page):

    print("Starting controlled scroll")

    for i in range(15):

        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(4000)

        print(f"Scroll cycle {i+1}/15")


def scrape_connections():

    with sync_playwright() as p:

        browser = p.chromium.launch_persistent_context(
            user_data_dir="backend/session",
            headless=False
        )

        page = browser.new_page()

        try:

            print("Opening LinkedIn connections...")

            # retry navigation
            for attempt in range(3):

                try:
                    page.goto(
                        "https://www.linkedin.com/mynetwork/invite-connect/connections/",
                        timeout=60000
                    )
                    break
                except:
                    print("Navigation failed. Retrying...")
                    time.sleep(5)

            page.wait_for_timeout(8000)

            auto_scroll(page)

            # collect all links
            links = page.locator("a[href*='/in/']").all()

            print("Links detected:", len(links))

            collected = set()

            for link in links:
                href = link.get_attribute("href")
                if href and "/in/" in href:
                    full_url = href.split("?")[0]
                    print("Detected:", full_url)
                save_user(full_url)

            print("Total profiles:", len(collected))

            input("Press ENTER to close browser")

        except Exception as e:

            print("Error:", e)

        finally:

            try:
                browser.close()
            except:
                pass
scrape_connections()