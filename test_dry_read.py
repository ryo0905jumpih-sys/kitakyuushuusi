import requests
import json
import datetime

# 修正後のコードでテスト
DRY_AIR_CODE = '21'
TARGET_AREA_CODE = '4010000' # 北九州地方
WARNING_JSON_URL = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"

def test_dry_air_read():
    try:
        url = f"{WARNING_JSON_URL}?_={int(datetime.datetime.now().timestamp())}"
        print(f"Fetching from: {url}")
        data = requests.get(url, timeout=10).json()
        
        is_dry = False
        found_area = False
        
        if 'areaTypes' in data:
            for at in data['areaTypes']:
                for a in at.get('areas', []):
                    if a.get('code') == TARGET_AREA_CODE:
                        found_area = True
                        print(f"Found area in areaTypes: {TARGET_AREA_CODE}")
                        warnings = a.get('warnings', [])
                        print(f"Warnings in area (areaTypes): {[w.get('code') for w in warnings]}")
                        for w in warnings:
                            code = w.get('code')
                            status = w.get('status')
                            if code == DRY_AIR_CODE:
                                print(f"MATCH: Code {code} found in areaTypes with status {status}")
                                if status in ['発表', '継続']:
                                    is_dry = True
        
        # timeSeriesのチェックを追加
        if 'timeSeries' in data and not is_dry:
            for ts in data['timeSeries']:
                for at in ts.get('areaTypes', []):
                    for a in at.get('areas', []):
                        if a.get('code') == TARGET_AREA_CODE:
                            for w in a.get('warnings', []):
                                if w.get('code') == DRY_AIR_CODE:
                                    for level in w.get('levels', []):
                                        for la in level.get('localAreas', []):
                                            vals = la.get('values', [])
                                            # "10" 以上の値があれば有効とみなす
                                            if any(v and v >= "10" for v in vals):
                                                print(f"MATCH: Code {DRY_AIR_CODE} found in timeSeries for {la.get('localAreaName')}")
                                                is_dry = True
        
        # Headlineのチェックを追加
        headline = data.get('headlineText', '')
        if not is_dry and "乾燥" in headline and "北九州" in headline:
            print("MATCH: '乾燥' and '北九州' found in headline")
            is_dry = True
        
        print(f"\nFinal Test Result - is_dry: {is_dry}")
        if not found_area:
            print(f"WARNING: Target area code {TARGET_AREA_CODE} not found in top-level JSON!")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_dry_air_read()
