import os
import time
import subprocess
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path("tests/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path("/Users/user/.gemini/antigravity/brain/df0dea92-4777-4f23-83b7-b96a85193151/screenshots")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8899
SERVER_URL = f"http://127.0.0.1:{PORT}"

def run():
    print(f"Starting server on port {PORT}...")
    proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})

            print("Navigating to home page...")
            page.goto(SERVER_URL)
            page.wait_for_timeout(1000)

            # 1. Homepage Initial
            page.screenshot(path=str(SCREENSHOTS_DIR / "01_homepage_initial.png"))
            print("1. Saved 01_homepage_initial.png")

            # 2. Case Search via CNR
            print("Running CNR search...")
            page.locator("button:has-text('Fetch eCourts Intelligence')").click()
            page.wait_for_selector("text=Punjab National Bank", timeout=15000)
            page.wait_for_timeout(800)
            page.screenshot(path=str(SCREENSHOTS_DIR / "02_case_results_cnr.png"))
            print("2. Saved 02_case_results_cnr.png")

            # 3. Hearing History Tab
            print("Clicking Hearings tab...")
            page.locator("button:has-text('Hearings')").click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOTS_DIR / "03_hearing_history.png"))
            print("3. Saved 03_hearing_history.png")

            # 4. Orders Tab & Modal
            print("Clicking Orders tab...")
            page.locator("button:has-text('Orders')").click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_orders_judgments.png"))
            print("4. Saved 04_orders_judgments.png")

            # 5. Prefill Draft Studio
            print("Clicking Draft Legal Pleading button...")
            page.locator("button:has-text('Draft Legal Pleading')").click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(SCREENSHOTS_DIR / "05_drafting_studio_prefilled.png"))
            print("5. Saved 05_drafting_studio_prefilled.png")

            # 6. Assemble Court Pleading
            print("Clicking Assemble Court Pleading...")
            page.locator("button:has-text('Assemble Court Pleading')").click()
            page.wait_for_selector("button:has-text('Download .docx')", timeout=10000)
            page.wait_for_timeout(800)
            page.screenshot(path=str(SCREENSHOTS_DIR / "06_draft_markdown.png"))
            print("6. Saved 06_draft_markdown.png")

            # 7. Draft Schema JSON Tab
            print("Clicking Schema JSON tab...")
            page.locator("button:has-text('Schema JSON')").click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(SCREENSHOTS_DIR / "07_draft_json.png"))
            print("7. Saved 07_draft_json.png")

            # 8. Architecture Tab
            print("Navigating to Architecture tab...")
            page.locator("nav button:has-text('System Architecture')").click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOTS_DIR / "08_architecture_tab.png"))
            print("8. Saved 08_architecture_tab.png")

            # 9. Case Number Hierarchy Search
            print("Navigating to Scraper -> Case Number Search...")
            page.locator("nav button:has-text('eCourts Scraper')").click()
            page.wait_for_timeout(400)
            page.locator("button:has-text('Case Number Search')").click()
            page.wait_for_timeout(400)
            page.locator("button:has-text('Search District Court Registry')").click()
            page.wait_for_selector("text=Punjab National Bank", timeout=15000)
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOTS_DIR / "09_case_number_results.png"))
            print("9. Saved 09_case_number_results.png")

            # 10. Dark Mode Showcase
            print("Toggling Dark Mode...")
            page.locator("header button[title*='Mode']").click()
            page.wait_for_timeout(600)
            page.screenshot(path=str(SCREENSHOTS_DIR / "10_dark_mode_showcase.png"))
            print("10. Saved 10_dark_mode_showcase.png")

            browser.close()
    finally:
        proc.terminate()
        proc.wait()

    # Copy screenshots to artifact directory
    for f in SCREENSHOTS_DIR.glob("*.png"):
        shutil.copy(f, ARTIFACT_DIR / f.name)
    print("All screenshots updated and copied to artifact directory.")

if __name__ == "__main__":
    run()
