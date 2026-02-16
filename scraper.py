import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin

# Konfiguracja
URLS_FILE = 'urls.txt'
DATA_FILE = 'data.json'
DATA_JS_FILE = 'data.js'
MAX_NEWS_PER_SITE = 5  # Limit, aby plik nie był zbyt ciężki

# Selektory CSS dla różnych grup stron
RULES = {
    "gov.pl": ".art-prev > a",
    "sejm.gov.pl": "tr td a",
    "portaloswiatowy.pl": ".news-title > a",
    "dziennikustaw.gov.pl": "tr td.title a",
    "default": "h2 a, .title a, .news-item a, article a"
}

def get_selector(url):
    for key in sorted(RULES.keys(), key=len, reverse=True):
        if key in url:
            return RULES[key]
    return RULES["default"]

def scrape():
    # 1. Wczytaj listy URL
    try:
        with open(URLS_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {URLS_FILE}")
        return

    all_results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 2. Skanuj strony
    for url in urls:
        print(f"Skanowanie: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            selector = get_selector(url)
            elements = soup.select(selector)
            
            site_news_count = 0
            for el in elements:
                if site_news_count >= MAX_NEWS_PER_SITE:
                    break
                    
                title = el.get_text().strip()
                href = el.get('href')
                
                if not title or not href or len(title) < 5:
                    continue

                # Budowanie pełnego linku
                href = urljoin(url, href)

                all_results.append({
                    "title": title,
                    "url": href,
                    "domain": urlparse(url).netloc.replace('www.', ''),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                site_news_count += 1
                
        except Exception as e:
            print(f"Pominięto {url} z powodu błędu: {e}")

    # 3. Zapisz do data.json (nadpisuje nowymi danymi)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 4. Zapisz do data.js (dla index.html otwieranego lokalnie)
    with open(DATA_JS_FILE, 'w', encoding='utf-8') as f:
        json_str = json.dumps(all_results, ensure_ascii=False)
        f.write(f"const newsData = {json_str};")

    print(f"Zakończono! Znaleziono łącznie {len(all_results)} wpisów.")

if __name__ == "__main__":
    scrape()