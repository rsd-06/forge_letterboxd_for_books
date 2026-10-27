import os
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = os.path.join(os.getcwd(), "static", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1366, 'height': 850})
        page = context.new_page()

        print("1. Capturing rich home catalog...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_home_lighter_aesthetic_dropdown_faq.png"), full_page=False)

        print("2. Capturing browse books catalog...")
        page.goto(f"{BASE_URL}/search/")
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_curated_library_browse.png"), full_page=False)

        print("3. Capturing book detail with reviews & comments...")
        # Find ID of The Name of the Wind or Dune
        page.goto(f"{BASE_URL}/")
        page.wait_for_timeout(1000)
        page.locator("a[href*='/book/']").first.click()
        page.wait_for_timeout(1500)
        page.evaluate("window.scrollBy({top: 450, behavior: 'smooth'})")
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_user1_rate_and_spoiler_review.png"), full_page=False)

        print("4. Capturing Community readers...")
        page.goto(f"{BASE_URL}/community/")
        page.wait_for_timeout(1500)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "04_user2_friend_follow_and_comment.png"), full_page=False)

        print("5. Capturing community activity stream on home...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_timeout(1000)
        page.evaluate("window.scrollBy({top: 750, behavior: 'smooth'})")
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_community_activity_stream.png"), full_page=False)

        browser.close()
    print("Done capturing rich screenshots!")

if __name__ == '__main__':
    capture_screenshots()
