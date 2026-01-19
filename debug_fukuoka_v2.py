import requests
from bs4 import BeautifulSoup
url = 'https://www.data.jma.go.jp/stats/data/mdrr/tenkou/alltable/pre00.html'
resp = requests.get(url, timeout=15)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.text, 'html.parser')
rows = soup.find_all('tr')
with open('fukuoka_debug_utf8.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        cols = r.find_all(['th', 'td'])
        txts = [c.get_text(strip=True) for c in cols]
        if '福岡' in "".join(txts):
            f.write(f"Row: {txts}\n")
