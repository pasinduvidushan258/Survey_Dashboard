from nicegui import ui
import pandas as pd
import io
import view_data
import delete_data
import data_cleaning
import save_to_database
import temp_db

def dashboard_content():
    # Initialize application state to store the currently uploaded DataFrame
    app_state = {'current_df': None}

    # Clean up any orphan temporary database left from previous crashes
    temp_db.cleanup_orphan_temp_db()

    with ui.column().classes('p-4 w-full '):
     with ui.card().classes('w-full p-8 shadow-sm border border-gray-100 rounded-2xl bg-white'):
        # Main Heading & Subheading
        ui.label('Welcome to the Survey Dashboard').classes('text-4xl font-bold text-[#0b1132]')
        ui.label('Centre for Strategic Planning & University Statistics').classes('text-lg text-gray-500 mt-2 mb-8')
        
        # --- DYNAMIC UI UPDATE FUNCTION ---
        def update_ui(e=None):
            """
            Updates UI elements dynamically based on user selections.
            - Updates filename label
            - Controls visibility of upload section and warning message
            """
            survey = survey_dropdown.value if survey_dropdown.value else "Survey"
            year = year_input.value if year_input.value else "Year"
            dynamic_label.set_text(f'This file save "{survey}_{year}"')
            
            # Show upload section only when both survey and year are selected
            if survey_dropdown.value and year_input.value:
                upload_container.set_visibility(True)
                warning_message.set_visibility(False)
            else:
                upload_container.set_visibility(False)
                warning_message.set_visibility(True)

        # --- SELECTION FILTERS ---
        with ui.row().classes('w-full gap-6 items-end mb-8'):
            
            # Survey selection dropdown
            with ui.column().classes('gap-1'):
                ui.label('Select Survey').classes('text-sm font-bold text-gray-700 ml-1')
                survey_options = ['Student Satisfaction', 'Exit Survey', 'Graduate Employability']
                survey_dropdown = ui.select(
                    options=survey_options,
                    value=None,
                    label='Select a Survey...',
                    on_change=update_ui
                ).classes('w-72').props('outlined dense')
            
            # Year input field
            with ui.column().classes('gap-1'):
                ui.label('Year').classes('text-sm font-bold text-gray-700 ml-1')
                year_input = ui.input(
                    placeholder='e.g. 2023',
                    on_change=update_ui
                ).classes('w-48').props('outlined dense mask="####"')
        
        # Warning message displayed initially until required selections are made
        warning_message = ui.label(
            '⚠️ Please select a Survey and Year before uploading a file.'
        ).classes('text-red-500 font-bold mb-4')

        # --- FILE UPLOAD HANDLING FUNCTION ---
        async def handle_upload(e):
            """
            Handles file upload event:
            - Reads file (CSV or Excel)
            - Converts to DataFrame
            - Displays preview table
            - Stores data in application state
            """
            ui.notify(f'Successfully uploaded: {e.file.name}', color='positive')
            try:
                # Read uploaded file as bytes
                file_bytes = await e.file.read()
                file_content = io.BytesIO(file_bytes)
                
                # Load file into pandas DataFrame based on file type
                if e.file.name.endswith('.csv'):
                    df = pd.read_csv(file_content)
                elif e.file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file_content)
                else:
                    ui.notify('Invalid file format', color='negative')
                    return
                
                # Store uploaded data in application state (original copy)
                app_state['current_df'] = df

                # Save uploaded data to isolated staging database
                saved = temp_db.create_staging_db(df)
                if not saved:
                    ui.notify('Failed to stage uploaded data. Please try uploading again.', color='negative')
                    return

                # Display a safe preview from staging database (first 100 rows)
                staged_preview = temp_db.read_staging_preview(100)
                if staged_preview is None:
                    ui.notify('Unable to read staging preview.', color='negative')
                    return

                preview_df = staged_preview
                columns = [
                    {
                        'name': str(col),
                        'label': str(col),
                        'field': str(col),
                        'align': 'left',
                        'headerStyle': 'border-bottom: 3px solid black !important; font-weight: bold !important;'
                    }
                    for col in preview_df.columns
                ]
                rows = preview_df.to_dict('records')
                
                # Clear previous preview and render new table
                preview_container.clear()
                with preview_container:
                    ui.label(f'Data Preview ({len(rows)} Rows)').classes('text-lg font-bold text-[#0b1132] mb-2')
                    
                    ui.table(
                        columns=columns, 
                        rows=rows,
                        pagination={'rowsPerPage': 0}
                    ).classes('w-fit max-w-full border shadow-sm rounded-lg h-[500px]')\
                     .props('dense bordered separator="cell"')
                    
                    with ui.row().classes('w-full mt-4 gap-4'):
                        # View data in a separate window
                        ui.button(
                            'View',
                            on_click=lambda: view_data.show_view_window(df)
                        ).classes('bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded shadow')

                        # Delete uploaded file and reset UI
                        ui.button(
                            'Delete',
                            on_click=lambda: delete_data.delete_uploaded_file(
                                preview_container, 
                                upload_widget, 
                                survey_dropdown, 
                                year_input, 
                                update_ui  # Use update_ui to refresh UI state
                            )
                        ).classes('bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded shadow')

                        # Trigger data cleaning process
                        ui.button(
                            'Data Cleaning',
                            on_click=lambda: data_cleaning.process_and_clean_data(
                                app_state, 
                                survey_dropdown, 
                                year_input
                            )
                        ).classes('bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded shadow')

                        # Save uploaded file directly to database without cleaning
                        ui.button(
                            'Save to Database',
                            on_click=lambda: save_to_database.save_uploaded_file_to_db(
                                app_state,
                                survey_dropdown,
                                year_input,
                                preview_container,
                                upload_widget,
                                update_ui
                            )
                        ).classes('bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded shadow')

            except Exception as ex:
                ui.notify(f'Error reading file: {ex}', color='negative')

        # --- FILE UPLOAD SECTION (initially hidden) ---
        upload_container = ui.column().classes('w-full max-w-xl gap-1')
        with upload_container:
            ui.label('Upload Survey Data (CSV or Excel)').classes('text-sm font-bold text-gray-700 ml-1')
            
            upload_widget = ui.upload(
                label='Click or drag your CSV / Excel file here',
                auto_upload=True,
                on_upload=handle_upload, 
                multiple=False 
            ).classes('w-full').props('accept=".csv, .xls, .xlsx" max-files="1"')
            
            # Dynamic filename label based on selections
            dynamic_label = ui.label().classes('text-sm text-[#3B82F6] font-medium mt-1 ml-1')

        # Container for table preview
        preview_container = ui.column().classes('w-full mt-8')

        # Initialize UI state (hide upload section until selections are made)
        update_ui()