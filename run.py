#!/usr/bin/env python3
"""
Portfolio Application - Main Entry Point
Run this file to start the portfolio server
"""

import os
from app import create_app

def check_setup():
    """Check API configuration and dependencies"""
    print("🤖 Portfolio AI Chatbot - Modular Architecture")
    print("=" * 55)
    
    # Check dependencies
    missing_deps = []
    try:
        import google.generativeai as genai
    except ImportError:
        missing_deps.append("google-generativeai")
    
    try:
        from groq import Groq
    except ImportError:
        missing_deps.append("groq")
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install " + " ".join(missing_deps))
    
    # Check API keys
    gemini_key = os.getenv('GEMINI_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    print("\n✅ API Configuration:")
    print(f"   Gemini API: {'✓ Configured' if gemini_key else '✗ Not configured'}")
    print(f"   Groq API: {'✓ Configured' if groq_key else '✗ Not configured'}")
    
    if not gemini_key and not groq_key:
        print("\n⚠️  No API keys configured - using fallback responses only")
        print("   Set environment variables:")
        print("   GEMINI_API_KEY=your_key_here")
        print("   GROQ_API_KEY=your_key_here")
    
    return True

def main():
    """Main application entry point"""
    check_setup()
    
    # Create Flask app
    app = create_app()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Check if we're in production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    debug_mode = not is_production
    
    print(f"\n🚀 Starting Portfolio Application...")
    print(f"   Environment: {'Production' if is_production else 'Development'}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug_mode}")
    
    try:
        # Initialize AI manager in a non-blocking way
        try:
            from app.utils.ai_clients import get_ai_manager
            with app.app_context():
                ai_manager = get_ai_manager(app)
                ai_manager.init_app(app)
                print("✅ AI Manager initialized")
                
                # Debug status (only in development)
                if not is_production:
                    ai_manager.debug_status()
        except Exception as ai_error:
            print(f"⚠️  AI Manager initialization failed: {ai_error}")
            print("   App will continue with fallback responses")
        
        # Start the server
        print(f"🌐 Server starting at http://{host}:{port}")
        app.run(
            debug=debug_mode,
            host=host,
            port=port,
            use_reloader=False  # Disable reloader for production
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        if not is_production:
            import traceback
            traceback.print_exc()
        # Exit with error code for Railway to detect failure
        exit(1)

if __name__ == '__main__':
    main() 