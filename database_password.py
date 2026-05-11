import sqlite3

# ==============================
# Database Initialization
# ==============================
def setup_database():
    """
    Initializes the SQLite database by creating the 'users' table if it doesn't exist.
    Inserts a default admin user if not already present.
    """
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Check if default admin exists
    cursor.execute('SELECT * FROM users WHERE username="admin"')
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (username, password) VALUES ("admin", "password123")'
        )

    conn.commit()
    conn.close()

    # Cleanup orphan temp staging DB from previous unclean shutdowns
    try:
        from temp_db import cleanup_orphan_temp_db
        cleanup_orphan_temp_db()
    except Exception as e:
        print(f"Warning: Could not clean orphan temp DB on startup: {e}")


# ==============================
# Login Verification
# ==============================
def verify_login(username: str, password: str) -> bool:
    """
    Checks whether a username and password combination exists in the database.

    Args:
        username (str): Username to verify.
        password (str): Password to verify.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM users WHERE username=? AND password=?',
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user is not None


# ==============================
# Update Password
# ==============================
def update_password(current_pw: str, new_pw: str) -> bool:
    """
    Updates the password for the admin user after verifying the current password.

    Args:
        current_pw (str): Current admin password.
        new_pw (str): New password to set.

    Returns:
        bool: True if password updated successfully, False if current password is incorrect.
    """
    conn = sqlite3.connect('survey.db')
    cursor = conn.cursor()

    # Verify current password
    cursor.execute(
        'SELECT * FROM users WHERE username="admin" AND password=?',
        (current_pw,)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False

    # Update password
    cursor.execute(
        'UPDATE users SET password=? WHERE username="admin"',
        (new_pw,)
    )
    conn.commit()
    conn.close()
    return True