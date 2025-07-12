"""
Debug Encryption Service
"""

def test_encryption_debug():
    """Test the encryption service step by step"""
    from utils import EncryptionService
    
    # Test with a simple key
    test_key = "yuumuTAmPn6HeAFu_sDsqzGp3tz-BR7fnQPxPGAkfiY="
    print(f"Testing with key: {test_key}")
    
    encryption_service = EncryptionService(test_key)
    
    # Test simple encryption/decryption
    test_data = "1:4:2025-07-13T15:00:00.000000"
    print(f"\nOriginal data: {test_data}")
    
    # Encrypt
    encrypted = encryption_service.encrypt(test_data)
    print(f"Encrypted: {encrypted}")
    
    # Decrypt
    decrypted = encryption_service.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    if decrypted == test_data:
        print("✅ Encryption/Decryption working correctly!")
    else:
        print("❌ Encryption/Decryption failed!")
        
    # Test the exact token format
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(hours=24)
    token_data = f"1:4:{expires_at.isoformat()}"
    print(f"\nToken data: {token_data}")
    
    encrypted_token = encryption_service.encrypt(token_data)
    print(f"Encrypted token: {encrypted_token}")
    
    decrypted_token = encryption_service.decrypt(encrypted_token)
    print(f"Decrypted token: {decrypted_token}")
    
    if decrypted_token:
        try:
            file_id, user_id, expires_at_str = decrypted_token.split(':')
            expires_at_parsed = datetime.fromisoformat(expires_at_str)
            
            print(f"✅ Token parsing successful!")
            print(f"   File ID: {file_id}")
            print(f"   User ID: {user_id}")
            print(f"   Expires: {expires_at_parsed}")
            
            if datetime.utcnow() > expires_at_parsed:
                print("⚠️ Token is expired")
            else:
                print("✅ Token is valid")
                
        except Exception as e:
            print(f"❌ Token parsing failed: {e}")
    else:
        print("❌ Token decryption returned None")

if __name__ == "__main__":
    test_encryption_debug()
