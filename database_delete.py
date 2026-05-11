from nicegui import ui
import sqlite3

def delete_table(table_name: str):
    """
    Prompts the user for confirmation and deletes the specified database table.
    After deletion, the page is refreshed and a notification is shown.

    Args:
        table_name (str): Name of the SQLite table to delete.
    """
    # Prepare a user-friendly display name
    display_name = table_name.replace('_', ' ').title()
    
    # Confirmation dialog
    with ui.dialog() as confirm_dialog, ui.card().classes('p-6 rounded-xl'):
        ui.label('Confirm Deletion').classes('text-xl font-bold text-red-600 mb-2')
        ui.label(f'Are you sure you want to delete "{display_name}"?').classes('mb-1 text-base')
        ui.label('This action cannot be undone!').classes('text-sm text-gray-500 mb-6')
        
        with ui.row().classes('w-full justify-end gap-3'):
            # Cancel button
            ui.button('Cancel', on_click=confirm_dialog.close).props('flat color=gray')
            
            # Execute deletion
            def execute_delete():
                try:
                    conn = sqlite3.connect('survey.db')
                    cursor = conn.cursor()
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    conn.commit()
                    conn.close()
                    
                    ui.notify(f'{display_name} deleted successfully! 🗑️', color='positive')
                    confirm_dialog.close()
                    
                    # Refresh the Database Management page
                    ui.navigate.to('/database_management') 
                except Exception as e:
                    ui.notify(f"Database Error: {e}", color='negative')
                    print(f"delete_table error: {e}")

            ui.button('Yes, Delete', on_click=execute_delete, color='red').classes('px-4')
            
    # Open confirmation dialog
    confirm_dialog.open()