import requests
import json

url = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
data = requests.get(url).json()

print("Area codes and names in Fukuoka Prefecture (400000):")
if 'timeSeries' in data:
    for ts in data['timeSeries']:
        for at in ts.get('areaTypes', []):
            for a in at.get('areas', []):
                print(f"Code: {a.get('code')}, Name: {a.get('name')}")
                if a.get('code') == '4010000':
                     # Print local areas if available in warnings or just debug structure
                     # In timeSeries, structure can be diff.
                     pass

