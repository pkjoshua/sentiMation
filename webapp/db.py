#!/usr/bin/env python3
"""
SQLite persistence for SentiMation webapp
"""
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

_DB_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), 'data', 'app.db')


def _ensure_parent_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or _DB_PATH_DEFAULT
    _ensure_parent_dir(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    # jobs table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_name TEXT NOT NULL UNIQUE,
          type TEXT NOT NULL,
          prompt TEXT,
          character TEXT,
          environment TEXT,
          video_length INTEGER,
          fps INTEGER,
          width INTEGER,
          height INTEGER,
          schedule_kind TEXT NOT NULL,               -- one_time | recurring
          schedule_dt TEXT,                          -- ISO datetime for one_time
          recurring_days TEXT,                       -- CSV of days for recurring
          recurring_time TEXT,                       -- HH:mm for recurring
          status TEXT NOT NULL,                      -- pending|scheduled|running|completed|failed|cancelled
          host_script_path TEXT,
          host_log_path TEXT,
          last_error TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """
    )
    # Migration: ensure new columns exist if DB was created before they were added
    cur.execute("PRAGMA table_info(jobs)")
    existing_cols = {row[1] for row in cur.fetchall()}  # name is index 1
    migrations = []
    if 'video_length' not in existing_cols:
        migrations.append("ALTER TABLE jobs ADD COLUMN video_length INTEGER")
    if 'fps' not in existing_cols:
        migrations.append("ALTER TABLE jobs ADD COLUMN fps INTEGER")
    if 'width' not in existing_cols:
        migrations.append("ALTER TABLE jobs ADD COLUMN width INTEGER")
    if 'height' not in existing_cols:
        migrations.append("ALTER TABLE jobs ADD COLUMN height INTEGER")
    for sql in migrations:
        try:
            cur.execute(sql)
        except Exception:
            pass
    # job_runs table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS job_runs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          job_id INTEGER NOT NULL,
          started_at TEXT NOT NULL,
          finished_at TEXT,
          status TEXT NOT NULL,                      -- running|completed|failed
          output_path TEXT,
          log_path TEXT,
          host_exit_code INTEGER,
          error_message TEXT,
          FOREIGN KEY(job_id) REFERENCES jobs(id)
        )
        """
    )
    conn.commit()


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def create_job(
    conn: sqlite3.Connection,
    *,
    task_name: str,
    type: str,
    prompt: Optional[str],
    character: Optional[str],
    environment: Optional[str],
    schedule_kind: str,
    schedule_dt: Optional[str],
    recurring_days: Optional[str],
    recurring_time: Optional[str],
    status: str = 'pending',
    video_length: Optional[int] = None,
    fps: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> int:
    cur = conn.cursor()
    ts = _now_iso()
    cur.execute(
        """
        INSERT INTO jobs (
          task_name, type, prompt, character, environment,
          video_length, fps, width, height,
          schedule_kind, schedule_dt, recurring_days, recurring_time,
          status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_name, type, prompt, character, environment,
            video_length, fps, width, height,
            schedule_kind, schedule_dt, recurring_days, recurring_time,
            status, ts, ts,
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def update_job_task_name(conn: sqlite3.Connection, job_id: int, task_name: str) -> None:
    cur = conn.cursor()
    cur.execute(
        "UPDATE jobs SET task_name = ?, updated_at = ? WHERE id = ?",
        (task_name, _now_iso(), job_id),
    )
    conn.commit()


def update_job_status(
    conn: sqlite3.Connection,
    job_id: int,
    *,
    status: Optional[str] = None,
    host_script_path: Optional[str] = None,
    host_log_path: Optional[str] = None,
    last_error: Optional[str] = None,
) -> None:
    fields: List[str] = []
    params: List[Any] = []
    if status is not None:
        fields.append('status = ?')
        params.append(status)
    if host_script_path is not None:
        fields.append('host_script_path = ?')
        params.append(host_script_path)
    if host_log_path is not None:
        fields.append('host_log_path = ?')
        params.append(host_log_path)
    if last_error is not None:
        fields.append('last_error = ?')
        params.append(last_error)
    fields.append('updated_at = ?')
    params.append(_now_iso())
    params.append(job_id)

    if len(fields) == 1:  # only updated_at
        return

    sql = f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()


def get_job_by_id(conn: sqlite3.Connection, job_id: int) -> Optional[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cur.fetchone()
    return row


def get_job_by_task_name(conn: sqlite3.Connection, task_name: str) -> Optional[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE task_name = ?", (task_name,))
    return cur.fetchone()


def list_jobs(conn: sqlite3.Connection, limit: int = 100) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))
    return cur.fetchall()


essential_job_fields = (
    'id','task_name','type','prompt','character','environment',
    'video_length','fps','width','height',
    'schedule_kind','schedule_dt','recurring_days','recurring_time',
    'status','host_script_path','host_log_path','last_error','created_at','updated_at'
)


def create_job_run(
    conn: sqlite3.Connection,
    *,
    job_id: int,
    status: str = 'running',
    log_path: Optional[str] = None,
) -> int:
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO job_runs (job_id, started_at, status, log_path)
        VALUES (?, ?, ?, ?)
        """,
        (job_id, _now_iso(), status, log_path),
    )
    conn.commit()
    return int(cur.lastrowid)


def complete_job_run(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    status: str,
    output_path: Optional[str] = None,
    host_exit_code: Optional[int] = None,
    error_message: Optional[str] = None,
) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE job_runs
        SET finished_at = ?, status = ?, output_path = ?, host_exit_code = ?, error_message = ?
        WHERE id = ?
        """,
        (_now_iso(), status, output_path, host_exit_code, error_message, run_id),
    )
    conn.commit()


def list_runs_for_job(conn: sqlite3.Connection, job_id: int, limit: int = 20) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM job_runs WHERE job_id = ? ORDER BY started_at DESC LIMIT ?",
        (job_id, limit),
    )
    return cur.fetchall()
