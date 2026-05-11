from nicegui import ui
import sidebar
from settings_dialog import create_settings_dialog

@ui.page('/exit_survey')
def exit_survey_page():
    """
    Renders the Exit Survey page of the dashboard.
    Includes the settings dialog, sidebar, and page-specific content.
    """
    # Create settings dialog (global dashboard settings)
    settings_dialog = create_settings_dialog()

    # Render the sidebar and highlight the active page
    sidebar.create_sidebar(settings_dialog, active_page='/exit_survey')
    
    # Main content column (adjusted for sidebar offset)
    with ui.column().classes('p-10 ml-[80px]'):
        # Page title
        ui.label('Welcome to the Exit Survey').classes('text-3xl font-bold text-[#0b1132]')
        # Placeholder content
        ui.label('hhhhh')  # TODO: Replace with actual Exit Survey UI components