"""
Database decryption utility for troubleshooting
Purpose: Decrypt and display user data for a specific UserID
Useful for viewing encrypted database records
"""
import sqlite3
import sys
import os

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variables import database_path
from Utils.encryption_service import EncryptionService


def decrypt_user_by_id(user_id):
    """
    Decrypt and display all data for a specific user.
    
    Args:
        user_id: The UserID to decrypt data for
    """
    try:
        # Initialize encryption service
        protecting = EncryptionService()
        
        # Connect to database
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        
        # Query user by UserID
        cur.execute(
            "SELECT UserID, UserName, Password, Money, GamesPlayed FROM Users WHERE UserID = ?",
            (user_id,)
        )
        user = cur.fetchone()
        conn.close()
        
        if not user:
            print(f"\n✗ No user found with UserID: {user_id}")
            return False
        
        user_id, encrypted_username, encrypted_password, encrypted_money, encrypted_games = user
        
        # Decrypt all fields
        try:
            decrypted_username = protecting.decrypt(encrypted_username) if encrypted_username else ""
            decrypted_password = protecting.decrypt(encrypted_password) if encrypted_password else ""
            decrypted_money = protecting.decrypt(encrypted_money) if encrypted_money else "0"
            decrypted_games = protecting.decrypt(encrypted_games) if encrypted_games else "0"
            
            # Display results
            print("\n" + "="*60)
            print(f"USER DATA - UserID {user_id}")
            print("="*60)
            print(f"  Username:      {decrypted_username}")
            print(f"  Password:      {decrypted_password}")
            print(f"  Balance:       {decrypted_money}")
            print(f"  Games Played:  {decrypted_games}")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"\n✗ Decryption failed: {e}")
            print("  Data in database may be corrupted or not encrypted.")
            print(f"  Raw encrypted data:")
            print(f"    Username:  {encrypted_username[:50]}...")
            print(f"    Password:  {encrypted_password[:50]}...")
            print(f"    Money:     {encrypted_money[:50]}...")
            print(f"    Games:     {encrypted_games[:50]}...")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main interactive loop for decrypting user data"""
    print("="*60)
    print("USER DATA DECRYPTION UTILITY")
    print("="*60)
    
    while True:
        try:
            user_input = input("\nEnter UserID to decrypt (or 'exit' to quit): ").strip()
            
            if user_input.lower() == 'exit':
                print("\nGoodbye!")
                break
            
            # Validate input is a number
            try:
                user_id = int(user_input)
            except ValueError:
                print(f"✗ Invalid input: '{user_input}' is not a valid number")
                continue
            
            # Decrypt and display
            decrypt_user_by_id(user_id)
            
        except EOFError:
            print("\n\nEnd of input reached. Goodbye!")
            break
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            break


if __name__ == "__main__":
    # If UserID provided as command-line argument, decrypt that user directly
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
            decrypt_user_by_id(user_id)
        except ValueError:
            print(f"✗ Invalid UserID: '{sys.argv[1]}' is not a valid number")
            sys.exit(1)
    else:
        # Otherwise, start interactive mode
        main()
