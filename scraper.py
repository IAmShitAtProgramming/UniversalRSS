import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urlparse

def get_news():
    # Tu lista Twoich URL (skrócona dla przykładu)
    urls = ["https://www.gov.pl/web/premier/wplip-rm", "https://legislacja.gov.pl/"]
    results = []
    
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Szukamy linków (uproszczony selektor dla gov.pl)
            links = soup.select('.art-prev > a') or soup.select('h2 a')
            
            for link in links[:5]: # Tylko 5 najnowszych z każdego źródła
                title = link.text.strip()
                href = link['href']
                if href.startswith('/'):
                    href = f"https://{urlparse(url).netloc}{href}"
                
                results.append({
                    "title": title,
                    "url": href,
                    "domain": urlparse(url).netloc,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
        except:
            continue
    return results

# Ładowanie starych danych i łączenie z nowymi (bez duplikatów)
all_news = get_news()
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)