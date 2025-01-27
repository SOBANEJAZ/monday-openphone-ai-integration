import subprocess
import os

scripts = [
    "01_reference_collecter.py",
    "03_notes_cleaner7.py",
    "04_call_logs_retriever.py",
    "06_call_logs_ids_combiner7.py",
    "07_call_transcript_retriever.py",
    "08_call_transcript_cleaner.py",
    "09_calls_notes_combiner.py",
    "10_ai_1_transcript_analyzer.py",
    "10_ai_2_start.py",
    "10_ai_3_end.py",
    "10_ai_4_service.py",
    "10_ai_5_bills.py",
    "10_ai_6_columns.py",
    "11_CST_to_UTC.py",
    "12_1_groups_columns_fetcher.py",
    "12_2_units.py",
    "13.py",
    "14_hired_units.py",
    "14_units_monday7.py",
    "remover.py",
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
