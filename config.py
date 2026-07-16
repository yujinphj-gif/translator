"""
MSSQL 연결 설정을 위한 설정 파일
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """기본 설정"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    DEBUG = False
    TESTING = False
    
    # Flask-SocketIO 설정
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """테스트 환경 설정"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# MSSQL 설정
MSSQL_CONFIG = {
    'server': os.getenv('MSSQL_SERVER', 'localhost'),
    'database': os.getenv('MSSQL_DATABASE', 'EnglishChatDB'),
    'username': os.getenv('MSSQL_USERNAME', 'sa'),
    'password': os.getenv('MSSQL_PASSWORD', ''),
    'driver': os.getenv('MSSQL_DRIVER', '{ODBC Driver 17 for SQL Server}'),
}

# 번역 서비스 설정
TRANSLATOR_TYPE = os.getenv('TRANSLATOR_TYPE', 'none')  # google, azure, papago, none

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env: str = None):
    """환경에 맞는 설정 반환"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
