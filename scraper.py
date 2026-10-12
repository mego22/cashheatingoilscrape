import argparse
import re
from datetime import datetime
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.cashheatingoil.com"
DEFAULT_ZIP_CODE = "06062"


def build_listing_url(zip_code: str = DEFAULT_ZIP_CODE) -> str:
    cleaned_zip = str(zip_code).strip()
    if not cleaned_zip:
        raise ValueError("A ZIP code is required.")
    return f"{BASE_URL}/plainville_ct_oil_prices/{cleaned_zip}"


def parse_price(value: str) -> float:
    cleaned = value.strip().replace("$", "").replace(",", "").strip()
    return float(cleaned)


def parse_date(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", cleaned)
    try:
        parsed = datetime.strptime(cleaned, "%b %d %Y")
    except ValueError:
        return cleaned
    return parsed.strftime("%Y-%m-%d")


def extract_listing_data(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")

    defs = {}
    for row in soup.select("table tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if len(cells) < 3:
            continue
        key = cells[0].strip()
        if key in {"LISTING ID", "State", "City"}:
            defs[key] = cells[2]

    page_text = soup.get_text(" ", strip=True)
    delivery_match = re.search(
        r"Delivery Date\s*:\s*([A-Z][a-z]{2}\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4})",
        page_text,
    )
    updated_match = re.search(
        r"Price Updated on\s*:\s*([A-Z][a-z]{2}\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4})",
        page_text,
    )
    delivery_text = delivery_match.group(1) if delivery_match else ""
    updated_text = updated_match.group(1) if updated_match else ""

    listing_id = defs.get("LISTING ID", "")
    state = defs.get("State", "")
    city = defs.get("City", "")

    data = {
        "listing_id": listing_id,
        "state": state,
        "city": city,
        "delivery_date": parse_date(delivery_text) if delivery_text else "",
        "updated_on": parse_date(updated_text) if updated_text else "",
        "cash_prices": [],
        "credit_prices": [],
    }

    for table in soup.select("table.paywithcash"):
        rows = table.select("tr")
        for row in rows[2:]:
            cols = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            if len(cols) < 2:
                continue
            gallons = cols[0]
            price = cols[1]
            if gallons.lower() == "gallons:" or price.lower() == "price/gallon":
                continue
            if gallons and price.startswith("$"):
                data["cash_prices"].append({"gallons": gallons, "price": parse_price(price)})

    for table in soup.select("table.paybycredit"):
        rows = table.select("tr")
        for row in rows[2:]:
            cols = [c.get_text(" ", strip=True) for c in row.find_all("td")]
            if len(cols) < 2:
                continue
            gallons = cols[0]
            price = cols[1]
            if gallons.lower() == "gallons:" or price.lower() == "price/gallon":
                continue
            if gallons and price.startswith("$"):
                data["credit_prices"].append({"gallons": gallons, "price": parse_price(price)})

    return data


def fetch_listing(zip_code: str = DEFAULT_ZIP_CODE) -> Dict[str, Any]:
    url = build_listing_url(zip_code)
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    return extract_listing_data(response.text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape heating oil prices for a ZIP code.")
    parser.add_argument("zip_code", nargs="?", default=DEFAULT_ZIP_CODE, help="ZIP code to scrape, e.g. 06062")
    parser.add_argument("--zip-code", dest="zip_code_flag", help="ZIP code to scrape, e.g. 06062")
    args = parser.parse_args()
    zip_code = args.zip_code_flag or args.zip_code
    return argparse.Namespace(zip_code=zip_code)


def main() -> None:
    args = parse_args()
    data = fetch_listing(args.zip_code)
    print(f"ZIP code: {args.zip_code}")
    print(f"Listing ID: {data['listing_id']}")
    print(f"Location: {data['city']}, {data['state']}")
    print(f"Delivery Date: {data['delivery_date']}")
    print(f"Updated On: {data['updated_on']}")
    print("Cash prices:")
    for entry in data["cash_prices"]:
        print(f"  {entry['gallons']}: ${entry['price']:.2f}/gal")
    print("Credit prices:")
    for entry in data["credit_prices"]:
        print(f"  {entry['gallons']}: ${entry['price']:.2f}/gal")


if __name__ == "__main__":
    main()
