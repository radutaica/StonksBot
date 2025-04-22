import os
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from config import *

# Load environment variables
load_dotenv()

# Initialize Alpaca API
api = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_API_SECRET'),
    os.getenv('ALPACA_BASE_URL'),
    api_version='v2'
)

class TradingBot:
    def __init__(self):
        self.positions = {}
        self.check_trading_environment()

    def check_trading_environment(self):
        """Check if the market is open and the API connection is working"""
        try:
            clock = api.get_clock()
            print(f"Market is {'open' if clock.is_open else 'closed'}")
            print(f"Next market open: {clock.next_open}")
            print(f"Next market close: {clock.next_close}")
        except Exception as e:
            print(f"Error connecting to Alpaca API: {e}")
            exit(1)

    def get_historical_data(self, symbol, period='1mo', interval='1h'):
        """Fetch historical data for technical analysis"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def calculate_indicators(self, df):
        """Calculate technical indicators"""
        # Calculate Moving Averages
        df['MA_fast'] = df['Close'].rolling(window=MOVING_AVERAGE_FAST).mean()
        df['MA_slow'] = df['Close'].rolling(window=MOVING_AVERAGE_SLOW).mean()

        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def check_buy_signal(self, df):
        """Check if we should buy based on our strategy"""
        if len(df) < MOVING_AVERAGE_SLOW:
            return False

        last_row = df.iloc[-1]
        
        # Check if fast MA crosses above slow MA
        ma_crossover = (df['MA_fast'].iloc[-2] <= df['MA_slow'].iloc[-2] and 
                       last_row['MA_fast'] > last_row['MA_slow'])
        
        # Check if RSI indicates oversold
        rsi_oversold = last_row['RSI'] < RSI_OVERSOLD

        return ma_crossover or rsi_oversold

    def check_sell_signal(self, df):
        """Check if we should sell based on our strategy"""
        if len(df) < MOVING_AVERAGE_SLOW:
            return False

        last_row = df.iloc[-1]
        
        # Check if fast MA crosses below slow MA
        ma_crossover = (df['MA_fast'].iloc[-2] >= df['MA_slow'].iloc[-2] and 
                       last_row['MA_fast'] < last_row['MA_slow'])
        
        # Check if RSI indicates overbought
        rsi_overbought = last_row['RSI'] > RSI_OVERBOUGHT

        return ma_crossover or rsi_overbought

    def execute_trade(self, symbol, side):
        """Execute a trade order"""
        try:
            if side == 'buy':
                api.submit_order(
                    symbol=symbol,
                    qty=QUANTITY,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Bought {QUANTITY} shares of {symbol}")
            else:
                api.submit_order(
                    symbol=symbol,
                    qty=QUANTITY,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Sold {QUANTITY} shares of {symbol}")
        except Exception as e:
            print(f"Error executing {side} order for {symbol}: {e}")

    def run(self):
        """Main bot loop"""
        while True:
            try:
                # Check if market is open
                clock = api.get_clock()
                if not clock.is_open and not PAPER_TRADING:
                    print("Market is closed. Waiting...")
                    time.sleep(60)
                    continue

                for symbol in SYMBOLS:
                    # Get historical data and calculate indicators
                    df = self.get_historical_data(symbol)
                    if df is None:
                        continue

                    df = self.calculate_indicators(df)

                    # Get current position
                    position = None
                    try:
                        position = api.get_position(symbol)
                    except:
                        pass

                    # Check signals and execute trades
                    if position is None:  # No position, look for buy signals
                        if self.check_buy_signal(df):
                            self.execute_trade(symbol, 'buy')
                    else:  # Have position, look for sell signals
                        if self.check_sell_signal(df):
                            self.execute_trade(symbol, 'sell')

                # Sleep before next iteration
                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run() 