import requests
import json
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

with open('warning_full_utf8.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
