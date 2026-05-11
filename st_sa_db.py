import sqlite3
import pandas as pd
from typing import List

def get_available_years() -> List[str]:
    """
    Retrieve a descending list of available survey years from the database.
    
    Scans the SQLite database for tables matching the 'student_satisfaction_*' 
    pattern and extracts the year suffix from the table names.
    
    Returns:
        List[str]: A list of years sorted in descending order. Returns an empty list if an error occurs.
    """
    try:
        # Using a context manager (with statement) ensures the database connection closes automatically
        with sqlite3.connect('survey.db') as conn:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'student_satisfaction_%';"
            tables = pd.read_sql_query(query, conn)['name'].tolist()
        
        # Extract the year string from the table names (e.g., 'student_satisfaction_2023' -> '2023')
        years = [t.split('_')[-1] for t in tables]
        
        # Sort years in descending order (most recent first)
        return sorted(years, reverse=True)
        
    except Exception as e:
        print(f"Error fetching years: {e}")
        return []

def load_data(selection: str) -> pd.DataFrame:
    """
    Load survey data into a Pandas DataFrame based on the selected year.
    
    Args:
        selection (str): The specific year to load (e.g., '2023'), or 'All' to load and concatenate all years.
        
    Returns:
        pd.DataFrame: A DataFrame containing the requested survey data. Returns an empty DataFrame if an error occurs.
    """
    try:
        with sqlite3.connect('survey.db') as conn:
            
            if selection == 'All':
                # If 'All' is selected, fetch all relevant table names from the database
                query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'student_satisfaction_%';"
                tables = pd.read_sql_query(query, conn)['name'].tolist()
                
                df_list = []
                for table in tables:
                    # Read each table into a DataFrame and append it to our list
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    df_list.append(df)
                
                # Concatenate all DataFrames into a single one, if data exists
                if df_list:
                    return pd.concat(df_list, ignore_index=True)
                else:
                    return pd.DataFrame()
                    
            else:
                # If a specific year is selected, query only the corresponding table
                df = pd.read_sql_query(f"SELECT * FROM student_satisfaction_{selection}", conn)
                return df
                
    except Exception as e:
        print(f"Error loading data for {selection}: {e}")
        return pd.DataFrame()