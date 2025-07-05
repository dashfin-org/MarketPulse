import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FinancialData(Base):
    """Store historical financial data"""
    __tablename__ = "financial_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    volume = Column(Float, default=0)
    data_type = Column(String(50), nullable=False)  # 'index', 'commodity', 'bond', 'vix', 'sector'
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class UserPreferences(Base):
    """Store user dashboard preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False, unique=True)
    auto_refresh = Column(Boolean, default=False)
    refresh_interval = Column(Integer, default=30)  # seconds
    favorite_symbols = Column(Text)  # JSON string of favorite symbols
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MarketAlerts(Base):
    """Store price alerts for symbols"""
    __tablename__ = "market_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(20), nullable=False)  # 'above', 'below'
    target_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Manage database operations for the finance dashboard"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def store_financial_data(self, symbol: str, data: Dict, data_type: str):
        """Store financial data in database"""
        session = None
        try:
            session = self.get_session()
            
            # Convert numpy types to Python native types
            price = float(data['price']) if data['price'] is not None else 0.0
            change = float(data['change']) if data['change'] is not None else 0.0
            change_pct = float(data['change_pct']) if data['change_pct'] is not None else 0.0
            volume = float(data.get('volume', 0))
            
            financial_record = FinancialData(
                symbol=symbol,
                price=price,
                change=change,
                change_pct=change_pct,
                volume=volume,
                data_type=data_type
            )
            
            session.add(financial_record)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error storing financial data for {symbol}: {str(e)}")
            if session:
                session.rollback()
                session.close()
    
    def get_historical_data(self, symbol: str, hours: int = 24) -> List[Dict]:
        """Get historical data for a symbol from the last N hours"""
        try:
            session = self.get_session()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            records = session.query(FinancialData).filter(
                FinancialData.symbol == symbol,
                FinancialData.timestamp >= cutoff_time
            ).order_by(FinancialData.timestamp.desc()).all()
            
            session.close()
            
            return [{
                'symbol': record.symbol,
                'price': record.price,
                'change': record.change,
                'change_pct': record.change_pct,
                'volume': record.volume,
                'timestamp': record.timestamp
            } for record in records]
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return []
    
    def save_user_preferences(self, user_id: str, preferences: Dict):
        """Save user preferences"""
        try:
            session = self.get_session()
            
            # Check if preferences exist
            existing = session.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if existing:
                # Update existing preferences
                for key, value in preferences.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new preferences
                user_prefs = UserPreferences(
                    user_id=user_id,
                    **preferences
                )
                session.add(user_prefs)
            
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error saving user preferences: {str(e)}")
            if session:
                session.rollback()
                session.close()
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            session = self.get_session()
            
            preferences = session.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            session.close()
            
            if preferences:
                return {
                    'auto_refresh': preferences.auto_refresh,
                    'refresh_interval': preferences.refresh_interval,
                    'favorite_symbols': preferences.favorite_symbols
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            return None
    
    def create_market_alert(self, user_id: str, symbol: str, alert_type: str, target_price: float):
        """Create a market alert"""
        try:
            session = self.get_session()
            
            alert = MarketAlerts(
                user_id=user_id,
                symbol=symbol,
                alert_type=alert_type,
                target_price=target_price
            )
            
            session.add(alert)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating market alert: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_active_alerts(self, user_id: str = None) -> List[Dict]:
        """Get active market alerts"""
        try:
            session = self.get_session()
            
            query = session.query(MarketAlerts).filter(MarketAlerts.is_active == True)
            if user_id:
                query = query.filter(MarketAlerts.user_id == user_id)
            
            alerts = query.all()
            session.close()
            
            return [{
                'id': str(alert.id),
                'user_id': alert.user_id,
                'symbol': alert.symbol,
                'alert_type': alert.alert_type,
                'target_price': alert.target_price,
                'created_at': alert.created_at
            } for alert in alerts]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {str(e)}")
            return []
    
    def check_alerts(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check if any alerts should be triggered"""
        triggered_alerts = []
        
        try:
            active_alerts = self.get_active_alerts()
            
            for alert in active_alerts:
                symbol = alert['symbol']
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    target_price = alert['target_price']
                    alert_type = alert['alert_type']
                    
                    triggered = False
                    if alert_type == 'above' and current_price >= target_price:
                        triggered = True
                    elif alert_type == 'below' and current_price <= target_price:
                        triggered = True
                    
                    if triggered:
                        triggered_alerts.append({
                            'alert_id': alert['id'],
                            'symbol': symbol,
                            'current_price': current_price,
                            'target_price': target_price,
                            'alert_type': alert_type,
                            'user_id': alert['user_id']
                        })
                        
                        # Deactivate the alert
                        self.deactivate_alert(alert['id'])
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
        
        return triggered_alerts
    
    def deactivate_alert(self, alert_id: str):
        """Deactivate a market alert"""
        try:
            session = self.get_session()
            
            alert = session.query(MarketAlerts).filter(
                MarketAlerts.id == uuid.UUID(alert_id)
            ).first()
            
            if alert:
                alert.is_active = False
                session.commit()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error deactivating alert {alert_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
    
    def get_market_statistics(self) -> Dict:
        """Get market statistics from stored data"""
        try:
            session = self.get_session()
            
            # Get latest data for each symbol type
            stats = {}
            
            # Count of stored records by type
            for data_type in ['index', 'commodity', 'bond', 'vix', 'sector']:
                count = session.query(FinancialData).filter(
                    FinancialData.data_type == data_type
                ).count()
                stats[f'{data_type}_records'] = count
            
            # Most volatile symbols (highest average absolute change)
            from sqlalchemy import func
            volatile_query = session.query(
                FinancialData.symbol,
                func.avg(func.abs(FinancialData.change_pct)).label('avg_volatility')
            ).group_by(FinancialData.symbol).order_by(
                func.avg(func.abs(FinancialData.change_pct)).desc()
            ).limit(5).all()
            
            stats['most_volatile'] = [
                {'symbol': row.symbol, 'avg_volatility': float(row.avg_volatility)}
                for row in volatile_query
            ]
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            return {}

# Initialize database manager
db_manager = DatabaseManager()