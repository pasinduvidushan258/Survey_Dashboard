from nicegui import ui
import temp_db

def delete_uploaded_file(preview_container, upload_widget, survey_dropdown, year_input, update_filename_func):
    """
    Clears all uploaded data, resets input fields, and updates the UI.

    Args:
        preview_container (ui.column): Container displaying the data preview table and action buttons
        upload_widget (ui.upload): The upload widget to reset
        survey_dropdown (ui.select): Dropdown to select the survey
        year_input (ui.input): Input field for the year
        update_filename_func (function): Function to update dynamic label or filename display
    """
    try:
        # 1. Clear the container holding the data table and action buttons
        preview_container.clear()
        
        # 2. Reset the upload widget to remove the previously uploaded file
        upload_widget.run_method('reset')
        
        # 3. Reset Survey selection and Year input fields
        survey_dropdown.value = None
        year_input.value = ''
        
        # 4. Refresh dynamic label / filename display
        update_filename_func()

        # 5. Delete staging DB to avoid orphaned temp files
        temp_db.drop_staging_db()

        # 6. Show a success notification
        ui.notify('All data and selections cleared successfully!', color='warning', position='top')
        
    except Exception as e:
        # Notify user if deletion fails and log the error
        ui.notify(f'Delete Error: {e}', color='negative', position='top')
        print(f"Delete Error: {e}")