
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

import requests

def get_price_and_market_cap_yahoo(ticker):
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}.AX?modules=price"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[WARN] Failed to fetch {ticker}: {response.status_code}")
        return None, None

    try:
        data = response.json()
        price_data = data["quoteSummary"]["result"][0]["price"]
        price = price_data.get("regularMarketPrice", {}).get("raw", None)
        market_cap = price_data.get("marketCap", {}).get("raw", None)
        return price, market_cap
    except Exception as e:
        print(f"[ERROR] Parsing failed for {ticker}: {e}")
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
