import os
import sqlite3
import pandas as pd

TEMP_DB_PATH = 'temp_survey_data.db'
TEMP_TABLE_NAME = 'staging_data'


def cleanup_orphan_temp_db():
    """Delete any existing orphan temp DB at startup or when manual cleanup is triggered."""
    try:
        if os.path.exists(TEMP_DB_PATH):
            os.remove(TEMP_DB_PATH)
    except Exception as e:
        print(f"Failed to cleanup orphan temp DB: {e}")


def create_staging_db(df: pd.DataFrame):
    """Create / replace temp staging DB with uploaded file contents."""
    try:
        cleanup_orphan_temp_db()
        conn = sqlite3.connect(TEMP_DB_PATH)
        df.to_sql(TEMP_TABLE_NAME, conn, if_exists='replace', index=False)
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating staging DB: {e}")
        return False


def read_staging_preview(rows=50):
    """Read a small preview from temp staging DB."""
    try:
        if not os.path.exists(TEMP_DB_PATH):
            return None
        conn = sqlite3.connect(TEMP_DB_PATH)
        query = f"SELECT * FROM {TEMP_TABLE_NAME} LIMIT ?"
        preview_df = pd.read_sql_query(query, conn, params=(rows,))
        conn.close()
        return preview_df
    except Exception as e:
        print(f"Error reading staging preview: {e}")
        return None


def read_staging_full():
    """Read the full staged dataset from temp DB."""
    try:
        if not os.path.exists(TEMP_DB_PATH):
            return None
        conn = sqlite3.connect(TEMP_DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {TEMP_TABLE_NAME}", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error reading staging full data: {e}")
        return None


def drop_staging_db():
    """Delete temp staging DB file and clear state."""
    try:
        if os.path.exists(TEMP_DB_PATH):
            os.remove(TEMP_DB_PATH)
            return True
    except Exception as e:
        print(f"Error deleting staging DB: {e}")
    return False


def commit_staging_to_production(survey_name: str, year: str):
    """Move staged data from temp DB to survey.db production DB."""
    try:
        df = read_staging_full()
        if df is None:
            return False, 'No staged data found to commit.'

        table_name = f"{survey_name.replace(' ', '_').lower()}_{year}"
        conn = sqlite3.connect('survey.db')
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()

        return True, table_name
    except Exception as e:
        return False, str(e)
