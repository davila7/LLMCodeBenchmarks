import os
import json
import pandas as pd

def list_json_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.json')]

def load_json_file(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def display_as_table(data):
    rows = []
    for entry in data:
        model = entry.get('model', '')
        for task in entry.get('task', []):
            rows.append({
                'Model': model,
                # 'Description': task.get('description', ''),
                # 'Generated Code': task.get('generated_code', ''),
                'Success': task.get('success', ''),
                'Message': task.get('message', ''),
                'Execution Time': task.get('execution_time', ''),
                'Response Time': task.get('response_time', '')
            })
    df = pd.DataFrame(rows)
    print(df)

def main():
    directory = 'results'
    json_files = list_json_files(directory)
    
    if not json_files:
        print("No JSON files found in the directory.")
        return
    
    print("Available JSON files:")
    for idx, file in enumerate(json_files):
        print(f"{idx + 1}: {file}")
    
    file_index = int(input("Enter the number of the file you want to display: ")) - 1
    
    if 0 <= file_index < len(json_files):
        filepath = os.path.join(directory, json_files[file_index])
        data = load_json_file(filepath)
        display_as_table(data)
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()
