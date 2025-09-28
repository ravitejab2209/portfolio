"""
Application Configuration Settings
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Application settings
    RESUME_PATH = os.path.join(os.getcwd(), 'assets', 'Raviteja_B_Resume.pdf')
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-set-secret-key-in-production' 