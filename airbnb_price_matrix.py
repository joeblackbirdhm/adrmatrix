import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import sys
import re

def get_price(listing_id, check_in, check_out, adults):
    url = f"https://www.airbnb.com/rooms/{listing_id}"
    params = {
        'adults': adults,
        'check_in': check_in,
        'check_out': check_out,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for {check_in} to {check_out}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract price (this might need adjustments depending on Airbnb's page structure)
    script_tags = soup.find_all('script')
    price = None

    for script in script_tags:
        if 'bootstrapData' in script.text:
            match = re.search(r'"rate":(\d+)', script.text)
            if match:
                price = int(match.group(1)) / 100  # Convert cents to dollars
                break

    return price

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
