import sqlite3
from datetime import datetime, timedelta


def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_date TEXT,
            is_premium INTEGER DEFAULT 0,
            premium_start TEXT,
            premium_end TEXT,
            premium_months INTEGER DEFAULT 0,
            premium_price INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY,
            info TEXT,
            file_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cartoons (
            code TEXT PRIMARY KEY,
            info TEXT,
            file_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_movies (
            code TEXT PRIMARY KEY,
            info TEXT,
            file_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS premium_cartoons (
            code TEXT PRIMARY KEY,
            info TEXT,
            file_id TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            channel_name TEXT,
            channel_link TEXT,
            channel_type TEXT DEFAULT 'telegram'
        )
    ''')
    # Eski bazaga channel_type ustunini qo'shish (agar yo'q bo'lsa)
    try:
        cursor.execute("ALTER TABLE channels ADD COLUMN channel_type TEXT DEFAULT 'telegram'")
    except Exception:
        pass  # Ustun allaqachon bor

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kino_channel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_link TEXT,
            channel_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            months INTEGER,
            price INTEGER,
            receipt_file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_date TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ===== USERS =====

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_all_users():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def get_users_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ===== ODDIY KINOLAR =====

def add_movie(code, info, file_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO movies (code, info, file_id) VALUES (?, ?, ?)', (code, info, file_id))
    conn.commit()
    conn.close()


def get_movie(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE code = ?', (code,))
    movie = cursor.fetchone()
    conn.close()
    return movie


def get_movies_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM movies')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def delete_movie(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM movies WHERE code = ?', (code,))
    conn.commit()
    conn.close()


# ===== ODDIY MULTFILMLAR =====

def add_cartoon(code, info, file_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO cartoons (code, info, file_id) VALUES (?, ?, ?)', (code, info, file_id))
    conn.commit()
    conn.close()


def get_cartoon(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cartoons WHERE code = ?', (code,))
    cartoon = cursor.fetchone()
    conn.close()
    return cartoon


def get_cartoons_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM cartoons')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def delete_cartoon(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cartoons WHERE code = ?', (code,))
    conn.commit()
    conn.close()


# ===== PREMIUM KINOLAR =====

def add_premium_movie(code, info, file_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO premium_movies (code, info, file_id) VALUES (?, ?, ?)', (code, info, file_id))
    conn.commit()
    conn.close()


def get_premium_movie(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM premium_movies WHERE code = ?', (code,))
    movie = cursor.fetchone()
    conn.close()
    return movie


def get_premium_movies_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM premium_movies')
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ===== PREMIUM MULTFILMLAR =====

def add_premium_cartoon(code, info, file_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO premium_cartoons (code, info, file_id) VALUES (?, ?, ?)', (code, info, file_id))
    conn.commit()
    conn.close()


def get_premium_cartoon(code):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM premium_cartoons WHERE code = ?', (code,))
    cartoon = cursor.fetchone()
    conn.close()
    return cartoon


def get_premium_cartoons_count():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM premium_cartoons')
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ===== OBUNA KANALLARI =====

def add_channel(channel_id, channel_name, channel_link, channel_type='telegram'):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO channels (channel_id, channel_name, channel_link, channel_type)
        VALUES (?, ?, ?, ?)
    ''', (channel_id, channel_name, channel_link, channel_type))
    conn.commit()
    conn.close()


def get_all_channels():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels')
    channels = cursor.fetchall()
    conn.close()
    return channels


def get_telegram_channels():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels WHERE channel_type = 'telegram'")
    channels = cursor.fetchall()
    conn.close()
    return channels


def delete_channel(channel_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM channels WHERE id = ?', (channel_id,))
    conn.commit()
    conn.close()


# ===== KINO TUGMASI KANALI =====

def set_kino_channel(channel_link, channel_name):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM kino_channel')
    cursor.execute('INSERT INTO kino_channel (channel_link, channel_name) VALUES (?, ?)', (channel_link, channel_name))
    conn.commit()
    conn.close()


def get_kino_channel():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kino_channel LIMIT 1')
    ch = cursor.fetchone()
    conn.close()
    return ch


def delete_kino_channel():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM kino_channel')
    conn.commit()
    conn.close()


# ===== TO'LOVLAR =====

def add_payment(user_id, months, price, receipt_file_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO payments (user_id, months, price, receipt_file_id, created_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, months, price, receipt_file_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()
    return payment_id


def get_payment(payment_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
    payment = cursor.fetchone()
    conn.close()
    return payment


def get_pending_payments():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE status = "pending"')
    payments = cursor.fetchall()
    conn.close()
    return payments


def approve_payment(payment_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, months FROM payments WHERE id = ?', (payment_id,))
    payment = cursor.fetchone()

    if payment:
        user_id, months = payment[0], payment[1]
        cursor.execute('SELECT premium_end FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        try:
            if user and user[0]:
                old_end = datetime.strptime(user[0], "%Y-%m-%d %H:%M:%S")
                new_end = (old_end + timedelta(days=30 * months)) if old_end > datetime.now() else (datetime.now() + timedelta(days=30 * months))
            else:
                new_end = datetime.now() + timedelta(days=30 * months)
        except Exception:
            new_end = datetime.now() + timedelta(days=30 * months)

        cursor.execute('''
            UPDATE users
            SET is_premium = 1, premium_start = ?, premium_end = ?, premium_months = ?,
                premium_price = (SELECT price FROM payments WHERE id = ?)
            WHERE user_id = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), new_end.strftime("%Y-%m-%d %H:%M:%S"),
              months, payment_id, user_id))
        cursor.execute('UPDATE payments SET status = "approved" WHERE id = ?', (payment_id,))
        conn.commit()
    conn.close()


def reject_payment(payment_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE payments SET status = "rejected" WHERE id = ?', (payment_id,))
    conn.commit()
    conn.close()


# ===== PREMIUM STATUS =====

def check_premium_status(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_premium, premium_end FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    if user and user[0] == 1:
        try:
            premium_end = datetime.strptime(user[1], "%Y-%m-%d %H:%M:%S")
            if premium_end > datetime.now():
                conn.close()
                return True
            else:
                cursor.execute('UPDATE users SET is_premium = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
        except Exception:
            pass
    conn.close()
    return False


def get_premium_users():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, first_name, premium_months, premium_end
        FROM users WHERE is_premium = 1
    ''')
    users = cursor.fetchall()
    conn.close()
    return users


def get_premium_users_by_months(months):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, first_name, premium_end
        FROM users WHERE is_premium = 1 AND premium_months = ?
        ORDER BY premium_end DESC
    ''', (months,))
    users = cursor.fetchall()
    conn.close()
    return users


def remove_premium(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET is_premium = 0, premium_start = NULL, premium_end = NULL
        WHERE user_id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()


def get_premium_info(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT premium_start, premium_end, premium_price, premium_months
        FROM users WHERE user_id = ?
    ''', (user_id,))
    info = cursor.fetchone()
    conn.close()
    return info

# Bot mashhudev tomonidan yaratildi izohlar yaxshiroq tushunishiz uchunn yozil