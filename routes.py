from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message
from models import db, User, UploadedFile, DownloadToken
from utils import EncryptionService, TokenService, allowed_file, generate_secure_filename, ensure_upload_directory
import os
from datetime import datetime, timedelta

# Create blueprints
auth_bp = Blueprint('auth', __name__)
ops_bp = Blueprint('ops', __name__)
client_bp = Blueprint('client', __name__)

# Initialize services (will be set in app factory)
encryption_service = None
token_service = None

def init_services(app):
    """Initialize services with app config"""
    global encryption_service, token_service
    encryption_key = app.config.get('ENCRYPTION_KEY', 'default-key')
    encryption_service = EncryptionService(encryption_key)
    token_service = TokenService(encryption_service)

# Authentication Routes
@auth_bp.route('/ops/login', methods=['POST'])
def ops_login():
    """Ops user login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email'], user_type='ops').first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user_type': 'ops',
            'message': 'Login successful'
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/client/signup', methods=['POST'])
def client_signup():
    """Client user signup with email verification"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400
    
    # Create new user
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        user_type='client',
        is_verified=False
    )
    
    # Generate verification token
    verification_token = user.generate_verification_token()
    
    db.session.add(user)
    db.session.commit()
    
    # Send verification email
    try:
        send_verification_email(user.email, verification_token)
        encrypted_url = encryption_service.encrypt(f"verify:{verification_token}")
        return jsonify({
            'message': 'User created successfully. Please check your email for verification.',
            'encrypted_verification_url': encrypted_url
        }), 201
    except Exception as e:
        return jsonify({'message': 'User created but email sending failed'}), 201

@auth_bp.route('/client/verify-email', methods=['POST'])
def verify_email():
    """Verify client email"""
    data = request.get_json()
    
    if not data or not data.get('token'):
        return jsonify({'message': 'Verification token is required'}), 400
    
    user = User.query.filter_by(verification_token=data['token'], user_type='client').first()
    
    if not user:
        return jsonify({'message': 'Invalid verification token'}), 400
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'}), 200

@auth_bp.route('/client/login', methods=['POST'])
def client_login():
    """Client user login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email'], user_type='client').first()
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_verified:
        return jsonify({'message': 'Please verify your email before logging in'}), 401
    
    if check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user_type': 'client',
            'message': 'Login successful'
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Ops Routes
@ops_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Ops user file upload"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.user_type != 'ops':
        return jsonify({'message': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'message': 'File type not allowed. Only .pptx, .docx, .xlsx files are permitted'}), 400
    
    try:
        # Ensure upload directory exists
        ensure_upload_directory(current_app.config['UPLOAD_FOLDER'])
        
        # Generate secure filename
        stored_filename = generate_secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
        
        # Save file
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Save file info to database
        uploaded_file = UploadedFile(
            original_filename=secure_filename(file.filename),
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.filename.rsplit('.', 1)[1].lower(),
            uploaded_by=user_id
        )
        
        db.session.add(uploaded_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': uploaded_file.id,
            'original_filename': uploaded_file.original_filename,
            'file_size': uploaded_file.file_size
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Upload failed: {str(e)}'}), 500

# Client Routes
@client_bp.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    """Client user list all uploaded files"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.user_type != 'client':
        return jsonify({'message': 'Unauthorized'}), 403
    
    files = UploadedFile.query.all()
    
    return jsonify({
        'files': [file.to_dict() for file in files],
        'message': 'success'
    }), 200

@client_bp.route('/download-file/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_download_link(assignment_id):
    """Generate secure download link for client"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.user_type != 'client':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Check if file exists
    file = UploadedFile.query.get(assignment_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404
    
    # Generate encrypted download token
    download_token = token_service.generate_download_token(assignment_id, user_id)
    
    # Store token in database
    db_token = DownloadToken(
        token=download_token,
        file_id=assignment_id,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.session.add(db_token)
    db.session.commit()
    
    download_url = f"{request.host_url}download-file/{download_token}"
    
    return jsonify({
        'download-link': download_url,
        'message': 'success'
    }), 200

@client_bp.route('/download-file/<token>', methods=['GET'])
def download_file(token):
    """Download file using encrypted token"""
    # Validate token
    token_data = token_service.validate_download_token(token)
    
    if not token_data:
        return jsonify({'message': 'Invalid or expired token'}), 401
    
    # Check if token exists in database and is not used
    db_token = DownloadToken.query.filter_by(token=token, is_used=False).first()
    
    if not db_token:
        return jsonify({'message': 'Token not found or already used'}), 401
    
    # Verify token matches the requesting conditions
    if (db_token.file_id != token_data['file_id'] or 
        db_token.user_id != token_data['user_id']):
        return jsonify({'message': 'Token validation failed'}), 401
    
    # Get the file
    file = UploadedFile.query.get(token_data['file_id'])
    
    if not file or not os.path.exists(file.file_path):
        return jsonify({'message': 'File not found'}), 404
    
    # Mark token as used
    db_token.is_used = True
    db.session.commit()
    
    try:
        return send_file(
            file.file_path,
            as_attachment=True,
            download_name=file.original_filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'message': f'Download failed: {str(e)}'}), 500

def send_verification_email(email, verification_token):
    """Send verification email to user"""
    from models import mail
    
    msg = Message(
        'Verify Your Email - File Sharing System',
        recipients=[email]
    )
    
    verification_url = f"{request.host_url}verify?token={verification_token}"
    
    msg.body = f"""
    Welcome to our File Sharing System!
    
    Please click the following link to verify your email address:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you did not create an account, please ignore this email.
    """
    
    msg.html = f"""
    <h2>Welcome to our File Sharing System!</h2>
    
    <p>Please click the button below to verify your email address:</p>
    
    <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">
        Verify Email
    </a>
    
    <p>Or copy and paste this link into your browser:</p>
    <p>{verification_url}</p>
    
    <p>This link will expire in 24 hours.</p>
    
    <p>If you did not create an account, please ignore this email.</p>
    """
    
    mail.send(msg)
