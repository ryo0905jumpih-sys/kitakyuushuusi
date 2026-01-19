import requests
url = 'https://www.jma.go.jp/bosai/warning/data/warning/400000.json'
resp = requests.get(url)
data = resp.json()

codes = []
def collect_codes(d):
    if isinstance(d, dict):
        if 'code' in d: codes.append(d['code'])
        for v in d.values(): collect_codes(v)
    elif isinstance(d, list):
        for item in d: collect_codes(item)

collect_codes(data)
print(sorted(list(set(codes))))
