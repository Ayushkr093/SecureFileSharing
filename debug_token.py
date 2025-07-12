"""
Debug Token Generation and Validation
"""

def test_token_debug():
    """Test token generation and validation"""
    import sys
    sys.path.append('.')
    
    from utils import EncryptionService, TokenService
    from config import Config
    
    # Initialize services
    encryption_key = Config.ENCRYPTION_KEY
    print(f"Encryption key: {encryption_key}")
    
    encryption_service = EncryptionService(encryption_key)
    token_service = TokenService(encryption_service)
    
    # Test data
    file_id = 1
    user_id = 4
    
    print(f"\n🔧 Testing Token Generation and Validation")
    print(f"File ID: {file_id}, User ID: {user_id}")
    
    # Generate token
    token = token_service.generate_download_token(file_id, user_id)
    print(f"\n✅ Generated Token: {token}")
    
    # Validate token
    token_data = token_service.validate_download_token(token)
    print(f"\n🔍 Validated Token Data: {token_data}")
    
    if token_data:
        print("✅ Token validation successful!")
        print(f"   File ID: {token_data['file_id']}")
        print(f"   User ID: {token_data['user_id']}")
        print(f"   Expires: {token_data['expires_at']}")
    else:
        print("❌ Token validation failed!")
    
    # Test with the actual app context
    print(f"\n🏗️ Testing with App Context")
    from app import create_app
    from models import db, DownloadToken
    
    app = create_app()
    with app.app_context():
        # Create a database token entry
        from datetime import datetime, timedelta
        
        db_token = DownloadToken(
            token=token,
            file_id=file_id,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            is_used=False
        )
        
        # Check if token already exists
        existing_token = DownloadToken.query.filter_by(token=token).first()
        if existing_token:
            print("⚠️ Token already exists in database")
        else:
            db.session.add(db_token)
            db.session.commit()
            print("✅ Token added to database")
        
        # Now test retrieval
        retrieved_token = DownloadToken.query.filter_by(token=token, is_used=False).first()
        if retrieved_token:
            print("✅ Token found in database")
            print(f"   DB File ID: {retrieved_token.file_id}")
            print(f"   DB User ID: {retrieved_token.user_id}")
            print(f"   DB Is Used: {retrieved_token.is_used}")
        else:
            print("❌ Token not found in database")

if __name__ == "__main__":
    test_token_debug()
