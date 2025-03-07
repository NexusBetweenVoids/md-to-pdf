"""
Markdown to PDF Converter - Web Application

This module provides a Flask-based web interface for converting Markdown files to PDF.
It allows users to either upload a Markdown file or enter Markdown text directly,
then converts it to a styled PDF document.

Author: NexusBetweenVoids (Original concept)
        Claude AI (Implementation assistance)
License: GPLv3
"""

import os
import uuid
import logging
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from converter import convert_md_to_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload size
app.config['DEBUG'] = False  # Set to False for production
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logger.info(f"Upload directory ready: {app.config['UPLOAD_FOLDER']}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """
    Endpoint to handle PDF conversion requests.
    
    Accepts either file upload or direct text input, processes the markdown,
    and returns the generated PDF for download.
    """
    try:
        # Check if the user provided a file or direct text input
        md_file = request.files.get('md_file')
        md_content = request.form.get('md_content')
        include_toc = request.form.get('include_toc') == 'on'
        
        if not md_file and not md_content:
            flash('Please provide either a Markdown file or direct text input.')
            return redirect(url_for('index'))
        
        # Generate unique filename for the output PDF
        output_filename = f"{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Process uploaded file if provided
        original_filename = 'document'  # Default name
        if md_file:
            original_filename = secure_filename(md_file.filename)
            # Check if it's a markdown file
            if not original_filename.lower().endswith(('.md', '.markdown')):
                flash('Only Markdown files (.md, .markdown) are allowed.')
                return redirect(url_for('index'))
            
            # Read content from file
            try:
                md_content = md_file.read().decode('utf-8')
                logger.info(f"Processing uploaded file: {original_filename}")
            except UnicodeDecodeError:
                flash('The uploaded file is not a valid text file.')
                return redirect(url_for('index'))
        
        # Set download name to original filename with pdf extension
        download_name = os.path.splitext(original_filename)[0] + '.pdf'
        
        # Convert markdown to PDF
        try:
            convert_md_to_pdf(md_content, output_path, include_toc=include_toc)
            logger.info(f"Successfully converted to PDF: {output_path}")
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}", exc_info=True)
            flash(f'Error converting file: {str(e)}')
            return redirect(url_for('index'))
        
        # Send the PDF file as a download
        return send_file(
            output_path, 
            as_attachment=True, 
            download_name=download_name, 
            mimetype='application/pdf'
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        flash('An unexpected error occurred. Please try again.')
        return redirect(url_for('index'))

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle request entity too large errors (file size exceeded)."""
    logger.warning("File upload exceeds size limit")
    flash(f'File too large. The limit is {app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)}MB.')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error("Server error", exc_info=True)
    return render_template('index.html', error="Server error. Please try again later."), 500

def cleanup_old_files():
    """Remove temporary files older than 1 hour to prevent disk filling up."""
    try:
        import time
        from datetime import datetime, timedelta
        
        upload_dir = app.config['UPLOAD_FOLDER']
        now = time.time()
        one_hour_ago = now - 3600  # 1 hour in seconds
        
        count = 0
        for filename in os.listdir(upload_dir):
            filepath = os.path.join(upload_dir, filename)
            if os.path.isfile(filepath):
                # Check file creation time
                if os.path.getctime(filepath) < one_hour_ago:
                    try:
                        os.remove(filepath)
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove old file {filepath}: {e}")
        
        if count > 0:
            logger.info(f"Cleaned up {count} old files from {upload_dir}")
    except Exception as e:
        logger.error(f"Error during file cleanup: {e}")

if __name__ == '__main__':
    # Clean up old files on startup
    cleanup_old_files()
    
    # Get configuration from environment variables or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Log startup configuration
    logger.info(f"Starting Markdown to PDF converter on {host}:{port} (debug={debug})")
    
    # Schedule cleanup to run periodically if this becomes a long-running service
    # This is commented out for now as it requires additional setup
    # import atexit
    # from apscheduler.schedulers.background import BackgroundScheduler
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=cleanup_old_files, trigger="interval", hours=1)
    # scheduler.start()
    # atexit.register(lambda: scheduler.shutdown())
    
    # Run the application
    app.run(host=host, port=port, debug=debug)
