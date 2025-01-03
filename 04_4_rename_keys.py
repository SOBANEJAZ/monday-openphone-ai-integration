import json
import os
from pathlib import Path

def transform_json_file(input_path, output_path):
    key_mapping = {
        'file_name': 'Board',
        'group_title': 'Group Title',
        'item_name': 'Item',
        'unit_value': 'Units',
        'update_text_body': 'Original Note'
    }
   
    def format_staff_name(name):
        """Remove dashes, underscores, and 'modified' from staff names"""
        return name.replace('-', ' ').replace('_modified', '').strip()
   
    # Check if input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
   
    # Read input JSON file
    with open(input_path, 'r') as f:
        data = json.load(f)
   
    transformed_data = []
   
    for item in data:
        # Create new dictionary with transformed keys and values
        new_item = {}
       
        # Define the desired order of keys
        desired_order = [ 'Board', 'Group Title', 'Item', 'Units', 'Original Note', 'AI Note']
       
        # Create temporary dictionary with renamed keys
        temp_item = {
            key_mapping.get(k, k): v for k, v in item.items()
        }
       
        # Format staff name
        if 'Staff' in temp_item:
            temp_item['Staff'] = format_staff_name(temp_item['Staff'])
       
        # Add empty AI Note field
        temp_item['AI Note'] = ""
       
        # Add items in desired order
        for key in desired_order:
            if key in temp_item:
                new_item[key] = temp_item[key]
       
        transformed_data.append(new_item)
   
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
   
    # Write transformed data to output file
    with open(output_path, 'w') as f:
        json.dump(transformed_data, f, indent=2)
   
    print(f"Transformation complete. Output saved to: {output_path}")

def process_directory(input_dir, output_dir):
    """
    Process all JSON files in the input directory and save transformed files to output directory.
    
    Args:
        input_dir (str): Path to directory containing input JSON files
        output_dir (str): Path to directory where transformed files will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all JSON files in the input directory
    input_path = Path(input_dir)
    json_files = list(input_path.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process each JSON file
    for input_file in json_files:
        try:
            # Create output file path with same name in output directory
            output_file = Path(output_dir) / f"transformed_{input_file.name}"
            
            print(f"\nProcessing: {input_file.name}")
            transform_json_file(str(input_file), str(output_file))
            
        except Exception as e:
            print(f"Error processing {input_file.name}: {str(e)}")

if __name__ == "__main__":
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Define input and output directories
    input_directory = os.path.join(current_dir, "not-in-use", "cleaned")
    output_directory = os.path.join(current_dir, "data", "transformed")
    
    try:
        process_directory(input_directory, output_directory)
    except Exception as e:
        print(f"Error: {str(e)}")