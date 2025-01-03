import json
import os

# Specify folder paths
input_folder_path = 'not-in-use/notes'  # Replace with your input folder path
output_folder_path = 'not-in-use/cleaned'  # Replace with your output folder path

# Ensure output folder exists
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Process each JSON file in the input folder
for filename in os.listdir(input_folder_path):
    file_path = os.path.join(input_folder_path, filename)
    if os.path.isfile(file_path) and filename.endswith('.json'):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            file_name = os.path.splitext(filename)[0]
            cleaned_data = []
            
            # Safely access data structures
            boards = data.get('data', {}).get('boards', [])
            for board in boards:
                groups = board.get('groups', [])
                for group in groups:
                    group_title = group.get('title', 'N/A')
                    items_page = group.get('items_page', {})
                    items = items_page.get('items', [])
                    for item in items:
                        item_name = item.get('name', 'N/A')
                        item_id = item.get('id', 'N/A')
                        updates = item.get('updates', [])
                        Units = item.get('column_values', [])
                        for unit in Units:
                            unit_value = unit.get('value', 'N/A')
                        for update in updates:
                            update_text_body = update.get('text_body', 'N/A')
                            cleaned_data.append({
                                'group_title': group_title,
                                'file_name': file_name,
                                'item_name': item_name,
                                'item_id': item_id,
                                'unit_value': unit_value,
                                'update_text_body': update_text_body
                            })
            
            output_file_name = os.path.join(output_folder_path, f'cleaned_{file_name}.json')
            with open(output_file_name, 'w') as f:
                json.dump(cleaned_data, f, indent=4)
        
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON in file {filename}: {e}')
        except KeyError as e:
            print(f'Key error in file {filename}: {e}')
        except Exception as e:
            print(f'An error occurred with file {filename}: {e}')