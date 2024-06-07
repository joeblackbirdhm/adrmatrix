import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import sys

def get_price(listing_id, check_in, check_out, adults):
    url = f"https://www.airbnb.com/rooms/{listing_id}"
    params = {
        'adults': adults,
        'check_in': check_in,
        'check_out': check_out,
    }
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract price (this might need adjustments depending on Airbnb's page structure)
    price_element = soup.find('div', {'data-testid': 'price'})
    if price_element:
        price_text = price_element.get_text()
        price = float(price_text.replace('$', '').replace(',', ''))
        return price
    return None

def create_price_matrix(listing_id, start_date, end_date, adults):
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

if __name__ == "__main__":
    main()
