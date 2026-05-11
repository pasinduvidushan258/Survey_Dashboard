from nicegui import ui
import sqlite3
import sidebar
from settings_dialog import create_settings_dialog

# Import helper functions from separate files
from database_view import view_table_data
from database_download import download_table_csv
from database_delete import delete_table

def get_tables_by_survey(survey_keyword: str):
    """
    Retrieves all table names from the SQLite database that match the survey keyword.

    Args:
        survey_keyword (str): A keyword to filter tables (e.g., 'student_satisfaction')

    Returns:
        List[str]: List of table names containing the keyword
    """
    try:
        conn = sqlite3.connect('survey.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        # Filter tables by keyword (case-insensitive)
        return [table for table in all_tables if survey_keyword in table.lower()]
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

@ui.page('/database_management')
def database_management_page():
    """
    Renders the Database Management page of the dashboard.
    Displays all saved survey tables, allowing the user to view, download, or delete them.
    """
    # Initialize global settings dialog
    settings_dialog = create_settings_dialog()

    # Render the sidebar and highlight active page
    sidebar.create_sidebar(settings_dialog, active_page='/database_management')
    
    with ui.column().classes('p-6 md:p-10 w-full max-w-7xl mx-auto'):
        # Page title
        ui.label('Database Management').classes('text-3xl font-bold text-[#0b1132]')
        ui.label('Manage your saved survey data tables here.').classes('text-gray-500 mb-6')

        def render_compact_table_list(tables):
            """
            Renders a list of table cards with action buttons: View, Download, Delete.

            Args:
                tables (List[str]): List of table names to render
            """
            if not tables:
                ui.label('No data saved yet.').classes('text-gray-400 italic py-4 text-sm text-center w-full')
                return
            
            with ui.column().classes('w-full gap-2 mt-2'):
                for table_name in tables:
                    # Extract year from table name for display
                    year_part = table_name.split('_')[-1] if '_' in table_name else ''
                    display_name = f"Data {year_part}"

                    with ui.row().classes('w-full justify-between items-center p-2 bg-gray-50 border rounded-lg hover:bg-gray-100 no-wrap'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('description', color='#6B7280').classes('text-sm')
                            ui.label(display_name).classes('text-sm font-medium text-[#0b1132]')
                        
                        # Action buttons
                        with ui.row().classes('gap-0'):
                            ui.button(icon='visibility', color='blue', on_click=lambda t=table_name: view_table_data(t)).props('flat dense size=sm').tooltip('View Data')
                            ui.button(icon='download', color='green', on_click=lambda t=table_name: download_table_csv(t)).props('flat dense size=sm').tooltip('Download CSV')
                            ui.button(icon='delete', color='red', on_click=lambda t=table_name: delete_table(t)).props('flat dense size=sm').tooltip('Delete Table')

        # Render table grids by survey type
        with ui.grid().classes('w-full grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 items-start'):
            # Student Satisfaction
            with ui.card().classes('w-full p-4 border shadow-sm rounded-xl bg-white'):
                with ui.row().classes('items-center gap-2 mb-3 border-b pb-2 w-full no-wrap'):
                    ui.icon('bar_chart', color='#3B82F6').classes('text-xl')
                    ui.label('Student Satisfaction').classes('text-lg font-bold text-[#0b1132] truncate')
                render_compact_table_list(get_tables_by_survey('student_satisfaction'))

            # Exit Survey
            with ui.card().classes('w-full p-4 border shadow-sm rounded-xl bg-white'):
                with ui.row().classes('items-center gap-2 mb-3 border-b pb-2 w-full no-wrap'):
                    ui.icon('school', color='#10B981').classes('text-xl')
                    ui.label('Exit Survey').classes('text-lg font-bold text-[#0b1132] truncate')
                render_compact_table_list(get_tables_by_survey('exit_survey'))

            # Graduate Employability
            with ui.card().classes('w-full p-4 border shadow-sm rounded-xl bg-white'):
                with ui.row().classes('items-center gap-2 mb-3 border-b pb-2 w-full no-wrap'):
                    ui.icon('work', color='#F59E0B').classes('text-xl')
                    ui.label('Graduate Employability').classes('text-lg font-bold text-[#0b1132] truncate')
                render_compact_table_list(get_tables_by_survey('graduate_employability'))