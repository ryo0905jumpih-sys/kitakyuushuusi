import asyncio
from playwright.async_api import async_playwright
import os
import json

async def run():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 600, 'height': 800})
        
        # Load local index.html
        # Note: In GitHub Actions, the current working directory is the repo root.
        abs_path = os.path.abspath("docs/index.html")
        await page.goto(f"file://{abs_path}")
        
        # Wait for data.js to be loaded and UI to update
        # The updateUI function is called on DOMContentLoaded or after fetch.
        # Adding a small sleep to ensure rendering is complete.
        await asyncio.sleep(3)
        
        # Take screenshot of the container or full page
        await page.screenshot(path="screenshot.png")
        
        await browser.close()

def export_env():
    # Extract data for GitHub Actions ENV
    try:
        with open("docs/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        with open(os.environ.get("GITHUB_ENV", "dev_env.txt"), "a", encoding="utf-8") as f:
            f.write(f"REPORT_DATE={data['updated_at'].split(' ')[0]}\n")
            f.write(f"UPDATED_AT={data['updated_at']}\n")
            f.write(f"RESULT_TEXT={data['result_text']}\n")
            f.write(f"JUDGMENT_LEVEL={data['level']}\n")
    except Exception as e:
        print(f"Error exporting env: {e}")

if __name__ == "__main__":
    # Ensure Playwright is installed: playwright install chromium
    asyncio.run(run())
    export_env()
