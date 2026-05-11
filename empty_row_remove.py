import pandas as pd

def remove_low_completion_rows(df, ignore_columns=None, required_pct=50
                               
                               ):
    """
    Remove rows with low data completion based on a specified threshold.

    This function evaluates the percentage of non-missing (filled) values
    in each row, excluding specified columns. Rows with a completion
    percentage lower than the required threshold are removed.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing survey or tabular data.

    ignore_columns : list, optional
        A list of column names to exclude from the completion check.

    required_pct : float, optional (default=50)
        The minimum percentage of filled values required for a row
        to be retained.

    Returns:
    -------
    cleaned_df : pandas.DataFrame
        DataFrame containing rows that meet the completion threshold.

    removed_df : pandas.DataFrame
        DataFrame containing rows that were removed due to low completion,
        with an additional 'reason' column explaining the removal.
    """

    # Initialize ignore_columns as an empty list if not provided
    if ignore_columns is None:
        ignore_columns = []

    # Step 1: Select columns to evaluate (excluding ignored columns)
    check_columns = [col for col in df.columns if col not in ignore_columns]
    
    # Step 2: Calculate the fraction of filled values per row
    # Treat whitespace, 'nan', 'None', and empty strings as missing values
    filled_fraction = df[check_columns].apply(
        lambda x: x.astype(str)
                  .str.strip()
                  .replace(['nan', 'None', ''], pd.NA)
    ).notnull().mean(axis=1)
    
    # Step 3: Create a mask for rows meeting the required completion percentage
    mask = (filled_fraction * 100) >= required_pct
    
    # Step 4: Retain rows that satisfy the completion threshold
    cleaned_df = df[mask].copy() 
    
    # Step 5: Extract rows that do not meet the threshold
    removed_df = df[~mask].copy()
    
    if not removed_df.empty:
        # Add a reason column indicating why rows were removed
        removed_df['reason'] = f'Filled < {required_pct}%'
    else:
        # Create an empty DataFrame with the same structure plus 'reason'
        removed_df = pd.DataFrame(columns=list(df.columns) + ['reason'])
        
    # Return cleaned and removed datasets
    return cleaned_df, removed_df