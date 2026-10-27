import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "static", "screenshots")
ARTIFACTS_DIR = r"C:\Users\rsudh\.gemini\antigravity-ide\brain\079113c3-9929-4a83-a84c-a0c66e0cfb51"

def save_screenshot(page, filename):
    local_path = os.path.join(SCREENSHOTS_DIR, filename)
    page.screenshot(path=local_path, full_page=False)
    print(f"Saved screenshot: {local_path}", flush=True)
    if os.path.exists(ARTIFACTS_DIR):
        art_path = os.path.join(ARTIFACTS_DIR, filename)
        page.screenshot(path=art_path, full_page=False)
        print(f"Saved artifact screenshot: {art_path}", flush=True)

def run_simulation():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser1 = p.chromium.launch(headless=True)
        browser2 = p.chromium.launch(headless=True)

        context1 = browser1.new_context(viewport={'width': 1280, 'height': 850})
        context2 = browser2.new_context(viewport={'width': 1280, 'height': 850})

        page1 = context1.new_page()
        page2 = context2.new_page()

        print("=== STEP 1: Visiting Home Page & Testing Minimal Dropdown FAQs ===", flush=True)
        page1.goto(f"{BASE_URL}/")
        page1.wait_for_timeout(1000)

        # Open first two FAQ dropdown items to demonstrate minimal clean accordion
        faq_details = page1.locator("section details summary").all()
        if len(faq_details) > 0:
            faq_details[0].click()
            page1.wait_for_timeout(400)
        if len(faq_details) > 1:
            faq_details[1].click()
            page1.wait_for_timeout(400)

        save_screenshot(page1, "01_home_lighter_aesthetic_dropdown_faq.png")

        print("=== STEP 2: Browser 1 — User 1 ('clara_reader') Sign Up & Review ===", flush=True)
        page1.goto(f"{BASE_URL}/register/")
        
        suffix = int(time.time()) % 10000
        u1 = f"clara_{suffix}"
        u2 = f"marcus_{suffix}"

        page1.fill("input[name='username']", u1)
        page1.fill("input[name='email']", f"{u1}@example.com")
        page1.fill("input[name='password']", "BookboxdPass2026!")
        page1.fill("input[name='password_confirm']", "BookboxdPass2026!")
        page1.click("button[type='submit']")
        page1.wait_for_url(f"{BASE_URL}/")
        print(f"User 1 registered and logged in as {u1}", flush=True)

        # Navigate to Book #1 (Dune)
        page1.goto(f"{BASE_URL}/book/1/")
        page1.wait_for_timeout(1000)

        # Add to shelf "Currently Reading"
        shelf_btn = page1.locator("button:has-text('Currently Reading')").first
        if shelf_btn.is_visible():
            shelf_btn.click()
            page1.wait_for_timeout(800)

        # Rate Dune 5 stars
        page1.select_option("select[name='rating']", "5.0")

        # Enter review text
        page1.fill("textarea[name='review_text']", "Dune is an absolute masterpiece of science fiction and ecological worldbuilding! The desert planet Arrakis and spice politics are gripping from beginning to end. Beware the massive sandworm climax and Paul's prescient destiny!")
        
        # Check spoiler checkbox
        page1.check("input[name='contains_spoilers']")
        page1.wait_for_timeout(400)

        # Submit review
        page1.locator("form[action*='/rate/'] button[type='submit']").click()
        page1.wait_for_timeout(1500)

        save_screenshot(page1, "02_user1_rate_and_spoiler_review.png")

        print("=== STEP 3: Browser 1 — Ask AI Chatbot with Prefilled Question ===", flush=True)
        # Open floating chat widget
        page1.click("#ai-chat-toggle")
        page1.wait_for_selector("#ai-chat-widget", state="visible")
        page1.wait_for_timeout(600)

        # Click a prefilled suggestion pill
        quick_btn = page1.locator(".quick-ai-btn[data-prompt*='sci-fi']").first
        if quick_btn.is_visible():
            quick_btn.click()
        else:
            page1.fill("#ai-chat-input", "Recommend me 2 great sci-fi books like Dune")
            page1.click("#ai-chat-send")

        # Wait for AI response bubble to appear
        try:
            page1.wait_for_selector(".chat-scroll .justify-start:nth-child(2)", timeout=20000)
            page1.wait_for_timeout(1500)
        except Exception as e:
            print(f"Chat response timeout, saving current state: {e}", flush=True)

        save_screenshot(page1, "03_user1_ask_ai_prefilled_questions.png")

        print("=== STEP 4: Browser 2 — User 2 ('marcus_books') Sign Up, Follow & Comment ===", flush=True)
        page2.goto(f"{BASE_URL}/register/")
        page2.fill("input[name='username']", u2)
        page2.fill("input[name='email']", f"{u2}@example.com")
        page2.fill("input[name='password']", "BookboxdPass2026!")
        page2.fill("input[name='password_confirm']", "BookboxdPass2026!")
        page2.click("button[type='submit']")
        page2.wait_for_url(f"{BASE_URL}/")
        print(f"User 2 registered and logged in as {u2}", flush=True)

        # Visit clara's profile to follow
        page2.goto(f"{BASE_URL}/user/{u1}/")
        page2.wait_for_timeout(1000)

        # Click Follow button
        follow_btn = page2.locator("a:has-text('Follow')").first
        if follow_btn.is_visible():
            follow_btn.click()
            page2.wait_for_timeout(1000)

        # Go to Book #1 to read clara's review and comment
        page2.goto(f"{BASE_URL}/book/1/")
        page2.wait_for_timeout(1000)

        # Reveal Clara's spoilers
        reveal_btn = page2.locator(".spoiler-toggle-btn").first
        if reveal_btn.is_visible():
            reveal_btn.click()
            page2.wait_for_timeout(500)

        # Add comment on Clara's review
        comment_input = page2.locator("input[name='comment_text']").first
        if comment_input.is_visible():
            comment_input.fill("Totally agree Clara! The political maneuvering between House Atreides and the Harkonnens is unparalleled.")
            page2.locator("button:has-text('Post')").first.click()
            page2.wait_for_timeout(1200)

        save_screenshot(page2, "04_user2_friend_follow_and_comment.png")

        print("=== STEP 5: Community & Live Social Activity Stream ===", flush=True)
        page2.goto(f"{BASE_URL}/")
        page2.wait_for_timeout(1000)
        save_screenshot(page2, "05_community_activity_stream.png")

        print("All simulation actions completed successfully!", flush=True)

        browser1.close()
        browser2.close()

if __name__ == '__main__':
    run_simulation()
