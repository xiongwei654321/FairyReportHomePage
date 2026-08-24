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


def get_applications_count() -> int:
    """返回申请总条数"""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return count


def get_applications(offset: int = 0, limit: int = 20) -> list:
    """按 id 倒序分页返回申请记录"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT id, name, phone, company, report_type, source, created_at
           FROM applications
           ORDER BY id DESC
           LIMIT ? OFFSET ?""",
        (limit, offset),
    ).fetchall()
    conn.close()
    return rows


def update_application(id_: int, name: str, phone: str,
                        company: str, report_type: str) -> None:
    """更新一条申请记录的可编辑字段"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """UPDATE applications
           SET name=?, phone=?, company=?, report_type=?
           WHERE id=?""",
        (name, phone, company, report_type, id_),
    )
    conn.commit()
    conn.close()


def delete_application(id_: int) -> None:
    """删除一条申请记录"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM applications WHERE id=?", (id_,))
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
