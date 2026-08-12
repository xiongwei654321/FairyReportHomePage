import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "applications.db"


def init_db() -> None:
    """建表（首次运行时执行，之后幂等）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            phone       TEXT    NOT NULL,
            company     TEXT    DEFAULT '',
            report_type TEXT    DEFAULT '',
            source      TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_application(
    name: str,
    phone: str,
    company: str = "",
    report_type: str = "",
    source: str = "",
) -> None:
    """写入一条申请记录"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO applications
           (name, phone, company, report_type, source, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, phone, company, report_type, source,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
