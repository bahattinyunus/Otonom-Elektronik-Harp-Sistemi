import sqlite3
import time
import os
import threading

class MissionLogger:
    """SQLite Blackbox for recording mission events and signals."""
    def __init__(self, db_path="mission_log.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
        
    def _init_db(self):
        if os.path.dirname(self.db_path) and not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    freq_idx INTEGER,
                    snr REAL,
                    type TEXT,
                    aoa REAL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    mode TEXT,
                    target_count INTEGER,
                    reward REAL
                )
            ''')
            conn.commit()

    def log_signals(self, signals):
        if not signals: return
        now = time.time()
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    "INSERT INTO signals (timestamp, freq_idx, snr, type, aoa) VALUES (?, ?, ?, ?, ?)",
                    [(now, s['freq_idx'], s['snr'], s['type'], s['aoa']) for s in signals]
                )
                conn.commit()

    def log_action(self, ea_status):
        now = time.time()
        # Ensure we record the status context
        mode = ea_status.get('status', 'UNKNOWN')
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO actions (timestamp, mode, target_count, reward) VALUES (?, ?, ?, ?)",
                    (now, mode, ea_status.get('target_count', 0), ea_status.get('reward', 0))
                )
                conn.commit()
