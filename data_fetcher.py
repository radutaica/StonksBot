import yfinance as yf
from datetime import datetime, timedelta
from database import Database

class DataFetcher:
    def __init__(self):
        self.db = Database()
    
    def fetch_intraday_data(self, symbol, period='7d'):
        """
        Fetch 1-minute intraday data from Yahoo Finance
        
        Parameters:
        - symbol: Stock symbol (e.g., 'AAPL')
        - period: Time period ('1d', '5d', '7d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        """
        try:
            # Fetch data from Yahoo Finance
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval='1m')
            
            # Save symbol info
            info = stock.info
            self.db.save_symbol(
                symbol=symbol,
                company_name=info.get('longName'),
                sector=info.get('sector'),
                industry=info.get('industry')
            )
            
            # Save time intervals
            self.db.save_time_interval(symbol, data)
            
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_multiple_symbols(self, symbols, period='7d'):
        """Fetch data for multiple symbols"""
        results = {}
        for symbol in symbols:
            data = self.fetch_intraday_data(symbol, period)
            results[symbol] = data
        return results
    
    def close(self):
        """Close database connection"""
        self.db.close()

# Example usage
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # Example: Fetch data for some popular stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    data = fetcher.fetch_multiple_symbols(symbols, period='7d')
    
    fetcher.close() 