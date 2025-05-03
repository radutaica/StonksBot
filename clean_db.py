from database import Database, Symbol, TimeInterval
from sqlalchemy import func
from datetime import datetime

def clean_database():
    db = Database()
    try:
        print("Starting database cleanup...")
        
        # Get all duplicate time intervals
        duplicates = db.session.query(
            TimeInterval.symbol_id,
            TimeInterval.start_time,
            func.min(TimeInterval.id).label('keep_id')
        ).group_by(
            TimeInterval.symbol_id,
            TimeInterval.start_time
        ).having(
            func.count(TimeInterval.id) > 1
        ).subquery()
        
        # Delete all duplicates except the one with the minimum ID
        delete_query = TimeInterval.__table__.delete().where(
            TimeInterval.id.notin_(
                db.session.query(duplicates.c.keep_id)
            )
        )
        
        result = db.session.execute(delete_query)
        deleted_count = result.rowcount
        
        print(f"Cleaned up {deleted_count} duplicate entries")
        
        # Commit the changes
        db.session.commit()
        
        # Print final counts
        total_symbols = db.session.query(Symbol).count()
        total_intervals = db.session.query(TimeInterval).count()
        
        print("\n=== Database Summary After Cleanup ===")
        print(f"Total Symbols: {total_symbols}")
        print(f"Total Time Intervals: {total_intervals}")
        
    finally:
        db.close()

if __name__ == "__main__":
    clean_database() 