import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.env_charts as env_charts
import st_sa.env_additional_charts as env_additional_charts

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
    
    overall_col = find_col('overall assessment of the learning environment')
    q_security = find_col('security system')
    q_lecture = find_col('lecture halls')
    q_academic = find_col('support from academic staff')
    q_temp_academic = find_col('temporary academic staff')
    q_admin = find_col('administrative and non-academic')
    q_senior = find_col('senior students')
    q_ind_work = find_col('spaces for individual work')
    q_team_work = find_col('spaces for team work')
    q_clean = find_col('cleanliness and orderliness')
    q_landscape = find_col('pleasant view')

    all_env_questions = {
        'What is your overall assessment of the learning environment in the University (විශ්වවිද්‍යාලයේ ඉගෙනුම් පරිසරය පිළිබඳ ඔබේ සමස්ත තක්සේරුව කුමක්ද):': overall_col,
        'University security system (විශ්වවිද්‍යාල ආරක්ෂක පද්ධතිය):': q_security,
        'Lecture halls and their facilities (දේශන ශාලා සහ ඒවායේ පහසුකම්):': q_lecture,
        'Support from Academic staff (අධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_academic,
        'Support from Temporary academic staff (තාවකාලික අධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_temp_academic,
        'Support from Administrative and Non-academic staff (පරිපාලන හා අනධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_admin,
        'Support from Senior Students (ජ්‍යෙෂ්ඨ සිසුන්ගේ සහාය):': q_senior,
        'Adequacy of spaces for individual work outside classroom (පන්ති කාමරයෙන් පිටත තනි වැඩ සඳහා ඉඩකඩ ප්‍රමාණවත් වීම):': q_ind_work,
        'Adequacy of spaces for team work (discussion) outside classroom (පන්ති කාමරයෙන් පිටත කණ්ඩායම් වැඩ (සාකච්ඡා) සඳහා ඉඩකඩ ප්‍රමාණවත් වීම):': q_team_work,
        'Cleanliness and orderliness of the University Premises (විශ්වවිද්‍යාල පරිශ්‍රයේ පිරිසිදුකම සහ ක්‍රමවත් බව):': q_clean,
        'Pleasant view of the University landscape (විශ්ව විද්‍යාල භූ දර්ශනයේ ප්‍රසන්න දසුන):': q_landscape
    }

    quick_stats_questions = {
        'University security system (විශ්වවිද්‍යාල ආරක්ෂක පද්ධතිය):': q_security,
        'Lecture halls and their facilities (දේශන ශාලා සහ ඒවායේ පහසුකම්):': q_lecture,
        'Support from Academic staff (අධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_academic,
        'Support from Temporary academic staff (තාවකාලික අධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_temp_academic,
        'Support from Administrative and Non-academic staff (පරිපාලන හා අනධ්‍යයන කාර්ය මණ්ඩලයේ සහාය):': q_admin,
        'Support from Senior Students (ජ්‍යෙෂ්ඨ සිසුන්ගේ සහාය):': q_senior,
        'Adequacy of spaces for individual work outside classroom (පන්ති කාමරයෙන් පිටත තනි වැඩ සඳහා ඉඩකඩ ප්‍රමාණවත් වීම):': q_ind_work,
        'Adequacy of spaces for team work (discussion) outside classroom (පන්ති කාමරයෙන් පිටත කණ්ඩායම් වැඩ (සාකච්ඡා) සඳහා ඉඩකඩ ප්‍රමාණවත් වීම):': q_team_work,
        'Cleanliness and orderliness of the University Premises (විශ්වවිද්‍යාල පරිශ්‍රයේ පිරිසිදුකම සහ ක්‍රමවත් බව):': q_clean,
        'Pleasant view of the University landscape (විශ්ව විද්‍යාල භූ දර්ශනයේ ප්‍රසන්න දසුන):': q_landscape
    }

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Learning Environment').classes('text-3xl font-bold text-[#0b1132] mb-2')
        with ui.tabs().classes('w-full border-b text-[#3B82F6]') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.lower() == 'all': t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
                    ui.label('Overall satisfaction of Learning Environment').classes('font-bold text-[#0b1132] mb-4')
                    with ui.row().classes('w-full gap-4 items-center'):
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            env_charts.draw_overall_satisfaction_gauge_only(df, overall_col)
                        with ui.column().classes('flex-1 min-w-[300px]'):
                            env_charts.draw_overall_faculty_bar_only(df, overall_col, fac_col)
                    ui.label('💡 This section shows the overall satisfaction level and how it varies across different faculties.').classes('text-xs text-gray-400 italic text-center w-full mt-2')
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-6')
                env_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'): 
                env_charts.draw_dynamic_faculty_bar(df, all_env_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        env_charts.draw_gender_overall_bar(df, [overall_col], gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): 
                        env_charts.draw_clustered_faculty_gender(df, [overall_col], fac_col, gen_col)

            if selected_year.lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        # පරණ Year Analysis ග්‍රාෆ් 2
                        env_additional_charts.draw_year_comparison_bar(cdf, [overall_col], 'Trend_Year')
                        env_additional_charts.draw_clustered_faculty_year(cdf, [overall_col], fac_col, 'Trend_Year')
                        
                        # 🔴 අලුත් ග්‍රාෆ් 2 (Row එකක Columns 2කට කඩලා දැම්මා)
                        with ui.row().classes('w-full gap-4 mt-6'):
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                env_additional_charts.draw_spaces_year_comparison(cdf, q_ind_work, q_team_work, 'Trend_Year')
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                env_additional_charts.draw_support_year_comparison(cdf, q_academic, q_temp_academic, q_admin, q_senior, 'Trend_Year')