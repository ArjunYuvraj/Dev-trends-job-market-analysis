# Github Dev Ecosystem × Job Demand Signal

A Python data pipeline and Power BI dashboard that compares **GitHub developer activity with job-market demand** across 10 technologies and 5 categories.

### 🎯 Core Question

> **Do technologies with higher developer activity also have higher job demand?**

The project combines GitHub ecosystem data with job posting data to identify demand patterns and skills where hiring demand is high relative to their developer footprint.

## 🔄 Pipeline

```text
                                GitHub API + Adzuna API
                                          ↓
                                     Python Pipeline
                                          ↓
                                   Transform & Clean
                                          ↓
                                       SQLite
                                          ↓
                                      Power BI
```

### ETL Pipeline

**Extract**

* Pulls GitHub repository activity and Adzuna job-market data for 30 technologies.
* Captures repository counts, top repositories, stars, and job posting metrics.
* Includes retry handling for transient API failures.
* Stores raw API responses as dated JSON snapshots.

**Transform**

* Normalizes both sources using a common `skill` + `date_pulled` structure.
* Flattens GitHub's nested `top_repos` data into average and maximum star metrics.
* Maps each technology to one of 9 categories.
* Produces clean, analysis-ready records directly through Python without a CSV intermediate layer.

**Load**

* Loads transformed data into SQLite tables: `github_metrics` and `job_postings`.
* Uses `(skill, date_pulled)` as a composite primary key.
* Uses `INSERT OR REPLACE` for idempotent reruns and duplicate prevention.
* Preserves new dates as historical snapshots for future trend analysis.

**Orchestration**

* `run_pipeline.py` coordinates the complete Extract → Transform → Load workflow.
* Enables consistent weekly reruns as new snapshots are collected.

### 4. Dashboard

Power BI visualizes:

* Total job postings
* GitHub ecosystem size
* Demand by category
* Skill demand rankings
* Historical trends
* **Job Density Ratio**



## 🛠️ Tech Stack

**Python · Requests · Pandas · SQLite · Power BI · Power Query · DAX · GitHub API · Adzuna API**

## 🚀 Future Scope

The pipeline is designed for weekly execution. As historical snapshots accumulate, it can be used to analyze whether **GitHub activity leads, follows, or moves independently of job-market demand**.
