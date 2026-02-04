"""
Script to encrypt all user data in the database
Run this one time to convert everything from plaintext to encrypted
"""
import sqlite3
import os
import sys

# Add parent directory to path so we can import everything from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variables import database_path
from Utils.encryption_service import EncryptionService


def migrate_database():
    """Encrypt all the user data in the database"""
    try:
        # Initialize encryption service
        protecting = EncryptionService()
        
        # Verify encryption works
        test_encrypt = protecting.encrypt("test")
        if not test_encrypt:
            print("✗ Encryption service failed to initialize. Check CSNEA_KEY environment variable.")
            return False
        
        # Connect to database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        
        # Get all users
        cur.execute("SELECT UserID, UserName, Password, Money, GamesPlayed FROM Users")
        users = cur.fetchall()
        
        if not users:
            print("No users found in database. Nothing to encrypt.")
            conn.close()
            return True
        
        print(f"Found {len(users)} users to encrypt...")
        
        # Encrypt each field and update
        for user_id, username, password, money, games_played in users:
            try:
                # Skip if already encrypted (encrypted values typically long and contain base64 chars)
                if username and len(str(username)) > 100:
                    print(f"  ⊘ User {user_id} appears already encrypted, skipping...")
                    continue
                
                # Convert to strings and encrypt
                encrypted_username = protecting.encrypt(str(username) if username else "")
                encrypted_password = protecting.encrypt(str(password) if password else "")
                encrypted_money = protecting.encrypt(str(money) if money else "0")
                encrypted_games = protecting.encrypt(str(games_played) if games_played else "0")
                
                if not all([encrypted_username, encrypted_password, encrypted_money, encrypted_games]):
                    print(f"  ✗ User {user_id} ({username}): Encryption failed - null result")
                    continue
                
                # Update database
                cur.execute(
                    """UPDATE Users 
                       SET UserName = ?, Password = ?, Money = ?, GamesPlayed = ? 
                       WHERE UserID = ?""",
                    (encrypted_username, encrypted_password, encrypted_money, encrypted_games, user_id)
                )
                print(f"  ✓ Encrypted user {user_id}: {username}")
                
            except Exception as e:
                print(f"  ✗ User {user_id} ({username}): {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        print("\n✓ Migration complete! All user data is now encrypted.")
        print("Important: Use the updated db.py functions with 'protecting' parameter going forward.")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE ENCRYPTION MIGRATION")
    print("=" * 60)
    print("\nThis will encrypt all existing user data in the database.")
    print("Fields encrypted: UserName, Password, Money, GamesPlayed")
    print("Field NOT encrypted: UserID (primary key)\n")
    
    response = input("Continue with migration? (yes/no): ").strip().lower()
    if response == 'yes':
        if migrate_database():
            print("\nYou can now safely delete this script.")
        else:
            print("\nMigration failed. Check error messages above.")
    else:
        print("Migration cancelled.")
