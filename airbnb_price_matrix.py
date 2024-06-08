import pandas as pd
from datetime import datetime, timedelta
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_price(listing_id, check_in, check_out, adults):
    print(f"Fetching price for {listing_id} from {check_in} to {check_out} for {adults} adults")
    url = f"https://www.airbnb.com/rooms/{listing_id}"
    params = f"?adults={adults}&check_in={check_in}&check_out={check_out}"
    full_url = url + params

    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(full_url)
    time.sleep(5)  # Allow time for the page to load

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="price"]').text
        price_text = price_element.replace('$', '').replace(',', '')
        price = float(price_text)
        print(f"Found price: {price}")
    except Exception as e:
        print(f"Error fetching price for {check_in} to {check_out}: {e}")
        price = None

    driver.quit()
    return price

def create_price_matrix(listing_id, start_date, end_date, adults):
    print(f"Creating price matrix for listing {listing_id} from {start_date} to {end_date} for {adults} adults")
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    matrix = []

    for check_in in dates:
        row = []
        for check_out in dates:
            if check_in >= check_out:
                row.append(None)
            else:
                price = get_price(listing_id, check_in.strftime('%Y-%m-%d'), check_out.strftime('%Y-%m-%d'), adults)
                row.append(price)
        matrix.append(row)

    df = pd.DataFrame(matrix, index=[d.strftime('%Y-%m-%d') for d in dates], columns=[d.strftime('%Y-%m-%d') for d in dates])
    return df

def main():
    if len(sys.argv) != 5:
        print("Usage: python airbnb_price_matrix.py <listing_id> <start_date> <end_date> <adults>")
        sys.exit(1)

    listing_id = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    adults = int(sys.argv[4])

    df = create_price_matrix(listing_id, start_date, end_date, adults)
    df.to_csv('price_matrix.csv')
    print("Price matrix saved to price_matrix.csv")

if __name__ == "__main__":
    main()

