from nicegui import ui
import pandas as pd
import sqlite3
import temp_db


def save_uploaded_file_to_db(app_state, survey_dropdown, year_input, preview_container, upload_widget, update_ui):
    """
    Saves the uploaded file directly to the database without any data cleaning.
    Opens a dialog for the user to confirm the save operation.

    Args:
        app_state (dict): Dictionary storing current DataFrame and other UI state
        survey_dropdown (ui.select): Dropdown selection for survey type
        year_input (ui.input): Input field for the year
        preview_container (ui.column): Container displaying the data preview table
        upload_widget (ui.upload): Upload widget to reset
        update_ui (function): Function to refresh UI state
    """
    
    # 1. Retrieve staged DataFrame and user selections
    df = temp_db.read_staging_full()
    survey = survey_dropdown.value
    year = year_input.value

    # --- Input Validation ---
    if df is None or df.empty:
        ui.notify('Please upload and stage a file first!', color='negative', position='top')
        return
    
    if not survey or not year:
        ui.notify('Please select both Survey and Year before saving!', color='warning', position='top')
        return

    try:
        # Generate table name
        table_name = f"{survey.replace(' ', '_').lower()}_{year}"

        with ui.dialog() as dialog, ui.card().classes('w-full max-w-md p-6'):
            ui.label('Save to Database').classes('text-2xl font-bold text-[#0b1132] mb-4')
            
            ui.label(f'Survey: {survey}').classes('text-sm text-gray-700 mb-1')
            ui.label(f'Year: {year}').classes('text-sm text-gray-700 mb-4')
            
            # Custom name input field
            ui.label('Table Name (Optional)').classes('text-sm font-medium text-gray-700 mb-1')
            name_input = ui.input(
                placeholder=f'Default: {table_name}',
                value=table_name
            ).classes('w-full').props('outlined dense')
            
            ui.label(f'Rows to Save: {len(df)}').classes('text-sm text-gray-600 mb-4 font-semibold')

            # Action buttons
            with ui.row().classes('w-full justify-end gap-2 mt-6'):
                ui.button(
                    'Cancel',
                    on_click=dialog.close
                ).classes('bg-gray-400 hover:bg-gray-500 text-white')

                def confirm_save():
                    """Saves the data to the database with the specified name."""
                    final_table_name = name_input.value if name_input.value else table_name
                    final_table_name = final_table_name.replace(' ', '_').lower()

                    try:
                        # Save to SQLite database
                        conn = sqlite3.connect('survey.db')
                        df.to_sql(final_table_name, conn, if_exists='replace', index=False)
                        conn.close()

                        ui.notify(
                            f'Data saved to table: {final_table_name} 💾',
                            color='positive',
                            position='top'
                        )

                        # Cleanup: remove temp staging DB after commit
                        temp_db.drop_staging_db()

                        dialog.close()

                        # Reset UI back to initial state
                        preview_container.clear()
                        survey_dropdown.set_value(None)
                        year_input.set_value('')
                        update_ui()

                    except Exception as e:
                        ui.notify(f'Database Error: {e}', color='negative', position='top')

                ui.button(
                    'Save to Database',
                    on_click=confirm_save
                ).classes('bg-green-600 hover:bg-green-700 text-white')

        dialog.open()

    except Exception as e:
        ui.notify(f'Error: {e}', color='negative', position='top')
        print(f"Save to Database Error: {e}")
