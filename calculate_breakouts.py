"""
Module for calculating volume breakouts based on adjusted volume SMA.
"""
from typing import List, Dict
from datetime import datetime
import pandas as pd
from database import Database, TimeInterval, Symbol
from tests.utils.test_utils import TechnicalAnalysis

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
        
        for (symbol_id,) in symbols:
            # Get symbol name
            symbol = db.session.query(Symbol).filter(Symbol.id == symbol_id).first()
            if not symbol:
                continue
                
            # Get all time intervals for this symbol, ordered by time
            intervals = db.session.query(TimeInterval).filter(
                TimeInterval.symbol_id == symbol_id
            ).order_by(TimeInterval.start_time.asc()).all()
            
            if not intervals:
                continue
            
            # Process each interval (except the first lookback_period ones)
            for i in range(lookback_period, len(intervals)):
                current_interval = intervals[i]
                
                # Calculate adjusted volume SMA for the lookback period
                adjusted_volume_sma = ta.calculate_adjusted_sma(
                    type='V',
                    period=lookback_period,
                    ticker_time=ticker_time,
                    timeinterval_id=current_interval.id
                )
                
                if not adjusted_volume_sma or adjusted_volume_sma == 0:
                    continue
                
                # Calculate volume ratio
                volume_ratio = current_interval.volume / adjusted_volume_sma
                
                # Check if the volume ratio exceeds the threshold
                if volume_ratio > volume_ratio_threshold:
                    breakout_info = {
                        'Symbol': symbol.symbol,
                        'Date': current_interval.start_time.strftime('%Y-%m-%d'),
                        'Time': current_interval.start_time.strftime('%H:%M'),
                        'Volume': round(current_interval.volume, 2),
                        'Vol SMA': round(adjusted_volume_sma, 2),
                        'Vol Ratio': round(volume_ratio, 2),
                        'Open': round(current_interval.open, 2),
                        'High': round(current_interval.high, 2),
                        'Low': round(current_interval.low, 2),
                        'Close': round(current_interval.close, 2)
                    }
                    breakouts.append(breakout_info)
        
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