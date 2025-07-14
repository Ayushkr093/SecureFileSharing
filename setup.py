#!/usr/bin/env python3
"""
Secure File Sharing System Setup Script
"""

import os
import secrets
import string
from cryptography.fernet import Fernet

def generate_secret_key(length=50):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a secure encryption key"""
    return Fernet.generate_key().decode()

def setup_environment():
    """Setup environment file with secure keys"""
    print("Setting up secure environment...")
    
    # Generate secure keys
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///file_sharing.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Email Configuration (Configure with your email provider)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME='divanshlinkdin@gmail.com'
MAIL_PASSWORD='poff tmxg lrno tjzg'
MAIL_DEFAULT_SENDER='divanshlinkdin@gmail.com'

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Encryption Configuration
ENCRYPTION_KEY={encryption_key}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created with secure keys")
    print("⚠️  Please update email configuration in .env file")

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'instance']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 Setting up Secure File Sharing System...")
    
    setup_environment()
    create_directories()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Update email configuration in .env file")
    print("3. Run the application: python app.py")
    print("\nDefault Ops User:")
    print("Email: ops@example.com")
    print("Password: ops123")

if __name__ == "__main__":
    main()
