"""
run_pipeline.py
Orchestrates the full Extract -> Transform -> Load pipeline.
Run from the project root: python run_pipeline.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from Extract.extract import main as run_extract
from Transform.transform import get_transformed_data
from Load.load import load_data


def main():
    print("=" * 50)
    print("STEP 1/3: EXTRACT")
    print("=" * 50)
    run_extract()
    print("Extract complete.\n")

    print("=" * 50)
    print("STEP 2/3: TRANSFORM")
    print("=" * 50)
    github_rows, job_rows = get_transformed_data()
    print(f"Transformed {len(github_rows)} github rows, {len(job_rows)} job rows.\n")

    print("=" * 50)
    print("STEP 3/3: LOAD")
    print("=" * 50)
    load_data(github_rows, job_rows)
    print("Load complete.\n")

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()