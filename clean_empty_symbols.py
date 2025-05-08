from database import Database, Symbol, TimeInterval
from sqlalchemy import func

def clean_empty_symbols():
    """
    Remove symbols from the database that don't have any associated time intervals.
    """
    db = Database()
    try:
        print("Starting cleanup of empty symbols...")
        
        # Find symbols that don't have any time intervals
        empty_symbols = db.session.query(Symbol).outerjoin(TimeInterval).group_by(Symbol.id).having(func.count(TimeInterval.id) == 0).all()
        
        if not empty_symbols:
            print("No empty symbols found.")
            return
        
        print(f"\nFound {len(empty_symbols)} symbols without time intervals:")
        for symbol in empty_symbols:
            print(f"- {symbol.symbol}")
        
        # Delete the empty symbols
        for symbol in empty_symbols:
            db.session.delete(symbol)
        
        # Commit the changes
        db.session.commit()
        print(f"\nSuccessfully removed {len(empty_symbols)} empty symbols from the database.")
        
        # Print final counts
        total_symbols = db.session.query(Symbol).count()
        total_intervals = db.session.query(TimeInterval).count()
        
        print("\n=== Database Summary After Cleanup ===")
        print(f"Total Symbols: {total_symbols}")
        print(f"Total Time Intervals: {total_intervals}")
        
    finally:
        db.close()

if __name__ == '__main__':
    clean_empty_symbols() 