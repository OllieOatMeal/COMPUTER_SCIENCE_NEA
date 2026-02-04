"""
Database helper utilities for SQLite interactions.
Centralises SQL used by scenes; encrypts/decrypts all user fields except UserID.

All fields (UserName, Password, Money, GamesPlayed) are encrypted on write and 
decrypted on read when protecting (EncryptionService) is provided.
"""
import sqlite3
from typing import List, Tuple, Optional
from variables import database_path


def _connect():
    return sqlite3.connect(database_path)


def get_user_password(username: str, protecting=None) -> Optional[str]:
    """
    Get password for a user. Encrypts username to query, returns decrypted password.
    
    Args:
        username: Plain text username
        protecting: EncryptionService instance (optional). If provided, encrypts/decrypts fields.
    
    Returns:
        Plain text password or None if user not found
    """
    try:
        conn = _connect()
        cur = conn.cursor()
        # Encrypt username to match DB storage
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
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
    try:
        conn = _connect()
        cur = conn.cursor()
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
        cur.execute("SELECT 1 FROM Users WHERE UserName = ?", (encrypted_username,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    except Exception:
        return False


def create_user(username: str, password: str, protecting=None, money: int = 10000, games_played: int = 0) -> bool:
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
    try:
        conn = _connect()
        cur = conn.cursor()
        
        # Encrypt all fields if protecting provided
        if protecting:
            encrypted_username = protecting.encrypt(username)
            encrypted_password = protecting.encrypt(password)
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(games_played))
        else:
            encrypted_username = username
            encrypted_password = password
            encrypted_money = str(money)
            encrypted_games = str(games_played)
        
        cur.execute(
            "INSERT INTO Users (UserName, Password, Money, GamesPlayed) VALUES (?, ?, ?, ?)",
            (encrypted_username, encrypted_password, encrypted_money, encrypted_games)
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
    try:
        conn = _connect()
        cur = conn.cursor()
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
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
    try:
        conn = _connect()
        cur = conn.cursor()
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
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
    try:
        conn = _connect()
        cur = conn.cursor()
        
        if protecting:
            encrypted_username = protecting.encrypt(username)
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(games_played))
        else:
            encrypted_username = username
            encrypted_money = str(money)
            encrypted_games = str(games_played)
        
        cur.execute(
            "UPDATE Users SET Money = ?, GamesPlayed = ? WHERE UserName = ?",
            (encrypted_money, encrypted_games, encrypted_username)
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
    try:
        conn = _connect()
        cur = conn.cursor()
        
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
        
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
        if protecting:
            encrypted_money = protecting.encrypt(str(money))
            encrypted_games = protecting.encrypt(str(new_games))
        else:
            encrypted_money = str(money)
            encrypted_games = str(new_games)
        
        cur.execute(
            "UPDATE Users SET Money = ?, GamesPlayed = ? WHERE UserName = ?",
            (encrypted_money, encrypted_games, encrypted_username)
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
    try:
        conn = _connect()
        cur = conn.cursor()
        if protecting:
            encrypted_username = protecting.encrypt(username)
        else:
            encrypted_username = username
        cur.execute("DELETE FROM Users WHERE UserName = ?", (encrypted_username,))
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
    try:
        conn = _connect()
        cur = conn.cursor()
        
        # Validate sort column
        valid_columns = ["GamesPlayed", "Money", "UserName"]
        if order_by not in valid_columns:
            order_by = "GamesPlayed"
        
        # Query all users
        query = f"SELECT UserName, Money, GamesPlayed FROM Users ORDER BY {order_by} DESC"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        
        # Decrypt all fields if protecting provided
        if protecting:
            decrypted_rows = []
            for username, money, games in rows:
                decrypted_username = protecting.decrypt(username) if username else ""
                decrypted_money = int(protecting.decrypt(money)) if money else 0
                decrypted_games = int(protecting.decrypt(games)) if games else 0
                decrypted_rows.append((decrypted_username, decrypted_money, decrypted_games))
            return decrypted_rows
        else:
            # If no protecting, return as-is
            return [(username, int(money) if money else 0, int(games) if games else 0) 
                    for username, money, games in rows]
    except Exception:
        return []
