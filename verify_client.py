"""
Manual Client User Verification Script
Run this after signing up a client user to verify them manually
"""

def verify_client_user(email):
    """Manually verify a client user"""
    import sys
    sys.path.append('.')
    
    from app import create_app
    from models import db, User
    
    app = create_app()
    
    with app.app_context():
        user = User.query.filter_by(email=email, user_type='client').first()
        
        if not user:
            print(f"❌ Client user with email {email} not found")
            return False
        
        if user.is_verified:
            print(f"✅ User {email} is already verified")
            return True
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        print(f"✅ User {email} has been verified successfully")
        return True

if __name__ == "__main__":
    email = input("Enter client email to verify: ")
    verify_client_user(email)
