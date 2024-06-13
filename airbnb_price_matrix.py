import sys
import time
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def fetch_price(driver, listing_id, checkin, checkout, adults):
    url = f"https://www.airbnb.com/rooms/{listing_id}?adults={adults}&check_in={checkin}&check_out={checkout}"
    driver.get(url)
    time.sleep(10)  # Wait for the page to load

    try:
        price_element = driver.find_element(By.XPATH, '//*[@data-testid="price-summary__total"]')
        price = price_element.text
        return price
    except Exception as e:
        print(f"Error fetching price for {checkin} to {checkout}: {e}")
        return None

def create_price_matrix(listing_id, start_date, end_date, adults):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Setup the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    current_date = start_date
    delta = timedelta(days=1)
    price_matrix = []

    while current_date < end_date:
        row = [current_date.strftime("%Y-%m-%d")]
        for n in range(1, (end_date - current_date).days + 1):
            checkin = current_date.strftime("%Y-%m-%d")
            checkout = (current_date + timedelta(days=n)).strftime("%Y-%m-%d")
            price = fetch_price(driver, listing_id, checkin, checkout, adults)
            row.append(price if price else "N/A")
        price_matrix.append(row)
        current_date += delta

    driver.quit()

    return price_matrix

def save_to_csv(price_matrix, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(price_matrix)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python airbnb_price_matrix.py <listing_id> <start_date> <end_date> <adults>")
        sys.exit(1)

    listing_id = sys.argv[1]
    start_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    end_date = datetime.strptime(sys.argv[3], "%Y-%m-%d")
    adults = int(sys.argv[4])

    print(f"Creating price matrix for listing {listing_id} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} for {adults} adults")

    price_matrix = create_price_matrix(listing_id, start_date, end_date, adults)
    save_to_csv(price_matrix, f"price_matrix_{listing_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv")
