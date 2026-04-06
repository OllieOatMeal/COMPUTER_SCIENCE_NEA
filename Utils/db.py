"""

# Code to handle accessing the database

"""

"""
# Import nessicary functions/ procedures
"""
import sqlite3
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from Utils.variables import database_path


# Returns the current date & time in the ISO format
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Preloads the database
def _ensure_schema(conn: sqlite3.Connection) -> None:
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
        return

# Connects to the database
def _connect():
    conn = sqlite3.connect(database_path)
    _ensure_schema(conn)
    return conn

# Encrypts the username
def _encode_username(username: str, protecting=None) -> str:
    if protecting:
        try:
            return protecting.encrypt_deterministic(username)
        except Exception:
            return username
    return username

# Gets the users password
def get_user_password(username: str, protecting=None) -> Optional[str]:
    try:
        conn = _connect()
        cur = conn.cursor()
        encrypted_username = _encode_username(username, protecting)
        cur.execute("SELECT Password FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        password = row[0]
        if protecting and password:
            password = protecting.decrypt(password)
        return password
    except Exception:
        return None

# Checks if a username already exists
def user_exists(username: str, protecting=None) -> bool:
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

# Creates a new user with predefined perameters
def create_user(
    username: str,
    password: str,
    protecting=None,
    money: int = 10000,
    games_played: int = 0,
    is_admin: bool = False,
) -> bool:
    try:
        conn = _connect()
        cur = conn.cursor()
        
        now_iso = _now_iso()

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

# Gets the users balance
def get_money(username: str, protecting=None) -> int:
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
        if protecting and money:
            money = protecting.decrypt(money)
        return int(money)
    except Exception:
        return 0

# Gets the users games played value
def get_games_played(username: str, protecting=None) -> int:
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
        if protecting and games:
            games = protecting.decrypt(games)
        return int(games)
    except Exception:
        return 0

# Sets the users current balance and games played
def update_money_and_games(username: str, money: int, games_played: int, protecting=None) -> bool:
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

# Sets the users balance and games played after each game
def increment_games_and_update_money(username: str, money: int, protecting=None) -> bool:
    try:
        conn = _connect()
        cur = conn.cursor()
        
        encrypted_username = _encode_username(username, protecting)
        
        cur.execute("SELECT GamesPlayed FROM Users WHERE UserName = ?", (encrypted_username,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        
        current_games = row[0]
        if protecting:
            current_games = protecting.decrypt(current_games)
        
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

# Deletes a user from the database
def delete_user(username: str, protecting=None) -> bool:
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

# Sets the users last logged in timestamp
def update_last_login(username: str, protecting=None) -> bool:
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

# Gets the data needed to display the leaderboard
def get_leaderboard(protecting=None, order_by: str = "GamesPlayed") -> List[Tuple[str, int, int]]:
    try:
        conn = _connect()
        cur = conn.cursor()
        
        valid_columns = ["GamesPlayed", "Money", "UserName"]
        if order_by not in valid_columns:
            order_by = "GamesPlayed"
        
        query = "SELECT UserName, Money, GamesPlayed FROM Users"
        if not protecting:
            query += f" ORDER BY {order_by} DESC"
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        
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
            return [(username, int(money) if money else 0, int(games) if games else 0) 
                    for username, money, games in rows]
    except Exception:
        return []

# Gets the admin status of a user
def get_is_admin(username: str, protecting=None) -> bool:
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

# Sets the admin status of a user
def set_is_admin(username: str, is_admin: bool, protecting=None) -> bool:
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

# Gets all usernames from the database
def get_all_usernames(protecting=None) -> List[str]:
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

# Gets all the data from a specific user
def get_user_data(username: str, protecting=None) -> Optional[dict]:
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

# Sets the users password
def update_user_password(username: str, new_password: str, protecting=None) -> bool:
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

# Sets the users balance
def update_user_balance(username: str, new_balance: int, protecting=None) -> bool:
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