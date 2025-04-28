import yfinance as yf
from datetime import datetime, timedelta
from database import Database
import pandas as pd

def fetch_and_save_data(symbols, period='7d'):
    """
    Fetch data from Yahoo Finance and save to database
    
    Parameters:
    - symbols: List of stock symbols (e.g., ['AAPL', 'MSFT'])
    - period: Time period ('1d', '5d', '7d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    """
    db = Database()
    
    for symbol in symbols:
        print(f"Processing {symbol}...")
        try:
            # Fetch data from Yahoo Finance
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval='1m')
            
            if data.empty:
                print(f"No data found for {symbol}")
                continue
            
            # Get company info
            info = stock.info
            company_name = info.get('longName', '')
            
            # Save symbol info
            db.save_symbol(
                symbol=symbol,
                company_name=company_name
            )
            
            # Save time intervals
            db.save_time_interval(symbol, data)
            
            print(f"Successfully saved data for {symbol}")
            
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
    
    db.close()

def main():
    # List of symbols to fetch
    symbols = [
        'AAPL',  # Apple
        'MSFT',  # Microsoft
        'GOOGL', # Google
        'AMZN',  # Amazon
        'META',  # Meta (Facebook)
        'TSLA',  # Tesla
        'NVDA',  # NVIDIA
        'JPM',   # JPMorgan Chase
        'V',     # Visa
        'WMT'    # Walmart
    ]
    
    # Fetch last 7 days of 1-minute data
    fetch_and_save_data(symbols, period='7d')
    
    print("Data population complete!")

if __name__ == "__main__":
    main() 