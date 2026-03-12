from playwright.sync_api import sync_playwright

def create_session():

    with sync_playwright() as p:

        browser = p.chromium.launch_persistent_context(
            user_data_dir="backend/session",
            headless=False
        )

        page = browser.new_page()

        page.goto("https://www.linkedin.com/login")

        print("Login manually in the browser.")

        # Wait for user login
        input("After logging in press ENTER here...")

        print("Session saved successfully.")

        # Keep browser open for verification
        input("Press ENTER to close the browser...")

        browser.close()


create_session()