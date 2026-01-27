import csv
import json
import os

HISTORY_FILE = "data/history.csv"
JSON_PATH = "docs/history.json"

def export_history_to_json():
    """Convert history.csv to history.json for the frontend"""
    history_data = []
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Clean up data types
                    try:
                        row['level'] = int(row.get('level', 0))
                    except:
                        row['level'] = 0
                        
                    try:
                        row['p3d'] = float(row.get('p3d', 0.0))
                    except:
                        row['p3d'] = 0.0
                        
                    try:
                        row['p30d'] = float(row.get('p30d', 0.0))
                    except:
                        row['p30d'] = 0.0
                        
                    # Boolean handling
                    # 'is_dry' might be 'True', 'False' string
                    row['is_dry'] = str(row.get('is_dry', '')).lower() == 'true'
                    
                    history_data.append(row)
        except Exception as e:
            print(f"Error reading history for json export: {e}")
            
    # Remove duplicates? Or keep all entries (including multiple times per day)?
    # For graph, maybe we want the latest entry per day? Or all?
    # Let's keep all for now, frontend can filter.
    
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print(f"Exported {len(history_data)} items to {JSON_PATH}")

if __name__ == "__main__":
    export_history_to_json()
