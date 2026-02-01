import requests
import json

url = "https://www.jma.go.jp/bosai/warning/data/warning/400000.json"
resp = requests.get(url)
data = resp.json()

print(f"Headline: {data.get('headlineText')}")
