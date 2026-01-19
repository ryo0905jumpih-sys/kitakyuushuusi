import json
with open('warning_debug.json', encoding='utf-8') as f:
    data = json.load(f)

kitakyushu_code = '4010100'
target_area = None
for at in data.get('areaTypes', []):
    for a in at.get('areas', []):
        if a.get('code') == kitakyushu_code:
            target_area = a
            break
    if target_area: break

if target_area:
    print(f"Area: {target_area.get('name')}")
    warnings = target_area.get('warnings', [])
    for w in warnings:
        # code 06 is strong wind
        # status '発表' or '継続'
        print(f"Code: {w.get('code')}, Name: {w.get('name', 'N/A')}, Status: {w.get('status')}")
else:
    print("Kitakyushu not found")
