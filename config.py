# Trading pairs configuration
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']  # Stocks to trade

# Technical Analysis Parameters
MOVING_AVERAGE_FAST = 9
MOVING_AVERAGE_SLOW = 21
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Trading Parameters
TIMEFRAME = '1h'  # Trading timeframe
QUANTITY = 1  # Number of shares per trade

# Risk Management
MAX_POSITION_SIZE = 1000  # Maximum position size in USD
STOP_LOSS_PERCENTAGE = 2.0  # Stop loss percentage
TAKE_PROFIT_PERCENTAGE = 4.0  # Take profit percentage

# API Configuration
PAPER_TRADING = True  # Set to False for live trading

# Database Configuration
DB_USER = 'admin'
DB_PASSWORD = 'admin'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'trading_bot' 