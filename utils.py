from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
import string
from datetime import datetime, timedelta
import os

class EncryptionService:
    def __init__(self, password: str):
        """Initialize encryption service with a password"""
        password_bytes = password.encode()
        salt = b'salt_'  # In production, use a random salt per encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        self.cipher_suite = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return original string"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return None

class TokenService:
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def generate_download_token(self, file_id: int, user_id: int, expires_in_hours: int = 24) -> str:
        """Generate an encrypted download token"""
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        # Use timestamp instead of isoformat to avoid colon issues
        expires_timestamp = expires_at.timestamp()
        token_data = f"{file_id}:{user_id}:{expires_timestamp}"
        return self.encryption_service.encrypt(token_data)
    
    def validate_download_token(self, token: str) -> dict:
        """Validate and decode download token"""
        decrypted_data = self.encryption_service.decrypt(token)
        if not decrypted_data:
            return None
        
        try:
            file_id, user_id, expires_timestamp_str = decrypted_data.split(':')
            expires_timestamp = float(expires_timestamp_str)
            expires_at = datetime.fromtimestamp(expires_timestamp)
            
            if datetime.utcnow() > expires_at:
                return None
            
            return {
                'file_id': int(file_id),
                'user_id': int(user_id),
                'expires_at': expires_at
            }
        except (ValueError, TypeError):
            return None

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_secure_filename(original_filename):
    """Generate a secure filename for storage"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    random_name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    return f"{random_name}.{ext}"

def ensure_upload_directory(upload_folder):
    """Ensure upload directory exists"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
