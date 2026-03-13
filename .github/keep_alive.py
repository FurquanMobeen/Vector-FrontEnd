"""
Keep-Alive Script for Streamlit App
This script uses Playwright to visit the Streamlit app and keep it awake.
"""
import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def keep_alive(app_url: str, timeout: int = 60000):
    """
    Visit a Streamlit app to keep it alive.

    Args:
        app_url: The URL of the Streamlit app
        timeout: Maximum time to wait for page load (in milliseconds)
    """
    print(f"🚀 Attempting to wake up Streamlit app at: {app_url}")

    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()

            # Navigate to the app
            print("📡 Navigating to app...")
            page.goto(app_url, wait_until="networkidle", timeout=timeout)

            # Wait for Streamlit to initialize (look for common Streamlit elements)
            print("⏳ Waiting for Streamlit to load...")
            try:
                # Wait for the Streamlit app container to appear
                page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
                print("✅ Streamlit app loaded successfully!")
            except PlaywrightTimeoutError:
                print("⚠️  Streamlit container not found, but page loaded. App might be awake.")

            # Take a screenshot for verification (optional, useful for debugging)
            screenshot_path = "streamlit_app_screenshot.png"
            page.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved to {screenshot_path}")

            # Keep the page open for a few seconds to ensure WebSocket connection
            print("🔌 Maintaining connection for 10 seconds...")
            page.wait_for_timeout(10000)

            # Close browser
            browser.close()
            print("✅ Keep-alive completed successfully!")
            return True

    except PlaywrightTimeoutError as e:
        print(f"❌ Timeout error: {e}")
        print("⚠️  The app took too long to respond. It might be sleeping or having issues.")
        return False
    except Exception as e:
        print(f"❌ Error keeping app alive: {e}")
        return False


if __name__ == "__main__":
    # Get the app URL from environment variable or use default
    # TODO: Replace this with your actual Streamlit app URL
    app_url = os.getenv(
        "STREAMLIT_APP_URL",
        "https://your-app-name.streamlit.app"  # ⚠️ CHANGE THIS to your actual URL
    )

    if "your-app-name" in app_url:
        print("⚠️  WARNING: Using placeholder URL. Please set STREAMLIT_APP_URL environment variable")
        print("   or update the default URL in this script.")
        sys.exit(1)

    success = keep_alive(app_url)
    sys.exit(0 if success else 1)
