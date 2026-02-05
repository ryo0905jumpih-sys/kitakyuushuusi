import requests
import json
import sys

# URL for Fukuoka Prefecture Warnings
url = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
resp = requests.get(url)
data = resp.json()

print(f"Report Datetime: {data.get('reportDatetime')}")


# Write to file with explicit UTF-8 encoding
with open('debug_output_utf8.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Saved to debug_output_utf8.json")

