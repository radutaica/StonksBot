# StonksBot - Stock Trading Bot

A Python-based automated trading bot that implements technical analysis strategies for stock trading.

## Features
- Real-time stock data fetching using yfinance
- Technical analysis indicators
- Automated trading using Alpaca API
- Configurable trading strategies
- Risk management features

## Setup
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Alpaca API credentials:
   ```
   ALPACA_API_KEY=your_api_key
   ALPACA_API_SECRET=your_api_secret
   ALPACA_BASE_URL=https://paper-api.alpaca.markets  # For paper trading
   ```

## Usage
Run the bot:
```bash
python trading_bot.py
```

## Configuration
Edit `config.py` to modify:
- Trading pairs
- Strategy parameters
- Risk management settings
- Trading timeframes

## Disclaimer
This bot is for educational purposes only. Always understand the risks involved in automated trading. Never trade with money you cannot afford to lose.
