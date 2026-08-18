
# Load the API Keys from the .env file

import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY")

# Define your Skill List.

LANGUAGE_SKILLS = ["python", "javascript", "typescript", "go", "rust"]
FRONTEND_SKILLS = ["react", "vue", "tailwindcss"]
BACKEND_SKILLS = ["django", "fastapi", "nodejs"]
AI_ML_SKILLS = ["tensorflow", "pytorch", "pandas"]
DATA_SKILLS = ["spark", "airflow", "dbt", "kafka", "snowflake"]
DATABASE_SKILLS = ["postgresql", "mongodb", "redis"]
CLOUD_SKILLS = ["aws", "azure", "gcp"]
DEVOPS_SKILLS = ["docker", "kubernetes", "terraform"]
MOBILE_SKILLS = ["flutter", "react-native"]

ALL_SKILLS = (
    LANGUAGE_SKILLS + FRONTEND_SKILLS + BACKEND_SKILLS + AI_ML_SKILLS
    + DATA_SKILLS + DATABASE_SKILLS + CLOUD_SKILLS + DEVOPS_SKILLS + MOBILE_SKILLS
)


# Github Skill Trends Extraction

import requests

def get_github_metrics(skill):
    if skill in LANGUAGE_SKILLS:
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

def call_with_retry(func, skill, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func(skill)
        except requests.exceptions.HTTPError as e:
            print(f"  Attempt {attempt + 1} failed for {skill}: {e}")
            time.sleep(3)  # wait longer before retrying
    print(f"  Giving up on {skill} after {max_retries} attempts")
    return None

import json, time
from datetime import date

def main():
    os.makedirs("data", exist_ok=True)
    github_results, adzuna_results = [], []

    for skill in ALL_SKILLS:
        print(f"Processing: {skill}")

        gh = call_with_retry(get_github_metrics, skill)
        if gh:
            github_results.append(gh)
            print(f"  GitHub OK: {gh['total_count']} repos found")
        time.sleep(1)

        az = call_with_retry(get_adzuna_metrics, skill)
        if az:
            adzuna_results.append(az)
            print(f"  Adzuna OK: {az['job_count']} jobs found")
        time.sleep(1)

    today = date.today().isoformat()
    with open(f"data/raw_github_{today}.json", "w") as f:
        json.dump(github_results, f, indent=2)
    with open(f"data/raw_adzuna_{today}.json", "w") as f:
        json.dump(adzuna_results, f, indent=2)

    print(f"\nSaved data/raw_github_{today}.json ({len(github_results)} skills)")
    print(f"Saved data/raw_adzuna_{today}.json ({len(adzuna_results)} skills)")


if __name__ == "__main__":
    main()
    print("\nThe program ran successfully")



