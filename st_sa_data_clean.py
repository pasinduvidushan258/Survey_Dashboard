import pandas as pd
from duplicate_data import remove_survey_duplicates
from empty_row_remove import remove_low_completion_rows
from combine_repeated_columns import combine_repeated_columns

def clean_student_satisfaction_data(df):
    """
    Perform a complete data cleaning pipeline for student satisfaction survey data.

    This function applies the following steps:
    - Removes unnecessary metadata columns
    - Merges repeated columns with suffixes (e.g., .1, .2)
    - Removes rows with low completion percentage
    - Removes duplicate records
    - Combines all removed rows into a single dataset
    - Returns metadata describing the cleaning process

    Parameters:
    ----------
    df : pandas.DataFrame
        The raw input DataFrame containing student satisfaction survey data.

    Returns:
    -------
    cleaned_df : pandas.DataFrame
        The cleaned dataset after applying all transformations.

    final_removed_df : pandas.DataFrame
        DataFrame containing all removed rows (low completion + duplicates),
        including a 'reason' column.

    success : bool
        Indicates whether the cleaning process was successful.

    message : str
        Description of the performed cleaning process or error message.

    metadata : dict
        Dictionary containing summary details:
        - Number of rows removed due to low completion
        - Number of duplicate rows removed
        - List of removed columns
        - List of combined columns
    """

    try:
        # Create a copy to avoid modifying the original DataFrame
        df = df.copy()

        # Add a row identifier for traceability
        df['row_id'] = df.index + 2

        # Identify and remove unnecessary metadata columns
        removed_cols = []
        for col in ['Survey Identifier', 'Survey Timestamp']:
            if col in df.columns:
                removed_cols.append(col)

        df = df.drop(columns=[c for c in removed_cols if c in df.columns], errors='ignore')

        # Merge repeated columns (e.g., duplicate columns with suffixes)
        df, combined_cols = combine_repeated_columns(df)

        # Define columns to ignore during validation steps
        ignore_cols = [
            'row_id',
            'Record ID',
            'Survey Identifier',
            'Survey Timestamp'
        ]

        # Step 1: Remove rows with less than 15% completion
        cleaned_df, removed_empty = remove_low_completion_rows(
            df,
            ignore_columns=ignore_cols,
            required_pct=15
        )
        
        # Step 2: Remove duplicate rows
        cleaned_df, removed_dupes = remove_survey_duplicates(
            cleaned_df,
            ignore_columns=ignore_cols
        )

        # Step 3: Combine all removed rows into a single DataFrame
        if not removed_empty.empty and not removed_dupes.empty:
            final_removed_df = pd.concat([removed_empty, removed_dupes], ignore_index=True)
        elif not removed_empty.empty:
            final_removed_df = removed_empty
        else:
            final_removed_df = removed_dupes

        # Collect metadata about the cleaning process
        metadata = {
            'removed_empty_count': len(removed_empty),
            'removed_duplicates_count': len(removed_dupes),
            'removed_columns': removed_cols,
            'combined_columns': combined_cols
        }

        # Return cleaned data, removed data, and process details
        return (
            cleaned_df,
            final_removed_df,
            True,
            "Student Satisfaction (20% Completion checked & Duplicates removed)",
            metadata
        )

    except Exception as e:
        # Handle unexpected errors gracefully
        return None, None, False, str(e), {}