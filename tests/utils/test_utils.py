"""
Utility functions for testing the StonksBot application.
This module contains reusable test methods that can be imported and used across different test files.
"""
from typing import List, Union, Literal
from database import Database, TimeInterval
from datetime import datetime, timedelta
from sqlalchemy import and_, extract

class TechnicalAnalysis:
    def __init__(self):
        """Initialize the TechnicalAnalysis class with a database connection."""
        self.db = Database()
    
    def __del__(self):
        """Clean up database connection when the object is destroyed."""
        if hasattr(self, 'db'):
            self.db.close()
    
    def calculate_sma(
        self,
        symbol: str,
        type: Literal['O', 'H', 'L', 'C', 'V'],
        period: int,
        ticker_time: int,
        timeinterval_id: int
    ) -> float:
        """
        Calculate Simple Moving Average (SMA) for a given symbol and time interval.
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            type (Literal['O', 'H', 'L', 'C', 'V']): Type of data to calculate SMA for
                O = Open, H = High, L = Low, C = Close, V = Volume
            period (int): Number of periods/bars to calculate the moving average
            ticker_time (int): Time interval in minutes (e.g., 5 for 5-minute intervals)
            timeinterval_id (int): The starting point (time interval ID) from where to calculate
            
        Returns:
            float: The calculated SMA value, or None if not enough data points
            
        Example:
            >>> ta = TechnicalAnalysis()
            >>> sma = ta.calculate_sma('AAPL', 'C', 20, 5, 1000)
            >>> print(sma)
            150.25
        """
        # Get the current time interval
        current_interval = self.db.session.query(TimeInterval).filter(
            TimeInterval.id == timeinterval_id
        ).first()
        
        if not current_interval:
            return None
        
        # Calculate the start time for the period
        start_time = current_interval.start_time - timedelta(minutes=ticker_time * period)
        
        # Query the required time intervals
        intervals = self.db.session.query(TimeInterval).filter(
            and_(
                TimeInterval.symbol_id == current_interval.symbol_id,
                TimeInterval.start_time >= start_time,
                TimeInterval.start_time <= current_interval.start_time,
                # Filter for specific minute intervals using extract
                extract('minute', TimeInterval.start_time) % ticker_time == 0
            )
        ).order_by(TimeInterval.start_time.desc()).limit(period).all()
        
        if len(intervals) < period:
            return None
        
        # Extract the values based on the type
        values = []
        for interval in intervals:
            if type == 'O':
                values.append(interval.open)
            elif type == 'H':
                values.append(interval.high)
            elif type == 'L':
                values.append(interval.low)
            elif type == 'C':
                values.append(interval.close)
            elif type == 'V':
                values.append(interval.volume)
        
        # Calculate SMA
        return sum(values) / len(values)

def setup_test_environment():
    """
    Set up the test environment with necessary configurations.
    This can include database setup, mock objects, or any other test prerequisites.
    """
    pass

def teardown_test_environment():
    """
    Clean up the test environment after tests are complete.
    This can include database cleanup, removing temporary files, etc.
    """
    pass 