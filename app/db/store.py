import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'feather.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code       TEXT UNIQUE NOT NULL,
            species         TEXT NOT NULL,
            human_is_bird_a INTEGER NOT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed       INTEGER DEFAULT 0,
            judge_correct   INTEGER
        );

        CREATE TABLE IF NOT EXISTS score_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            room_code   TEXT NOT NULL,
            species     TEXT NOT NULL,
            ai_fooled   INTEGER NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


def create_session(room_code, species, human_is_bird_a):
    conn = get_db()
    conn.execute(
        'INSERT INTO game_sessions (room_code, species, human_is_bird_a) VALUES (?, ?, ?)',
        (room_code, species, int(human_is_bird_a))
    )
    conn.commit()
    conn.close()


def get_session(room_code):
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM game_sessions WHERE room_code = ?', (room_code,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def complete_session(room_code, judge_correct):
    conn = get_db()
    session = conn.execute(
        'SELECT species, human_is_bird_a FROM game_sessions WHERE room_code = ?',
        (room_code,)
    ).fetchone()
    if session:
        # ai_fooled = judge guessed wrong (thought AI was human)
        ai_fooled = 1 if not judge_correct else 0
        conn.execute(
            'UPDATE game_sessions SET completed = 1, judge_correct = ? WHERE room_code = ?',
            (int(judge_correct), room_code)
        )
        conn.execute(
            'INSERT INTO score_records (room_code, species, ai_fooled) VALUES (?, ?, ?)',
            (room_code, session['species'], ai_fooled)
        )
        conn.commit()
    conn.close()


def get_leaderboard():
    conn = get_db()
    rows = conn.execute('''
        SELECT species,
               COUNT(*) AS total_games,
               SUM(ai_fooled) AS times_fooled,
               ROUND(100.0 * SUM(ai_fooled) / COUNT(*), 1) AS fool_rate
        FROM score_records
        GROUP BY species
        ORDER BY fool_rate DESC
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]
