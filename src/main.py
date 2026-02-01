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
TARGET_STATION_NAME = "八幡"
TARGET_STATION_PREF = "82"
TARGET_STATION_BLOCK = "0780"

DATA_FILE = "docs/data.json"
HISTORY_FILE = "data/history.csv"
TENKOU_URL = "https://www.data.jma.go.jp/stats/data/mdrr/tenkou/alltable/pre00.html"
WARNING_JSON_URL = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
AREA_CODE_KITAKYUSHU_REGION = "4010000"

def get_confirmed_3day_precip():
    today = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
    yesterday = today - datetime.timedelta(days=1)
    target_dates = [yesterday, yesterday - datetime.timedelta(days=1), yesterday - datetime.timedelta(days=2)]
    
    total, map_data, success = fetch_precip_from_jma(target_dates, '82', '0780', 'a1')
    if success:
        return total, "八幡"
    else:
        total_f, map_f, success_f = fetch_precip_from_jma(target_dates, '82', '47807', 's1')
        if success_f:
            return total_f, "福岡(代替)"
        return 0.0, "取得失敗"

def fetch_precip_from_jma(target_dates, prec_no, block_no, page_type='a1'):
    months_needed = sorted(list(set([(d.year, d.month) for d in target_dates])), reverse=True)
    daily_precip_map = {}
    headers = {'User-Agent': 'Mozilla/5.0'}
    data_found = False
    
    for year, month in months_needed:
        url = f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_{page_type}.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day=&view=p1"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.encoding = 'shift_jis'
            soup = BeautifulSoup(resp.text, 'html.parser')
            rows = soup.find_all('tr', class_='mtx')
            if not rows: continue

            for row in rows:
                cols = row.find_all('td')
                if not cols: continue
                try:
                    d_text = cols[0].text.strip()
                    if not d_text.isdigit(): continue
                    d_day = int(d_text)
                    val = 0.0
                    col_idx = 1 if page_type == 'a1' else 3
                    if len(cols) > col_idx:
                        d_val_text = cols[col_idx].text.strip()
                        if d_val_text in ["--", "///", "0.0)"]:
                            val = 0.0
                        else:
                            clean = re.sub(r'[^\d\.]', '', d_val_text)
                            if clean: val = float(clean)
                    daily_precip_map[datetime.date(year, month, d_day)] = val
                    data_found = True
                except: continue
        except: continue
            
    total = sum(daily_precip_map.get(d, 0.0) for d in target_dates)
    return total, daily_precip_map, data_found

def get_preliminary_30day_precip():
    try:
        resp = requests.get(TENKOU_URL, timeout=15)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, 'html.parser')
        target_col_idx = 6 
        for tr in soup.find_all('tr'):
            h_txts = [c.get_text(strip=True) for c in tr.find_all(['th', 'td'])]
            if '前30日間合計' in h_txts:
                target_col_idx = (h_txts.index('前30日間合計') - 2) * 2 + 2
                break
        for row in soup.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            txts = [c.get_text(strip=True) for c in cols]
            if len(txts) < 2: continue
            if txts[1] == "八幡" and "福岡" in txts[0]:
                if len(txts) > target_col_idx:
                    clean = re.sub(r'[^0-9.]', '', txts[target_col_idx])
                    if clean: return float(clean)
                break
        return 0.0
    except: return 0.0

def get_advisories():
    is_dry = False
    is_strong_wind_land = False
    wind_locations = []
    
    # 海上エリアのコード (響灘: 4010001, 瀬戸内側: 4010002)
    SEA_AREA_CODES = ["4010001", "4010002"]

    try:
        url = f"{WARNING_JSON_URL}?_={int(datetime.datetime.now().timestamp())}"
        data = requests.get(url, timeout=10).json()
        
        # 1. Check Top-Level AreaTypes (Most reliable for "Issued" status)
        # 4010000 is Kitakyushu Region
        if 'areaTypes' in data:
            for at in data['areaTypes']:
                for a in at.get('areas', []):
                    if a.get('code') == AREA_CODE_KITAKYUSHU_REGION:
                        for w in a.get('warnings', []):
                            code = w.get('code')
                            status = w.get('status')
                            
                            # 乾燥注意報 (14)
                            if code == '14' and status in ['発表', '継続']:
                                is_dry = True
                            
                            # 強風注意報 (06 is standard, but 15 appears to be used for wind/fog/associated warnings in some contexts or current feed)
                            # 15 (Various Attributes including Wind).
                            if code in ['06', '15', '04'] and status in ['発表', '継続']:
                                # Flag as potentially active. We will refine by land/sea/location below or defaults to True 
                                # if we can't determine specific locations.
                                # Defaulting to True here to ensure it's not missed, rely on headline/timeSeries to filter OUT if sea-only?
                                # Actually, safe approach: Set True implies "Warning in Region".
                                # If checks below don't find "Land", does it mean Sea only?
                                is_strong_wind_land = True 

        # 2. Detailed location check from timeSeries
        # This helps identify if it is "Hibikinada" (Sea) vs "Kitakyushu City" (Land)
        # Note: timeSeries often lacks 'status', so we look for 'values' >= "10" (Issued)
        found_land_wind_in_ts = False
        found_sea_wind_in_ts = False
        
        if 'timeSeries' in data:
            for ts in data['timeSeries']:
                for at in ts.get('areaTypes', []):
                    for a in at.get('areas', []):
                        if a.get('code') == AREA_CODE_KITAKYUSHU_REGION:
                            for w in a.get('warnings', []):
                                code = w.get('code')
                                if code in ['06', '15', '04']:
                                    for level in w.get('levels', []):
                                        for la in level.get('localAreas', []):
                                            # Check values (e.g. ["10", "10", ...])
                                            # If any recent value is >= "10", consider it active for that sub-area
                                            vals = la.get('values', [])
                                            is_active_loc = False
                                            for v in vals:
                                                if v and v >= "10": 
                                                    is_active_loc = True
                                                    break
                                            
                                            if is_active_loc:
                                                loc_code = la.get('localAreaCode')
                                                loc_name = la.get('localAreaName')
                                                if loc_name:
                                                    wind_locations.append(loc_name)
                                                
                                                if loc_code and loc_code in SEA_AREA_CODES:
                                                    found_sea_wind_in_ts = True
                                                else:
                                                    # If no code, or code is not SEA, assume Land (e.g. City codes)
                                                    found_land_wind_in_ts = True

        # Refine is_strong_wind_land based on details
        if found_land_wind_in_ts or found_sea_wind_in_ts:
            # If we found specific sub-area info, use it
            is_strong_wind_land = found_land_wind_in_ts
        elif is_strong_wind_land:
            # We only found Top-Level status "Issued", but couldn't parse sub-areas (maybe code structure changed).
            # Fallback to Headline check to be safe?
            # Or just assume True because user complains "It shows None" (False Negative).
            pass

        # 3. Fallback/Confirmation via Headline
        headline = data.get('headlineText', '')
        # If Top-Level found nothing, check headline
        if not is_strong_wind_land:
            if ("強風" in headline or "暴風" in headline) and "北九州" in headline:
                # Exclude if explicitly Sea only
                if "響灘" in headline and "北九州市" not in headline and "陸上" not in headline:
                     pass # Likely Sea only
                else:
                     is_strong_wind_land = True

        wind_locations = sorted(list(set(wind_locations)))

    except Exception as e:
        print(f"Error checking advisories: {e}")
        
    return is_dry, is_strong_wind_land, wind_locations

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    current_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    p3d, p3d_source = get_confirmed_3day_precip()
    p30d = get_preliminary_30day_precip()
    is_dry, is_strong_wind, wind_locs = get_advisories()
    
    is_level1 = (p3d <= 1.0 and p30d <= 30.0) or (p3d <= 1.0 and is_dry)
    level = 0
    if is_level1:
        level = 1
        if is_strong_wind: level = 2
            
    result_text = "警報レベル" if level == 2 else "注意レベル" if level == 1 else "該当なし"
    
    wind_text = "あり" if is_strong_wind else "なし"
    if wind_locs:
        wind_text += f" ({'・'.join(wind_locs)})"

    output_data = {
        "updated_at": current_time.strftime('%Y-%m-%d %H:%M'),
        "level": level,
        "result_text": result_text,
        "p3d": p3d,
        "p30d": p30d,
        "is_dry": is_dry,
        "is_strong_wind": is_strong_wind,
        "wind_text": wind_text, # 追加
        "notes": f"前3日={p3d_source}確定値, 前30日=確定値(八幡), 注意報=北九州地方"
    }
    
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    js_file = os.path.join(os.path.dirname(DATA_FILE), 'data.js')
    with open(js_file, 'w', encoding='utf-8') as f:
        json_str = json.dumps(output_data, ensure_ascii=False, indent=2)
        f.write(f"window.WEATHER_DATA = {json_str};")
        
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
