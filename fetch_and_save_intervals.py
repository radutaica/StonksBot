from alpha_vantage.timeseries import TimeSeries
from database import Database
import pandas as pd
import time

API_KEY = 'ANDUERC5B9R0YR80'  # <-- Replace with your real API key

REQUESTS_PER_MIN = 5
SLEEP_SECONDS = 80

def fetch_and_save(symbols, intervals=['1min', '5min', '15min'], max_retries=3):
    db = Database()
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    try:
        requests_made = 0
        for symbol in symbols:
            for interval in intervals:
                print(f"Fetching {interval} data for {symbol}...")
                for attempt in range(max_retries):
                    try:
                        data, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')
                        requests_made += 1
                        if requests_made >= REQUESTS_PER_MIN:
                            print(f"Reached {REQUESTS_PER_MIN} requests, sleeping for {SLEEP_SECONDS} seconds...")
                            time.sleep(SLEEP_SECONDS)
                            requests_made = 0
                        if not data.empty:
                            try:
                                data = data.rename(columns={
                                    '1. open': 'Open',
                                    '2. high': 'High',
                                    '3. low': 'Low',
                                    '4. close': 'Close',
                                    '5. volume': 'Volume'
                                })
                                data.index.name = 'Datetime'
                                print(f"Saving {interval} data for {symbol}...")
                                db.save_time_interval(symbol, data, interval_type=interval)
                            except Exception as save_err:
                                print(f"Error saving {interval} data for {symbol}: {save_err}")
                        else:
                            print(f"No data for {symbol} at interval {interval}")
                        break
                    except Exception as e:
                        print(f"Error fetching {interval} for {symbol}: {e}")
                        if attempt < max_retries - 1:
                            print("Retrying after 20 seconds...")
                            time.sleep(20)
                        else:
                            print("Giving up on this interval.")
    finally:
        db.close()

if __name__ == '__main__':
    # Fetch for the specified symbols
    symbols = [
        'LTM',   # LATAM Airlines Group S.A.
        'BIRK',  # Birkenstock Holding plc
        'MRNO'   # Murano Global Investments Plc
    ]
    fetch_and_save(symbols) 