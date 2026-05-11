from nicegui import ui
import sidebar
from settings_dialog import create_settings_dialog
import st_sa_db

# අලුතින් හදපු Navigation Bar ෆයිල් එක Import කරගැනීම
import st_sa.st_sa_dashboard as st_sa_dashboard

@ui.page('/student_satisfaction')
def student_satisfaction_page():
    """
    Student Satisfaction සඳහා ප්‍රධාන ඇතුල්වීමේ පිටුව.
    """
    ui.query('body').style('background-color:#d3dae0;')
    settings_dialog = create_settings_dialog()
    sidebar.create_sidebar(settings_dialog, active_page='/student_satisfaction')
    
    # ප්‍රධාන Container එක - මේක ඇතුළේ තමයි ඔක්කොම දේවල් මාරු වෙන්නේ
    main_container = ui.column().classes('p-2 w-full')

    def load_dashboard(selected_year: str):
        """අවුරුද්දක් තේරුවට පස්සේ Dashboard එකට (Tabs ටිකට) යන ෆන්ක්ෂන් එක"""
        main_container.clear() 
        with main_container:
            # st_sa_nav_bar එකට තෝරගත්ත අවුරුද්ද සහ Back යන්න ඕන ෆන්ක්ෂන් එක යවනවා
            st_sa_dashboard.render_dashboard(selected_year, show_year_selection, load_dashboard)

    def show_year_selection():
        """අවුරුදු තෝරන මෙනුව පෙන්වන ෆන්ක්ෂන් එක"""
        main_container.clear()
        
        with main_container:
            with ui.card().classes('w-full p-8 shadow-sm border border-gray-100 rounded-2xl bg-white'):
                ui.label('📊 Student Satisfaction').classes('text-4xl font-bold text-[#0b1132]')
                ui.label('Centre for Strategic Planning & University Statistics').classes('text-lg mt-2 ml-6')
                ui.label('Welcome to the Student Satisfaction').classes('text-gray-500 ml-6 mt-1 mb-8')

                # 'All Years' කාඩ් එක
                with ui.card().classes('w-64 p-3 ml-6 cursor-pointer hover:bg-gray-100 border transition-all').on('click', lambda: load_dashboard('All')):
                    ui.label('All Years').classes('text-lg font-bold text-[#0b1132] text-center w-full')

                # ඩේටාබේස් එකෙන් අවුරුදු ටික අරගෙන කාඩ් හදනවා
                years = st_sa_db.get_available_years()
                for year in years:
                    with ui.card().classes('w-64 p-3 ml-6 mt-3 cursor-pointer hover:bg-gray-100 border transition-all').on('click', lambda e, y=year: load_dashboard(y)):
                        ui.label(year).classes('text-lg font-bold text-[#0b1132] text-center w-full')

    # පිටුව ලෝඩ් වෙද්දී මුලින්ම අවුරුදු තෝරන මෙනුව පෙන්නන්න
    show_year_selection()