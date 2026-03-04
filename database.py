import sqlite3

DB_NAME = "health_ai.db"


# =====================================
# DATABASE CONNECTION
# =====================================
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================
# SAFE COLUMN CHECK (Prevents Future Errors)
# =====================================
def column_exists(table, column):
    with get_connection() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = [row["name"] for row in cursor.fetchall()]
        return column in columns


# =====================================
# USER TABLE
# =====================================
def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                height REAL,
                weight REAL,
                activity_level TEXT,
                goal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_user(name, age, gender, height, weight, activity_level, goal):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users
            (name, age, gender, height, weight, activity_level, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, age, gender, height, weight, activity_level, goal))
        conn.commit()


def get_user(name):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT age, gender, height, weight, activity_level, goal
            FROM users
            WHERE name = ?
            ORDER BY id DESC
            LIMIT 1
        """, (name,))
        return cursor.fetchone()


# =====================================
# CALORIE LOG TABLE (Auto-Migration Safe)
# =====================================
def create_log_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calorie_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                required_calories REAL,
                consumed_calories REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    # Auto-fix old database versions
    if not column_exists("calorie_logs", "required_calories"):
        with get_connection() as conn:
            conn.execute("ALTER TABLE calorie_logs ADD COLUMN required_calories REAL")
            conn.commit()

    if not column_exists("calorie_logs", "consumed_calories"):
        with get_connection() as conn:
            conn.execute("ALTER TABLE calorie_logs ADD COLUMN consumed_calories REAL")
            conn.commit()


def add_log(name, date, required, consumed):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO calorie_logs
            (name, date, required_calories, consumed_calories)
            VALUES (?, ?, ?, ?)
        """, (name, date, required, consumed))
        conn.commit()


def get_logs(name):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT date, required_calories, consumed_calories
            FROM calorie_logs
            WHERE name = ?
            ORDER BY date ASC
        """, (name,))
        return cursor.fetchall()


# =====================================
# AUTH TABLE (Improved)
# =====================================
def create_auth_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def register_user(username, password):
    try:
        with get_connection() as conn:
            conn.execute("""
                INSERT INTO auth_users (username, password)
                VALUES (?, ?)
            """, (username, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def login_user(username, password):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM auth_users
            WHERE username = ? AND password = ?
        """, (username, password))
        return cursor.fetchone()