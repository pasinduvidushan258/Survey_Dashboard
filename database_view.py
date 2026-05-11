from nicegui import ui
import sqlite3
import pandas as pd

def view_table_data(table_name: str):
    """
    Opens a dialog to preview the contents of a given database table.
    Displays the data in a scrollable NiceGUI table with pagination.

    Args:
        table_name (str): Name of the SQLite table to view.
    """
    try:
        # 1️⃣ Fetch table data from SQLite database
        conn = sqlite3.connect('survey.db')
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()

        # 2️⃣ Prepare a user-friendly display name (e.g., student_satisfaction_2023 -> Student Satisfaction 2023)
        display_name = table_name.replace('_', ' ').title()

        # 3️⃣ Configure columns and rows for NiceGUI table
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
            } for col in col_list
        ]
        rows = df.to_dict('records')

        # 4️⃣ Create a scrollable dialog to display table data
        with ui.dialog() as dialog, ui.card().classes('w-11/12 max-w-none h-[85vh] flex flex-col p-6 bg-white'):
            
            # Top row: title and close button
            with ui.row().classes('w-full justify-between items-center mb-4 border-b pb-2'):
                ui.label(f'Data Preview : {display_name} ({len(rows)} Rows)').classes('text-2xl font-bold text-[#0b1132]')
                ui.button('CLOSE', on_click=dialog.close).classes(
                    'bg-[#5B89C8] hover:bg-blue-600 text-white font-bold py-1 px-6 rounded shadow'
                )

            # Scrollable area containing the table
            with ui.scroll_area().classes('w-full flex-grow'):
                if not df.empty:
                    ui.table(
                        columns=columns,
                        rows=rows,
                        pagination={'rowsPerPage': 100}  # Show 50 rows per page
                    ).classes('w-full border shadow-sm rounded-lg').props('dense bordered separator="cell"')
                else:
                    ui.label('This table is empty.').classes('text-gray-500 m-auto text-lg pt-10')

        # Open the dialog
        dialog.open()

    except Exception as e:
        # Notify the user if something goes wrong
        ui.notify(f"Error loading data: {e}", color='negative')
        print(f"view_table_data error: {e}")