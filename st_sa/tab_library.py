import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.library_charts as library_charts
import st_sa.library_additional_charts as library_additional_charts

def get_combined_trend_data(db_path="survey.db"):
    try:
        conn = sqlite3.connect(db_path)
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE name LIKE 'student_satisfaction_%'", conn)['name'].tolist()
        dfs = [pd.read_sql_query(f"SELECT * FROM {t}", conn).assign(Trend_Year=t.split('_')[-1]) for t in tables]
        conn.close()
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    except: return pd.DataFrame()

def render_content(df, selected_year: str):
    if df is None or df.empty:
        ui.label(f"No data available.").classes('text-gray-400 italic')
        return

    def find_col(kw):
        for c in df.columns:
            if kw.lower() in c.lower(): return c
        return kw

    fac_col = find_col('what is your faculty')
    gen_col = find_col('gender')
    usage_col = find_col('how often do you use the library facility')
    
    # --- ප්‍රශ්න 18ම Keywords මගින් අඳුනා ගැනීම ---
    overall_col = find_col('overall assessment of the library services')
    q1 = find_col('number of books available')
    q2 = find_col('electronic resources')
    q3 = find_col('number of thesis')
    q4 = find_col('opening hours of the library')
    q5 = find_col('library orientation')
    q6 = find_col('answering your queries')
    q7 = find_col('photocopying service')
    q8 = find_col('amount of books that can be borrowed')
    q9 = find_col('waiting time for borrowing')
    q10 = find_col('opac (online public access catalogue)')
    q11 = find_col('seating capacity')
    q12 = find_col('sanitary facilities')
    q13 = find_col('lighting inside the library')
    q14 = find_col('ventilation inside the library')
    q15 = find_col('quietness inside the library')
    q16 = find_col('cleanliness in the library')
    q17 = find_col('arrangement of books on shelves')

    # Dropdown එක සහ KPI සඳහා සම්පූර්ණ CSV Column නම් සහිත Dictionary එක
    all_lib_questions = {
        'What is your overall assessment of the library services and resources provided by the library (පුස්තකාලය මඟින් සපයනු ලබන පුස්තකාල සේවා සහ සම්පත් පිළිබඳ ඔබේ සමස්ත තක්සේරුව කුමක්ද):': overall_col,
        'Number of books available in the library (පුස්තකාලයේ ඇති පොත් ගණන):': q1,
        'Electronic resources (E-Books/ E-Journals/ E-Database) available in the library (පුස්තකාලයේ ඇති ඉලෙක්ට්‍රොනික සම්පත් (විද්‍යුත් ග්‍රන්ථ/ විද්‍යුත් සඟරා/ විද්‍යුත් දත්ත සමුදාය):': q2,
        'Number of Thesis available in the library (පුස්තකාලයේ ඇති නිබන්ධන ගණන):': q3,
        'Opening hours of the library (පුස්තකාලය විවෘත වේලාවන්):': q4,
        'Library Orientation Programme (පුස්තකාල දිශානති වැඩසටහන):': q5,
        'Answering your queries (questions) by the library staff (පුස්තකාල කාර්ය මණ්ඩලය විසින් ඔබගේ විමසුම් (ප්‍රශ්න) වලට පිළිතුරු සැපයීම):': q6,
        'Photocopying service provide by the library (පුස්තකාලය මගින් සපයනු ලබන ඡායා පිටපත් කිරීමේ සේවාව):': q7,
        'Amount of books that can be borrowed (ලබා ගත හැකි පොත් ප්‍රමාණය):': q8,
        'Waiting time for borrowing and returning (පොත් ගැනීම සහ ආපසු ලබා දීම සඳහා ඇති පොරොත්තු කාලය):': q9,
        'OPAC (Online Public Access Catalogue) system (OPAC (Online Public Access Catalogue) පද්ධතිය):': q10,
        'Seating capacity in the library (පුස්තකාලයේ ආසන ධාරිතාව):': q11,
        'Sanitary facilities in the library (පුස්තකාලයේ සනීපාරක්ෂක පහසුකම්):': q12,
        'Lighting inside the library (පුස්තකාලය තුළ ආලෝකකරණය):': q13,
        'Ventilation inside the library (පුස්තකාලය තුළ වාතාශ්‍රය):': q14,
        'Quietness inside the library (පුස්තකාලය තුළ නිහඬ බව):': q15,
        'Cleanliness in the library (පුස්තකාලය තුළ පිරිසිදුභාවය):': q16,
        'Arrangement of books on shelves (රාක්කවල පොත් සැකැස්ම):': q17
    }

    # Overall එක නැතුව ඉතිරි 17 KPI කොටු වලට
    quick_stats_questions = {k: v for k, v in all_lib_questions.items() if v != overall_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Library Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        with ui.tabs().classes('w-full border-b text-[#3B82F6]') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.lower() == 'all': t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                library_charts.draw_library_usage_donut(df, usage_col)
                
                with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
                    ui.label('Overall satisfaction of Library facilities').classes('font-bold text-[#0b1132] mb-4')
                    with ui.row().classes('w-full gap-4 items-center'):
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            library_charts.draw_overall_satisfaction_gauge_only(df, overall_col)
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            library_charts.draw_overall_faculty_bar_only(df, overall_col, fac_col)
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-6')
                library_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'): 
                library_charts.draw_dynamic_faculty_bar(df, all_lib_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        library_charts.draw_gender_overall_bar(df, [overall_col], gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        library_charts.draw_clustered_faculty_gender(df, [overall_col], fac_col, gen_col)

            if selected_year.lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        library_additional_charts.draw_year_comparison_bar(cdf, [overall_col], 'Trend_Year')
                        library_additional_charts.draw_clustered_faculty_year(cdf, [overall_col], fac_col, 'Trend_Year')