import requests
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
resp = requests.get(url)
data = resp.json()

target_code = '4010000'

for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        if a.get('code') == target_code:
            print(f"Code {target_code}:")
            for w in a.get('warnings', []):
                print(f"  Code: {w.get('code')}, Status: {w.get('status')}")
