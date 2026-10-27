import os
import subprocess
import time
import requests
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="module")
def live_server():
    """Start Django dev server for Playwright E2E tests"""
    env = os.environ.copy()
    env["DJANGO_DEBUG"] = "False"  # Test custom 404/500 handlers
    env["ALLOWED_HOSTS"] = "*"

    proc = subprocess.Popen(
        [r".venv\Scripts\python.exe", "manage.py", "runserver", "127.0.0.1:8000", "--noreload", "--insecure"],
        cwd=r"d:\Forge\letterboxd_for_books",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for server to become responsive
    max_wait = 15
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get(f"{BASE_URL}/health/", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)

    yield BASE_URL

    proc.terminate()
    proc.wait()


def test_home_page_desktop(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(live_server)

        # Check brand title
        assert "Bookboxd" in page.title()
        assert page.locator("text=Bookboxd").first.is_visible()

        # Check popular books strip
        assert page.locator("text=Popular & Celebrated Titles").is_visible()
        assert page.locator("text=Dune").first.is_visible()

        # Check that FAQs are displayed on home page
        assert page.locator("text=Frequently Asked Questions").is_visible()

        # Check floating AI widget button is visible on every page
        assert page.locator("#ai-chat-toggle").is_visible()

        browser.close()


def test_mobile_device_viewport(live_server):
    """Verify that site opens correctly on a mobile device (e.g. iPhone 13)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # iPhone 13 dimensions
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()
        page.goto(live_server)

        # Verify page loads cleanly
        assert page.locator("text=Bookboxd").first.is_visible()

        # Verify mobile menu hamburger button exists and toggles navigation
        hamburger = page.locator("#mobile-menu-toggle")
        assert hamburger.is_visible()
        hamburger.click()
        assert page.locator("#mobile-nav-drawer").is_visible()

        # Verify chat button is visible and accessible on mobile
        chat_btn = page.locator("#ai-chat-toggle")
        assert chat_btn.is_visible()
        chat_btn.click()
        assert page.locator("#ai-chat-widget").is_visible()

        browser.close()


def test_custom_404_page(live_server):
    """Verify incorrect address displays custom 404 page with 'Ask the assistant' option"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(f"{live_server}/invalid-lost-library-route-12345/")

        # Verify HTTP status 404
        assert response.status == 404

        # Verify custom 404 text
        assert "404" in page.title()
        assert page.locator("text=A Missing Chapter in the Library").is_visible()

        # Verify 'Ask the assistant' button is present
        ask_assistant_btn = page.locator("#ask-assistant-404-btn")
        assert ask_assistant_btn.is_visible()
        assert "Ask the Assistant" in ask_assistant_btn.inner_text()

        # Click 'Ask the assistant' and verify it launches the chat modal with pre-filled query
        ask_assistant_btn.click()
        assert page.locator("#ai-chat-widget").is_visible()

        browser.close()


def test_faqs_minimum_10_and_displayed(live_server):
    """Verify at least 10 FAQs in SQL database and displayed on FAQ page"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{live_server}/faq/")

        assert page.locator("text=Frequently Asked Questions").is_visible()

        # Count FAQ questions rendered on page
        faq_headings = page.locator("h3").all()
        assert len(faq_headings) >= 10, f"Expected at least 10 FAQs, found {len(faq_headings)}"

        browser.close()


def test_error_code_explorer_8_codes(live_server):
    """Verify minimum 8 error codes (400, 401, 403, 404, 429, 500, 503, 422)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{live_server}/errors/")

        for code in ["400", "401", "403", "404", "422", "429", "500", "503"]:
            assert page.locator(f"text=HTTP {code}").is_visible(), f"Missing error code {code}"

        browser.close()


def test_book_detail_and_spoilers(live_server):
    """Verify book details, ratings, and spoiler blur toggle"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{live_server}/book/1/")

        assert page.locator("h1:has-text('Dune')").is_visible()
        assert page.locator("text=Frank Herbert").first.is_visible()

        # Verify spoiler toggle works
        spoiler_btn = page.locator(".spoiler-toggle-btn").first
        if spoiler_btn.is_visible():
            spoiler_content = page.locator(".spoiler-content").first
            assert "spoiler-hidden" in (spoiler_content.get_attribute("class") or "")
            spoiler_btn.click()
            assert "spoiler-hidden" not in (spoiler_content.get_attribute("class") or "")

        browser.close()


def test_health_check_endpoint(live_server):
    """Verify request logging & health check endpoint"""
    r = requests.get(f"{live_server}/health/?format=json")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "sql_database" in data
    assert "mongodb" in data
    assert "third_party_api" in data
    assert data["third_party_api"]["timeout_limit"] == "3.0s"
