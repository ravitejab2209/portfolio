"""
AI Client Utilities for Gemini and Groq APIs
"""
import os
from flask import current_app

# Try to import AI libraries
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not available - install with: pip install google-generativeai")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq not available - install with: pip install groq")

class AIClientManager:
    """Manages AI client connections and requests"""
    
    def __init__(self, app=None):
        self.gemini_client = None
        self.groq_client = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app context"""
        with app.app_context():
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients with robust error handling"""
        try:
            # Configure Gemini (same approach as working chatbot)
            if GEMINI_AVAILABLE:
                gemini_key = None
                try:
                    gemini_key = current_app.config.get('GEMINI_API_KEY')
                except RuntimeError:
                    pass
                
                if not gemini_key:
                    gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
                
                if gemini_key:
                    try:
                        genai.configure(api_key=gemini_key)
                        self.gemini_client = genai
                        print("✅ Gemini client initialized")
                        
                        # Test the connection with working model
                        if self._test_gemini_connection():
                            print("✅ Gemini connection verified")
                        else:
                            print("⚠️ Gemini connection test failed but client initialized")
                        
                    except Exception as e:
                        print(f"❌ Gemini initialization failed: {e}")
                        self.gemini_client = None
                else:
                    print("⚠️ Gemini API key not found in config or environment")
            
            # Configure Groq (same approach as working chatbot)
            if GROQ_AVAILABLE:
                groq_key = None
                try:
                    groq_key = current_app.config.get('GROQ_API_KEY')
                except RuntimeError:
                    pass
                
                if not groq_key:
                    groq_key = os.getenv('GROQ_API_KEY')
                
                if groq_key:
                    try:
                        self.groq_client = Groq(api_key=groq_key)
                        print("✅ Groq client initialized")
                        
                        # Test the connection with working model
                        if self._test_groq_connection():
                            print("✅ Groq connection verified")
                        else:
                            print("⚠️ Groq connection test failed but client initialized")
                        
                    except Exception as e:
                        print(f"❌ Groq initialization failed: {e}")
                        self.groq_client = None
                else:
                    print("⚠️ Groq API key not found in config or environment")
                    
        except Exception as e:
            print(f"❌ Client initialization error: {e}")
            self.gemini_client = None
            self.groq_client = None
    
    def _test_gemini_connection(self):
        """Test Gemini connection with a simple request"""
        try:
            # Use the working model for testing
            model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
            response = model.generate_content("Hello", 
                generation_config={
                    'max_output_tokens': 10,
                    'temperature': 0.1
                }
            )
            if response and response.text:
                print("✅ Gemini connection test successful")
                return True
        except Exception as e:
            print(f"❌ Gemini connection test failed: {e}")
            return False
    
    def _test_groq_connection(self):
        """Test Groq connection with a simple request"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="llama-3.1-8b-instant",
                max_tokens=10
            )
            if chat_completion and chat_completion.choices:
                print("✅ Groq connection test successful")
                return True
        except Exception as e:
            print(f"❌ Groq connection test failed: {e}")
            return False
    
    def get_gemini_response(self, prompt):
        """Get response from Gemini API with automatic retry"""
        if not self.gemini_client:
            print("⚠️ Gemini client not available, attempting to reinitialize...")
            self._initialize_clients()
            if not self.gemini_client:
                print("❌ Gemini client still not available after reinitialize")
                return None
        
        # Updated model list with working models (tested and verified)
        gemini_models = [
            'models/gemini-2.0-flash-exp',     # ✅ Working! Primary choice - no quota issues
            'models/gemini-exp-1206',          # Experimental model - backup
            'models/gemini-2.0-flash-001',     # Stable version - backup
            'models/gemini-2.0-flash'           # Medium fallback
        ]
        
        for model_name in gemini_models:
            try:
                model = self.gemini_client.GenerativeModel(model_name)
                ai_response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.7,
                        'max_output_tokens': 1000,
                        'top_p': 0.8,
                        'top_k': 40
                    }
                )
                
                # Better response validation (same as working chatbot)
                if ai_response and hasattr(ai_response, 'text') and ai_response.text:
                    print(f"✅ Gemini response successful with model: {model_name}")
                    return ai_response.text.strip()
                elif ai_response and hasattr(ai_response, 'candidates') and ai_response.candidates:
                    # Handle cases where text is in candidates
                    try:
                        text = ai_response.candidates[0].content.parts[0].text
                        if text:
                            print(f"✅ Gemini response successful with model: {model_name}")
                            return text.strip()
                    except (IndexError, AttributeError):
                        pass
                else:
                    print(f"⚠️ Empty response from Gemini model: {model_name}")
                    continue  # Try next model
            except Exception as e:
                error_msg = str(e).lower()
                if "429" in str(e) or "quota" in error_msg or "rate_limit" in error_msg:
                    print(f"⚠️ Gemini quota/rate limit exceeded with {model_name}, trying next model...")
                elif "404" in str(e) or "not found" in error_msg:
                    print(f"⚠️ Model {model_name} not found, trying next model...")
                elif "invalid api key" in error_msg or "authentication" in error_msg:
                    print(f"❌ Gemini API key invalid or expired")
                    break  # No point trying other models with bad key
                else:
                    print(f"❌ Gemini API Error with {model_name}: {e}")
                continue
        
        print("❌ All Gemini models failed")
        return None
    
    def get_groq_response(self, messages):
        """Get response from Groq API with automatic retry"""
        if not self.groq_client:
            print("⚠️ Groq client not available, attempting to reinitialize...")
            self._initialize_clients()
            if not self.groq_client:
                print("❌ Groq client still not available after reinitialize")
                return None
        
        # Validate messages format
        if not isinstance(messages, list):
            print("❌ Messages must be a list")
            return None
        
        # Updated model list with current working models (tested and verified)
        groq_models = [
            "llama-3.1-8b-instant",      # ✅ Working! Primary choice
            "llama-3.1-70b-versatile",   # Backup - more capable
            "llama-3.2-1b-preview",      # Lightweight fallback
            "llama-3.2-3b-preview",      # Medium fallback
            "mixtral-8x7b-32768",        # Alternative architecture
            "gemma2-9b-it"               # Final fallback
        ]
        
        for model_name in groq_models:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=0.9
                )
                if chat_completion and chat_completion.choices and len(chat_completion.choices) > 0:
                    content = chat_completion.choices[0].message.content
                    if content:
                        print(f"✅ Groq response successful with model: {model_name}")
                        return content.strip()
                    else:
                        print(f"⚠️ Empty response from Groq model: {model_name}")
                        continue  # Try next model
            except Exception as e:
                error_msg = str(e).lower()
                if "rate_limit" in error_msg or "429" in str(e):
                    print(f"⚠️ Groq rate limit with {model_name}, trying next model...")
                elif "invalid api key" in error_msg or "authentication" in error_msg:
                    print(f"❌ Groq API key invalid or expired")
                    break  # No point trying other models with bad key
                else:
                    print(f"❌ Groq API Error with {model_name}: {e}")
                continue
        
        print("❌ All Groq models failed")
        return None
    
    def test_gemini_models(self):
        """Test and list available Gemini models"""
        if not GEMINI_AVAILABLE or not current_app.config.get('GEMINI_API_KEY'):
            return []
        
        try:
            available_models = []
            for model in self.gemini_client.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            return available_models
        except Exception as e:
            print(f"❌ Error listing Gemini models: {e}")
            return []

    def debug_status(self):
        """Print debug information about the current status"""
        print("\n=== AI Client Debug Status ===")
        print(f"Gemini Available: {GEMINI_AVAILABLE}")
        print(f"Groq Available: {GROQ_AVAILABLE}")
        print(f"Gemini Client: {'✅ Initialized' if self.gemini_client else '❌ Not initialized'}")
        print(f"Groq Client: {'✅ Initialized' if self.groq_client else '❌ Not initialized'}")
        
        # Check environment variables
        print("\n=== Environment Variables ===")
        gemini_keys = ['GEMINI_API_KEY', 'GOOGLE_API_KEY']
        groq_keys = ['GROQ_API_KEY']
        
        for key in gemini_keys:
            value = os.getenv(key)
            print(f"{key}: {'✅ Set' if value else '❌ Not set'}")
        
        for key in groq_keys:
            value = os.getenv(key)
            print(f"{key}: {'✅ Set' if value else '❌ Not set'}")
        
        # Check Flask config (if in app context)
        try:
            print("\n=== Flask Config ===")
            print(f"GEMINI_API_KEY in config: {'✅ Set' if current_app.config.get('GEMINI_API_KEY') else '❌ Not set'}")
            print(f"GROQ_API_KEY in config: {'✅ Set' if current_app.config.get('GROQ_API_KEY') else '❌ Not set'}")
        except RuntimeError:
            print("\n=== Flask Config ===")
            print("❌ Not in Flask app context")
        
        print("================================\n")

# Global AI client manager instance
ai_manager = None

def get_ai_manager(app=None):
    """Get or create AI manager instance"""
    global ai_manager
    if ai_manager is None:
        ai_manager = AIClientManager(app)
    return ai_manager

# Helper function to initialize with app
def init_ai_clients(app):
    """Initialize AI clients with Flask app"""
    manager = get_ai_manager()
    manager.init_app(app)
    return manager 