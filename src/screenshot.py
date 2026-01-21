import asyncio
from playwright.async_api import async_playwright
import os
import json

async def run():
    print("Starting screenshot generation...")
    async with async_playwright() as p:
        try:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 600, 'height': 800})
            
            # Load local index.html
            abs_path = os.path.abspath("docs/index.html")
            print(f"Loading page: file://{abs_path}")
            await page.goto(f"file://{abs_path}", timeout=60000)
            
            # Wait for data.js to be loaded and UI to update
            await asyncio.sleep(5)
            
            # Take screenshot
            await page.screenshot(path="screenshot.png")
            print("Screenshot saved to screenshot.png")
            
            await browser.close()
        except Exception as e:
            print(f"Error during screenshot generation: {e}")

def export_env():
    print("Exporting data to GITHUB_ENV...")
    try:
        data_path = "docs/data.json"
        if not os.path.exists(data_path):
            print(f"Error: {data_path} not found")
            return
            
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        env_file = os.environ.get("GITHUB_ENV")
        if env_file:
            with open(env_file, "a", encoding="utf-8") as f:
                f.write(f"REPORT_DATE={data['updated_at'].split(' ')[0]}\n")
                f.write(f"UPDATED_AT={data['updated_at']}\n")
                f.write(f"RESULT_TEXT={data['result_text']}\n")
                f.write(f"JUDGMENT_LEVEL={data['level']}\n")
                f.write(f"P3D={data['p3d']}\n")
                f.write(f"P30D={data['p30d']}\n")
                f.write(f"WIND_TEXT={data['wind_text']}\n")
                f.write(f"ADVISORY_DRY={'あり' if data['is_dry'] else 'なし'}\n")
            print("Environment variables exported successfully.")
        else:
            print("GITHUB_ENV not set, printing values instead:")
            print(f"UPDATED_AT={data['updated_at']}")
            print(f"RESULT_TEXT={data['result_text']}")
    except Exception as e:
        print(f"Error exporting env: {e}")

if __name__ == "__main__":
    asyncio.run(run())
    export_env()
