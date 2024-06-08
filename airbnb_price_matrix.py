import sys
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_price(listing_id, check_in, check_out, adults):
    url = f'https://www.airbnb.com/s/{listing_id}/homes?checkin={check_in}&checkout={check_out}&adults={adults}'
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to load completely

        price_element = driver.find_element("xpath", '//*[@data-testid="price-summary__total"]')

        price_text = price_element.text.replace('$', '').replace(',', '')
        price = float(price_text)
        
        print(f"Fetched price: ${price} for {check_in} to {check_out}")
    except Exception as e:
        print(f"Error fetching price for {check_in} to {check_out}: {e}")
        price = None
    finally:
        driver.quit()

    return price

def create_price_matrix(listing_id, start_date, end_date, adults):
    dates = pd.date_range(start_date, end_date - timedelta(days=1))
    price_matrix = pd.DataFrame(index=dates, columns=dates)

    for check_in in dates:
        for check_out in dates[dates > check_in]:
            price = get_price(listing_id, check_in.strftime('%Y-%m-%d'), check_out.strftime('%Y-%m-%d'), adults)
            price_matrix.at[check_in, check_out] = price

    return price_matrix

def main():
    if len(sys.argv) != 5:
        print("Usage: python airbnb_price_matrix.py <listing_id> <start_date> <end_date> <adults>")
        sys.exit(1)

    listing_id = sys.argv[1]
    start_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    end_date = datetime.strptime(sys.argv[3], '%Y-%m-%d')
    adults = int(sys.argv[4])

    print(f"Creating price matrix for listing {listing_id} from {start_date.date()} to {end_date.date()} for {adults} adults")

    price_matrix = create_price_matrix(listing_id, start_date, end_date, adults)

    filename = f'price_matrix_{listing_id}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}_{adults}adults.csv'
    price_matrix.to_csv(filename)
    print(f"Saved price matrix to {filename}")

if __name__ == '__main__':
    main()
