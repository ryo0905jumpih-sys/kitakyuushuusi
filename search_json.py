import requests
import json

url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

# Search for any area that contains "北九州" in its name
found_areas = []
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        # The JSON doesn't seem to have 'name' in most areas?
        # Wait, let's check one
        pass

# Let's check the code 4010100 specifically in the entire JSON string
import json
json_str = json.dumps(data)
if '4010100' in json_str:
    print("Code 4010100 FOUND in JSON string")
else:
    print("Code 4010100 NOT FOUND in JSON string")

# Maybe it's 40101 ?
if '40101"' in json_str:
    print("Code 40101 FOUND")
