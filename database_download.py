from nicegui import ui
import sqlite3
import pandas as pd

def download_table_csv(table_name: str):
    """
    Downloads the specified database table as a CSV file.
    Opens a NiceGUI download dialog and notifies the user.

    Args:
        table_name (str): Name of the SQLite table to download.
    """
    try:
        # 1️. Fetch table data from SQLite database
        conn = sqlite3.connect('survey.db')
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        # 2️. Prepare a user-friendly display name for notifications
        display_name = table_name.replace('_', ' ').title()
        
        # 3️. Convert DataFrame to CSV and encode as UTF-8
        csv_data = df.to_csv(index=False).encode('utf-8')
        
        # 4️. Trigger file download via NiceGUI
        ui.download(csv_data, f"{table_name}.csv")
        
        # 5️. Notify user of successful download
        ui.notify(f'{display_name} downloaded successfully! 📥', color='positive')
        
    except Exception as e:
        # Notify user and log error if something goes wrong
        ui.notify(f"Error downloading data: {e}", color='negative')
        print(f"download_table_csv error: {e}")