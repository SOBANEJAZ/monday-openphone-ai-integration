import subprocess
import os

scripts = [
    "01_reference_collecter.py",
    "02_notes_retriever.py",
    "03_notes_cleaner.py",
    "04_call_logs_retriever.py",
    "05_call_ids_retriever.py",
    "06_call_logs_ids_combiner.py",
    "07_call_transcript_retriever.py",
    "08_call_transcript_cleaner.py",
    "09_calls_notes_combiner.py",
    "10_ai_analyzer.py",
    "11_CST_to_UTC.py",
    "12_groups_columns_fetcher.py",
    "13_push_to_monday.py",
]

script_dir = os.getcwd()  # Current working directory

for script in scripts:
    script_path = os.path.join(script_dir, script)

    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        continue
    try:
        print(f"Running {script}...")
        result = subprocess.run(["python", script_path], check=True)
        print(f"Completed {script}.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}\n")
