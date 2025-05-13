from database import Database, Symbol, TimeInterval
from datetime import datetime, timedelta
from collections import defaultdict

def list_symbols():
    db = Database()
    try:
        print("\n=== Current Symbols in Database ===\n")
        
        # Get all symbols
        symbols = db.session.query(Symbol).all()
        if not symbols:
            print("No symbols found in database.")
            return
        
        # Print symbols in a nice format
        print("Total symbols:", len(symbols))
        print("\nSymbol List:")
        print("-" * 40)
        for symbol in symbols:
            print(f"{symbol.symbol:<8} | {symbol.company_name or 'N/A'}")
        print("-" * 40)
        
    finally:
        db.close()

def check_symbol_intervals():
    db = Database()
    try:
        print("\n=== Checking Symbol Intervals ===\n")
        
        # Get all symbols
        symbols = db.session.query(Symbol).all()
        if not symbols:
            print("No symbols found in database.")
            return
        
        # Track interval availability for each symbol
        interval_status = defaultdict(dict)
        required_intervals = ['1min', '5min', '15min']
        
        for symbol in symbols:
            print(f"\nChecking {symbol.symbol}...")
            
            # Check each required interval
            for interval in required_intervals:
                # Get the most recent interval of this type
                latest = db.session.query(TimeInterval)\
                    .filter(
                        TimeInterval.symbol_id == symbol.id,
                        TimeInterval.interval_type == interval
                    )\
                    .order_by(TimeInterval.start_time.desc())\
                    .first()
                
                if latest:
                    # Calculate how old the data is
                    age = datetime.utcnow() - latest.start_time
                    interval_status[symbol.symbol][interval] = {
                        'has_data': True,
                        'latest': latest.start_time,
                        'age': age
                    }
                    print(f"  {interval}: Latest data from {latest.start_time} ({age.days} days ago)")
                else:
                    interval_status[symbol.symbol][interval] = {
                        'has_data': False,
                        'latest': None,
                        'age': None
                    }
                    print(f"  {interval}: No data available")
        
        # Print summary
        print("\n=== Interval Availability Summary ===")
        print("\nSymbols missing intervals:")
        missing_count = 0
        for symbol, intervals in interval_status.items():
            missing = [interval for interval, status in intervals.items() if not status['has_data']]
            if missing:
                missing_count += 1
                print(f"\n{symbol}:")
                for interval in missing:
                    print(f"  - {interval}")
        
        if missing_count == 0:
            print("\nAll symbols have data for all intervals!")
        
        # Print total counts
        total_symbols = len(symbols)
        print(f"\nTotal symbols checked: {total_symbols}")
        print(f"Symbols with missing intervals: {missing_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    list_symbols()  # Changed to just list symbols 