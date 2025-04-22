from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import numpy as np
from db_config import DATABASE_URL

Base = declarative_base()

class StockData(Base):
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # Technical indicators
    ma_fast = Column(Float)
    ma_slow = Column(Float)
    rsi = Column(Float)
    
    # Analysis results
    signal = Column(String)  # 'buy', 'sell', or 'hold'
    confidence = Column(Float)  # Confidence score for the signal

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    strategy_name = Column(String)
    parameters = Column(String)  # JSON string of strategy parameters
    performance_metrics = Column(String)  # JSON string of performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_stock_data(self, symbol, data):
        """Save stock data to database"""
        for index, row in data.iterrows():
            # Convert numpy types to Python native types
            stock_data = StockData(
                symbol=symbol,
                timestamp=index,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume']),
                ma_fast=float(row.get('MA_fast')) if 'MA_fast' in row else None,
                ma_slow=float(row.get('MA_slow')) if 'MA_slow' in row else None,
                rsi=float(row.get('RSI')) if 'RSI' in row else None
            )
            self.session.add(stock_data)
        self.session.commit()
    
    def get_stock_data(self, symbol, start_date=None, end_date=None):
        """Retrieve stock data from database"""
        query = self.session.query(StockData).filter(StockData.symbol == symbol)
        if start_date:
            query = query.filter(StockData.timestamp >= start_date)
        if end_date:
            query = query.filter(StockData.timestamp <= end_date)
        return query.order_by(StockData.timestamp).all()
    
    def save_analysis_result(self, symbol, strategy_name, parameters, performance_metrics):
        """Save analysis results to database"""
        result = AnalysisResult(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            strategy_name=strategy_name,
            parameters=parameters,
            performance_metrics=performance_metrics
        )
        self.session.add(result)
        self.session.commit()
    
    def get_analysis_results(self, symbol=None, strategy_name=None):
        """Retrieve analysis results from database"""
        query = self.session.query(AnalysisResult)
        if symbol:
            query = query.filter(AnalysisResult.symbol == symbol)
        if strategy_name:
            query = query.filter(AnalysisResult.strategy_name == strategy_name)
        return query.order_by(AnalysisResult.timestamp.desc()).all()
    
    def close(self):
        """Close database connection"""
        self.session.close() 