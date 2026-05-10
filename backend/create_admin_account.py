import sys
import os

# Add backend dir to path to import database
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, User, get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        username = "Admin"
        password = "admin123"
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            new_user = User(
                username=username, 
                password_hash=get_password_hash(password), 
                is_admin=1, 
                is_verified=1
            )
            db.add(new_user)
            db.commit()
            print(f"Success: Created new admin user '{username}' with password '{password}'")
        else:
            user.is_admin = 1
            user.is_verified = 1
            user.password_hash = get_password_hash(password)
            db.commit()
            print(f"Success: Updated existing user '{username}' to be an admin with password '{password}'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
