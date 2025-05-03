from database import Database, Symbol, TimeInterval
from datetime import datetime

def print_database_contents():
    db = Database()
    try:
        # Get all symbols
        symbols = db.session.query(Symbol).all()
        
        print("\n=== DATABASE CONTENTS ===\n")
        
        if not symbols:
            print("No symbols found in database.")
            return
            
        total_entries = 0
        for symbol in symbols:
            # Count total intervals for this symbol
            interval_count = db.session.query(TimeInterval)\
                .filter(TimeInterval.symbol_id == symbol.id)\
                .count()
            total_entries += interval_count
            
            print(f"\nSymbol: {symbol.symbol}")
            print(f"Company Name: {symbol.company_name}")
            print(f"Active: {symbol.is_active}")
            print(f"Created: {symbol.created_at}")
            print(f"Last Updated: {symbol.updated_at}")
            print(f"Total Entries: {interval_count}")
            
            # Get time intervals for this symbol
            intervals = db.session.query(TimeInterval)\
                .filter(TimeInterval.symbol_id == symbol.id)\
                .order_by(TimeInterval.start_time.desc())\
                .limit(5).all()  # Show only last 5 intervals to avoid overwhelming output
            
            if intervals:
                print("\nRecent Time Intervals:")
                print("Start Time\t\tOpen\tHigh\tLow\tClose\tVolume")
                print("-" * 80)
                for interval in intervals:
                    print(f"{interval.start_time}\t{interval.open:.2f}\t{interval.high:.2f}\t{interval.low:.2f}\t{interval.close:.2f}\t{interval.volume}")
            else:
                print("\nNo time intervals found for this symbol.")
            
            print("\n" + "="*50)
        
        print(f"\nTotal number of symbols: {len(symbols)}")
        print(f"Total number of entries across all symbols: {total_entries}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print_database_contents() 