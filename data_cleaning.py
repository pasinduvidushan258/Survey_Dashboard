from nicegui import ui
import pandas as pd
import temp_db
import st_sa_data_clean 
import review_data_cleaning
import ex_su_data_clean
import gr_em_data_clean

# ==========================================
# MAIN ROUTING & DATA CLEANING CONTROLLER
# ==========================================
def process_and_clean_data(app_state, survey_dropdown, year_input):
    """
    Central controller for routing uploaded survey data to the appropriate
    survey-specific cleaning module. After cleaning, forwards results to 
    the Review Dashboard for user inspection.

    Args:
        app_state (dict): Dictionary storing current DataFrame and other UI state
        survey_dropdown (ui.select): Dropdown selection for survey type
        year_input (ui.input): Input field for the year
    """
    
    # 1. Retrieve staged DataFrame and user selections
    df = temp_db.read_staging_full()
    survey = survey_dropdown.value
    year = year_input.value

    # --- 2. Input Validation ---
    if df is None or df.empty:
        ui.notify('Please upload and stage a file first!', color='negative', position='top')
        return
    
    if not survey or not year:
        ui.notify('Please select both Survey and Year before proceeding to clean!', color='warning', position='top')
        return

    try:
        # --- 3. Routing Logic based on Selected Survey ---
        cleaned_df = None
        removed_df = None  # DataFrame to store removed rows and reasons
        status = False
        msg = ""

        metadata = {}
        if survey == 'Student Satisfaction':
            cleaned_df, removed_df, status, msg, metadata = st_sa_data_clean.clean_student_satisfaction_data(df)
            
        elif survey == 'Exit Survey':
            cleaned_df, removed_df, status, msg, metadata = ex_su_data_clean.clean_exit_survey_data(df)
            ui.notify('Exit Survey data cleaning is currently under development.', color='info', position='top')
           
        elif survey == 'Graduate Employability':
            cleaned_df, removed_df, status, msg, metadata = gr_em_data_clean.clean_graduate_employability_data(df)
            ui.notify('Graduate Employability data cleaning is currently under development.', color='info', position='top')
            
        else:
            # Invalid survey type
            ui.notify('Unknown survey type selected.', color='negative', position='top')
            return

        # --- 4. Post-Cleaning Action: Open Review Panel ---
        if status:
            ui.notify(f'{survey} data processed successfully. Opening Review Panel...', color='info', position='top')
            
            # Pass results to the Review Dashboard window
            review_data_cleaning.show_review_window(cleaned_df, removed_df, survey, year, metadata=metadata)
            
        else:
            # Display any logical errors caught during cleaning
            ui.notify(f'Cleaning process failed: {msg}', color='negative', position='top')

    except Exception as e:
        # Catch unexpected runtime/system errors
        ui.notify(f'A system error occurred during processing: {e}', color='negative', position='top')
        print(f"Data Cleaning Error: {e}")