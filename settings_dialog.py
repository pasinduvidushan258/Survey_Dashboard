from nicegui import ui
from database_password import update_password

def create_settings_dialog() -> ui.Dialog:
    """
    Creates a NiceGUI settings dialog for changing the admin password.
    Includes fields for current password, new password, and confirmation.

    Returns:
        ui.Dialog: The NiceGUI dialog object.
    """
    with ui.dialog() as settings_dialog, ui.card().classes('w-96 p-6'):
        # Title
        ui.label('Change Password').classes('text-h5 font-bold text-[#0b1132] mb-4')

        # Input fields
        current_pw = ui.input('Current Password', password=True)\
                        .classes('w-full mb-3').props('outlined dense')

        new_pw = ui.input('New Password', password=True)\
                    .classes('w-full mb-3').props('outlined dense')

        confirm_pw = ui.input('Confirm Password', password=True)\
                        .classes('w-full mb-4').props('outlined dense')

        # --- Function to update password ---
        def update_pw():
            # 1️⃣ Check if new password matches confirmation
            if new_pw.value != confirm_pw.value:
                ui.notify('Passwords do not match', color='negative')
                return

            # 2️⃣ Attempt password update in database
            success = update_password(current_pw.value, new_pw.value)

            if success:
                ui.notify('Password Updated Successfully', color='positive')
                settings_dialog.close()
            else:
                ui.notify('Current password incorrect', color='negative')

        # --- Dialog buttons ---
        with ui.row().classes('w-full justify-end'):
            ui.button('Cancel', on_click=settings_dialog.close).props('flat')
            ui.button('Update', on_click=update_pw)\
                .classes('bg-[#0b1132] text-white')

    return settings_dialog