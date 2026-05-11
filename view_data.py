from nicegui import ui
import pandas as pd

def show_view_window(df):
    """
    Opens a dialog window to display the full DataFrame in a scrollable, paginated table.
    
    Args:
        df (pd.DataFrame): The DataFrame to display
    """

    # Prepare table columns and rows for NiceGUI table
    # Reorder columns: move the last column to the first position
    col_list = list(df.columns)
    if len(col_list) > 1:
        col_list = [col_list[-1]] + col_list[:-1]
    
    columns = [
        {
            'name': str(col),
            'label': str(col),
            'field': str(col),
            'align': 'left',
            'headerStyle': 'border-bottom: 2px solid black !important; font-weight: bold !important;'
        }
        for col in col_list
    ]
    rows = df.to_dict('records')

    # Create a large dialog with a card layout for full data view
    with ui.dialog() as dialog, ui.card().classes('w-11/12 max-w-none h-[85vh] flex flex-col p-6'):
        
        # Header row: Title and Close button
        with ui.row().classes('w-full justify-between items-center mb-4'):
            ui.label(f'Full Data View ({len(rows)} Rows)').classes('text-2xl font-bold text-[#0b1132]')
            ui.button(
                'Close', 
                on_click=dialog.close
            ).classes('bg-red-500 hover:bg-red-600 text-white font-bold py-1 px-6 rounded shadow')

        # Scrollable section for the table
        with ui.scroll_area().classes('w-full flex-grow'):
            ui.table(
                columns=columns, 
                rows=rows,
                pagination={'rowsPerPage': 50}  # 50 rows per page; adjust as needed
            ).classes('w-full border shadow-sm rounded-lg').props('dense bordered separator="cell"')

    # Open the dialog to display the table
    dialog.open()