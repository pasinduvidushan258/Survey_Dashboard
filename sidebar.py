from nicegui import ui

import os
import sys

def get_image_path(image_name):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, image_name)

def create_sidebar(settings_dialog, active_page: str):
    """
    Creates a collapsible sidebar drawer for the dashboard with navigation items and settings.

    Args:
        settings_dialog (ui.Dialog): The settings dialog object to open when clicking Settings.
        active_page (str): URL of the currently active page to highlight the menu item.

    Returns:
        ui.LeftDrawer: The NiceGUI left drawer object.
    """
    # --- Custom CSS for drawer animations and mini mode ---
    ui.add_head_html('''
        <style>
            .q-drawer--mini .hide-on-mini { display: none !important; }
            .q-drawer--mini .nav-item, .q-drawer--mini .menu-row {
                justify-content: center !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
            }
            .q-drawer { transition: width 0.3s ease-in-out !important; }
        </style>
    ''')

    # --- Initialize Drawer ---
    drawer = ui.left_drawer(value=True, fixed=True)\
        .classes('bg-[#0b1132] text-white p-0 overflow-hidden')\
        .props('width=280 mini-width=70 breakpoint=0')

    is_mini = {'state': False}  # Drawer mini state toggle

    def toggle_mini():
        """Toggle between mini and full drawer."""
        is_mini['state'] = not is_mini['state']
        if is_mini['state']:
            drawer.props('mini')
        else:
            drawer.props(remove='mini')

    with drawer:
        with ui.column().classes('w-full h-full no-wrap'):
            # --- Top Section: Logo + Menu Button ---
            with ui.row().classes('w-full items-center no-wrap px-3 pt-4 menu-row'):
                ui.button(icon='menu', on_click=toggle_mini)\
                    .props('flat color=white').classes('cursor-pointer')
                ui.image(get_image_path('survey_logo.png')).classes('w-30 hide-on-mini')

            ui.separator().classes('bg-white/10')

            # --- Navigation Items ---
            with ui.column().classes('w-full mt-0 gap-2'):
                def nav_item(icon: str, label: str, target_url: str):
                    """Creates a single navigation row with active highlight."""
                    is_active = (active_page == target_url)
                    bg = 'bg-[#3B82F6]' if is_active else 'hover:bg-white/10'
                    with ui.row().classes(
                        f'{bg} items-center justify-center no-wrap gap-3 px-2 py-3 mx-5 rounded-lg cursor-pointer nav-item'
                    ).on('click', lambda: ui.navigate.to(target_url)):
                        ui.icon(icon).classes('text-2xl')
                        ui.label(label).classes('text-sm no-wrap hide-on-mini')

                # --- Dashboard Navigation ---
                nav_item('home', 'Home', '/home')
                nav_item('bar_chart', 'Student Satisfaction', '/student_satisfaction')
                nav_item('menu_book', 'Exit Survey', '/exit_survey')
                nav_item('people', 'Graduate Employability', '/graduate_employability')
                nav_item('storage', 'Database Management', '/database_management')

            # --- Bottom Section: Settings + Logout ---
            with ui.column().classes('w-full mt-auto mb-4 gap-1'):
                ui.separator().classes('bg-white/10 mb-2')

                # Settings button
                with ui.row().classes(
                    'hover:bg-white/10 items-center no-wrap px-2 py-3 mx-5 rounded-lg cursor-pointer nav-item'
                ).on('click', settings_dialog.open):
                    ui.icon('settings').classes('text-2xl')
                    ui.label('Settings').classes('hide-on-mini')

                # Logout button
                with ui.row().classes(
                    'hover:bg-white/10 items-center no-wrap px-2 py-3 mx-5 rounded-lg cursor-pointer nav-item'
                ).on('click', lambda: ui.navigate.to('/')):
                    ui.icon('logout').classes('text-2xl')
                    ui.label('Log Out').classes('hide-on-mini')

    return drawer