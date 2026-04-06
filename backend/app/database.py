"""
VISIONZ — Database Layer
Creates all tables. Seeds ONLY users — NO fake analytics, NO fake reports.
All data is generated from real user activity (video uploads + detections).
"""

import sqlite3
import os
from app.security import PasswordManager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "visionz.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt"""
    return PasswordManager.hash_password(password)


def init_db():
    conn = get_db()
    cur  = conn.cursor()

    # ── USERS ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            role        TEXT    NOT NULL DEFAULT 'operator',
            avatar      TEXT    NOT NULL DEFAULT 'U',
            department  TEXT,
            created_at  TEXT    DEFAULT (datetime('now')),
            last_login  TEXT
        )
    """)

    # ── SESSIONS ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(id),
            token        TEXT    NOT NULL UNIQUE,
            login_time   TEXT    DEFAULT (datetime('now')),
            logout_time  TEXT,
            is_active    INTEGER DEFAULT 1
        )
    """)

    # ── VIDEOS ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            filename      TEXT    NOT NULL,
            original_name TEXT    NOT NULL,
            file_size     INTEGER,
            duration      REAL,
            resolution    TEXT,
            uploaded_at   TEXT    DEFAULT (datetime('now')),
            status        TEXT    DEFAULT 'uploaded'
        )
    """)

    # ── DETECTIONS ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id        INTEGER REFERENCES videos(id),
            user_id         INTEGER NOT NULL REFERENCES users(id),
            defect_type     TEXT    NOT NULL,
            severity        TEXT    NOT NULL,
            confidence      REAL    NOT NULL,
            product         TEXT,
            line            TEXT,
            camera          TEXT,
            frame_number    INTEGER,
            video_timestamp REAL,
            bbox_x          REAL,
            bbox_y          REAL,
            bbox_w          REAL,
            bbox_h          REAL,
            detected_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── REPORTS ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            report_name   TEXT    NOT NULL,
            report_type   TEXT    NOT NULL DEFAULT 'session',
            period_start  TEXT,
            period_end    TEXT,
            total_scanned INTEGER DEFAULT 0,
            total_defects INTEGER DEFAULT 0,
            quality_score INTEGER DEFAULT 0,
            cat_counts    TEXT    DEFAULT '{}',
            downloaded    INTEGER DEFAULT 0,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()

    # ── SEED USERS ONLY (no analytics, no reports) ──
    seed_users = [
        ("Arun Kumar",    "arun@visionz.com",    "arun123",    "admin",    "AK", "Quality Control"),
        ("Priya Sharma",  "priya@visionz.com",   "priya123",   "manager",  "PS", "Production Management"),
        ("Ravi Operator", "ravi@visionz.com",    "ravi123",    "operator", "RO", "Line Operations"),
        ("Meena Devi",    "meena@visionz.com",   "meena123",   "admin",    "MD", "Quality Control"),
        ("Karthik Raja",  "karthik@visionz.com", "karthik123", "manager",  "KR", "Analytics"),
        ("Nivethitha S",  "nivethitha@visionz.com", "Nive!@#1131", "admin", "NS", "Quality Control"),
    ]
    for name, email, pw, role, avatar, dept in seed_users:
        cur.execute(
            "INSERT OR IGNORE INTO users (name,email,password,role,avatar,department) VALUES (?,?,?,?,?,?)",
            (name, email, hash_password(pw), role, avatar, dept),
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized. No fake data — all zeros until you upload a video.")
