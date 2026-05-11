from nicegui import ui
from database_password import setup_database, verify_login  # Import database setup and authentication logic

# Import UI components and route-related functions
from sidebar import create_sidebar
from settings_dialog import create_settings_dialog
from home import dashboard_content

# Import additional modules for survey pages and database management
import ex_su.ex_su_main as ex_su_main
import gr_em.gr_em_main as gr_em_main
import database_management_main
import st_sa.st_sa_main as st_sa_main


import os
import sys

def get_image_path(image_name):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, image_name)


# Initialize the database when the application starts
setup_database()


# --- Home Page Route ---
@ui.page('/home')
def show_home():
    # Set the background color for the page
    ui.query('body').style('background-color:#d3dae0;')

    # Initialize the settings dialog component
    settings_dialog = create_settings_dialog()

    # Render the sidebar and highlight the active page
    create_sidebar(settings_dialog, active_page='/home')

    # Load the main dashboard content
    dashboard_content()


# --- Login Logic ---
def attempt_login(username, password):
    """
    Validate user credentials against the database.
    If valid, redirect to the dashboard.
    Otherwise, display an error notification.
    """
    if verify_login(username, password):
        ui.notify('Login Successful!', color='positive')
        ui.navigate.to('/home')  # Redirect to dashboard
    else:
        ui.notify('Invalid Username or Password', color='negative')


# --- Login Page UI ---
@ui.page('/')
def login_page():
    # Apply background styling to the login page
    ui.query('body').style('background-color: #0b1132;')
    ui.query('body').classes('p-0 m-0')

    # Main container (centered layout)
    with ui.column().classes('w-full min-h-screen items-center justify-center'): 
        
        # Header section with logo and titles
        with ui.column().classes('items-center gap-0'):
            ui.image(get_image_path('survey_logo.png')).classes('w-48') 
            ui.label('Welcome to Survey dashboard').classes('text-h3 font-bold text-center -mt-6').style('color: #E5C158;')
            ui.label('Centre for Strategic Planning and University Statistics').classes('text-subtitle1 text-white text-center')

        # Login form card
        with ui.card().classes('shadow-2xl rounded-2xl p-10 w-96 bg-white transition-all duration-300 hover:scale-105 mt-8'):
            ui.label('Login').classes('text-h5 font-bold text-[#0b1132] text-center w-full mb-6')

            # Username input field
            username_input = ui.input('Username').classes('w-full').props('outlined dense') 
            with username_input.add_slot('prepend'):
                ui.icon('person', color='#0b1132')

            # Password input field
            password_input = ui.input('Password', password=True).classes('w-full mb-6 mt-4').props('outlined dense')
            with password_input.add_slot('prepend'):
                ui.icon('lock', color='#0b1132') 
            
            # Toggle password visibility (show/hide)
            with password_input.add_slot('append'):
                def toggle_password():
                    """
                    Toggle password field between visible and hidden states.
                    Also updates the icon accordingly.
                    """
                    if password_input._props.get('type') == 'password':
                        password_input._props['type'] = 'text'
                        eye_icon.name = 'visibility'
                    else:
                        password_input._props['type'] = 'password'
                        eye_icon.name = 'visibility_off'
                    password_input.update()
                
                eye_icon = ui.icon('visibility_off', color='#0b1132')\
                    .classes('cursor-pointer')\
                    .on('click', toggle_password)
            
            # Login button triggers authentication
            ui.button(
                'LOG IN',
                on_click=lambda: attempt_login(username_input.value, password_input.value)
            ).classes('w-full !bg-[#0b1132] text-white hover:!bg-[#050818] transition-all mt-2')


# --- Application Entry Point ---
# Start the NiceGUI application server with specified configurations
ui.run(title='Survey Dashboard', favicon='📊', port=8083, native=True, window_size=(1200, 800))