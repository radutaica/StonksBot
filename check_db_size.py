from database import Database, Symbol, TimeInterval
from sqlalchemy import func, text
import psycopg2
from db_config import DATABASE_URL
import sys

def get_db_size_info():
    """
    Get information about database size and limits.
    """
    # First, let's get some basic counts from SQLAlchemy
    db = Database()
    try:
        total_symbols = db.session.query(Symbol).count()
        total_intervals = db.session.query(TimeInterval).count()
        
        print("\n=== Current Database Usage ===")
        print(f"Total Symbols: {total_symbols}")
        print(f"Total Time Intervals: {total_intervals}")
        
        # Get average intervals per symbol
        avg_intervals = total_intervals / total_symbols if total_symbols > 0 else 0
        print(f"Average Intervals per Symbol: {avg_intervals:.2f}")
        
        # Now let's get PostgreSQL specific information
        # Extract connection info from DATABASE_URL
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get database size
        cur.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as db_size,
                   pg_size_pretty(pg_total_relation_size('time_intervals')) as intervals_size,
                   pg_size_pretty(pg_total_relation_size('symbols')) as symbols_size;
        """)
        sizes = cur.fetchone()
        
        print("\n=== Database Size Information ===")
        print(f"Total Database Size: {sizes[0]}")
        print(f"Time Intervals Table Size: {sizes[1]}")
        print(f"Symbols Table Size: {sizes[2]}")
        
        # Get PostgreSQL limits
        cur.execute("""
            SELECT name, setting, unit, context, short_desc
            FROM pg_settings
            WHERE name IN (
                'max_connections',
                'shared_buffers',
                'work_mem',
                'maintenance_work_mem',
                'effective_cache_size'
            );
        """)
        
        print("\n=== PostgreSQL Configuration Limits ===")
        for row in cur.fetchall():
            name, setting, unit, context, desc = row
            print(f"\n{name}:")
            print(f"  Value: {setting} {unit if unit else ''}")
            print(f"  Context: {context}")
            print(f"  Description: {desc}")
        
        # Get table statistics
        cur.execute("""
            SELECT relname, n_live_tup, n_dead_tup, pg_size_pretty(pg_total_relation_size(relid))
            FROM pg_stat_user_tables
            WHERE relname IN ('symbols', 'time_intervals');
        """)
        
        print("\n=== Table Statistics ===")
        for row in cur.fetchall():
            table_name, live_tuples, dead_tuples, total_size = row
            print(f"\n{table_name}:")
            print(f"  Live Tuples: {live_tuples}")
            print(f"  Dead Tuples: {dead_tuples}")
            print(f"  Total Size: {total_size}")
        
        cur.close()
        conn.close()
        
    finally:
        db.close()

if __name__ == '__main__':
    get_db_size_info() 