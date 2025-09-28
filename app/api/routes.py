"""
API routes for chat functionality
"""
import json
import time
from flask import Blueprint, request, jsonify, Response
from app.utils.ai_clients import get_ai_manager
from app.utils.resume_context import RESUME_CONTEXT, get_smart_fallback_response

api_bp = Blueprint('api', __name__)

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat API requests"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get AI manager instance
        ai_manager = get_ai_manager()
        
        # Ensure clients are initialized
        if not ai_manager.gemini_client and not ai_manager.groq_client:
            print("⚠️ No AI clients initialized, reinitializing...")
            ai_manager._initialize_clients()
        
        response = None
        api_used = "fallback"
        
        print(f"🔍 Processing user message: {user_message[:50]}...")
        
        # Try Gemini first
        print("🤖 Trying Gemini API...")
        prompt = f"{RESUME_CONTEXT}\n\nUser Question: {user_message}\n\nPlease provide a helpful, professional response:"
        response = ai_manager.get_gemini_response(prompt)
        if response:
            api_used = "gemini"
        
        # Try Groq if Gemini failed
        if response is None:
            print("🤖 Trying Groq API...")
            messages = [
                {"role": "system", "content": RESUME_CONTEXT},
                {"role": "user", "content": user_message}
            ]
            response = ai_manager.get_groq_response(messages)
            if response:
                api_used = "groq"
        
        # Use fallback ONLY if both APIs completely failed
        if response is None:
            print(f"⚠️ All APIs failed, using smart fallback for: {user_message}")
            response = get_smart_fallback_response(user_message)
            api_used = "fallback"
        
        print(f"✅ Response generated using: {api_used}")
        
        return jsonify({
            'response': response,
            'status': 'success',
            'api_used': api_used
        })
        
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({
            'response': get_smart_fallback_response(user_message if 'user_message' in locals() else ''),
            'status': 'fallback'
        })

@api_bp.route('/chat-stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint for real-time response generation"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        def generate_response():
            """Generator function for streaming response"""
            ai_manager = get_ai_manager()

            # Ensure clients are initialized
            if not ai_manager.gemini_client and not ai_manager.groq_client:
                print("⚠️ No AI clients initialized, reinitializing...")
                ai_manager._initialize_clients()

            response = None
            api_used = "fallback"

            print(f"🔍 Processing user message: {user_message[:50]}...")

            # Try Gemini first
            print("🤖 Trying Gemini API...")
            prompt = f"{RESUME_CONTEXT}\n\nUser Question: {user_message}\n\nPlease provide a helpful, professional response:"
            response = ai_manager.get_gemini_response(prompt)
            if response:
                api_used = "gemini"

            # Try Groq if Gemini failed
            if response is None:
                print("🤖 Trying Groq API...")
                messages = [
                    {"role": "system", "content": RESUME_CONTEXT},
                    {"role": "user", "content": user_message}
                ]
                response = ai_manager.get_groq_response(messages)
                if response:
                    api_used = "groq"

            # Use fallback if both failed
            if response is None:
                print(f"⚠️ All APIs failed, using smart fallback for: {user_message}")
                response = get_smart_fallback_response(user_message)
                api_used = "fallback"

            print(f"✅ Response generated using: {api_used}")

            # Stream the response word by word for realistic typing effect
            words = response.split()
            
            for word in words:
                # Send chunk
                chunk_data = {
                    'chunk': word + " ",
                    'api_used': api_used,
                    'complete': False
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Add small delay for realistic typing speed (very fast but visible)
                time.sleep(0.03)  # 30ms between words - extremely fast
            
            # Send completion signal
            yield f"data: {json.dumps({'complete': True, 'api_used': api_used})}\n\n"
            yield "data: [DONE]\n\n"

        return Response(
            generate_response(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

    except Exception as e:
        print(f"Streaming Chat Error: {e}")
        def error_response():
            fallback = get_smart_fallback_response(user_message if 'user_message' in locals() else '')
            words = fallback.split()
            for word in words:
                yield f"data: {json.dumps({'chunk': word + ' ', 'api_used': 'fallback'})}\n\n"
                time.sleep(0.03)
            yield "data: [DONE]\n\n"
        
        return Response(
            error_response(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        ) 