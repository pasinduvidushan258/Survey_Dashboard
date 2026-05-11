from nicegui import ui
import st_sa_db
from st_sa import (tab_env, tab_main, tab_library, tab_sports, 
                   tab_hostel, tab_medical, tab_ict, tab_canteen, tab_washroom)

def render_dashboard(selected_year: str, back_callback, refresh_callback=None):
    df = st_sa_db.load_data(selected_year)

    # ================= CSS FIX (ACTIVE TAB PATA KIRIMA) =================
    ui.add_head_html('''
        <style>
            .q-tabs__arrow { display: none !important; }

            .q-tab__label { 
                white-space: nowrap !important; 
                font-size: 9px !important;
                font-weight: bold !important;
            }

            .q-tab { 
                min-height: 40px !important;
                min-width: 0 !important; 
                flex: 1 1 0% !important; 
                padding: 0 2px !important;
                transition: all 0.3s; /* ලස්සනට පාට මාරු වෙන්න */
            }

            /* මෙන්න මෙතනින් තමයි දැනට ඉන්න Tab එක පාට කරන්නේ */
            .q-tab--active {
                background-color: #3b82f6 !important; /* අර නිල් පාටම දුන්නා */
                color: black !important; /* අකුරු කළු කළා */
                border-radius: 10px; /* ටැබ් එක පොඩ්ඩක් රවුම් කළා */
                margin: 1px;
            }

            .q-tabs__content {
                overflow: hidden !important;
            }
        </style>
    ''')

    # ================= HEADER (BACK & YEAR SELECTOR FIX) =================
    with ui.row().classes('w-full items-center justify-between mb-3 px-1'):
        
        # 1. Back Button
        # මෙතන bg-[#3b82f6] පාවිච්චි කරමු, bg-blue වලට වඩා ඒක active පාටට ගැලපෙනවා
        ui.button('BACK', icon='arrow_back', on_click=back_callback)\
            .props('flat')\
            .classes('text-black bg-white border border-[#3b82f6] rounded-md px-4 shadow-sm')\
            .style('height: 38px;')

        # 2. Title (4xl)
        header_title = ui.label('Overall Student Satisfaction')\
            .classes('text-4xl font-bold text-[#0b1132] text-center flex-grow')

        # 3. Year Filter (Dropdown එක බොත්තමක් වගේ හදමු)
        with ui.row().classes('items-center'):
            years = st_sa_db.get_available_years()
            year_options = {str(y): str(y) for y in years}
            year_options['All'] = 'All Years'

            # select එකට කෙලින්ම classes දානවා එතකොට ඒක බොත්තම වගේම වෙනවා
            ui.select(
                options=year_options,
                value=str(selected_year),
                on_change=lambda e: refresh_callback(e.value) if refresh_callback else None
            ).props('dense borderless hide-bottom-space') \
             .classes('bg-white text-black font-bold border border-[#3b82f6] rounded-md w-[120px] px-2 shadow-sm cursor-pointer') \
             .style('height: 38px; display: flex; align-items: center;')

    # ================= TABS (BREAKPOINT=0 දමා FIX කර ඇත) =================
    # whitespace-normal දාලා තියෙන්නේ ඉඩ මදි වුණොත් අකුරු පේළි දෙකකට යන්න ඉඩ දෙන්න
    tab_classes = 'text-[10px] px-1 py-1 rounded-md hover:bg-gray-100 whitespace-normal'

    with ui.tabs().props('dense no-caps breakpoint=0 shrink stretch')\
        .classes('w-full bg-white rounded-xl shadow-sm p-2 gap-1 border').style('height: 55px;') as tabs:

        ui.tab('main', label='🏠 MAIN').classes(tab_classes)
        ui.tab('env', label='🎓 UNIVERSITY ENVIRONMENT').classes(tab_classes)
        ui.tab('lib', label='📚 LIBRARY FACILITIES').classes(tab_classes)
        ui.tab('sport', label='🏅 SPORTS FACILITIES').classes(tab_classes)
        ui.tab('hostel', label='🏨 HOSTEL FACILITIES').classes(tab_classes)
        ui.tab('med', label='🏥 MEDICAL FACILITIES').classes(tab_classes)
        ui.tab('ict', label='💻 COMPUTER LAB FACILITIES').classes(tab_classes)
        ui.tab('cant', label='🍽️ CANTEEN FACILITIES').classes(tab_classes)
        ui.tab('wash', label='🚻 WASHROOM').classes(tab_classes)

    # ================= TITLE CHANGE LOGIC =================
    titles = {
        'main': '📊 Overall Student Satisfaction',
        'env': '🎓 Students satisfaction with University Environment',
        'lib': '📚 Students satisfaction with Library facilities',
        'sport': '🏅 Students satisfaction with Sports facilities',
        'hostel': '🏨 Students satisfaction with Hostel facilities',
        'med': '🏥 Medical facilities Satisfaction',
        'ict': '💻 Computer Lab facilities Satisfaction',
        'cant': '🍽️ Canteen facilities Satisfaction',
        'wash': '🚻 Washroom facilities Satisfaction'
    }

    def handle_tab_change():
        header_title.set_text(titles.get(tabs.value, 'Student Satisfaction'))

    tabs.on_value_change(handle_tab_change)
    # මුලින්ම load වෙද්දී title එක update කිරීමට
    ui.timer(0.01, handle_tab_change, once=True)

    # ================= CONTENT =================
    with ui.tab_panels(tabs, value='main')\
        .classes('w-full bg-transparent p-0 mt-3').style('transition: none;'):

        with ui.tab_panel('main'):
            tab_main.render_content(df, selected_year)

        with ui.tab_panel('env'):
            tab_env.render_content(df, selected_year)

        with ui.tab_panel('lib'):
            tab_library.render_content(df, selected_year)

        with ui.tab_panel('sport'):
            tab_sports.render_content(df, selected_year)

        with ui.tab_panel('hostel'):
            tab_hostel.render_content(df, selected_year)

        with ui.tab_panel('med'):
            tab_medical.render_content(df, selected_year)

        with ui.tab_panel('ict'):
            tab_ict.render_content(df, selected_year)

        with ui.tab_panel('cant'):
            tab_canteen.render_content(df, selected_year)

        with ui.tab_panel('wash'):
            tab_washroom.render_content(df, selected_year)