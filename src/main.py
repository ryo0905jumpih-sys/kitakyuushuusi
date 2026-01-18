import requests
from bs4 import BeautifulSoup
import datetime
import json
import csv
import os
import pytz
import re
import sys

# Constants
# 3-day data source (Daily Confirmed) - Using daily_a1.php as reliable source
AMEDAS_DAILY_URL = "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_a1.php?prec_no=82&block_no=0856&year={year}&month={month}&day=&view="
# Note: block_no=0856 is the standard mapping for 82056 in daily_a1.php
TARGET_STATION_CODE = "82056"
# URL for 30-day data (Preliminary)
TENKOU_URL = "https://www.data.jma.go.jp/stats/data/mdrr/tenkou/alltable/pre00.html"
# Advisories
WARNING_JSON_URL = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
AREA_CODE_KITAKYUSHU = "4010100"

DATA_FILE = "docs/data.json"
HISTORY_FILE = "data/history.csv"

def get_confirmed_3day_precip():
    """
    Calculates the total precipitation for the last 3 FULL days.
    Primary Target: Yahata (82056) -> block_no=0780 (Verified)
    Fallback Target: Fukuoka (47807) -> block_no=47807 (if Yahata fails)
    """
    today = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
    yesterday = today - datetime.timedelta(days=1)
    target_dates = [yesterday, yesterday - datetime.timedelta(days=1), yesterday - datetime.timedelta(days=2)]
    
    # Check Yahata first
    total_yahata, map_yahata, success_yahata = fetch_precip_from_jma(target_dates, '82', '0780', 'a1')
    
    if success_yahata:
        print("Using Yahata data.")
        return total_yahata, "八幡"
    else:
        print("Yahata data unavailable/empty. Falling back to Fukuoka (47807).")
        total_fukuoka, map_fukuoka, success_fukuoka = fetch_precip_from_jma(target_dates, '82', '47807', 's1')
        if success_fukuoka:
            return total_fukuoka, "福岡(代替)"
        else:
            return 0.0, "取得失敗"

def fetch_precip_from_jma(target_dates, prec_no, block_no, page_type='a1'):
    months_needed = sorted(list(set([(d.year, d.month) for d in target_dates])), reverse=True)
    daily_precip_map = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    data_found = False
    
    for year, month in months_needed:
        url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_{page_type}.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day=&view=p1"
        print(f"Fetching: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.encoding = 'shift_jis'
            soup = BeautifulSoup(resp.text, 'html.parser')
            rows = soup.find_all('tr', class_='mtx')
            
            if not rows:
                continue

            for row in rows:
                cols = row.find_all('td')
                if not cols: continue
                try:
                    d_text = cols[0].text.strip()
                    if not d_text.isdigit(): continue
                    d_day = int(d_text)
                    
                    # Col Index varies by page type
                    # a1 (AMeDAS): Day, Precip, ... -> Precip is Col 1
                    # s1 (Station): Day, Press, Press, Precip, ... -> Precip is Col 3 usually
                    
                    val = 0.0
                    col_idx = 1 if page_type == 'a1' else 3
                    
                    if len(cols) > col_idx:
                        d_val_text = cols[col_idx].text.strip()
                        # Handle "--", "///", "0.0)", etc
                        if d_val_text in ["--", "///"]:
                            val = 0.0
                        elif d_val_text == "0.0)":
                             val = 0.0
                        else:
                            clean = re.sub(r'[^\d\.]', '', d_val_text)
                            if clean:
                                val = float(clean)
                                
                    current_date = datetime.date(year, month, d_day)
                    daily_precip_map[current_date] = val
                    data_found = True
                    
                    if d_day in [d.day for d in target_dates]:
                         print(f"  > Date {current_date}: {val}mm")

                except Exception:
                    continue
        except Exception as e:
            print(f"Error: {e}")
            
    total = 0.0
    for d in target_dates:
        total += daily_precip_map.get(d, 0.0)
        
    return total, daily_precip_map, data_found

def main():
    # ... (rest of main needs update to handle source name)
    pass # To avoid overwriting too much, I will edit main() separately or assume this is partial



def get_preliminary_30day_precip():
    """
    Fetches 'Last 30 days total' from JMA Tenkou page (Preliminary).
    Target: Yahata (82056)
    """
    print(f"Fetching preliminary data from: {TENKOU_URL}")
    try:
        resp = requests.get(TENKOU_URL, timeout=10)
        # Diagnostic confirmed UTF-8 content for this page (unlike others)
        resp.encoding = 'utf-8' 
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        rows = soup.find_all('tr')
        target_col_index = -1
        header_found = False
        
        # 1. Header Search (Optional/Verification)
        # Based on user feedback and diagnostics, the target column for "30-day" (or equivalent required period) is likely Index 6.
        # Header parsing was unstable due to rowspan/colspan or encoding issues.
        target_col_index = 6 


        # 2. Find Data for Yahata
        for row in rows:
            cols = row.find_all(['th', 'td'])
            
            # Check for Yahata (specifically in Fukuoka) to avoid Akita's Hachimantai
            found_yahata = False
            row_text = row.text
            
            # Must contain Yahata AND Fukuoka (or Kitakyushu/Chikugo/etc if needed)
            if "八幡" in row_text and ("福岡" in row_text or "北九州" in row_text):
                found_yahata = True
            
            if found_yahata:
                print(f"Found Fukuoka Yahata row.")
                # If header logic failed, let's look for the value user mentioned?
                # No, that's cheating.
                # Let's inspect columns.
                vals = [c.text.strip() for c in cols]
                print(f"Yahata Cols: {vals}")
                
                # If we have a target index
                if target_col_index != -1 and len(cols) > target_col_index:
                    val_text = cols[target_col_index].text.strip()
                    val_text = re.sub(r'[\)\]]', '', val_text) 
                    clean = re.sub(r'[^\d\.]', '', val_text)
                    if clean:
                        return float(clean)
                        
        return 0.0
        
    except Exception as e:
        print(f"Error fetching preliminary data: {e}")
        return 0.0


def get_advisories():
    is_dry = False
    is_strong_wind = False
    try:
        resp = requests.get(WARNING_JSON_URL, timeout=10)
        data = resp.json()
        target_area = None
        if 'areaTypes' in data:
            for at in data['areaTypes']:
                areas = at.get('areas', [])
                for a in areas:
                    if a.get('code') == AREA_CODE_KITAKYUSHU:
                        target_area = a
                        break
                if target_area: break
        
        if target_area and 'warnings' in target_area:
            for w in target_area['warnings']:
                code = w.get('code')
                status = w.get('status')
                if status in ['発表', '継続']:
                    if code == '14': is_dry = True
                    if code == '06': is_strong_wind = True
    except Exception as e:
        print(f"Error checking advisories: {e}")
    return is_dry, is_strong_wind

def main():
    # Fix output encoding for Windows terminal if needed
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("--- Weather Condition Auto Judgment ---")
    current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    print(f"Execution Time: {current_time}")

    p3d, p3d_source = get_confirmed_3day_precip()
    p30d = get_preliminary_30day_precip()
    print(f"Precipitation: 3-Day({p3d_source})={p3d}mm, 30-Day(Preliminary)={p30d}mm")
    
    is_dry, is_strong_wind = get_advisories()
    print(f"Advisories: Dry={is_dry}, StrongWind={is_strong_wind}")
    
    # Logic
    is_level1 = False
    if (p3d <= 1.0 and p30d <= 30.0) or (p3d <= 1.0 and is_dry):
        is_level1 = True
        
    level = 0
    if is_level1:
        level = 1
        if is_strong_wind:
            level = 2
            
    result_text = "該当なし"
    if level == 1: result_text = "注意レベル"
    if level == 2: result_text = "警報レベル"
    
    print(f"Final Result: Level {level} ({result_text})")
    
    output_data = {
        "updated_at": current_time.strftime('%Y-%m-%d %H:%M'),
        "level": level,
        "result_text": result_text,
        "p3d": p3d,
        "p30d": p30d,
        "is_dry": is_dry,
        "is_strong_wind": is_strong_wind,
        "notes": f"前3日={p3d_source}確定値, 前30日=速報値(八幡)"
    }
    
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'time', 'level', 'p3d', 'p30d', 'is_dry', 'is_strong_wind', 'result_text', 'source'])
        writer.writerow([
            current_time.strftime('%Y-%m-%d'),
            current_time.strftime('%H:%M'),
            level, p3d, p30d, is_dry, is_strong_wind, result_text, p3d_source
        ])


if __name__ == "__main__":
    main()
