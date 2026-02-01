import asyncio
from playwright.async_api import async_playwright
import os
import datetime
import time

# --- 設定 ---
# デモの進行速度（秒）
STEP_WAIT = 2.0 
READ_WAIT = 3.0

# 対象URL
URL_3DAY = "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_a1.php?prec_no=82&block_no=0856&year={year}&month={month}&day=&view=p1"
URL_30DAY = "https://www.data.jma.go.jp/stats/data/mdrr/tenkou/alltable/pre00.html"
URL_WARNING = "https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=4010100" # Kitakyushu Land

async def highlight_element(page, selector, text_content=None):
    """指定した要素を赤枠で囲み、少し待機する"""
    try:
        if text_content:
            # テキストを含む要素を探す (簡易的)
            # selectorが一般的なタグの場合
            await page.evaluate(f"""() => {{
                const elements = Array.from(document.querySelectorAll('{selector}'));
                const target = elements.find(el => el.innerText.includes('{text_content}'));
                if (target) {{
                    target.style.border = '5px solid red';
                    target.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}""")
        else:
            # セレクタ指定
            await page.evaluate(f"""() => {{
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.style.border = '5px solid red';
                    el.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
                    el.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
            }}""")
        
        await asyncio.sleep(READ_WAIT)
        
        # 枠を消す（必要なら）
        # await page.evaluate(...)
        
    except Exception as e:
        print(f"Highlight warning: {e}")

async def run():
    print("デモモードを開始します...")
    async with async_playwright() as p:
        # ブラウザを「見える状態(headless=False)」で起動
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        # ---------------------------------------------------------
        # 1. 過去3日間の雨量データ (八幡)
        # ---------------------------------------------------------
        print("1. 気象詳細データ（3日雨量）へ移動中...")
        now = datetime.datetime.now()
        url_formatted = URL_3DAY.format(year=now.year, month=now.month)
        
        await page.goto(url_formatted)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(STEP_WAIT)

        # 昨日の日付を探してハイライト
        # 日付は td の最初のカラムにあることが多い
        yesterday = now.day - 1
        if yesterday > 0:
            print(f"  昨日の日付({yesterday}日)のデータを探索...")
            # テーブルの行を探して、昨日の日付の行をハイライトするJS
            row_selector = f"tr.mtx"
            # 特定の日付行を見つけるのは少し複雑なので、JavaScriptで検索
            await page.evaluate(f"""() => {{
                const rows = document.querySelectorAll('tr.mtx');
                for (let row of rows) {{
                    const cells = row.querySelectorAll('td');
                    if (cells.length > 0 && cells[0].innerText.trim() == '{yesterday}') {{
                        row.style.border = '4px solid red';
                        row.style.backgroundColor = 'yellow';
                        row.scrollIntoView({{behavior: "smooth", block: "center"}});
                        break;
                    }}
                }}
            }}""")
            await asyncio.sleep(READ_WAIT)

        # ---------------------------------------------------------
        # 2. 過去30日間の雨量データ (天候・速報)
        # ---------------------------------------------------------
        print("2. 天候データ（30日雨量）へ移動中...")
        await page.goto(URL_30DAY)
        await page.wait_for_load_state("domcontentloaded") # 重いページなのでnetworkidleだと長いかも
        await asyncio.sleep(STEP_WAIT)

        print("  八幡のデータを探索...")
        # "八幡" を含む行を探す
        await page.evaluate("""() => {
            const rows = document.querySelectorAll('tr');
            for (let row of rows) {
                if (row.innerText.includes('八幡') && (row.innerText.includes('福岡') || row.innerText.includes('北九州'))) {
                    row.style.border = '4px solid red';
                    row.style.backgroundColor = 'yellow';
                    row.scrollIntoView({behavior: "smooth", block: "center"});
                    
                    // 30日値のカラム（だいたい7番目くらい）も強調
                    const cells = row.querySelectorAll('td');
                    if (cells.length > 6) {
                        cells[6].style.border = '4px solid blue';
                        cells[6].style.fontWeight = 'bold';
                        cells[6].style.fontSize = '1.5em';
                    }
                    break;
                }
            }
        }""")
        await asyncio.sleep(READ_WAIT)

        # ---------------------------------------------------------
        # 3. 注意報・警報データ
        # ---------------------------------------------------------
        print("3. 注意報ページへ移動中...")
        await page.goto(URL_WARNING)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(STEP_WAIT)

        # ページ内の北九州市を探す
        # JMAのページは複雑なDOMだが、テキスト検索で...
        # iframeや動的生成が多いので、単純なテキスト検索で妥協
        # 実際には地図をクリックしたりリストから探すが、ここでは「北九州市」の文字を探して強調
        # 少しスクロールして雰囲気を見せる
        await page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(STEP_WAIT)

        # ---------------------------------------------------------
        # 4. 最終結果画面
        # ---------------------------------------------------------
        print("4. 判定ツール画面へ移動中...")
        # ローカルファイルを開く
        local_path = os.path.abspath("docs/index.html")
        await page.goto(f"file:///{local_path}")
        await asyncio.sleep(STEP_WAIT)

        # 結果を強調
        await highlight_element(page, ".result-card")
        
        print("デモ終了。5秒後に閉じます。")
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
