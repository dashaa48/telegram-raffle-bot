import sqlite3
import random
from datetime import datetime, date
from config import Config

DB = Config.DB_PATH


def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            started_at TEXT,
            contact_name TEXT,
            contact_agreed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner TEXT NOT NULL,
            code TEXT NOT NULL,
            valid_until TEXT,
            is_used INTEGER DEFAULT 0,
            used_by INTEGER,
            used_at TEXT
        );
        CREATE TABLE IF NOT EXISTS user_promo (
            user_id INTEGER,
            partner TEXT,
            code TEXT,
            issued_at TEXT,
            PRIMARY KEY (user_id, partner, issued_at)
        );
        CREATE TABLE IF NOT EXISTS daily_raffles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            partner TEXT,
            raffle_date TEXT,
            registered_at TEXT,
            UNIQUE(user_id, partner, raffle_date)
        );
        CREATE TABLE IF NOT EXISTS chances (
            user_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS winners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prize_type TEXT,   -- 'daily' | 'final'
            partner TEXT,
            prize_name TEXT,
            won_at TEXT,
            notified INTEGER DEFAULT 0,
            claimed INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS partners (
            partner TEXT PRIMARY KEY,
            channel_username TEXT,
            active INTEGER DEFAULT 1
        );
        """)
        conn.commit()


# ---------- USERS ----------
def register_user(user_id, username, first_name):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, NULL, 0)",
            (user_id, username, first_name, datetime.now().isoformat())
        )
        conn.commit()


def user_exists(user_id):
    with sqlite3.connect(DB) as conn:
        return conn.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,)).fetchone() is not None


def get_available_promo(partner):
    with sqlite3.connect(DB) as conn:
        row = conn.execute(
            "SELECT id, code FROM promo_codes WHERE partner=? AND is_used=0 LIMIT 1",
            (partner,)
        ).fetchone()
        return row


def issue_promo(user_id, partner):
    today = date.today().isoformat()
    with sqlite3.connect(DB) as conn:
        existing = conn.execute(
            "SELECT code FROM user_promo WHERE user_id=? AND partner=? AND date(issued_at)=?",
            (user_id, partner, today)
        ).fetchone()
        if existing:
            return ('already', existing[0])

        promo = get_available_promo(partner)
        if not promo:
            return ('empty', None)

        promo_id, code = promo
        conn.execute(
            "UPDATE promo_codes SET is_used=1, used_by=?, used_at=? WHERE id=?",
            (user_id, datetime.now().isoformat(), promo_id)
        )
        conn.execute(
            "INSERT INTO user_promo VALUES (?, ?, ?, ?)",
            (user_id, partner, code, datetime.now().isoformat())
        )
        conn.commit()
        return ('ok', code)


def promo_left(partner):
    with sqlite3.connect(DB) as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM promo_codes WHERE partner=? AND is_used=0", (partner,)
        ).fetchone()[0]


def register_for_raffle(user_id, partner):
    today = date.today().isoformat()
    with sqlite3.connect(DB) as conn:
        try:
            conn.execute(
                "INSERT INTO daily_raffles (user_id, partner, raffle_date, registered_at) VALUES (?, ?, ?, ?)",
                (user_id, partner, today, datetime.now().isoformat())
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # уже участвует


def get_raffle_partners(partner):
    today = date.today().isoformat()
    with sqlite3.connect(DB) as conn:
        return [r[0] for r in conn.execute(
            "SELECT user_id FROM daily_raffles WHERE partner=? AND raffle_date=?",
            (partner, today)
        ).fetchall()]


def add_chance(user_id):
    today = date.today().isoformat()
    with sqlite3.connect(DB) as conn:
        already = conn.execute(
            "SELECT 1 FROM daily_raffles WHERE user_id=? AND raffle_date=?",
            (user_id, today)
        ).fetchone()
        promo_today = conn.execute(
            "SELECT 1 FROM user_promo WHERE user_id=? AND date(issued_at)=?",
            (user_id, today)
        ).fetchone()
        if not (already or promo_today):
            return 0

        conn.execute("INSERT OR IGNORE INTO chances VALUES (?, 0)", (user_id,))
        # считаем уникальные активные дни
        days = conn.execute("""
            SELECT COUNT(DISTINCT date) FROM (
                SELECT date(registered_at) AS date FROM daily_raffles WHERE user_id=?
                UNION
                SELECT date(issued_at) AS date FROM user_promo WHERE user_id=?
            )
        """, (user_id, user_id)).fetchone()[0]
        days = min(days, 10)
        conn.execute("UPDATE chances SET count=? WHERE user_id=?", (days, user_id))
        conn.commit()
        return days


def get_chances(user_id):
    with sqlite3.connect(DB) as conn:
        row = conn.execute("SELECT count FROM chances WHERE user_id=?", (user_id,)).fetchone()
        return row[0] if row else 0


def get_user_partners(user_id):
    with sqlite3.connect(DB) as conn:
        p1 = [r[0] for r in conn.execute("SELECT DISTINCT partner FROM daily_raffles WHERE user_id=?", (user_id,)).fetchall()]
        p2 = [r[0] for r in conn.execute("SELECT DISTINCT partner FROM user_promo WHERE user_id=?", (user_id,)).fetchall()]
        return sorted(set(p1 + p2))


def draw_daily_winners(partner, prize_name, count):
    participants = get_raffle_partners(partner)
    if not participants:
        return []
    winners = random.sample(participants, min(count, len(participants)))
    with sqlite3.connect(DB) as conn:
        for uid in winners:
            conn.execute(
                "INSERT INTO winners (user_id, prize_type, partner, prize_name, won_at) VALUES (?, 'daily', ?, ?, ?)",
                (uid, partner, prize_name, datetime.now().isoformat())
            )
        conn.commit()
    return winners


def draw_final_winners(ticket_count=10):
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT user_id, count FROM chances WHERE count>0").fetchall()
    pool = []
    for uid, c in rows:
        pool.extend([uid] * c)
    if not pool:
        return []
    # 5 уникальных победителей
    winners = []
    seen = set()
    random.shuffle(pool)
    for uid in pool:
        if uid not in seen:
            winners.append(uid)
            seen.add(uid)
        if len(winners) * 2 >= ticket_count:
            break
    with sqlite3.connect(DB) as conn:
        for uid in winners:
            conn.execute(
                "INSERT INTO winners (user_id, prize_type, partner, prize_name, won_at) VALUES (?, 'final', 'MAIN', 'Билет на Канье Уэста (2 шт)', ?)",
                (uid, datetime.now().isoformat())
            )
        conn.commit()
    return winners


def get_stats():
    with sqlite3.connect(DB) as conn:
        started = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        today = date.today().isoformat()
        new_today = conn.execute("SELECT COUNT(*) FROM users WHERE date(started_at)=?", (today,)).fetchone()[0]
        promo_req = conn.execute("SELECT COUNT(*) FROM user_promo").fetchone()[0]
        promo_issued = conn.execute("SELECT COUNT(*) FROM promo_codes WHERE is_used=1").fetchone()[0]
        participants = conn.execute("SELECT COUNT(*) FROM daily_raffles WHERE raffle_date=?", (today,)).fetchone()[0]
        partners_left = {r[0]: r[1] for r in conn.execute("SELECT partner, COUNT(*) FROM promo_codes WHERE is_used=0 GROUP BY partner").fetchall()}
        return {
            "started": started,
            "new_today": new_today,
            "promo_requests": promo_req,
            "promo_issued": promo_issued,
            "today_participants": participants,
            "partners_left": partners_left,
        }