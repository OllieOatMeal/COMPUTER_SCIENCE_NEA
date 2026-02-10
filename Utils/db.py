"""
All my database functions in one place
Handles encrypting/decrypting data when reading from and writing to the database
"""
import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from variables import database_path


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    # Simple timestamp helper
    return datetime.now(timezone.utc).isoformat()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure optional columns exist on Users table."""
    # Patch in missing columns without breaking older DBs
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
        if cur.fetchone() is None:
            return

        cur.execute("PRAGMA table_info(Users)")
        existing_cols = {row[1] for row in cur.fetchall()}

        if "CreatedAt" not in existing_cols:
            cur.execute("ALTER TABLE Users ADD COLUMN CreatedAt TEXT")
        if "UpdatedAt" not in existing_cols:
            cur.execute("ALTER TABLE Users ADD COLUMN UpdatedAt TEXT")
        if "LastLogin" not in existing_cols:
            cur.execute("ALTER TABLE Users ADD COLUMN LastLogin TEXT")
        if "IsAdmin" not in existing_cols:
            cur.execute("ALTER TABLE Users ADD COLUMN IsAdmin INTEGER DEFAULT 0")

        conn.commit()
    except Exception:
        # If schema update fails, continue without blocking normal DB usage
        return


def _connect():
    # Open DB connection and make sure schema is up to date
    conn = sqlite3.connect(database_path)
    _ensure_schema(conn)
    return conn


def _encode_username(username: str, protecting=None) -> str:
    """
    Encode username deterministically for DB lookups.
    Uses deterministic encryption when protecting is provided.
    """
    # Keep lookups consistent when encryption is on
    if protecting:
        try:
            return protecting.encrypt_deterministic(username)
        except Exception:
            return username
    return username


def get_user_password(username: str, protecting=None) -> Optional[str]:
    """Look up a user and return their password"""
    # Fetch and decrypt the password for login checks
    try:
        conn = _connect()
        cur = conn.cursor()
        # Encode username deterministically for DB lookup
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT Password FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        # Decrypt password if protecting provided
        password = row[0]
        if protecting and password:
            password = protecting.decrypt(password)
        return password
    except Exception:
        return None


def user_exists(username: str, protecting=None) -> bool:
    """
    Check if user exists. Encrypts username for query.
    
    Args:
        username: Plain text username
        protecting: EncryptionService instance (optional)
    
    Returns:
        True if user exists, False otherwise
    """
    # Quick existence check for signup/login
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT 1 FROM Users WHERE UserName = ?", (encrypted_username,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    except Exception:
        return False


def create_user(
    username: str,
    password: str,
    protecting=None,
    money: int = 10000,
    games_played: int = 0,
    is_admin: bool = False,
) -> bool:
    """
    Create new user account. Encrypts all fields (username, password, money, games).
    
    Args:
        username: Plain text username
        password: Plain text password
        protecting: EncryptionService instance (optional)
        money: Starting balance (default 10000)
        games_played: Starting games count (default 0)
    
    Returns:
        True if successful, False otherwise
    """
    # Insert a new user record (encrypted if needed)
    try:
        conn = _connect()
        cur = conn.cursor()
        
        now_iso = _now_iso()

        # Encrypt all fields if protecting provided
        if protecting:
            encrypted_username = _encode_username(username, protecting)
            encrypted_password = protecting.encrypt(password)
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(games_played))
            encrypted_created = protecting.encrypt(now_iso)
            encrypted_updated = protecting.encrypt(now_iso)
            encrypted_last_login = protecting.encrypt(now_iso)
            encrypted_is_admin = protecting.encrypt("1" if is_admin else "0")
        else:
            encrypted_username = username
            encrypted_password = password
            encrypted_money = str(money)
            encrypted_games = str(games_played)
            encrypted_created = now_iso
            encrypted_updated = now_iso
            encrypted_last_login = now_iso
            encrypted_is_admin = 1 if is_admin else 0
        
        cur.execute(
            """
            INSERT INTO Users (UserName, Password, Money, GamesPlayed, CreatedAt, UpdatedAt, LastLogin, IsAdmin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                encrypted_username,
                encrypted_password,
                encrypted_money,
                encrypted_games,
                encrypted_created,
                encrypted_updated,
                encrypted_last_login,
                encrypted_is_admin,
            )
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_money(username: str, protecting=None) -> int:
    """
    Get user's current balance. Encrypts username to query, decrypts money.
    
    Args:
        username: Plain text username
        protecting: EncryptionService instance (optional)
    
    Returns:
        User's balance as integer
    """
    # Read and decrypt user balance
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT Money FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return 0
        
        money = row[0]
        # Decrypt money if protecting provided
        if protecting and money:
            money = protecting.decrypt(money)
        return int(money)
    except Exception:
        return 0


def get_games_played(username: str, protecting=None) -> int:
    """
    Get user's games played count. Encrypts username to query, decrypts games.
    
    Args:
        username: Plain text username
        protecting: EncryptionService instance (optional)
    
    Returns:
        Games played count as integer
    """
    # Read and decrypt games played
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT GamesPlayed FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return 0
        
        games = row[0]
        # Decrypt games if protecting provided
        if protecting and games:
            games = protecting.decrypt(games)
        return int(games)
    except Exception:
        return 0


def update_money_and_games(username: str, money: int, games_played: int, protecting=None) -> bool:
    """
    Update user's balance and games played. Encrypts all fields.
    
    Args:
        username: Plain text username
        money: New balance
        games_played: New games count
        protecting: EncryptionService instance (optional)
    
    Returns:
        True if successful, False otherwise
    """
    # Update balance and games together
    try:
        conn = _connect()
        cur = conn.cursor()
        
        now_iso = _now_iso()

        if protecting:
            encrypted_username = _encode_username(username, protecting)
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(games_played))
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_username = username
            encrypted_money = str(money)
            encrypted_games = str(games_played)
            encrypted_updated = now_iso
        
        cur.execute(
            "UPDATE Users SET Money = ?, GamesPlayed = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_money, encrypted_games, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def increment_games_and_update_money(username: str, money: int, protecting=None) -> bool:
    """
    Update user's balance and increment games by 1. Encrypts all fields.
    
    Args:
        username: Plain text username
        money: New balance
        protecting: EncryptionService instance (optional)
    
    Returns:
        True if successful, False otherwise
    """
    # Add one game and update balance in one write
    try:
        conn = _connect()
        cur = conn.cursor()
        
        encrypted_username = _encode_username(username, protecting)
        
        # Get current games played
        cur.execute("SELECT GamesPlayed FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        
        current_games = row[0]
        if protecting:
            current_games = protecting.decrypt(current_games)
        
        # Increment and encrypt
        new_games = int(current_games) + 1
        now_iso = _now_iso()

        if protecting:
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(new_games))
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_money = str(money)
            encrypted_games = str(new_games)
            encrypted_updated = now_iso
        
        cur.execute(
            "UPDATE Users SET Money = ?, GamesPlayed = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_money, encrypted_games, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def delete_user(username: str, protecting=None) -> bool:
    """
    Delete a user. Encrypts username for query.
    
    Args:
        username: Plain text username
        protecting: EncryptionService instance (optional)
    
    Returns:
        True if successful, False otherwise
    """
    # Remove a user row
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("DELETE FROM Users WHERE UserName = ?", (encrypted_username,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_last_login(username: str, protecting=None) -> bool:
    """Update user's last login timestamp (and UpdatedAt)."""
    # Touch last_login and updated_at fields
    try:
        conn = _connect()
        cur = conn.cursor()

        encrypted_username = _encode_username(username, protecting)
        now_iso = _now_iso()

        if protecting:
            encrypted_last_login = protecting.encrypt(now_iso)
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_last_login = now_iso
            encrypted_updated = now_iso

        cur.execute(
            "UPDATE Users SET LastLogin = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_last_login, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_leaderboard(protecting=None, order_by: str = "GamesPlayed") -> List[Tuple[str, int, int]]:
    """
    Get leaderboard. Returns decrypted data if protecting provided.
    
    Returns list of tuples: (username, money, games_played) - all decrypted if protecting provided.
    
    Args:
        protecting: EncryptionService instance (optional)
        order_by: Column to sort by - "GamesPlayed", "Money", or "UserName" (default: "GamesPlayed")
    
    Returns:
        List of (username, money, games_played) tuples
    """
    # Fetch leaderboard data and decrypt if needed
    try:
        conn = _connect()
        cur = conn.cursor()
        
        # Validate sort column
        valid_columns = ["GamesPlayed", "Money", "UserName"]
        if order_by not in valid_columns:
            order_by = "GamesPlayed"
        
        # Query all users
        query = "SELECT UserName, Money, GamesPlayed FROM Users"
        if not protecting:
            query += f" ORDER BY {order_by} DESC"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        
        # Decrypt all fields if protecting provided
        if protecting:
            decrypted_rows = []
            for username, money, games in rows:
                decrypted_username = protecting.decrypt_deterministic(username) if username else ""
                decrypted_money = int(protecting.decrypt(money)) if money else 0
                decrypted_games = int(protecting.decrypt(games)) if games else 0
                decrypted_rows.append((decrypted_username, decrypted_money, decrypted_games))
            if order_by == "Money":
                decrypted_rows.sort(key=lambda row: row[1], reverse=True)
            elif order_by == "GamesPlayed":
                decrypted_rows.sort(key=lambda row: row[2], reverse=True)
            elif order_by == "UserName":
                decrypted_rows.sort(key=lambda row: row[0])
            return decrypted_rows
        else:
            # If no protecting, return as-is
            return [(username, int(money) if money else 0, int(games) if games else 0) 
                    for username, money, games in rows]
    except Exception:
        return []


def get_is_admin(username: str, protecting=None) -> bool:
    """Return True if the user is marked as admin."""
    # Check admin flag for menu gating
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT IsAdmin FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return False

        is_admin = row[0]
        if protecting and is_admin is not None:
            is_admin = protecting.decrypt(is_admin)
        try:
            return int(is_admin) == 1
        except Exception:
            return False
    except Exception:
        return False


def set_is_admin(username: str, is_admin: bool, protecting=None) -> bool:
    """Set the admin flag for a user."""
    # Update admin flag and timestamps
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        now_iso = _now_iso()

        if protecting:
            encrypted_is_admin = protecting.encrypt("1" if is_admin else "0")
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_is_admin = 1 if is_admin else 0
            encrypted_updated = now_iso

        cur.execute(
            "UPDATE Users SET IsAdmin = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_is_admin, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def get_all_usernames(protecting=None) -> List[str]:
    """Get list of all usernames (decrypted)."""
    # Pull a list of usernames for admin screens
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT UserName FROM Users ORDER BY UserName")
        rows = cur.fetchall()
        conn.close()

        if protecting:
            return [protecting.decrypt_deterministic(row[0]) for row in rows if row[0]]
        else:
            return [row[0] for row in rows if row[0]]
    except Exception:
        return []


def get_user_data(username: str, protecting=None) -> Optional[dict]:
    """Get all user data for a username."""
    # Fetch full user row and decrypt if needed
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        
        cur.execute("PRAGMA table_info(Users)")
        cols = {row[1] for row in cur.fetchall()}
        
        select_cols = ["UserName", "Password", "Money", "GamesPlayed"]
        if "IsAdmin" in cols:
            select_cols.append("IsAdmin")
        if "CreatedAt" in cols:
            select_cols.append("CreatedAt")
        if "UpdatedAt" in cols:
            select_cols.append("UpdatedAt")
        if "LastLogin" in cols:
            select_cols.append("LastLogin")
        
        cur.execute(f"SELECT {', '.join(select_cols)} FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        
        if not row:
            return None
        
        data = {}
        idx = 0
        if protecting:
            data["username"] = protecting.decrypt_deterministic(row[idx]) if row[idx] else ""
            idx += 1
            data["password"] = protecting.decrypt(row[idx]) if row[idx] else ""
            idx += 1
            data["money"] = int(protecting.decrypt(row[idx])) if row[idx] else 0
            idx += 1
            data["games_played"] = int(protecting.decrypt(row[idx])) if row[idx] else 0
            idx += 1
            if "IsAdmin" in cols:
                data["is_admin"] = int(protecting.decrypt(row[idx])) == 1 if row[idx] else False
                idx += 1
            if "CreatedAt" in cols:
                data["created_at"] = protecting.decrypt(row[idx]) if row[idx] else ""
                idx += 1
            if "UpdatedAt" in cols:
                data["updated_at"] = protecting.decrypt(row[idx]) if row[idx] else ""
                idx += 1
            if "LastLogin" in cols:
                data["last_login"] = protecting.decrypt(row[idx]) if row[idx] else ""
        else:
            data["username"] = row[idx]
            idx += 1
            data["password"] = row[idx]
            idx += 1
            data["money"] = int(row[idx]) if row[idx] else 0
            idx += 1
            data["games_played"] = int(row[idx]) if row[idx] else 0
            idx += 1
            if "IsAdmin" in cols:
                data["is_admin"] = int(row[idx]) == 1 if row[idx] else False
                idx += 1
            if "CreatedAt" in cols:
                data["created_at"] = row[idx]
                idx += 1
            if "UpdatedAt" in cols:
                data["updated_at"] = row[idx]
                idx += 1
            if "LastLogin" in cols:
                data["last_login"] = row[idx]
        
        return data
    except Exception:
        return None


def update_user_password(username: str, new_password: str, protecting=None) -> bool:
    """Update user's password."""
    # Change password with optional encryption
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        now_iso = _now_iso()
        
        if protecting:
            encrypted_password = protecting.encrypt(new_password)
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_password = new_password
            encrypted_updated = now_iso
        
        cur.execute(
            "UPDATE Users SET Password = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_password, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_user_balance(username: str, new_balance: int, protecting=None) -> bool:
    """Update user's balance."""
    # Change balance with optional encryption
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        now_iso = _now_iso()
        
        if protecting:
            encrypted_money = protecting.encrypt(str(new_balance))
            encrypted_updated = protecting.encrypt(now_iso)
        else:
            encrypted_money = str(new_balance)
            encrypted_updated = now_iso
        
        cur.execute(
            "UPDATE Users SET Money = ?, UpdatedAt = ? WHERE UserName = ?",
            (encrypted_money, encrypted_updated, encrypted_username)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False