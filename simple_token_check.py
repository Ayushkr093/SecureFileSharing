import time
import json
import base64

# Your token from the console
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjMzMjY0MywianRpIjoiOWRmNjJhZmQtNTZhZS00NWVlLWIyZGYtZjEyMmNjMWM3NDUyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NTIzMzI2NDMsImV4cCI6MTc1MjMzMzU0M30.Clz4cDFvaWQ0Co-ILVVIJUeCike7AOnwr6XQKlqWVHQ"

try:
    # Split the token and decode the payload
    parts = token.split('.')
    payload = parts[1]
    
    # Add padding if needed
    padding = len(payload) % 4
    if padding:
        payload += '=' * (4 - padding)
    
    # Decode the base64 payload
    decoded_bytes = base64.b64decode(payload)
    decoded_json = json.loads(decoded_bytes)
    
    print("Token payload:", decoded_json)
    
    # Check expiration
    exp = decoded_json.get('exp')
    iat = decoded_json.get('iat')
    current_time = int(time.time())
    
    print(f"Token issued at: {iat} ({time.ctime(iat)})")
    print(f"Token expires at: {exp} ({time.ctime(exp)})")
    print(f"Current time: {current_time} ({time.ctime(current_time)})")
    print(f"Token expired: {current_time > exp}")
    
    if current_time > exp:
        print("❌ Token has expired! You need to login again.")
        print(f"Token expired {current_time - exp} seconds ago.")
    else:
        print("✅ Token is still valid.")
        print(f"Token will expire in {exp - current_time} seconds.")
        
except Exception as e:
    print(f"Error decoding token: {e}")
