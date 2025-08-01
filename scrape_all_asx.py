
import requests
from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime
import os
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_asx_tickers():
    with open("asx_tickers.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [
            {
                "ticker": row["ASX code"].strip(),
                "company": row["Company name"].strip(),
                "industry": row["GICs industry group"].strip()
            }
            for row in reader
        ]

def get_price_and_market_cap_yahoo(ticker):
    url = f"https://au.finance.yahoo.com/quote/{ticker}.AX"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract price from qsp-price span
        price_tag = soup.find("span", {"data-testid": "qsp-price"})
        price = float(price_tag.text.replace(",", "")) if price_tag else None

        # Extract market cap
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
    print(f"Loaded {len(companies)} companies from CSV...")

    os.makedirs("data", exist_ok=True)
    results = []

    for company in companies:
        ticker = company["ticker"]
        price, market_cap = get_price_and_market_cap_yahoo(ticker)

        results.append({
            "ticker": ticker,
            "company": company["company"],
            "industry": company["industry"],
            "close": price if price is not None else 0.0,
            "market_cap": market_cap if market_cap else ""
        })
        time.sleep(1)  # be polite to Yahoo

    today = datetime.now().strftime("%Y-%m-%d")
    with open(f"data/{today}.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("data/latest.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"[DONE] Saved {len(results)} records to data/{today}.json and data/latest.json")

if __name__ == "__main__":
    main()
