import requests
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
resp = requests.get(url)
data = resp.json()

print(f"Data keys: {data.keys()}")
if 'areaTypes' in data:
    for at in data['areaTypes']:
        print(f"Type: {at.get('type')}, area count: {len(at.get('areas', []))}")
        for a in at.get('areas', [])[:10]:
            print(f"  Code: {a.get('code')}, Name: {a.get('name')}")
else:
    print("No areaTypes")
