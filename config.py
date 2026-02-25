"""
ARL-ET Configuration Module
Centralized configuration with environment variable fallbacks
"""
import os
import logging
from dataclasses import dataclass
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "arl-et-production")
    credentials_path: str = os.getenv("FIREBASE_CREDENTIALS", "./firebase-credentials.json")
    collection_prefix: str = os.getenv("FIREBASE_COLLECTION_PREFIX", "ARLET_")
    
    def validate(self) -> bool:
        """Validate Firebase configuration"""
        if not self.project_id:
            logging.error("FIREBASE_PROJECT_ID not configured")
            return False
        if not os.path.exists(self.credentials_path):
            logging.error(f"Firebase credentials not found at {self.credentials_path}")
            return False
        return True

@dataclass  
class TradingConfig:
    """Trading system configuration"""
    default_exchange: str = os.getenv("DEFAULT_EXCHANGE", "binance")
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "BTC/USDT")
    data_timeframe: str = os.getenv("DATA_TIMEFRAME", "1h")
    max_position_size: float = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
    risk_per_trade: float = float(os.getenv("RISK_PER_TRADE", "0.02"))
    
@dataclass
class RLConfig:
    """Reinforcement Learning configuration"""
    learning_rate: float = float(os.getenv("RL_LEARNING_RATE", "0.001"))
    discount_factor: float = float(os.getenv("RL_DISCOUNT_FACTOR", "0.95"))
    exploration_rate: float = float(os.getenv("RL_EXPLORATION_RATE", "0.1"))
    batch_size: int = int(os.getenv("RL_BATCH_SIZE", "32"))
    memory_size: int = int(os.getenv("RL_MEMORY_SIZE", "10000"))

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = os.getenv("LOG_FILE", "arl_et.log")

class ARLETConfig:
    """Main configuration orchestrator"""
    def __init__(self):
        self.firebase = FirebaseConfig()
        self.trading = TradingConfig()
        self.rl = RLConfig()
        self.logging = LoggingConfig()
        
    def validate_all(self) -> Dict[str, bool]:
        """Validate all configurations"""
        return {
            "firebase": self.firebase.validate(),
            "trading": self._validate_trading(),
            "rl": self._validate_rl()
        }
    
    def _validate_trading(self) -> bool:
        """Validate trading configuration"""
        if self.trading.max_position_size <= 0:
            logging.error("MAX_POSITION_SIZE must be positive")
            return False
        if not 0 < self.trading.risk_per_trade <= 1:
            logging.error("RISK_PER_TRADE must be between 0 and 1")
            return False
        return True
    
    def _validate_rl(self) -> bool:
        """Validate RL configuration"""
        if not 0 < self.rl.learning_rate <= 1:
            logging.error("RL_LEARNING_RATE must be between 0 and 1")
            return False
        if not 0 <= self.rl.exploration_rate <= 1:
            logging.error("RL_EXPLORATION_RATE must be between 0 and 1")
            return False
        return True

# Global configuration instance
config = ARLETConfig()