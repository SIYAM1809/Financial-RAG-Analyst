import csv
import os
from datetime import datetime

LOG_FILE = "rag_logs.csv"

def log_interaction(query, response, feedback=None):
    """Saves the Q&A to a CSV file for monitoring."""
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header if new file
        if not file_exists:
            writer.writerow(["Timestamp", "Query", "Response", "Feedback"])
            
        writer.writerow([datetime.now(), query, response, feedback])

def load_logs():
    """Reads logs for the dashboard."""
    if not os.path.exists(LOG_FILE):
        return []
    
    # Read CSV manually or with pandas (we'll use pandas in the dashboard)
    import pandas as pd
    return pd.read_csv(LOG_FILE)
