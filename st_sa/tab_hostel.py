import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.hostel_charts as hostel_charts
import st_sa.hostel_additional_charts as hostel_additional_charts

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
        ui.label(f"Data for {selected_year} is coming soon...").classes('text-gray-500 italic')
        return

    def find_col(kw):
        for c in df.columns:
            if kw.lower() in c.lower(): return c
        return kw

    fac_col = find_col('what is your faculty')
    gen_col = find_col('gender')
    usage_col = find_col('stay in hostels or have you ever stayed')
    hostel_name_col = find_col('name of the hostel')
    
    overall_col = find_col('overall assessment of the hostel facility')
    q1 = find_col('cafeteria facilities are adequate')
    q2 = find_col('environment is peaceful')
    q3 = find_col('hostels are clean')
    q4 = find_col('sanitary facilities are good')
    q5 = find_col('environment is secure')
    q6 = find_col('well furnished')
    q7 = find_col('renovated when necessary')

    all_hostel_questions = {
        'What is your overall assessment of the hostel facility in the university (විශ්වවිද්‍යාලයේ නේවාසිකාගාර පහසුකම් පිළිබඳ ඔබගේ සමස්ත තක්සේරුව කුමක්ද):': overall_col,
        'Hostel cafeteria facilities are adequate (නේවාසිකාගාර ආපනශාලා පහසුකම් ප්‍රමාණවත් වේ):': q1,
        'Hostel environment is peaceful (නේවාසිකාගාර පරිසරය සාමකාමීය):': q2,
        'Hostels are clean (නේවාසිකාගාර පිරිසිදු ය):': q3,
        'Hostel sanitary facilities are good (නේවාසිකාගාර සනීපාරක්ෂක පහසුකම් හොඳ තත්ත්වයේ ඇත):': q4,
        'Hostel environment is secure (නේවාසිකාගාර පරිසරය ආරක්ෂිතය):': q5,
        'Hostels are well furnished (නේවාසිකාගාර අංගසම්පූර්ණ වේ):': q6,
        'Hostels are renovated when necessary (අවශ්‍ය වූ විට නේවාසිකාගාර ප්‍රතිසංස්කරණය කෙරේ):': q7
    }

    quick_stats_questions = {k: v for k, v in all_hostel_questions.items() if v != overall_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Hostel Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        with ui.tabs().classes('w-full border-b text-[#3B82F6]') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.lower() == 'all': t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                hostel_charts.draw_hostel_usage_gauge(df, usage_col)
                
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        hostel_charts.draw_overall_satisfaction_gauge(df, overall_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        hostel_charts.draw_overall_faculty_col(df, overall_col, fac_col)

                # 🔴 මෙතැනදී fac_col එකත් යවනවා Science/Non-Science කඩන්න
                with ui.row().classes('w-full gap-4 mt-4'):
                    hostel_charts.draw_hostel_population_rose_chart(df, hostel_name_col, fac_col)

                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-4')
                hostel_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'): 
                hostel_charts.draw_dynamic_faculty_bar(df, all_hostel_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        hostel_charts.draw_gender_overall_bar(df, [overall_col], gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        hostel_charts.draw_clustered_faculty_gender(df, [overall_col], fac_col, gen_col)

            if selected_year.lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        hostel_additional_charts.draw_year_comparison_bar(cdf, [overall_col], 'Trend_Year')
                        hostel_additional_charts.draw_clustered_faculty_year(cdf, [overall_col], fac_col, 'Trend_Year')