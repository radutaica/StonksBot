from database import Database, Symbol, TimeInterval
from datetime import datetime
from sqlalchemy import func
from tests.utils.test_utils import TechnicalAnalysis
import pandas as pd

def analyze_symbol_status():
    db = Database()
    ta = TechnicalAnalysis()
    target_time = datetime(2025, 4, 10, 10, 10, 0)
    
    print('\nAnalyzing symbols for volume breakouts with SMA details:')
    print('-' * 100)
    print(f"{'Symbol':<10} {'Has Latest Interval':<20} {'Has Valid SMA':<15} {'Interval Count':>15} {'Latest Volume':>15} {'SMA Value':>15}")
    print('-' * 100)
    
    symbols = db.session.query(Symbol).all()
    for symbol in symbols:
        # Check for latest interval
        latest = db.session.query(TimeInterval).filter(
            TimeInterval.symbol_id == symbol.id,
            TimeInterval.interval_type == '5min',
            TimeInterval.end_time < target_time
        ).order_by(TimeInterval.end_time.desc()).first()
        
        has_latest = 'Yes' if latest else 'No'
        has_sma = 'N/A'
        latest_volume = 'N/A'
        sma_value = 'N/A'
        
        if latest:
            latest_volume = f"{latest.volume:,}"
            
            # Get the last 20 intervals for this symbol
            intervals = db.session.query(TimeInterval).filter(
                TimeInterval.symbol_id == symbol.id,
                TimeInterval.interval_type == '5min',
                TimeInterval.end_time <= latest.end_time
            ).order_by(TimeInterval.end_time.desc()).limit(20).all()
            
            if len(intervals) == 20:  # Only calculate if we have enough data
                # Try to calculate adjusted SMA
                adj_sma = ta.calculate_adjusted_sma(
                    type='V',
                    period=20,
                    interval_type='5min',
                    timeinterval_id=latest.id
                )
                has_sma = 'Yes' if adj_sma and adj_sma != 0 else 'No'
                sma_value = f"{adj_sma:,.2f}" if adj_sma else 'None/0'
                
                if not adj_sma or adj_sma == 0:
                    print(f"\nDetailed analysis for {symbol.symbol}:")
                    print("Last 20 intervals volumes:")
                    for i, interval in enumerate(intervals):
                        print(f"Interval {i+1:2d}: {interval.end_time} - Volume: {interval.volume:,}")
        
        # Get total interval count
        interval_count = db.session.query(func.count(TimeInterval.id)).filter(
            TimeInterval.symbol_id == symbol.id,
            TimeInterval.interval_type == '5min',
            TimeInterval.end_time < target_time
        ).scalar()
        
        print(f"{symbol.symbol:<10} {has_latest:<20} {has_sma:<15} {interval_count:>15,} {latest_volume:>15} {sma_value:>15}")
        
        # If SMA calculation failed, show more details
        if latest and has_sma == 'No':
            print(f"  -> {symbol.symbol} has {len(intervals)} intervals for SMA calculation (needs 20)")
    
    print('-' * 100)
    print(f"Total symbols analyzed: {len(symbols)}")

if __name__ == "__main__":
    analyze_symbol_status() 