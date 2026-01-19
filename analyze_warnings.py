import json

with open('warning_full_utf8.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Report Time: {data.get('reportDatetime')}")

# Try to find any area with code 06 (Strong Wind)
found_06 = []
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        for w in a.get('warnings', []):
            if w.get('code') == '06':
                found_06.append(a.get('code'))

print(f"Areas with code 06: {found_06}")

# Try to find any area with code 15 (Thunder?) that has wind properties
found_15_wind = []
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        for w in a.get('warnings', []):
            if w.get('code') == '15':
                # Just collect area codes for now
                found_15_wind.append(a.get('code'))

# Check area 4010000 (Kitakyushu Region) specifically
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        if a.get('code') == '4010000':
            print(f"Area 4010000 warnings: {a.get('warnings')}")

# Check any area with "北九州" in its ward or city name if available
# The JSON doesn't seem to have names in types 0 or 1, but maybe in timeSeries?
if 'timeSeries' in data:
    for ts in data['timeSeries']:
        for at in ts.get('areaTypes', []):
            for a in at.get('areas', []):
                # We can't easily map code to name here without another file, 
                # but let's check a few
                pass
