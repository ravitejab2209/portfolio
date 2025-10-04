"""
Main application routes
"""
import os
from flask import Blueprint, render_template, send_file, jsonify, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main portfolio page"""
    return render_template('portfolio.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'message': 'Portfolio app is running',
        'version': '1.0.0'
    }), 200

@main_bp.route('/download-resume')
def download_resume():
    """Download resume file"""
    try:
        # Get the current working directory and construct the path
        current_dir = os.getcwd()
        
        # Try the actual filename with spaces first
        resume_path = os.path.join(current_dir, 'assets', 'Raviteja_B_Resume.pdf')
        
        print(f"Looking for resume at: {resume_path}")
        print(f"File exists: {os.path.exists(resume_path)}")
        
        if os.path.exists(resume_path):
            return send_file(
                resume_path,
                as_attachment=True,
                download_name='Raviteja_B_Resume.pdf',
                mimetype='application/pdf'
            )
        else:
            # Try without spaces as fallback
            alt_path = os.path.join(current_dir, 'assets', 'Raviteja_B_Resume.pdf')
            print(f"Trying alternative path: {alt_path}")
            
            if os.path.exists(alt_path):
                return send_file(
                    alt_path,
                    as_attachment=True,
                    download_name='Raviteja_B_Resume.pdf',
                    mimetype='application/pdf'
                )
            else:
                return jsonify({'error': f'Resume file not found at {resume_path} or {alt_path}'}), 404
                
    except Exception as e:
        print(f"Resume download error: {e}")
        return jsonify({'error': f'Failed to download resume: {str(e)}'}), 500 