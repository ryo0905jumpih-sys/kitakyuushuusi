import requests

url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
resp = requests.get(url)
data = resp.json()

wind_advisory_code = '06'
count = 0

for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        for w in a.get('warnings', []):
            if w.get('code') == wind_advisory_code and w.get('status') in ['発表', '継続']:
                print(f"Active Wind Advisory in Area Code: {a.get('code')}")
                count += 1

print(f"Total active wind advisories: {count}")
