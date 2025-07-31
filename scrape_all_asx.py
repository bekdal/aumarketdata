
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

HEADERS = { "User-Agent": "Mozilla/5.0" }

def get_asx_tickers():
    url = "https://www.marketindex.com.au/asx-listed-companies"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"[ERROR] Failed to load ASX list. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if not table:
        print("[ERROR] Could not find <table> in page — page structure may have changed or request was blocked.")
        return []

    rows = table.find("tbody").find_all("tr")
    
    companies = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            code = cols[0].text.strip()
            name = cols[1].text.strip()
            companies.append({"ticker": code, "company": name})
    
    return companies


def get_price_and_market_cap_yahoo(ticker):
    url = f"https://au.finance.yahoo.com/quote/{ticker}.AX"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        
        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
        price = float(price_tag.text.replace(",", "")) if price_tag else None

        market_cap = None
        rows = soup.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2 and "Market Cap" in cells[0].text:
                market_cap = cells[1].text.strip()
                break

        return price, market_cap
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None, None

def main():
    companies = get_asx_tickers()
    print(f"Found {len(companies)} ASX listings...")

    results = []
    for company in companies:
        ticker = company["ticker"]
        price, market_cap = get_price_and_market_cap_yahoo(ticker)
        if price is not None:
            results.append({
                "ticker": ticker,
                "company": company["company"],
                "close": price,
                "market_cap": market_cap
            })
        time.sleep(1)

    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"data/{today}.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("data/latest.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"[DONE] Saved {len(results)} entries to data/{today}.json")

if __name__ == "__main__":
    main()
