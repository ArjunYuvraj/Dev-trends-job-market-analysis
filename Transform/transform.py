import json
import os
import re
from glob import glob

DATA_DIR = "data"


def get_latest_file(pattern):
    """Find the most recently created file in data/ matching a glob pattern,
    e.g. 'raw_github_*.json'"""
    files = glob(os.path.join(DATA_DIR, pattern))
    if not files:
        raise FileNotFoundError(f"No files found matching {pattern} in {DATA_DIR}/")
    return max(files, key=os.path.getctime)


def extract_date_from_filename(filepath):
    """Pull the YYYY-MM-DD date out of a filename like raw_github_2026-08-18.json"""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(filepath))
    if not match:
        raise ValueError(f"Could not find a date in filename: {filepath}")
    return match.group(1)


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_github(raw_list, date_pulled):
    """Turn raw GitHub skill dicts into clean flat rows for the github_metrics table."""
    rows = []
    for entry in raw_list:
        top_repos = entry.get("top_repos", [])
        stars = [r["stars"] for r in top_repos if "stars" in r]
        rows.append({
            "skill": entry["skill"],
            "date_pulled": date_pulled,
            "total_count": entry.get("total_count", 0),
            "top_repos_avg_stars": round(sum(stars) / len(stars), 1) if stars else 0,
            "top_repos_max_stars": max(stars) if stars else 0,
        })
    return rows


def flatten_adzuna(raw_list, date_pulled):
    """Turn raw Adzuna skill dicts into clean flat rows for the job_postings table."""
    rows = []
    for entry in raw_list:
        rows.append({
            "skill": entry["skill"],
            "date_pulled": date_pulled,
            "job_count": entry.get("job_count", 0),
        })
    return rows


def get_transformed_data():
    """Main entry point other scripts (like load.py) should call.
    Returns (github_rows, job_rows) as lists of clean dicts."""
    github_file = get_latest_file("raw_github_*.json")
    adzuna_file = get_latest_file("raw_adzuna_*.json")

    # Sanity check: both files should be from the same pull
    github_date = extract_date_from_filename(github_file)
    adzuna_date = extract_date_from_filename(adzuna_file)
    if github_date != adzuna_date:
        print(f"WARNING: github file date ({github_date}) and adzuna file date "
              f"({adzuna_date}) don't match. Using github's date for both.")

    github_raw = load_json(github_file)
    adzuna_raw = load_json(adzuna_file)

    github_rows = flatten_github(github_raw, github_date)
    job_rows = flatten_adzuna(adzuna_raw, github_date)

    return github_rows, job_rows


if __name__ == "__main__":
    github_rows, job_rows = get_transformed_data()
    print(f"Transformed {len(github_rows)} github rows, {len(job_rows)} job rows.\n")
    print("Sample github row:", github_rows[0] if github_rows else "none")
    print("Sample job row:", job_rows[0] if job_rows else "none")