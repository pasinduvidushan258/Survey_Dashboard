import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.washroom_charts as washroom_charts
import st_sa.washroom_additional_charts as washroom_additional_charts

def get_combined_trend_data():
    try:
        db_path = "survey.db" 
        conn = sqlite3.connect(db_path)
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'student_satisfaction_%';"
        tables = pd.read_sql_query(query, conn)['name'].tolist()
        
        all_data = []
        for table in tables:
            year_str = table.split('_')[-1] 
            df_year = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            df_year['Trend_Year'] = year_str 
            all_data.append(df_year)
            
        conn.close()
        return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
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
    
    # Washroom ප්‍රශ්න හඳුනාගැනීම
    overall_col = find_col('overall assessment of the washroom facilities')
    q1 = find_col('adequacy of washrooms in the university')
    q2 = find_col('sufficient water and soap')
    q3 = find_col('disposal of sanitary napkins')
    q4 = find_col('washroom accessories in usable condition')
    q5 = find_col('cleanliness of washrooms')

    # 🔴 ඔයා දීපු විදිහටම සම්පූර්ණ ප්‍රශ්න 6ම ඇතුළත් කළා
    all_washroom_questions = {
        'What is your overall assessment of the washroom facilities in the university (විශ්ව විද්‍යාලයේ වැසිකිළි පහසුකම් පිළිබඳ ඔබේ සමස්ත තක්සේරුව කුමක්ද):': overall_col,
        'Adequacy of washrooms in the university (විශ්වවිද්‍යාලයේ වැසිකිළි වල ප්‍රමාණවත් බව):': q1,
        'Sufficient water and soap in the washrooms (වැසිකිළිවල ප්‍රමාණවත් ජලය සහ සබන් තිබීම):': q2,
        'Having adequate facilities for the disposal of sanitary napkins in ladies washrooms (කාන්තා වැසිකිලි වල සනීපාරක්ෂක තුවා බැහැර කිරීම සඳහා ප්‍රමාණවත් පහසුකම් තිබීම):': q3,
        'Availability of all washroom accessories in usable condition (සියලුම නානකාමර උපාංග භාවිතා කළ හැකි තත්වයේ තිබීම):': q4,
        'Cleanliness of washrooms (වැසිකිළි වල පිරිසිදුකම):': q5
    }

    # 🔴 KPI කොටු සඳහා 'Overall' එක හැර ඉතිරි ප්‍රශ්න 5
    quick_stats_questions = {k: v for k, v in all_washroom_questions.items() if v != overall_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Washroom Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        
        with ui.tabs().classes('w-full text-[#3B82F6] border-b') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.strip().lower() == 'all':
                t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        washroom_charts.draw_overall_satisfaction_donut(df, overall_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        washroom_charts.draw_overall_faculty_col(df, overall_col, fac_col)
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-4')
                washroom_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'):
                with ui.card().classes('w-full p-0 shadow-none bg-transparent'): 
                    washroom_charts.draw_dynamic_faculty_bar(df, all_washroom_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                 with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        washroom_charts.draw_gender_overall_bar(df, list(all_washroom_questions.values()), gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        washroom_charts.draw_clustered_faculty_gender(df, list(all_washroom_questions.values()), fac_col, gen_col)

            if selected_year.strip().lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                washroom_additional_charts.draw_year_comparison_bar(cdf, [overall_col], 'Trend_Year')
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                washroom_additional_charts.draw_clustered_faculty_year(cdf, [overall_col], fac_col, 'Trend_Year')