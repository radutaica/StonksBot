from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import enum
from db_config import DATABASE_URL

Base = declarative_base()

class Symbol(Base):
    __tablename__ = 'symbols'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to TimeInterval
    intervals = relationship("TimeInterval", back_populates="symbol")

class TimeInterval(Base):
    __tablename__ = 'time_intervals'
    
    id = Column(Integer, primary_key=True)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Price data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Relationship to Symbol
    symbol = relationship("Symbol", back_populates="intervals")
    
    # Create composite index for efficient querying
    __table_args__ = (
        Index('idx_symbol_time', 'symbol_id', 'start_time'),
        Index('idx_time_range', 'start_time', 'end_time'),
    )

class Database:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_symbol(self, symbol, company_name=None):
        """Save or update a symbol"""
        existing_symbol = self.session.query(Symbol).filter(Symbol.symbol == symbol).first()
        if existing_symbol:
            existing_symbol.company_name = company_name
            existing_symbol.updated_at = datetime.utcnow()
        else:
            new_symbol = Symbol(
                symbol=symbol,
                company_name=company_name
            )
            self.session.add(new_symbol)
        self.session.commit()
    
    def save_time_interval(self, symbol, data):
        """Save time interval data to database"""
        symbol_obj = self.session.query(Symbol).filter(Symbol.symbol == symbol).first()
        if not symbol_obj:
            symbol_obj = Symbol(symbol=symbol)
            self.session.add(symbol_obj)
            self.session.commit()
        
        for index, row in data.iterrows():
            # Convert numpy types to Python native types
            time_interval = TimeInterval(
                symbol_id=symbol_obj.id,
                start_time=index,
                end_time=index + timedelta(minutes=1),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            self.session.add(time_interval)
        self.session.commit()
    
    def get_time_intervals(self, symbol, start_date=None, end_date=None):
        """Retrieve time intervals from database"""
        query = self.session.query(TimeInterval)\
            .join(Symbol)\
            .filter(Symbol.symbol == symbol)
        
        if start_date:
            query = query.filter(TimeInterval.start_time >= start_date)
        if end_date:
            query = query.filter(TimeInterval.end_time <= end_date)
        
        return query.order_by(TimeInterval.start_time).all()
    
    def get_latest_intervals(self, symbol, limit=100):
        """Get the most recent time intervals for a symbol"""
        return self.session.query(TimeInterval)\
            .join(Symbol)\
            .filter(Symbol.symbol == symbol)\
            .order_by(TimeInterval.start_time.desc())\
            .limit(limit)\
            .all()
    
    def save_analysis_result(self, symbol, start_date, end_date, strategy_name, parameters, performance_metrics):
        """Save analysis results to database"""
        symbol_obj = self.session.query(Symbol).filter(Symbol.symbol == symbol).first()
        if not symbol_obj:
            raise ValueError(f"Symbol {symbol} not found")
        
        result = AnalysisResult(
            symbol_id=symbol_obj.id,
            start_date=start_date,
            end_date=end_date,
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
            query = query.join(Symbol).filter(Symbol.symbol == symbol)
        if strategy_name:
            query = query.filter(AnalysisResult.strategy_name == strategy_name)
        return query.order_by(AnalysisResult.created_at.desc()).all()
    
    def close(self):
        """Close database connection"""
        self.session.close() 