# Cash Heating Oil Scraper

Scrapes the current cash and credit heating oil prices for Plainville, CT from
CashHeatingOil.com.

## Usage

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper with a ZIP code:
   ```bash
   python main.py 06062
   ```
   or:
   ```bash
   python main.py --zip-code 06062
   ```

The scraper builds the target URL dynamically from the ZIP code, so you can
reuse it for any location:

https://www.cashheatingoil.com/plainville_ct_oil_prices/<zip_code>

## Daily scheduling

On macOS or Linux, edit your crontab with `crontab -e` and add a daily job,
adjusting the path if needed:

```cron
0 8 * * * cd /Users/d/cashheatingoilscrape && .venv/bin/python main.py 06062 >> scraper.log 2>&1
```

Run the parser tests with:

```bash
python -m pytest -q
```
