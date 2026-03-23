import sqlite3
import time
import os
import threading
import queue


class MissionLogger:
    """SQLite Blackbox — records signals/actions asynchronously to prevent blocking the main loop."""

    def __init__(self, db_path="mission_log.db"):
        self.db_path = db_path
        self.queue   = queue.Queue()
        self._init_db()
        
        # Start background worker
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()

    # ── Schema ───────────────────────────────────────────────────────────────
    def _init_db(self):
        dirp = os.path.dirname(self.db_path)
        if dirp and not os.path.exists(dirp):
            os.makedirs(dirp)

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp     REAL,
                    freq_idx      INTEGER,
                    freq_mhz      REAL,
                    snr           REAL,
                    type          TEXT,
                    confidence    REAL,
                    threat_level  TEXT,
                    aoa           REAL,
                    df_confidence REAL,
                    track_id      TEXT,
                    track_hits    INTEGER,
                    rfi_hash      TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp    REAL,
                    action       TEXT,
                    target_count INTEGER,
                    reward       REAL,
                    epsilon      REAL,
                    episode      INTEGER,
                    q_states     INTEGER
                )
            ''')
            conn.commit()
            self._migrate(c, conn)

    def _migrate(self, c, conn):
        """Non-destructive column additions for existing databases."""
        existing_sig = {r[1] for r in c.execute("PRAGMA table_info(signals)")}
        for col, typedef in {
            "freq_mhz":      "REAL DEFAULT 0",
            "confidence":    "REAL DEFAULT 0",
            "threat_level":  "TEXT DEFAULT 'LOW'",
            "df_confidence": "REAL DEFAULT 0",
            "track_hits":    "INTEGER DEFAULT 1",
        }.items():
            if col not in existing_sig:
                c.execute(f"ALTER TABLE signals ADD COLUMN {col} {typedef}")

        existing_act = {r[1] for r in c.execute("PRAGMA table_info(actions)")}
        for col, typedef in {
            "action":  "TEXT DEFAULT 'UNKNOWN'",
            "epsilon": "REAL DEFAULT 1.0",
            "episode": "INTEGER DEFAULT 0",
            "q_states": "INTEGER DEFAULT 0",
        }.items():
            if col not in existing_act:
                c.execute(f"ALTER TABLE actions ADD COLUMN {col} {typedef}")

        conn.commit()

    # ── Worker ───────────────────────────────────────────────────────────────
    def _worker(self):
        """Background thread that processes log entries from the queue."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        while True:
            try:
                # Blocks until an item is available
                item_type, data = self.queue.get()
                
                cursor = conn.cursor()
                if item_type == "SIGNALS":
                    cursor.executemany(
                        """INSERT INTO signals
                           (timestamp, freq_idx, freq_mhz, snr, type, confidence,
                            threat_level, aoa, df_confidence, track_id, track_hits, rfi_hash)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                        data
                    )
                elif item_type == "ACTION":
                    cursor.execute(
                        "INSERT INTO actions (timestamp, action, target_count, reward, epsilon, episode, q_states) "
                        "VALUES (?,?,?,?,?,?,?)",
                        data
                    )
                
                conn.commit()
                self.queue.task_done()
            except Exception as e:
                # Basic error reporting to console, avoid stopping the thread
                print(f"[MissionLogger] Worker Error: {e}")
                time.sleep(1.0) 

    # ── Write (Non-blocking) ──────────────────────────────────────────────────
    def log_signals(self, signals):
        if not signals:
            return
        now = time.time()
        payload = [
            (now, s["freq_idx"], s.get("freq_mhz", 0), s["snr"], s["type"], 
             s.get("confidence", 0), s.get("threat_level", "LOW"), s["aoa"],
             s.get("df_confidence", 0), s.get("track_id", "N/A"),
             s.get("track_hits", 1), s.get("rfi_hash", "N/A"))
            for s in signals
        ]
        self.queue.put(("SIGNALS", payload))

    def log_action(self, ea_status):
        now = time.time()
        payload = (
            now, ea_status.get("action", "UNKNOWN"),
            ea_status.get("target_count", 0),
            ea_status.get("reward", 0),
            ea_status.get("epsilon", 1.0),
            ea_status.get("episode", 0),
            ea_status.get("q_states", 0)
        )
        self.queue.put(("ACTION", payload))

    # ── Read / AAR ────────────────────────────────────────────────────────────
    def get_recent_signals(self, n: int = 50) -> list:
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT timestamp, freq_mhz, snr, type, confidence, "
                    "threat_level, aoa, df_confidence, track_id, rfi_hash "
                    "FROM signals ORDER BY timestamp DESC LIMIT ?", (n,)
                )
                cols = ["timestamp", "freq_mhz", "snr", "type", "confidence",
                        "threat_level", "aoa", "df_confidence", "track_id", "rfi_hash"]
                return [dict(zip(cols, row)) for row in c.fetchall()]
        except Exception:
            return []

    def get_threat_stats(self, window_sec: int = 300) -> dict:
        """Signal count per threat level in the last window_sec seconds."""
        try:
            cutoff = time.time() - window_sec
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT threat_level, COUNT(*) FROM signals "
                    "WHERE timestamp > ? GROUP BY threat_level", (cutoff,)
                )
                return dict(c.fetchall())
        except Exception:
            return {}

    def get_action_history(self, n: int = 100) -> list:
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT timestamp, action, target_count, reward, epsilon, episode, q_states "
                    "FROM actions ORDER BY timestamp DESC LIMIT ?", (n,)
                )
                cols = ["timestamp", "action", "target_count", "reward", "epsilon", "episode", "q_states"]
                return [dict(zip(cols, row)) for row in c.fetchall()]
        except Exception:
            return []

    def get_type_stats(self, window_sec: int = 300) -> dict:
        """Signal count per modulation type in the last window_sec seconds."""
        try:
            cutoff = time.time() - window_sec
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT type, COUNT(*) FROM signals "
                    "WHERE timestamp > ? GROUP BY type", (cutoff,)
                )
                return dict(c.fetchall())
        except Exception:
            return {}
