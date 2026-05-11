import pandas as pd

def remove_survey_duplicates(df, ignore_columns=None):
    """
    Remove duplicate rows from a DataFrame based on selected columns.

    This function identifies duplicate rows by comparing all columns
    except those specified in the ignore_columns list. The first occurrence
    of each unique row is retained, while subsequent duplicates are removed.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing survey data.

    ignore_columns : list, optional
        A list of column names to exclude from duplicate checking.
        These columns will not be considered when identifying duplicates.

    Returns:
    -------
    cleaned_df : pandas.DataFrame
        DataFrame with duplicate rows removed.

    removed_df : pandas.DataFrame
        DataFrame containing the removed duplicate rows, with an additional
        'reason' column indicating why the rows were removed.
    """

    # Initialize ignore_columns as an empty list if not provided
    if ignore_columns is None:
        ignore_columns = []

    # Select columns to be used for duplicate detection (excluding ignored columns)
    check_columns = [col for col in df.columns if col not in ignore_columns]
    
    # Identify duplicate rows based on the selected columns
    # keep='first' ensures the first occurrence is kept and others are marked as duplicates
    dup_mask = df.duplicated(subset=check_columns, keep='first')
    
    # Extract rows identified as duplicates
    removed_df = df[dup_mask].copy()

    # Add a reason column if duplicates exist
    if not removed_df.empty:
        removed_df['reason'] = 'Duplicate row'
    else:
        # Create an empty DataFrame with the same structure plus 'reason' column
        removed_df = pd.DataFrame(columns=list(df.columns) + ['reason'])
        
    # Keep only non-duplicate rows
    cleaned_df = df[~dup_mask].copy()
    
    # Return cleaned data and removed duplicate records
    return cleaned_df, removed_df