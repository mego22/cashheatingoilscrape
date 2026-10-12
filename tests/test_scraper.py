from scraper import build_listing_url, extract_listing_data


SAMPLE_HTML = """
<html>
  <body>
    <table>
      <tr><td>LISTING ID</td><td>:</td><td>WXXpbAS</td></tr>
      <tr><td>State</td><td>:</td><td>CT</td></tr>
      <tr><td>City</td><td>:</td><td class="varlabel">Plainville</td></tr>
    </table>

    <table>
      <tr><td>Delivery Date&nbsp;:&nbsp;</td><td>Sep 17th 2026</td></tr>
      <tr><td>Price Updated on&nbsp;:&nbsp;</td><td>Sep 15th 2026</td></tr>
    </table>

    <table class="paywithcash" width="100%">
      <tr><td>Cash Prices :</td></tr>
      <tr><td><b>Gallons:</b></td><td><b>Price/Gallon</b></td></tr>
      <tr><td>50-99</td><td>$6.04</td></tr>
      <tr><td>100-149</td><td>$5.39</td></tr>
    </table>

    <table class="paybycredit" width="100%">
      <tr><td>Credit Card Prices :</td></tr>
      <tr><td><b>Gallons:</b></td><td><b>Price/Gallon</b></td></tr>
      <tr><td>50-99</td><td>$6.04</td></tr>
      <tr><td>100-149</td><td>$5.54</td></tr>
    </table>
  </body>
</html>
"""


def test_extract_listing_data_parses_all_fields() -> None:
    data = extract_listing_data(SAMPLE_HTML)

    assert data["listing_id"] == "WXXpbAS"
    assert data["state"] == "CT"
    assert data["city"] == "Plainville"
    assert data["delivery_date"] == "2026-09-17"
    assert data["updated_on"] == "2026-09-15"
    assert data["cash_prices"] == [
        {"gallons": "50-99", "price": 6.04},
        {"gallons": "100-149", "price": 5.39},
    ]
    assert data["credit_prices"] == [
        {"gallons": "50-99", "price": 6.04},
        {"gallons": "100-149", "price": 5.54},
    ]


def test_build_listing_url_uses_zip_code() -> None:
    assert build_listing_url("06062") == "https://www.cashheatingoil.com/plainville_ct_oil_prices/06062"
    assert build_listing_url("12345") == "https://www.cashheatingoil.com/plainville_ct_oil_prices/12345"
