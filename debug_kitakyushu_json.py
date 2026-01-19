import requests
import json
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

kitakyushu_reg = '4010000'
kitakyushu_city = '4010100'

res = {}
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        if a.get('code') in [kitakyushu_reg, kitakyushu_city]:
            res[a.get('code')] = a

with open('kitakyushu_data.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
