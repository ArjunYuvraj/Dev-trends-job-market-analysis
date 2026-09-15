import json
import os

SKILL_CATEGORIES = {

    # Programming Languages
    "python": "Languages",
    "javascript": "Languages",
    "typescript": "Languages",
    "go": "Languages",
    "rust": "Languages",

    # Frontend
    "react": "Frontend",
    "vue": "Frontend",
    "tailwindcss": "Frontend",

    # Backend / API
    "nodejs": "Backend",
    "django": "Backend",
    "fastapi": "Backend",

    # AI / Machine Learning
    "tensorflow": "AI/ML",
    "pytorch": "AI/ML",

    # Data Engineering
    "airflow": "Data",
    "dbt": "Data",
    "kafka": "Data",
    "spark": "Data",
    "pandas": "Data",

    # Databases / Data Platforms
    "postgresql": "Database",
    "mongodb": "Database",
    "redis": "Database",
    "snowflake": "Database",

    # Cloud
    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",

    # DevOps / Infrastructure
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "terraform": "DevOps",

    # Mobile
    "react-native": "Mobile",
    "flutter": "Mobile",
}

DATA_FILE = os.path.join("data", "pipeline.json")


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_github(raw_list, date_pulled):
    """Turn raw GitHub skill dicts into clean flat rows for the github_metrics table."""
    rows = []
    for entry in raw_list:
        top_repos = entry.get("top_repos", [])
        stars = [r["stars"] for r in top_repos if "stars" in r]
        skill = entry["skill"]
        record_date = entry.get("date_pulled", date_pulled)
        if not record_date:
            raise ValueError(f"Missing date_pulled for GitHub skill: {skill}")
        rows.append({
            "skill": skill,
            "category": SKILL_CATEGORIES.get(skill, "Other"),
            "date_pulled": record_date,
            "total_count": entry.get("total_count", 0),
            "top_repos_avg_stars": round(sum(stars) / len(stars), 1) if stars else 0,
            "top_repos_max_stars": max(stars) if stars else 0,
        })
    return rows


def flatten_adzuna(raw_list, date_pulled):
    """Turn raw Adzuna skill dicts into clean flat rows for the job_postings table."""
    rows = []
    for entry in raw_list:
        skill = entry["skill"]
        record_date = entry.get("date_pulled", date_pulled)
        if not record_date:
            raise ValueError(f"Missing date_pulled for Adzuna skill: {skill}")
        rows.append({
            "skill": skill,
            "category": SKILL_CATEGORIES.get(skill, "Other"),
            "date_pulled": record_date,
            "job_count": entry.get("job_count", 0),
        })
    return rows


def get_transformed_data():
    """Main entry point other scripts (like load.py) should call.
    Returns (github_rows, job_rows) as lists of clean dicts."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"No consolidated extract found at {DATA_FILE}")

    store = load_json(DATA_FILE)
    github_raw = store.get("github", [])
    adzuna_raw = store.get("adzuna", [])

    github_rows = flatten_github(github_raw, None)
    job_rows = flatten_adzuna(adzuna_raw, None)

    return github_rows, job_rows


if __name__ == "__main__":
    github_rows, job_rows = get_transformed_data()
    print(f"Transformed {len(github_rows)} github rows, {len(job_rows)} job rows.\n")
    print("Sample github row:", github_rows[0] if github_rows else "none")
    print("Sample job row:", job_rows[0] if job_rows else "none")