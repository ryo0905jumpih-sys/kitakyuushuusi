import requests
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
resp = requests.get(url)
data = resp.json()

target_code = '4010100'

def find_area_and_print(d, code):
    if isinstance(d, dict):
        if d.get('code') == code:
            print(f"Found Code {code}: {d}")
            return True
        for k, v in d.items():
            if find_area_and_print(v, code): return True
    elif isinstance(d, list):
        for item in d:
            if find_area_and_print(item, code): return True
    return False

find_area_and_print(data, target_code)
