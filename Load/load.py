import sqlite3
import os
import sys
from pathlib import Path

# Get the project root (one level up from this file's folder), and add it to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Transform.transform import get_transformed_data

DB_PATH = os.path.join("data", "pipeline.db")


def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS github_metrics (
            skill TEXT NOT NULL,
            date_pulled TEXT NOT NULL,
            total_count INTEGER,
            top_repos_avg_stars REAL,
            top_repos_max_stars INTEGER,
            PRIMARY KEY (skill, date_pulled)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            skill TEXT NOT NULL,
            date_pulled TEXT NOT NULL,
            job_count INTEGER,
            PRIMARY KEY (skill, date_pulled)
        )
    """)


def insert_github(conn, rows):
    conn.executemany("""
        INSERT OR REPLACE INTO github_metrics
        (skill, date_pulled, total_count, top_repos_avg_stars, top_repos_max_stars)
        VALUES (:skill, :date_pulled, :total_count, :top_repos_avg_stars, :top_repos_max_stars)
    """, rows)


def insert_jobs(conn, rows):
    conn.executemany("""
        INSERT OR REPLACE INTO job_postings
        (skill, date_pulled, job_count)
        VALUES (:skill, :date_pulled, :job_count)
    """, rows)


def main():
    github_rows, job_rows = get_transformed_data()

    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    insert_github(conn, github_rows)
    insert_jobs(conn, job_rows)
    conn.commit()

    gh_count = conn.execute("SELECT COUNT(*) FROM github_metrics").fetchone()[0]
    job_count = conn.execute("SELECT COUNT(*) FROM job_postings").fetchone()[0]
    print(f"Loaded. github_metrics: {gh_count} rows total, job_postings: {job_count} rows total.")

    conn.close()


if __name__ == "__main__":
    main()