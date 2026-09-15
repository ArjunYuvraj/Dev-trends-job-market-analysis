

import os
import sys
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")

# Define your Skill List.

CORE_SKILLS = ["python", "C++", "java"]

WEB_SKILLS = ["react", "nodejs"]

AI_ML_SKILLS = ["pytorch", "tensorflow"]

DATA_SKILLS = ["pandas", "spark"]

DATABASE_SKILLS = ["postgresql", "mongodb"]

CLOUD_DEVOPS_SKILLS = ["aws", "docker"]

MOBILE_SKILLS = ["flutter"]

ALL_SKILLS = (
    CORE_SKILLS   + AI_ML_SKILLS
    + DATA_SKILLS + DATABASE_SKILLS  + MOBILE_SKILLS
)


# Github Skill Trends Extraction

import requests

def get_github_metrics(skill):
    if skill in CORE_SKILLS:
        query = f"language:{skill}"
    else:
        query = f"topic:{skill}"

    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 5}
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    return {
        "skill": skill,
        "total_count": data.get("total_count", 0),
        "top_repos": [
            {"name": r["full_name"], "stars": r["stargazers_count"]}
            for r in data.get("items", [])
        ],
    }
    
# Adzuna Job Demand Extraction

def get_adzuna_metrics(skill):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 1,
        "what": skill,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return {"skill": skill, "job_count": data.get("count", 0)}


# Store the Extracted Information from Github and Adzuna

import time


class ProgressBar:
    def __init__(self, total):
        self.total = total
        self.completed = 0

    def render(self, status=""):
        width = 30
        filled = int(width * self.completed / self.total) if self.total else width
        bar = "#" * filled + "-" * (width - filled)
        message = f"[{bar}] {self.completed}/{self.total} {status}"
        sys.stdout.write(f"\r\033[2K{message}")
        sys.stdout.flush()

    def update(self, status=""):
        self.completed += 1
        self.render(status)

    def finish(self):
        self.render("Complete")
        sys.stdout.write("\n")
        sys.stdout.flush()


def call_with_retry(func, skill, max_retries=3, status_callback=None):
    for attempt in range(max_retries):
        try:
            return func(skill)
        except requests.exceptions.HTTPError as e:
            if status_callback:
                status_callback(f"{skill}: retry {attempt + 1}/{max_retries}")
            else:
                print(f"  Attempt {attempt + 1} failed for {skill}: {e}")
            time.sleep(3)  # wait longer before retrying
    if status_callback:
        status_callback(f"{skill}: failed")
    else:
        print(f"  Giving up on {skill} after {max_retries} attempts")
    return None

import json, time
from datetime import date

DATA_FILE = os.path.join("data", "pipeline.json")


def save_results(github_results, adzuna_results, pulled_date):
    """Upsert this pull into one JSON file, keyed by source, date, and skill."""
    store = {"github": [], "adzuna": []}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f)
        store["github"] = existing.get("github", [])
        store["adzuna"] = existing.get("adzuna", [])

    for source, results in (("github", github_results), ("adzuna", adzuna_results)):
        current = {
            (record["date_pulled"], record["skill"]): record
            for record in store[source]
        }
        for record in results:
            record["date_pulled"] = pulled_date
            current[(pulled_date, record["skill"])] = record
        store[source] = sorted(
            current.values(), key=lambda record: (record["date_pulled"], record["skill"])
        )

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)

def main():
    os.makedirs("data", exist_ok=True)
    github_results, adzuna_results = [], []
    progress = ProgressBar(total=len(ALL_SKILLS) * 2)
    progress.render("Starting extraction")

    for skill in ALL_SKILLS:
        gh = call_with_retry(
            get_github_metrics,
            skill,
            status_callback=lambda status: progress.render(status),
        )
        if gh:
            github_results.append(gh)
        progress.update(f"GitHub: {skill}")
        time.sleep(1)

        az = call_with_retry(
            get_adzuna_metrics,
            skill,
            status_callback=lambda status: progress.render(status),
        )
        if az:
            adzuna_results.append(az)
        progress.update(f"Adzuna: {skill}")
        time.sleep(1)

    progress.finish()

    today = date.today().isoformat()
    save_results(github_results, adzuna_results, today)

    print(f"\nSaved {DATA_FILE} ({len(github_results)} GitHub skills, "
          f"{len(adzuna_results)} Adzuna skills for {today})")
    return DATA_FILE


if __name__ == "__main__":
    main()
    print("\nThe program ran successfully")



