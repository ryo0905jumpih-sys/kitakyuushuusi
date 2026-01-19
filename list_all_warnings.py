import requests
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
data = requests.get(url).json()

all_warnings = []
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        for w in a.get('warnings', []):
            all_warnings.append({
                'area_code': a.get('code'),
                'warning_code': w.get('code'),
                'status': w.get('status')
            })

with open('all_warnings_list.json', 'w', encoding='utf-8') as f:
    import json
    json.dump(all_warnings, f, ensure_ascii=False, indent=2)

codes_found = set([w['warning_code'] for w in all_warnings])
print(f"Unique warning codes found: {codes_found}")
