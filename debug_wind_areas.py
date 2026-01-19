import requests
import json

url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

kitakyushu_reg = '4010000'
details = []

if 'timeSeries' in data:
    for ts in data['timeSeries']:
        for at in ts.get('areaTypes', []):
            for a in at.get('areas', []):
                if a.get('code') == kitakyushu_reg:
                    for w in a.get('warnings', []):
                        # Strong wind is usually 15 in this summary JSON
                        if w.get('code') == '15':
                            for level in w.get('levels', []):
                                for la in level.get('localAreas', []):
                                    name = la.get('localAreaName', '不明')
                                    # If any value is >= 10, it's an active advisory level
                                    # JMA uses "10" for advisory, "30" for warning, etc.
                                    if any(v >= "10" for v in la.get('values', [])):
                                        details.append(name)

unique_details = sorted(list(set(details)))
print(f"Wind Advisory active areas for Kitakyushu: {unique_details}")
