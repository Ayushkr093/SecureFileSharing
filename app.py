from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from models import db, jwt, mail
from routes import auth_bp, ops_bp, client_bp, init_services
import os

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)  # Enable CORS for frontend requests
    
    # Initialize services
    init_services(app)
    
    # Create upload directory
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ops_bp, url_prefix='/api/ops')
    app.register_blueprint(client_bp, url_prefix='/api/client')
    
    # Frontend route
    @app.route('/')
    def index():
        """Serve the frontend application"""
        return render_template('index.html')
    
    @app.route('/api-tester')
    def api_tester():
        """Serve the API testing interface"""
        from flask import send_from_directory
        return send_from_directory('.', 'api_tester.html')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default ops user if it doesn't exist
        from models import User
        from werkzeug.security import generate_password_hash
        
        ops_user = User.query.filter_by(email='ops@example.com', user_type='ops').first()
        if not ops_user:
            ops_user = User(
                email='ops@example.com',
                password_hash=generate_password_hash('ops123'),
                user_type='ops',
                is_verified=True
            )
            db.session.add(ops_user)
            db.session.commit()
            print("Default ops user created: ops@example.com / ops123")
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'message': 'File Sharing API is running'}, 200
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """API documentation"""
        return {
            'message': 'Secure File Sharing System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'ops_login': 'POST /api/auth/ops/login',
                    'client_signup': 'POST /api/auth/client/signup',
                    'client_verify': 'POST /api/auth/client/verify-email',
                    'client_login': 'POST /api/auth/client/login'
                },
                'ops': {
                    'upload_file': 'POST /api/ops/upload (requires JWT)'
                },
                'client': {
                    'list_files': 'GET /api/client/files (requires JWT)',
                    'get_download_link': 'GET /api/client/download-file/{assignment_id} (requires JWT)',
                    'download_file': 'GET /api/client/download-file/{encrypted_token}'
                }
            },
            'default_ops_user': {
                'email': 'ops@example.com',
                'password': 'ops123'
            }
        }, 200
    
    @app.route('/download-file/<token>', methods=['GET'])
    def download_file_global(token):
        """Global download route for encrypted tokens"""
        from routes import download_file
        from flask import request
        
        # Import the download function from routes and call it
        # This allows the same logic to be used with a simpler URL
        return download_file(token)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
