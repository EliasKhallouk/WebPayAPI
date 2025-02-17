import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
