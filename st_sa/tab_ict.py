import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.it_charts as it_charts
import st_sa.it_additional_charts as it_additional_charts

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
    
    # 🔴 IT ප්‍රශ්න 17 හඳුනාගැනීම
    overall_it_col = find_col('overall assessment of the it facilities')
    q1 = find_col('adequacy of computer labs')
    q2 = find_col('adequacy of computers in the main it centre')
    q3 = find_col('adequacy of computers in the faculty')
    q4 = find_col('performance of computers in computer labs')
    q5 = find_col('available software')
    q6 = find_col('opportunities to learn and use computers')
    q7 = find_col('allocated time period per day for students')
    q8 = find_col('facilities provided for the students to store their data')
    q9 = find_col('internet facility provided by the university')
    # 🔴 Wi-Fi සඳහා 'wi-fi facility' keyword එක පාවිච්චි කරමු (Student Satisfaction 2023 CSV එකේ තියෙන විදිහට)
    q10 = find_col('wi-fi facility provided by the university')
    q11 = find_col('adequacy of phone charging ports')
    q12 = find_col('adequacy of laptop charging ports')
    q13 = find_col('email service provided by the university')
    q14 = find_col('learning management system')
    q15 = find_col('assistance of the technical officers')
    q16 = find_col('knowledge and skill level of computer lab staff')

    # 🔴 සම්පූර්ණ ප්‍රශ්න 17ම Dropdown එක සඳහා
    all_it_questions = {
        'What is your overall assessment of the IT facilities in the university (විශ්වවිද්‍යාලයේ තොරතුරු තාක්ෂණ පහසුකම් පිළිබඳ ඔබගේ සමස්ත තක්සේරුව කුමක්ද):': overall_it_col,
        'Adequacy of computer labs (පරිගණක විද්‍යාගාරවල ප්‍රමාණවත් බව):': q1,
        'Adequacy of computers in the main IT Centre computer labs (ප්‍රධාන තොරතුරු තාක්ෂණ මධ්‍යස්ථානයේ පරිගණක විද්‍යාගාරවල පරිගණක ප්‍රමාණවත් වීම):': q2,
        'Adequacy of computers in the faculty computer labs (පීඨයේ පරිගණක විද්‍යාගාරවල ඇති පරිගණක ප්‍රමාණවත් බව):': q3,
        'Performance of computers in computer labs in the University (විශ්වවිද්‍යාලයේ පරිගණක විද්‍යාගාරවල පරිගණක ක්‍රියාකාරීත්වය):': q4,
        'Available software (Windows, MS-Office, ect.) installed in the computers (පවතින මෘදුකාංග (Windows, MS-Office, ect.) පරිගණක තුළ ස්ථාපනය කර ඇත):': q5,
        'Opportunities to learn and use computers (පරිගණක ඉගෙනීමට සහ භාවිතා කිරීමට ඇති අවස්ථා):': q6,
        'Allocated time period per day for students for working in IT labs in the University (opened hours) (විශ්වවිද්‍යාලයේ තොරතුරු තාක්ෂණ විද්‍යාගාරවල වැඩ කිරීම සඳහා සිසුන් සඳහා දිනකට වෙන් කර ඇති කාල සීමාව (විවෘත වේලාවන්)):': q7,
        'Facilities provided for the students to store their data in University server (සිසුන්ට තම දත්ත විශ්ව විද්‍යාල සේවාදායකයේ ගබඩා කිරීමට පහසුකම් සපයා ඇත):': q8,
        'Internet facility provided by the University (විශ්වවිද්‍යාලය විසින් සපයනු ලබන අන්තර්ජාල පහසුකම්):': q9,
        'Wi-Fi facility provided by the University (විශ්වවිද්‍යාලය විසින් සපයනු ලබන Wi-Fi පහසුකම):': q10,
        'Adequacy of phone charging ports (දුරකථන ආරෝපණ පේනු ප්‍රමාණවත් වීම):': q11,
        'Adequacy of laptop charging ports (ලැප්ටොප් ආරෝපණ පේනු ප්‍රමාණවත් වීම):': q12,
        'Email service provided by the University (විශ්වවිද්‍යාලය විසින් සපයනු ලබන විද්‍යුත් තැපැල් සේවාව):': q13,
        'Learning Management System (LMS) service provided by the University (විශ්වවිද්‍යාලය විසින් සපයනු ලබන ඉගෙනුම් කළමනාකරණ පද්ධතිය (LMS) සේවාව):': q14,
        'Assistance of the technical officers in computer labs (පරිගණක විද්‍යාගාරවල තාක්ෂණික නිලධාරීන්ගේ සහාය):': q15,
        'Knowledge and skill level of computer lab staff (පරිගණක විද්‍යාගාර කාර්ය මණ්ඩලයේ දැනුම සහ කුසලතා මට්ටම):': q16
    }

    # 🔴 KPI කොටු සඳහා 'Overall' එක හැර ඉතිරි ප්‍රශ්න 16
    quick_stats_questions = {k: v for k, v in all_it_questions.items() if v != overall_it_col}

    # Gender Analysis සඳහා ප්‍රශ්න ඔක්කොම
    all_it_cols = list(all_it_questions.values())

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('Welcome to University Computer Lab Facilities').classes('text-3xl font-bold text-[#0b1132] mb-2')
        
        with ui.tabs().classes('w-full text-[#3B82F6] border-b') as tabs:
            t_ov = ui.tab('Overview', icon='pie_chart')
            t_fa = ui.tab('Faculty Analysis', icon='bar_chart')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            if selected_year.strip().lower() == 'all':
                t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        it_charts.draw_overall_satisfaction_donut(df, overall_it_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        it_charts.draw_overall_faculty_col(df, overall_it_col, fac_col)
                
                ui.label('Key Performance Indicators').classes('font-bold text-xl text-[#0b1132] mt-4')
                # 🔴 ප්‍රශ්න 16ම පෙන්වන KPI කොටු
                it_charts.draw_quick_stats_boxes(df, quick_stats_questions)

            with ui.tab_panel(t_fa).classes('w-full p-0'):
                with ui.card().classes('w-full p-0 shadow-none bg-transparent'): 
                    # 🔴 Dropdown එකට ප්‍රශ්න 17ම යනවා
                    it_charts.draw_dynamic_faculty_bar(df, all_it_questions, fac_col)
            
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                 with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        it_charts.draw_gender_overall_bar(df, all_it_cols, gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'):
                        it_charts.draw_clustered_faculty_gender(df, all_it_cols, fac_col, gen_col)

            if selected_year.strip().lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                it_additional_charts.draw_year_comparison_bar(cdf, [overall_it_col], 'Trend_Year')
                            with ui.column().classes('flex-1 min-w-[300px]'):
                                it_additional_charts.draw_clustered_faculty_year(cdf, [overall_it_col], fac_col, 'Trend_Year')