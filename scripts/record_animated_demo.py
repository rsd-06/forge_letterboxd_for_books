import os
import sys
import time
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = os.path.join(os.getcwd(), "static", "screenshots")
ARTIFACTS_DIR = r"C:\Users\rsudh\.gemini\antigravity-ide\brain\079113c3-9929-4a83-a84c-a0c66e0cfb51"

def record_demo():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    frames = []

    def capture_frame(page, count=1):
        # Capture screenshot to memory and append as PIL Image
        img_bytes = page.screenshot(full_page=False)
        import io
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        # Resize to 960x600 for sharp crisp rendering and compact file size
        img = img.resize((960, 600), Image.Resampling.LANCZOS)
        for _ in range(count):
            frames.append(img)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use clean context with 1280x800 viewport
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("1. Opening home page...", flush=True)
        page.goto(f"{BASE_URL}/")
        page.wait_for_timeout(1000)
        capture_frame(page, count=3)

        print("2. Scrolling to popular books...", flush=True)
        page.evaluate("window.scrollBy({top: 300, behavior: 'smooth'})")
        page.wait_for_timeout(600)
        capture_frame(page, count=2)

        print("3. Scrolling to Minimal Dropdown FAQs...", flush=True)
        page.evaluate("window.scrollBy({top: 550, behavior: 'smooth'})")
        page.wait_for_timeout(600)
        capture_frame(page, count=2)

        print("4. Expanding FAQ 1...", flush=True)
        faq_items = page.locator("section details summary").all()
        if len(faq_items) > 0:
            faq_items[0].click()
            page.wait_for_timeout(500)
            capture_frame(page, count=3)

        print("5. Expanding FAQ 2...", flush=True)
        if len(faq_items) > 1:
            faq_items[1].click()
            page.wait_for_timeout(500)
            capture_frame(page, count=3)

        print("6. Scrolling back up to test Ask AI widget...", flush=True)
        page.evaluate("window.scrollTo({top: 150, behavior: 'smooth'})")
        page.wait_for_timeout(600)
        capture_frame(page, count=2)

        print("7. Clicking Ask AI toggle button...", flush=True)
        page.click("#ai-chat-toggle")
        page.wait_for_selector("#ai-chat-widget", state="visible")
        page.wait_for_timeout(500)
        capture_frame(page, count=3)

        print("8. Clicking prefilled suggestion chip (Sci-fi picks)...", flush=True)
        quick_btn = page.locator(".quick-ai-btn[data-prompt*='sci-fi']").first
        if quick_btn.is_visible():
            quick_btn.click()
        else:
            page.fill("#ai-chat-input", "Recommend me 2 great sci-fi books like Dune")
            page.click("#ai-chat-send")
        
        page.wait_for_timeout(800)
        capture_frame(page, count=2)

        print("9. Waiting for AI response...", flush=True)
        try:
            page.wait_for_selector(".chat-scroll .justify-start:nth-child(2)", timeout=15000)
            page.wait_for_timeout(1000)
            capture_frame(page, count=6)
        except Exception as e:
            print(f"Chat wait warning: {e}", flush=True)
            capture_frame(page, count=3)

        print("10. Visiting Book detail page...", flush=True)
        page.goto(f"{BASE_URL}/book/1/")
        page.wait_for_timeout(1000)
        capture_frame(page, count=4)

        browser.close()

    print(f"Compiling {len(frames)} frames into animated formats...", flush=True)
    if frames:
        # Save as animated WebP
        webp_path = os.path.join(OUTPUT_DIR, "user_flow_demo.webp")
        frames[0].save(
            webp_path,
            format="WEBP",
            save_all=True,
            append_images=frames[1:],
            duration=350,
            loop=0,
            quality=85
        )
        print(f"Saved animated WebP ({os.path.getsize(webp_path)} bytes): {webp_path}", flush=True)

        # Save as animated GIF for universal Markdown viewer compatibility
        gif_path = os.path.join(OUTPUT_DIR, "user_flow_demo.gif")
        frames[0].save(
            gif_path,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=350,
            loop=0,
            optimize=True
        )
        print(f"Saved animated GIF ({os.path.getsize(gif_path)} bytes): {gif_path}", flush=True)

        # Also copy to artifacts dir
        if os.path.exists(ARTIFACTS_DIR):
            import shutil
            shutil.copy2(webp_path, os.path.join(ARTIFACTS_DIR, "user_flow_demo.webp"))
            shutil.copy2(gif_path, os.path.join(ARTIFACTS_DIR, "user_flow_demo.gif"))
            print("Copied animations to artifacts directory.", flush=True)

if __name__ == '__main__':
    record_demo()
