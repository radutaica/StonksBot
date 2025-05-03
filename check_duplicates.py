from database import Database, Symbol, TimeInterval
from sqlalchemy import func
from datetime import datetime

def check_duplicates():
    db = Database()
    try:
        print("\n=== Checking for Duplicates ===\n")
        
        # Check for duplicate symbols
        duplicate_symbols = db.session.query(Symbol.symbol, func.count(Symbol.id))\
            .group_by(Symbol.symbol)\
            .having(func.count(Symbol.id) > 1)\
            .all()
        
        if duplicate_symbols:
            print("Found duplicate symbols:")
            for symbol, count in duplicate_symbols:
                print(f"{symbol}: {count} entries")
        else:
            print("No duplicate symbols found.")
        
        # Check for duplicate time intervals
        print("\nChecking for duplicate time intervals...")
        for symbol in db.session.query(Symbol).all():
            duplicates = db.session.query(
                TimeInterval.symbol_id,
                TimeInterval.start_time,
                func.count(TimeInterval.id)
            ).filter(
                TimeInterval.symbol_id == symbol.id
            ).group_by(
                TimeInterval.symbol_id,
                TimeInterval.start_time
            ).having(
                func.count(TimeInterval.id) > 1
            ).all()
            
            if duplicates:
                print(f"\nFound duplicates for {symbol.symbol}:")
                for symbol_id, start_time, count in duplicates:
                    print(f"Time: {start_time}, Count: {count}")
            else:
                print(f"No duplicates found for {symbol.symbol}")
        
        # Print total counts
        total_symbols = db.session.query(Symbol).count()
        total_intervals = db.session.query(TimeInterval).count()
        
        print(f"\n=== Database Summary ===")
        print(f"Total Symbols: {total_symbols}")
        print(f"Total Time Intervals: {total_intervals}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_duplicates() 