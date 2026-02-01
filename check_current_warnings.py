import requests
import json

url = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
resp = requests.get(url)
data = resp.json()

print(f"Report Datetime: {data.get('reportDatetime')}")

# Find areas and their warnings
areas_found = []
if 'timeSeries' in data:
    for ts in data['timeSeries']:
        for at in ts.get('areaTypes', []):
            for a in at.get('areas', []):
                code = a.get('code')
                name = a.get('name')
                warnings = a.get('warnings', [])
                active_warnings = []
                for w in warnings:
                    stat = w.get('status')
                    if stat in ['発表', '継続']:
                        active_warnings.append(w.get('code'))
                
                if active_warnings:
                    areas_found.append({"code": code, "name": name, "warnings": active_warnings})

print("Areas with active warnings:")
for area in areas_found:
    print(area)
