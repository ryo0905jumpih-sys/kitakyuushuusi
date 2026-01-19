import requests
import json

kitakyushu_code = '4010100'
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'

print(f"Fetching: {url}")
resp = requests.get(url)
data = resp.json()

target_area = None
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        if a.get('code') == kitakyushu_code:
            target_area = a
            break
    if target_area: break

if target_area:
    print(f"Area: {target_area.get('name')}")
    warnings = target_area.get('warnings', [])
    for w in warnings:
        # code 06 is strong wind
        # status '発表' or '継続'
        print(f"Code: {w.get('code')}, Status: {w.get('status')}")
else:
    print("Kitakyushu not found")
