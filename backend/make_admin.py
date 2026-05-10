import sqlite3
import sys

def make_admin(username):
    try:
        conn = sqlite3.connect('phishing.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: User '{username}' not found in the database.")
            return
            
        # Update user to admin
        cursor.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()
        
        print(f"Success! '{username}' is now an admin. Please logout and login again in the app.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
    else:
        make_admin(sys.argv[1])
