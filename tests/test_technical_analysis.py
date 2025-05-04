"""
Test file for TechnicalAnalysis class.
"""
import unittest
from datetime import datetime, timedelta
from database import Database, Symbol, TimeInterval
from tests.utils import TechnicalAnalysis

class TestTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.db = Database()
        self.ta = TechnicalAnalysis()
    
    def tearDown(self):
        """Clean up after each test."""
        self.db.close()
    
    def test_calculate_sma_aapl(self):
        """Test SMA and EMA calculations for AAPL stock data."""
        # Get the most recent AAPL interval
        latest_interval = self.db.session.query(TimeInterval)\
            .join(Symbol)\
            .filter(Symbol.symbol == 'AAPL')\
            .order_by(TimeInterval.start_time.desc())\
            .first()
            
        self.assertIsNotNone(latest_interval, "No AAPL data found in database")
        
        # Calculate SMA and EMA for different metrics
        periods = [5, 10, 20]  # Test different periods
        metrics = ['O', 'H', 'L', 'C', 'V']  # Test all available metrics
        
        print("\nTesting AAPL Technical Indicators:")
        print("-" * 50)
        
        for period in periods:
            print(f"\nPeriod: {period} intervals")
            for metric in metrics:
                # Calculate SMA
                sma = self.ta.calculate_sma(
                    metric,
                    period=period,
                    ticker_time=1,  # 1-minute intervals
                    timeinterval_id=latest_interval.id
                )
                
                # Calculate EMA
                ema = self.ta.calculate_ema(
                    metric,
                    period=period,
                    ticker_time=1,  # 1-minute intervals
                    timeinterval_id=latest_interval.id
                )
                
                self.assertIsNotNone(sma)
                self.assertIsNotNone(ema)
                self.assertIsInstance(sma, float)
                self.assertIsInstance(ema, float)
                
                # Print the results
                metric_names = {
                    'O': 'Open',
                    'H': 'High',
                    'L': 'Low',
                    'C': 'Close',
                    'V': 'Volume'
                }
                print(f"{metric_names[metric]}:")
                print(f"  SMA: {sma:.2f}")
                print(f"  EMA: {ema:.2f}")
                print(f"  Diff: {abs(sma - ema):.2f}")
        
        # Test with different time intervals
        print("\nTesting different time intervals:")
        intervals = [1, 5, 15]  # 1-min, 5-min, 15-min
        for interval in intervals:
            sma = self.ta.calculate_sma(
                'C',  # Using close price
                period=20,
                ticker_time=interval,
                timeinterval_id=latest_interval.id
            )
            ema = self.ta.calculate_ema(
                'C',  # Using close price
                period=20,
                ticker_time=interval,
                timeinterval_id=latest_interval.id
            )
            self.assertIsNotNone(sma)
            self.assertIsNotNone(ema)
            print(f"{interval}-minute interval:")
            print(f"  SMA(20): {sma:.2f}")
            print(f"  EMA(20): {ema:.2f}")
            print(f"  Diff: {abs(sma - ema):.2f}")

    def test_calculate_adjusted_sma(self):
        """Test adjusted SMA calculations for AAPL stock data."""
        # Get the most recent AAPL interval
        latest_interval = self.db.session.query(TimeInterval)\
            .join(Symbol)\
            .filter(Symbol.symbol == 'AAPL')\
            .order_by(TimeInterval.start_time.desc())\
            .first()
            
        self.assertIsNotNone(latest_interval, "No AAPL data found in database")
        
        # Test periods
        periods = [5, 10, 20]
        
        print("\nTesting AAPL Adjusted SMA:")
        print("-" * 50)
        
        for period in periods:
            # Calculate regular SMA and adjusted SMA for volume
            regular_sma = self.ta.calculate_sma(
                'V',  # Volume
                period=period,
                ticker_time=1,  # 1-minute intervals
                timeinterval_id=latest_interval.id
            )
            
            adjusted_sma = self.ta.calculate_adjusted_sma(
                'V',  # Volume
                period=period,
                ticker_time=1,  # 1-minute intervals
                timeinterval_id=latest_interval.id
            )
            
            self.assertIsNotNone(regular_sma)
            self.assertIsNotNone(adjusted_sma)
            self.assertIsInstance(regular_sma, float)
            self.assertIsInstance(adjusted_sma, float)
            
            # The adjusted SMA should be different from regular SMA
            self.assertNotEqual(regular_sma, adjusted_sma)
            
            print(f"\nPeriod: {period} intervals")
            print(f"Regular SMA: {regular_sma:.2f}")
            print(f"Adjusted SMA: {adjusted_sma:.2f}")
            print(f"Difference: {abs(regular_sma - adjusted_sma):.2f}")
            
            # Test with different time intervals
            print("\nTesting different time intervals:")
            intervals = [1, 5, 15]  # 1-min, 5-min, 15-min
            for interval in intervals:
                adjusted_sma = self.ta.calculate_adjusted_sma(
                    'V',  # Volume
                    period=period,
                    ticker_time=interval,
                    timeinterval_id=latest_interval.id
                )
                self.assertIsNotNone(adjusted_sma)
                print(f"{interval}-minute interval:")
                print(f"  Adjusted SMA({period}): {adjusted_sma:.2f}")

if __name__ == '__main__':
    unittest.main() 