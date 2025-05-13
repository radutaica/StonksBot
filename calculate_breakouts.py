"""
Module for calculating volume breakouts based on adjusted volume SMA.
"""
from typing import List, Dict
from datetime import datetime, timedelta
import pandas as pd
from database import Database, TimeInterval, Symbol
from tests.utils.test_utils import TechnicalAnalysis
from sqlalchemy import extract, and_

def find_volume_breakouts(
    ticker_time: int = 5,
    lookback_period: int = 20,
    volume_ratio_threshold: float = 10.0
) -> List[Dict]:
    """
    Find stocks with significant volume breakouts based on adjusted volume SMA.
    
    Args:
        ticker_time (int): Time interval in minutes (default: 5)
        lookback_period (int): Number of bars to look back (default: 20)
        volume_ratio_threshold (float): Minimum ratio of current volume to adjusted SMA (default: 10.0)
    
    Returns:
        List[Dict]: List of dictionaries containing breakout information for each matching symbol
    """
    db = Database()
    ta = TechnicalAnalysis()
    
    try:
        # Get all unique symbols from the database
        symbols = db.session.query(TimeInterval.symbol_id).distinct().all()
        breakouts = []
        
        print("\nSymbol Analysis:")
        print("-" * 50)
        print(f"{'Symbol':<10} {'Adj SMA':>12} {'Volume':>12} {'Vol Ratio':>12}")
        print("-" * 50)
        
        for (symbol_id,) in symbols:
            symbol = db.session.query(Symbol).filter(Symbol.id == symbol_id).first()
            if not symbol:
                continue

            # Get the most recent interval for this symbol
            latest_interval = db.session.query(TimeInterval).filter(
                TimeInterval.symbol_id == symbol_id,
                TimeInterval.interval_type == f'{ticker_time}min',
                TimeInterval.end_time < datetime(2025, 4, 10, 10, 10, 0)  # Less than or equal to target time
            ).order_by(TimeInterval.end_time.desc()).first()  # Order by end_time descending to get closest one
            
            if not latest_interval:
                continue

            # Calculate adjusted SMA using the TechnicalAnalysis method
            adj_sma = ta.calculate_adjusted_sma(
                type='V',
                period=lookback_period,
                interval_type=f'{ticker_time}min',
                timeinterval_id=latest_interval.id
            )
            
            if adj_sma is None or adj_sma == 0:
                continue
                
            vol_ratio = latest_interval.volume / adj_sma
            
            # Print all values regardless of threshold
            print(f"{symbol.symbol:<10} {adj_sma:>12,.2f} {latest_interval.volume:>12,.2f} {vol_ratio:>12,.2f}")
            
            if vol_ratio > volume_ratio_threshold:
                breakout_info = {
                    'Symbol': symbol.symbol,
                    'Date': latest_interval.start_time.strftime('%Y-%m-%d'),
                    'Time': latest_interval.start_time.strftime('%H:%M'),
                    'Volume': round(latest_interval.volume, 2),
                    'Vol SMA': round(adj_sma, 2),
                    'Vol Ratio': round(vol_ratio, 2),
                    'Open': round(latest_interval.open, 2),
                    'High': round(latest_interval.high, 2),
                    'Low': round(latest_interval.low, 2),
                    'Close': round(latest_interval.close, 2)
                }
                breakouts.append(breakout_info)
        
        print("-" * 50)
        return breakouts
    
    finally:
        db.close()

def export_breakouts_to_excel(breakouts: List[Dict], output_file: str = 'volume_breakouts.xlsx'):
    """
    Export breakout data to an Excel file with a single, well-formatted sheet.
    
    Args:
        breakouts (List[Dict]): List of breakout information dictionaries
        output_file (str): Name of the output Excel file
    """
    if not breakouts:
        print("No breakouts found to export.")
        return
    
    # Convert to DataFrame and sort by date and time
    df = pd.DataFrame(breakouts)
    df = df.sort_values(['Date', 'Time', 'Symbol'], ascending=[False, False, True])
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write the data
        df.to_excel(writer, sheet_name='Volume Breakouts', index=False)
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Volume Breakouts']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right'
        })
        
        volume_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right'
        })
        
        date_format = workbook.add_format({
            'align': 'center'
        })
        
        # Set column widths and formats
        worksheet.set_column('A:A', 10)  # Symbol
        worksheet.set_column('B:B', 12)  # Date
        worksheet.set_column('C:C', 8)   # Time
        worksheet.set_column('D:D', 12, volume_format)  # Volume
        worksheet.set_column('E:E', 12, volume_format)  # Vol SMA
        worksheet.set_column('F:F', 10, number_format)  # Vol Ratio
        worksheet.set_column('G:J', 10, number_format)  # OHLC prices
        
        # Write headers with format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Add alternating row colors
        for row in range(1, len(df) + 1):
            if row % 2 == 0:
                worksheet.set_row(row, None, workbook.add_format({'bg_color': '#F2F2F2'}))

if __name__ == "__main__":
    # Find breakouts
    breakouts = find_volume_breakouts()
    
    # Export to Excel
    export_breakouts_to_excel(breakouts)
    
    print(f"Found {len(breakouts)} volume breakouts. Results exported to 'volume_breakouts.xlsx'") 