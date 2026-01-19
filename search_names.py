import requests
import json
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

wards = ["小倉", "若松", "戸畑", "八幡", "門司"]
json_str = json.dumps(data, ensure_ascii=False)

for w in wards:
    if w in json_str:
        print(f"Ward '{w}' FOUND in JSON")
    else:
        print(f"Ward '{w}' NOT FOUND in JSON")

# Search for "北九州"
if "北九州" in json_str:
    print("北九州 FOUND in JSON")
