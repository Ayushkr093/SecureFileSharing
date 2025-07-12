import jwt
import datetime

# Your token from the console
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjMzMjY0MywianRpIjoiOWRmNjJhZmQtNTZhZS00NWVlLWIyZGYtZjEyMmNjMWM3NDUyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NTIzMzI2NDMsImV4cCI6MTc1MjMzMzU0M30.Clz4cDFvaWQ0Co-ILVVIJUeCike7AOnwr6XQKlqWVHQ"

try:
    # Decode without verification to see the payload
    decoded = jwt.decode(token, options={"verify_signature": False})
    print("Token payload:", decoded)
    
    # Check expiration
    exp = decoded.get('exp')
    if exp:
        exp_time = datetime.datetime.fromtimestamp(exp)
        current_time = datetime.datetime.now()
        print(f"Token expires at: {exp_time}")
        print(f"Current time: {current_time}")
        print(f"Token expired: {current_time > exp_time}")
        
        if current_time > exp_time:
            print("❌ Token has expired! You need to login again.")
        else:
            print("✅ Token is still valid.")
            
except Exception as e:
    print(f"Error decoding token: {e}")
