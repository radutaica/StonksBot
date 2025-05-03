"""
Test file for TechnicalAnalysis class.
"""
import unittest
from datetime import datetime, timedelta
from database import Database, Symbol, TimeInterval
from tests.utils import TechnicalAnalysis

class TestTechnicalAnalysis(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test."""
        self.db = Database()
        self.ta = TechnicalAnalysis()
        
        # Create a test symbol
        self.symbol = Symbol(
            symbol='TEST',
            company_name='Test Company',
            is_active=True
        )
        self.db.session.add(self.symbol)
        self.db.session.commit()
        
        # Create test time intervals
        base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        for i in range(30):  # Create 30 minutes of data
            interval = TimeInterval(
                symbol_id=self.symbol.id,
                start_time=base_time - timedelta(minutes=i),
                end_time=base_time - timedelta(minutes=i-1),
                open=100.0 + i,
                high=105.0 + i,
                low=95.0 + i,
                close=102.0 + i,
                volume=1000 + i
            )
            self.db.session.add(interval)
        self.db.session.commit()
        
        # Store the first interval ID for testing
        self.first_interval = self.db.session.query(TimeInterval)\
            .filter(TimeInterval.symbol_id == self.symbol.id)\
            .order_by(TimeInterval.start_time.desc())\
            .first()
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove test data
        self.db.session.query(TimeInterval).filter(
            TimeInterval.symbol_id == self.symbol.id
        ).delete()
        self.db.session.query(Symbol).filter(
            Symbol.symbol == 'TEST'
        ).delete()
        self.db.session.commit()
        self.db.close()
    
    def test_calculate_sma(self):
        """Test SMA calculation for different types of data."""
        # Test SMA for close prices
        sma_close = self.ta.calculate_sma(
            'TEST',
            'C',
            period=20,
            ticker_time=1,
            timeinterval_id=self.first_interval.id
        )
        self.assertIsNotNone(sma_close)
        self.assertIsInstance(sma_close, float)
        
        # Test SMA for volume
        sma_volume = self.ta.calculate_sma(
            'TEST',
            'V',
            period=20,
            ticker_time=1,
            timeinterval_id=self.first_interval.id
        )
        self.assertIsNotNone(sma_volume)
        self.assertIsInstance(sma_volume, float)
        
        # Test with invalid timeinterval_id
        invalid_sma = self.ta.calculate_sma(
            'TEST',
            'C',
            period=20,
            ticker_time=1,
            timeinterval_id=999999
        )
        self.assertIsNone(invalid_sma)

    def test_calculate_sma_aapl(self):
        """Test SMA calculation for AAPL stock data."""
        # Get the most recent AAPL interval
        latest_interval = self.db.session.query(TimeInterval)\
            .join(Symbol)\
            .filter(Symbol.symbol == 'AAPL')\
            .order_by(TimeInterval.start_time.desc())\
            .first()
            
        self.assertIsNotNone(latest_interval, "No AAPL data found in database")
        
        # Calculate 5-minute SMA for different metrics
        periods = [5, 10, 20]  # Test different periods
        metrics = ['O', 'H', 'L', 'C', 'V']  # Test all available metrics
        
        print("\nTesting AAPL SMAs:")
        print("-" * 50)
        
        for period in periods:
            print(f"\nPeriod: {period} intervals")
            for metric in metrics:
                sma = self.ta.calculate_sma(
                    'AAPL',
                    metric,
                    period=period,
                    ticker_time=1,  # 1-minute intervals
                    timeinterval_id=latest_interval.id
                )
                
                self.assertIsNotNone(sma)
                self.assertIsInstance(sma, float)
                
                # Print the results
                metric_names = {
                    'O': 'Open',
                    'H': 'High',
                    'L': 'Low',
                    'C': 'Close',
                    'V': 'Volume'
                }
                print(f"{metric_names[metric]} SMA: {sma:.2f}")
        
        # Test with different time intervals
        print("\nTesting different time intervals:")
        intervals = [1, 5, 15]  # 1-min, 5-min, 15-min
        for interval in intervals:
            sma = self.ta.calculate_sma(
                'AAPL',
                'C',  # Using close price
                period=20,
                ticker_time=interval,
                timeinterval_id=latest_interval.id
            )
            self.assertIsNotNone(sma)
            print(f"{interval}-minute interval SMA(20): {sma:.2f}")

if __name__ == '__main__':
    unittest.main() 