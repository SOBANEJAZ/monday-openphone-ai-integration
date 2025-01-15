import os


def delete_files_in_dirs(paths):
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                # Handle directory
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            print(f"Deleted file: {file_path}")
                        except Exception as e:
                            print(f"Failed to delete {file_path}. Reason: {e}")
            elif os.path.isfile(path):
                # Handle individual file
                try:
                    os.remove(path)
                    print(f"Deleted file: {path}")
                except Exception as e:
                    print(f"Failed to delete {path}. Reason: {e}")
        else:
            print(f"Path not found: {path}")


# List of directories and files to delete
dirs_to_clean = [
    "AI Revised 1",
    "AI Revised 2",
    "AI Revised 3",
    "AI Revised 4",
    "AI Revised 5",
    "AI Revised 6",
    "data/call_logs",
    "data/notes/cleaned_notes",
    "data/notes/filtered_notes",
    "data/reference",
    "final",
    "Output",
    "Output_units",
    "_columns_units.json",
    "_groups_units.json",
    "_columns.json",
    "_groups.json",
]

# Call the function
delete_files_in_dirs(dirs_to_clean)
