"""
Portfolio Application Package
"""
from flask import Flask
from flask_cors import CORS
from app.config.settings import Config

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.api.routes import api_bp
    from app.api.main_routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app 