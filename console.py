from database import Database, Symbol, TimeInterval
from datetime import datetime, timedelta
from IPython import embed
from IPython.terminal.interactiveshell import TerminalInteractiveShell
import sys

def start_console():
    # Initialize database connection
    db = Database()
    
    # Configure IPython to show all object attributes
    TerminalInteractiveShell.ast_node_interactivity = "all"
    
    # Create a dictionary of available objects
    console_globals = {
        'db': db,
        'Symbol': Symbol,
        'TimeInterval': TimeInterval,
        'datetime': datetime,
        'timedelta': timedelta,
    }
    
    # Print welcome message
    print("\n=== StonksBot IPython Console ===")
    print("Available objects:")
    print("  db          - Database session")
    print("  Symbol      - Symbol model")
    print("  TimeInterval - TimeInterval model")
    print("  datetime    - datetime module")
    print("  timedelta   - timedelta module")
    print("\nExample queries:")
    print("  # List all symbols")
    print("  db.session.query(Symbol).all()")
    print("  # Get a specific symbol")
    print("  db.session.query(Symbol).filter_by(symbol='AAPL').first()")
    print("  # Get recent intervals")
    print("  db.session.query(TimeInterval).filter_by(symbol='AAPL').order_by(TimeInterval.start_time.desc()).limit(5).all()")
    print("\nIPython Tips:")
    print("  - Use Tab for auto-completion")
    print("  - Use ? after an object to see its help (e.g., Symbol?)")
    print("  - Use ?? to see source code")
    print("  - Use %history to see command history")
    print("  - Use %run to run a Python file")
    print("  - Use Ctrl+D to exit")
    print("=" * 40 + "\n")
    
    # Start IPython console
    try:
        embed(using=False, colors='Linux', user_ns=console_globals)
    finally:
        db.close()

if __name__ == '__main__':
    start_console() 