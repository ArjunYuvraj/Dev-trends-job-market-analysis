import sqlite3
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Transform.transform import get_transformed_data

DB_PATH = os.path.join("data", "pipeline.db")


def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INTEGER PRIMARY KEY,
            skill_name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_id INTEGER PRIMARY KEY,
            date_pulled TEXT NOT NULL UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS github_metrics (
            skill_id INTEGER NOT NULL,
            snapshot_id INTEGER NOT NULL,
            github_repo_count INTEGER,
            top_repos_avg_stars REAL,
            top_repos_max_stars INTEGER,
            PRIMARY KEY (skill_id, snapshot_id),
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(snapshot_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            skill_id INTEGER NOT NULL,
            snapshot_id INTEGER NOT NULL,
            job_count INTEGER,
            PRIMARY KEY (skill_id, snapshot_id),
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(snapshot_id)
        )
    """)


def insert_dimensions(conn, github_rows, job_rows):
    all_rows = github_rows + job_rows
    conn.executemany("""
        INSERT INTO skills (skill_name, category)
        VALUES (:skill, :category)
        ON CONFLICT(skill_name) DO UPDATE SET category = excluded.category
    """, all_rows)
    conn.executemany("""
        INSERT OR IGNORE INTO snapshots (date_pulled)
        VALUES (:date_pulled)
    """, all_rows)


def get_dimension_ids(conn):
    skill_ids = {
        skill: skill_id
        for skill, skill_id in conn.execute(
            "SELECT skill_name, skill_id FROM skills"
        )
    }
    snapshot_ids = {
        date_pulled: snapshot_id
        for date_pulled, snapshot_id in conn.execute(
            "SELECT date_pulled, snapshot_id FROM snapshots"
        )
    }
    return skill_ids, snapshot_ids


def insert_github(conn, rows, skill_ids, snapshot_ids):
    records = [
        {
            "skill_id": skill_ids[row["skill"]],
            "snapshot_id": snapshot_ids[row["date_pulled"]],
            "github_repo_count": row["total_count"],
            "top_repos_avg_stars": row["top_repos_avg_stars"],
            "top_repos_max_stars": row["top_repos_max_stars"],
        }
        for row in rows
    ]
    conn.executemany("""
        INSERT OR REPLACE INTO github_metrics
        (skill_id, snapshot_id, github_repo_count, top_repos_avg_stars, top_repos_max_stars)
        VALUES (:skill_id, :snapshot_id, :github_repo_count, :top_repos_avg_stars, :top_repos_max_stars)
    """, records)


def insert_jobs(conn, rows, skill_ids, snapshot_ids):
    records = [
        {
            "skill_id": skill_ids[row["skill"]],
            "snapshot_id": snapshot_ids[row["date_pulled"]],
            "job_count": row["job_count"],
        }
        for row in rows
    ]
    conn.executemany("""
        INSERT OR REPLACE INTO job_postings
        (skill_id, snapshot_id, job_count)
        VALUES (:skill_id, :snapshot_id, :job_count)
    """, records)

def load_data(github_rows, job_rows):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    try:
        insert_dimensions(conn, github_rows, job_rows)
        skill_ids, snapshot_ids = get_dimension_ids(conn)
        insert_github(conn, github_rows, skill_ids, snapshot_ids)
        insert_jobs(conn, job_rows, skill_ids, snapshot_ids)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    


def main():
    github_rows, job_rows = get_transformed_data()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    create_tables(conn)
    try:
        insert_dimensions(conn, github_rows, job_rows)
        skill_ids, snapshot_ids = get_dimension_ids(conn)
        insert_github(conn, github_rows, skill_ids, snapshot_ids)
        insert_jobs(conn, job_rows, skill_ids, snapshot_ids)
        conn.commit()

        gh_count = conn.execute("SELECT COUNT(*) FROM github_metrics").fetchone()[0]
        job_count = conn.execute("SELECT COUNT(*) FROM job_postings").fetchone()[0]
        print(f"Loaded. github_metrics: {gh_count} rows total, job_postings: {job_count} rows total.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()