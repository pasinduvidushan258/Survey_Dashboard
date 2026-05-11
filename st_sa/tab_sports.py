import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.sports_charts as sports_charts
import st_sa.sports_additional_charts as sports_additional_charts

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
    
    usage_col = find_col('involved in sports')
    
    # 🔴 Columns හඳුනාගැනීම
    overall_col = find_col('overall assessment of the sports facilities')
    q1 = find_col('available sports activities')
    q2 = find_col('quality of the sport equipment')
    q3 = find_col('space allocated for sport activities')
    q4 = find_col('changing rooms and shower cubicles')
    q5 = find_col('helpfulness and support of sport complex staff')

    # 🔴 Dropdown එක සඳහා සම්පූර්ණ ප්‍රශ්න ලැයිස්තුව
    all_sports_questions = {
        'What is your overall assessment of the Sports facilities in the University (විශ්ව විද්‍යාලයේ ක්‍රීඩා පහසුකම් පිළිබඳ ඔබගේ සමස්ත තක්සේරුව කුමක්ද):': overall_col,
        'Available sports activities (පවතින ක්‍රීඩා ක්‍රියාකාරකම්):': q1,
        'Quality of the sport equipment (ක්‍රීඩා උපකරණවල ගුණාත්මකභාවය):': q2,
        'Space allocated for sport activities (ක්‍රීඩා කටයුතු සඳහා වෙන් කරන ලද ඉඩකඩ ප්‍රමාණය):': q3,
        'Changing rooms and shower cubicles (මාරු කරන කාමර සහ ස්නානය කරන කුටි):': q4,
        'Helpfulness and support of sport complex staff (ක්‍රීඩා සංකීර්ණ කාර්ය මණ්ඩලයේ උපකාරය සහ සහාය):': q5
    }

    # 🔴 KPI කොටු සඳහා 'Overall' එක හැර ඉතිරි ප්‍රශ්න 5
    quick_stats_questions = {k: v for k, v in all_sports_questions.items() if v != overall_col}

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Sports Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        with ui.tabs().classes('w-full border-b text-[#3B82F6]') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.lower() == 'all': t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                
                sports_charts.draw_sports_usage_gauge(df, usage_col)
                
                with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
                    ui.label('Overall satisfaction of Sports facilities').classes('font-bold text-[#0b1132] mb-4')
                    with ui.row().classes('w-full gap-4 items-center'):
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            sports_charts.draw_overall_satisfaction_gauge_only(df, overall_col)
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            sports_charts.draw_overall_faculty_bar_only(df, overall_col, fac_col)
                    ui.label('💡 This section shows the overall satisfaction level and how it varies across different faculties.').classes('text-xs text-gray-400 italic text-center w-full mt-2')
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-6')
                sports_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'): 
                sports_charts.draw_dynamic_faculty_bar(df, all_sports_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        sports_charts.draw_gender_overall_bar(df, [overall_col], gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        sports_charts.draw_clustered_faculty_gender(df, [overall_col], fac_col, gen_col)

            if selected_year.lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        sports_additional_charts.draw_year_comparison_bar(cdf, [overall_col], 'Trend_Year')
                        sports_additional_charts.draw_clustered_faculty_year(cdf, [overall_col], fac_col, 'Trend_Year')