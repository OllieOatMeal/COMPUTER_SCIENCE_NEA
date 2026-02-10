import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from variables import database_path
from Utils.encryption_service import EncryptionService
from Utils.db import (
    set_is_admin,
    update_user_password,
    update_user_balance,
    get_all_usernames,
    get_user_data,
    create_user,
    delete_user,
)


def get_protecting():
    protecting = EncryptionService()
    protecting.get_key()
    return protecting


def decrypt_username(value, protecting):
    if value is None:
        return ""
    raw = str(value)
    try:
        return protecting.decrypt_deterministic(raw)
    except Exception:
        try:
            return protecting.decrypt(raw)
        except Exception:
            return raw


def decrypt_user_by_id(user_id):
    try:
        protecting = get_protecting()
        conn = sqlite3.connect(database_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(Users)")
        cols = [row[1] for row in cur.fetchall()]

        select_cols = ["UserID", "UserName", "Password", "Money", "GamesPlayed"]
        for name in ["CreatedAt", "UpdatedAt", "LastLogin", "IsAdmin"]:
            if name in cols:
                select_cols.append(name)

        cur.execute(f"SELECT {', '.join(select_cols)} FROM Users WHERE UserID = ?", (user_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            print(f"No user found with UserID: {user_id}")
            return False

        data = dict(zip(select_cols, row))
        username = decrypt_username(data.get("UserName"), protecting)
        password = protecting.decrypt(data.get("Password")) if data.get("Password") else ""
        money = protecting.decrypt(data.get("Money")) if data.get("Money") else "0"
        games = protecting.decrypt(data.get("GamesPlayed")) if data.get("GamesPlayed") else "0"
        created_at = protecting.decrypt(data.get("CreatedAt")) if data.get("CreatedAt") else ""
        updated_at = protecting.decrypt(data.get("UpdatedAt")) if data.get("UpdatedAt") else ""
        last_login = protecting.decrypt(data.get("LastLogin")) if data.get("LastLogin") else ""
        is_admin = protecting.decrypt(data.get("IsAdmin")) if data.get("IsAdmin") else "0"

        print("=" * 60)
        print(f"USER DATA - UserID {user_id}")
        print("=" * 60)
        print(f"  Username:      {username}")
        print(f"  Password:      {password}")
        print(f"  Balance:       {money}")
        print(f"  Games Played:  {games}")
        if "CreatedAt" in data:
            print(f"  Created At:    {created_at}")
        if "UpdatedAt" in data:
            print(f"  Updated At:    {updated_at}")
        if "LastLogin" in data:
            print(f"  Last Login:    {last_login}")
        if "IsAdmin" in data:
            print(f"  Is Admin:      {is_admin}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def set_admin(username, flag):
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    ok = set_is_admin(username, flag, protecting)
    if ok:
        print(f"✓ IsAdmin set to {flag} for user '{username}'.")
        return True
    print("✗ Failed to update IsAdmin.")
    return False


def set_password(username, new_password):
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    ok = update_user_password(username, new_password, protecting)
    if ok:
        print(f"✓ Password updated for user '{username}'.")
        return True
    print("✗ Failed to update password.")
    return False


def set_balance(username, amount):
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    ok = update_user_balance(username, amount, protecting)
    if ok:
        print(f"✓ Balance set to {amount} for user '{username}'.")
        return True
    print("✗ Failed to update balance.")
    return False


def add_user(username, password, balance, games, is_admin):
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    ok = create_user(username, password, protecting, money=balance, games_played=games, is_admin=is_admin)
    if ok:
        print(f"✓ User '{username}' created.")
        return True
    print("✗ Failed to create user.")
    return False


def remove_user(username):
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    ok = delete_user(username, protecting)
    if ok:
        print(f"✓ User '{username}' deleted.")
        return True
    print("✗ Failed to delete user.")
    return False


def list_users():
    try:
        protecting = get_protecting()
    except Exception as e:
        print(f"Error: {e}")
        return False

    usernames = get_all_usernames(protecting)
    if not usernames:
        print("No users found.")
        return True

    print(f"\nFound {len(usernames)} users:")
    print("=" * 60)
    for i, username in enumerate(usernames, 1):
        user_data = get_user_data(username, protecting)
        if user_data:
            admin_status = "ADMIN" if user_data.get("is_admin", False) else "USER"
            balance = user_data.get("money", 0)
            print(f"  {i}. {username:<20} Balance: ${balance:>10,}  [{admin_status}]")
        else:
            print(f"  {i}. {username}")
    print("=" * 60)
    return True


def main():
    if len(sys.argv) < 2:
        return run_menu()

    command = sys.argv[1].strip().lower()

    if command == "set-admin":
        if len(sys.argv) < 3:
            print("Missing username.")
            return 1
        username = sys.argv[2]
        flag = True
        if len(sys.argv) >= 4:
            raw = sys.argv[3].strip().lower()
            flag = raw in ("1", "true", "yes", "y", "on")
        return 0 if set_admin(username, flag) else 1

    if command == "decrypt-user":
        if len(sys.argv) < 3:
            print("Missing user_id.")
            return 1
        try:
            user_id = int(sys.argv[2])
        except ValueError:
            print("user_id must be a number.")
            return 1
        return 0 if decrypt_user_by_id(user_id) else 1

    if command == "set-password":
        if len(sys.argv) < 4:
            print("Missing username or new_password.")
            return 1
        return 0 if set_password(sys.argv[2], sys.argv[3]) else 1

    if command == "create-user":
        if len(sys.argv) < 4:
            print("Missing username or password.")
            return 1
        username = sys.argv[2]
        password = sys.argv[3]
        balance = 10000
        games = 0
        is_admin = False
        if len(sys.argv) >= 5:
            try:
                balance = int(sys.argv[4])
            except ValueError:
                print("Balance must be a number.")
                return 1
        if len(sys.argv) >= 6:
            try:
                games = int(sys.argv[5])
            except ValueError:
                print("Games must be a number.")
                return 1
        if len(sys.argv) >= 7:
            raw = sys.argv[6].strip().lower()
            is_admin = raw in ("1", "true", "yes", "y", "on")
        return 0 if add_user(username, password, balance, games, is_admin) else 1

    if command == "set-balance":
        if len(sys.argv) < 4:
            print("Missing username or amount.")
            return 1
        try:
            amount = int(sys.argv[3])
        except ValueError:
            print("Amount must be a number.")
            return 1
        return 0 if set_balance(sys.argv[2], amount) else 1

    if command == "delete-user":
        if len(sys.argv) < 3:
            print("Missing username.")
            return 1
        return 0 if remove_user(sys.argv[2]) else 1

    if command == "list-users":
        return 0 if list_users() else 1

    if command in ("menu", "help"):
        return run_menu()

    print("Unknown command.")
    return 1


def run_menu():
    print("\nAdmin Tool Menu")
    print("1) List users")
    print("2) Create user")
    print("3) Delete user")
    print("4) Set admin")
    print("5) Set password")
    print("6) Set balance")
    print("7) Decrypt user by ID")
    print("8) Exit")

    choice = input("Choose an option (1-8): ").strip()

    if choice == "1":
        return 0 if list_users() else 1

    if choice == "2":
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        if not username or not password:
            print("Missing username or password.")
            return 1
        raw_balance = input("Starting balance (default 10000): ").strip()
        raw_games = input("Starting games (default 0): ").strip()
        raw_admin = input("Is admin? (true/false): ").strip().lower()
        balance = 10000
        games = 0
        if raw_balance:
            try:
                balance = int(raw_balance)
            except ValueError:
                print("Balance must be a number.")
                return 1
        if raw_games:
            try:
                games = int(raw_games)
            except ValueError:
                print("Games must be a number.")
                return 1
        is_admin = raw_admin in ("1", "true", "yes", "y", "on")
        return 0 if add_user(username, password, balance, games, is_admin) else 1

    if choice == "3":
        username = input("Username: ").strip()
        if not username:
            print("Missing username.")
            return 1
        return 0 if remove_user(username) else 1

    if choice == "4":
        username = input("Username: ").strip()
        if not username:
            print("Missing username.")
            return 1
        raw = input("Is admin? (true/false): ").strip().lower()
        flag = raw in ("1", "true", "yes", "y", "on")
        return 0 if set_admin(username, flag) else 1

    if choice == "5":
        username = input("Username: ").strip()
        new_password = input("New password: ").strip()
        if not username or not new_password:
            print("Missing username or password.")
            return 1
        return 0 if set_password(username, new_password) else 1

    if choice == "6":
        username = input("Username: ").strip()
        raw_amount = input("Amount: ").strip()
        try:
            amount = int(raw_amount)
        except ValueError:
            print("Amount must be a number.")
            return 1
        return 0 if set_balance(username, amount) else 1

    if choice == "7":
        raw_id = input("User ID: ").strip()
        try:
            user_id = int(raw_id)
        except ValueError:
            print("User ID must be a number.")
            return 1
        return 0 if decrypt_user_by_id(user_id) else 1

    print("Goodbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
