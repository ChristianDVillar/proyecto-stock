"""
Configuration management for different environments
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES_DAYS = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_DAYS', '1'))
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10
    }
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    
    # JWT
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ERROR_MESSAGE_KEY = 'error'
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_SESSION_COOKIE = False
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize app with config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # SQLite for development
    DATABASE_URI = os.environ.get('DATABASE_URI')
    if not DATABASE_URI:
        INSTANCE_DIR.mkdir(exist_ok=True)
        db_path = INSTANCE_DIR / 'mi_base_datos.db'
        DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = False
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    SECRET_KEY = 'test-secret-key'
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # PostgreSQL for production
    _DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = _DATABASE_URI if _DATABASE_URI else 'sqlite:///instance/prod.db'  # Fallback para desarrollo
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = 'None'
    
    # Security
    _SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = _SECRET_KEY if _SECRET_KEY else 'prod-secret-key-change-me'  # Fallback para desarrollo
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    
    # Rate limiting with Redis in production
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/0')
    
    @staticmethod
    def init_app(app):
        """Validate production settings"""
        if not ProductionConfig._DATABASE_URI:
            import warnings
            warnings.warn("DATABASE_URI not set in production, using SQLite fallback", UserWarning)
        if not ProductionConfig._SECRET_KEY:
            import warnings
            warnings.warn("SECRET_KEY not set in production, using default", UserWarning)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Class method to get config
Config.get_config = lambda name: config.get(name, config['default'])
