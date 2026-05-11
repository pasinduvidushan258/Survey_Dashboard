import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.canteen_charts as canteen_charts
import st_sa.canteen_additional_charts as canteen_additional_charts

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
    usage_col = find_col('which canteen do you mostly use')
    
    # Canteen ප්‍රශ්න හඳුනාගැනීම
    overall_canteen_col = find_col('overall assessment of the canteen facilities')
    q1 = find_col('adequacy of canteens')
    q2 = find_col('quality of food')
    q3 = find_col('prices in canteens')
    q4 = find_col('environment in canteens')
    q5 = find_col('friendliness of canteen staff')

    # 🔴 ඔයා දීපු විදිහටම සම්පූර්ණ ප්‍රශ්න 6 Dropdown එක සඳහා
    all_canteen_questions = {
        'What is your overall assessment of the canteen facilities in the university (විශ්ව විද්‍යාලයේ ආපනශාලා පහසුකම් පිළිබඳ ඔබේ සමස්ත තක්සේරුව කුමක්ද):': overall_canteen_col,
        'Adequacy of canteens in the University (විශ්වවිද්‍යාලයේ ආපනශාලාවල ප්‍රමාණවත් බව):': q1,
        'Quality of food (ආහාරවල ගුණාත්මකභාවය):': q2,
        'Prices in canteens are acceptable (ආපනශාලා ආහාරවල මිල ගණන් පිළිගත හැකිය):': q3,
        'The environment in canteens is pleasant (ආපනශාලාවල පරිසරය ප්‍රසන්නය):': q4,
        'Friendliness of canteen staff (ආපනශාලා කාර්ය මණ්ඩලයේ සුහදශීලී බව):': q5
    }

    # 🔴 KPI කොටු සඳහා 'Overall' එක හැර ඉතිරි ප්‍රශ්න 5
    quick_stats_questions = {k: v for k, v in all_canteen_questions.items() if v != overall_canteen_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Canteen Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        
        with ui.tabs().classes('w-full text-[#3B82F6] border-b') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.strip().lower() == 'all':
                t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                # 1. Canteen Usage
                canteen_charts.draw_canteen_usage_pie(df, usage_col)

                # 2. Donut & Faculty Bar
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        canteen_charts.draw_overall_satisfaction_donut(df, overall_canteen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        canteen_charts.draw_overall_faculty_col(df, overall_canteen_col, fac_col)
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-4')
                # 🔴 ප්‍රශ්න 5 පෙන්වන KPI කොටු
                canteen_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'):
                with ui.card().classes('w-full p-0 shadow-none bg-transparent'): 
                    canteen_charts.draw_dynamic_faculty_bar(df, all_canteen_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                 with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        canteen_charts.draw_gender_overall_bar(df, list(all_canteen_questions.values()), gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        canteen_charts.draw_clustered_faculty_gender(df, list(all_canteen_questions.values()), fac_col, gen_col)

            if selected_year.strip().lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                canteen_additional_charts.draw_year_comparison_bar(cdf, [overall_canteen_col], 'Trend_Year')
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                canteen_additional_charts.draw_clustered_faculty_year(cdf, [overall_canteen_col], fac_col, 'Trend_Year')