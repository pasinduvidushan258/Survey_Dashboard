import pandas as pd

def combine_repeated_columns(df):
    """
    Identify and merge columns that share the same base name.

    Columns with suffixes such as '.1', '.2', etc. are considered duplicates
    of the same base column. This function consolidates such columns into a
    single column by prioritizing non-null values from left to right.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing potentially duplicated columns.

    Returns:
    -------
    new_df : pandas.DataFrame
        A new DataFrame with duplicated columns merged.

    combined_cols : list
        A list of base column names that were merged.
    """

    # Get all column names from the DataFrame
    cols = df.columns

    # List to store names of columns that were combined
    combined_cols = []

    # Create a copy of the original DataFrame to avoid modifying it directly
    new_df = df.copy()

    # Extract base column names by removing suffixes like '.1', '.2'
    base_columns = []
    for col in cols:
        base_name = col.split('.')[0].strip()
        if base_name not in base_columns:
            base_columns.append(base_name)

    # Iterate through each base column name
    for base in base_columns:

        # Find all columns that match the current base name
        related_cols = [c for c in cols if c.split('.')[0].strip() == base]

        # Proceed only if there are multiple columns with the same base name
        if len(related_cols) > 1:

            # Combine columns by taking the first non-null value across the row
            # 'bfill' fills missing values from left to right
            combined_series = df[related_cols].bfill(axis=1).iloc[:, 0]

            # Assign the combined result to the base column
            new_df[base] = combined_series

            # Identify duplicate columns to be removed (excluding the base column)
            cols_to_drop = [c for c in related_cols if c != base]

            # Drop the redundant columns from the DataFrame
            new_df = new_df.drop(columns=cols_to_drop)

            # Record the base column as processed
            combined_cols.append(base)

    # Return the cleaned DataFrame and list of merged columns
    return new_df, combined_cols