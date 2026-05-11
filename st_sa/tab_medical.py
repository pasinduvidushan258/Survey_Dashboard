import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.medical_charts as medical_charts
import st_sa.medical_additional_charts as medical_additional_charts

def get_combined_trend_data(db_path="survey.db"):
    try:
        conn = sqlite3.connect(db_path)
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE name LIKE 'student_satisfaction_%'", conn)['name'].tolist()
        dfs = []
        for t in tables:
            d = pd.read_sql_query(f"SELECT * FROM {t}", conn)
            d['Trend_Year'] = t.split('_')[-1]
            dfs.append(d)
        conn.close()
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    except Exception as e:
        print(f"Database Error: {e}")
        return pd.DataFrame()

def render_content(df, selected_year: str):
    if df is None or df.empty:
        ui.label(f"Data analysis for the year {selected_year} is coming soon...").classes('text-gray-500 text-lg italic')
        return

    def find_col(keyword):
        for col in df.columns:
            if keyword.lower() in col.lower(): return col
        return keyword 

    fac_col = find_col('what is your faculty')
    gen_col = find_col('gender')
    usage_col = find_col('have you ever got the service from the medical center')
    
    # Medical වලට අදාළ ප්‍රශ්න 
    overall_medical_col = find_col('overall assessment of the medical centre')
    q1 = find_col('medical centre cleanliness')
    q2 = find_col('emergency treatment facilities')
    q3 = find_col('day treatment facility')
    q4 = find_col('pharmacy and laboratory')
    q5 = find_col('dental service')
    q6 = find_col('availability of doctors')
    q7 = find_col('courtesy and competency of the doctors')
    q8 = find_col('courtesy and competency of the other staff')

    all_medical_cols = [q1, q2, q3, q4, q5, q6, q7, q8, overall_medical_col]

    # 🔴 සම්පූර්ණ ප්‍රශ්න 9ම Dropdown එක සඳහා
    all_medical_questions = {
        'What is your overall assessment of the medical centre (වෛද්‍ය මධ්‍යස්ථානය පිළිබඳ ඔබේ සමස්ත තක්සේරුව කුමක්ද):': overall_medical_col,
        'Medical centre cleanliness and arrangement (වෛද්‍ය මධ්‍යස්ථානයේ පිරිසිදුකම සහ පිළිවෙල):': q1,
        'Emergency treatment facilities (හදිසි ප්‍රතිකාර පහසුකම්):': q2,
        'Day treatment facility (දින ප්‍රතිකාර පහසුකම):': q3,
        'Pharmacy and Laboratory services (ෆාමසි සහ රසායනාගාර සේවා):': q4,
        'Dental Service (දන්ත වෛද්‍ය සේවාව):': q5,
        'Availability of doctors (වෛද්‍යවරුන් සිටීම):': q6,
        'Courtesy and competency of the doctors and nurses (වෛද්‍යවරුන්ගේ සහ හෙදියන්ගේ අනුග්‍රහය සහ නිපුණතාවය):': q7,
        'Courtesy and competency of the other staff (අනෙකුත් කාර්ය මණ්ඩලයේ අනුග්‍රහය සහ නිපුණතාවය):': q8
    }

    # 🔴 KPI කොටු සඳහා 'Overall' එක හැර ඉතිරි ප්‍රශ්න 8
    quick_stats_questions = {k: v for k, v in all_medical_questions.items() if v != overall_medical_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Medical Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        
        with ui.tabs().classes('w-full text-[#3B82F6] border-b') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.strip().lower() == 'all':
                t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            
            # --- TAB 1: OVERVIEW ---
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                # 1. Medical Usage Gauge 
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        medical_charts.draw_overall_satisfaction_gauge(df, overall_medical_col)

                # 2. Donut & Faculty Bar 
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        medical_charts.draw_overall_satisfaction_donut(df, overall_medical_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        medical_charts.draw_overall_faculty_col(df, overall_medical_col, fac_col)
                
                # 3. Quick Stats (කොටු 8 යන්නේ මෙතැනට)
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-4')
                medical_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            # --- TAB 2: FACULTY ANALYSIS ---
            with ui.tab_panel(t_fa).classes('w-full p-0'):
                with ui.card().classes('w-full p-0 shadow-none bg-transparent'): 
                    # Dropdown එකට ප්‍රශ්න 9ම යනවා
                    medical_charts.draw_dynamic_faculty_bar(df, all_medical_questions, fac_col)
            
            # --- TAB 3: GENDER ANALYSIS ---
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                 with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        medical_charts.draw_gender_overall_bar(df, all_medical_cols, gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        medical_charts.draw_clustered_faculty_gender(df, all_medical_cols, fac_col, gen_col)

            # --- TAB 4: YEAR ANALYSIS ---
            if selected_year.strip().lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                medical_additional_charts.draw_year_comparison_bar(cdf, [overall_medical_col], 'Trend_Year')
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                medical_additional_charts.draw_clustered_faculty_year(cdf, [overall_medical_col], fac_col, 'Trend_Year')
                    else:
                        ui.label("Could not load trend data from the database. Please make sure the database name is correct.").classes('text-red-500 font-bold p-4')