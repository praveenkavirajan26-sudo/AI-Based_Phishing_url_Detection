"""
reset_database.py - Delete old database and recreate with new schema
"""
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "phishing.db")

def reset_database():
    """Delete old database and recreate with new schema."""
    print("=" * 60)
    print("PhishGuard AI - Database Reset Tool")
    print("=" * 60)
    
    # Check if database exists
    if os.path.exists(DB_PATH):
        print(f"\n⚠️  Found existing database: {DB_PATH}")
        response = input("Do you want to DELETE it and create a new one? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("❌ Cancelled. Database not modified.")
            return
        
        try:
            os.remove(DB_PATH)
            print(f"✅ Old database deleted successfully!")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            print("\n🔧 Manual fix:")
            print(f"   Delete this file: {DB_PATH}")
            return
    else:
        print(f"\nℹ️  No existing database found.")
    
    # Import database module to create new schema
    print("\n📦 Creating new database with updated schema...")
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Import database module (this will create tables)
        from database import Base, engine, User, ScanHistory
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database created successfully!")
        print("\n📋 New schema includes:")
        print("   • users table:")
        print("     - id (primary key)")
        print("     - username (unique)")
        print("     - email (unique, nullable)")
        print("     - password_hash")
        print("     - is_verified (0 or 1)")
        print("     - verification_token")
        print("     - token_expiry")
        print("     - created_at")
        print("   • scan_history table:")
        print("     - id (primary key)")
        print("     - user_id (foreign key)")
        print("     - url")
        print("     - prediction")
        print("     - confidence_score")
        print("     - risk_score")
        print("     - timestamp")
        
        print("\n" + "=" * 60)
        print("✅ Database reset complete!")
        print("=" * 60)
        print("\n🚀 You can now restart the backend server:")
        print("   .\\venv\\Scripts\\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you're in the backend directory")
        print("   2. Activate virtual environment: .\\venv\\Scripts\\Activate")
        print("   3. Install dependencies: pip install -r requirements.txt")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_database()
