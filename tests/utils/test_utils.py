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
        type: Literal['O', 'H', 'L', 'C', 'V'],
        period: int,
        interval_type: Literal['1min', '5min', '15min'],
        timeinterval_id: int
    ) -> float:
        """
        Calculate Simple Moving Average (SMA) for a given symbol and time interval.
        
        Args:
            type (Literal['O', 'H', 'L', 'C', 'V']): Type of data to calculate SMA for
                O = Open, H = High, L = Low, C = Close, V = Volume
            period (int): Number of periods/bars to calculate the moving average
            interval_type (Literal['1min', '5min', '15min']): Type of time interval
            timeinterval_id (int): The starting point (time interval ID) from where to calculate
            
        Returns:
            float: The calculated SMA value, or None if not enough data points
            
        Example:
            >>> ta = TechnicalAnalysis()
            >>> sma = ta.calculate_sma('AAPL', 'C', '5min', 1000)
            >>> print(sma)
            150.25
        """
        # Get the current time interval
        current_interval = self.db.session.query(TimeInterval).filter(
            TimeInterval.id == timeinterval_id
        ).first()
        
        if not current_interval:
            return None
        
        # Convert interval_type to minutes for time calculation
        ticker_time = int(interval_type.replace('min', ''))
        
        # Calculate the start time for the period
        start_time = current_interval.start_time - timedelta(minutes=ticker_time * period)
        
        # Query the required time intervals
        intervals = self.db.session.query(TimeInterval).filter(
            and_(
                TimeInterval.symbol_id == current_interval.symbol_id,
                TimeInterval.start_time >= start_time,
                TimeInterval.start_time <= current_interval.start_time,
                TimeInterval.interval_type == interval_type
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

    def calculate_ema(
        self,
        type: Literal['O', 'H', 'L', 'C', 'V'],
        period: int,
        interval_type: Literal['1min', '5min', '15min'],
        timeinterval_id: int
    ) -> float:
        """
        Calculate Exponential Moving Average (EMA) for a given symbol and time interval.
        
        Args:
            type (Literal['O', 'H', 'L', 'C', 'V']): Type of data to calculate EMA for
                O = Open, H = High, L = Low, C = Close, V = Volume
            period (int): Number of periods/bars to calculate the moving average
            interval_type (Literal['1min', '5min', '15min']): Type of time interval
            timeinterval_id (int): The starting point (time interval ID) from where to calculate
            
        Returns:
            float: The calculated EMA value, or None if not enough data points
            
        Example:
            >>> ta = TechnicalAnalysis()
            >>> ema = ta.calculate_ema('AAPL', 'C', '5min', 1000)
            >>> print(ema)
            150.25
        """
        # Get the current time interval
        current_interval = self.db.session.query(TimeInterval).filter(
            TimeInterval.id == timeinterval_id
        ).first()
        
        if not current_interval:
            return None
        
        # Convert interval_type to minutes for time calculation
        ticker_time = int(interval_type.replace('min', ''))
        
        # Calculate the start time for the period
        start_time = current_interval.start_time - timedelta(minutes=ticker_time * period * 2)
        
        # Query the required time intervals
        intervals = self.db.session.query(TimeInterval).filter(
            and_(
                TimeInterval.symbol_id == current_interval.symbol_id,
                TimeInterval.start_time >= start_time,
                TimeInterval.start_time <= current_interval.start_time,
                TimeInterval.interval_type == interval_type
            )
        ).order_by(TimeInterval.start_time.asc()).all()
        
        if len(intervals) < period:
            return None
        
        # Extragem valorile în funcție de tip
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
        
        # Calculăm factorul de multiplicare (2/(period + 1))
        multiplier = 2 / (period + 1)
        
        # Calculăm SMA pentru prima perioadă ca valoare inițială pentru EMA
        sma = sum(values[:period]) / period
        
        # Calculăm EMA folosind formula corectă
        ema = sma
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema * (1 - multiplier))
            
        return ema

    def calculate_adjusted_sma(
        self,
        type: Literal['O', 'H', 'L', 'C', 'V'],
        period: int,
        interval_type: Literal['1min', '5min', '15min'],
        timeinterval_id: int
    ) -> float:
        """
        Calculate Adjusted Simple Moving Average (SMA) for a given symbol and time interval.
        This is particularly useful for volume analysis as it removes outliers.
        
        Formula: [sum(V1, V2,...Vi,...,Vn) - maxVi - minVi]/(n-2)
        
        Args:
            type (Literal['O', 'H', 'L', 'C', 'V']): Type of data to calculate adjusted SMA for
                O = Open, H = High, L = Low, C = Close, V = Volume
            period (int): Number of periods/bars to calculate the moving average
            interval_type (Literal['1min', '5min', '15min']): Type of time interval
            timeinterval_id (int): The starting point (time interval ID) from where to calculate
            
        Returns:
            float: The calculated adjusted SMA value, or None if not enough data points
            
        Example:
            >>> ta = TechnicalAnalysis()
            >>> adjusted_sma = ta.calculate_adjusted_sma('V', 20, '5min', 1000)
            >>> print(adjusted_sma)
            150.25
        """
        # Get the current time interval
        current_interval = self.db.session.query(TimeInterval).filter(
            TimeInterval.id == timeinterval_id
        ).first()
        
        if not current_interval:
            return None
        
        # Convert interval_type to minutes for time calculation
        ticker_time = int(interval_type.replace('min', ''))
        
        # Calculate the start time for the period
        start_time = current_interval.start_time - timedelta(minutes=ticker_time * period)
        
        # Query the required time intervals
        intervals = self.db.session.query(TimeInterval).filter(
            and_(
                TimeInterval.symbol_id == current_interval.symbol_id,
                TimeInterval.start_time >= start_time,
                TimeInterval.start_time <= current_interval.start_time,
                TimeInterval.interval_type == interval_type
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
        
        # Calculate adjusted SMA by removing max and min values
        total_sum = sum(values)
        max_value = max(values)
        min_value = min(values)
        
        # Apply the formula: [sum - max - min]/(n-2)
        return (total_sum - max_value - min_value) / (period - 2)

    def calculate_stdv(
        self,
        type: Literal['O', 'H', 'L', 'C', 'V'],
        period: int,
        interval_type: Literal['1min', '5min', '15min'],
        timeinterval_id: int
    ) -> float:
        """
        Calculate Standard Deviation (STDV) for a given symbol and time interval.
        Standard Deviation measures the amount of variation or dispersion in a set of values.
        
        Formula: σ = √(Σ(x - μ)² / n)
        where:
        - σ (sigma) is the standard deviation
        - x is each value in the dataset
        - μ (mu) is the mean of the dataset
        - n is the number of values
        
        Args:
            type (Literal['O', 'H', 'L', 'C', 'V']): Type of data to calculate STDV for
                O = Open, H = High, L = Low, C = Close, V = Volume
            period (int): Number of periods/bars to calculate the standard deviation
            interval_type (Literal['1min', '5min', '15min']): Type of time interval
            timeinterval_id (int): The starting point (time interval ID) from where to calculate
            
        Returns:
            float: The calculated standard deviation value, or None if not enough data points
            
        Example:
            >>> ta = TechnicalAnalysis()
            >>> stdv = ta.calculate_stdv('C', 20, '5min', 1000)
            >>> print(stdv)
            2.5
        """
        # Get the current time interval
        current_interval = self.db.session.query(TimeInterval).filter(
            TimeInterval.id == timeinterval_id
        ).first()
        
        if not current_interval:
            return None
        
        # Convert interval_type to minutes for time calculation
        ticker_time = int(interval_type.replace('min', ''))
        
        # Calculate the start time for the period
        start_time = current_interval.start_time - timedelta(minutes=ticker_time * period)
        
        # Query the required time intervals
        intervals = self.db.session.query(TimeInterval).filter(
            and_(
                TimeInterval.symbol_id == current_interval.symbol_id,
                TimeInterval.start_time >= start_time,
                TimeInterval.start_time <= current_interval.start_time,
                TimeInterval.interval_type == interval_type
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
        
        # Calculate the mean (μ)
        mean = sum(values) / len(values)
        
        # Calculate the sum of squared differences from mean
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        
        # Calculate standard deviation
        stdv = (squared_diff_sum / len(values)) ** 0.5
        
        return stdv

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