import sqlite3
import pandas as pd
from nicegui import ui
import st_sa.main_charts as main_charts
import st_sa.main_additional as main_additional

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
    eth_col = find_col('what is your ethnicity')
    fgen_col = find_col('first-generation student')
    
    # Base columns
    learn_col = find_col('overall assessment of the learning environment')
    lib_col = find_col('overall assessment of the library services')
    it_col = find_col('overall assessment of the it facilities')
    can_col = find_col('overall assessment of the canteen facilities')
    wash_col = find_col('overall assessment of the washroom facilities')
    base_cols = [c for c in [learn_col, lib_col, it_col, can_col, wash_col] if c != 'NOT FOUND']

    # Conditional columns
    sp_cond = find_col('involved in sports')
    sp_over = find_col('overall assessment of the sports facilities')
    ho_cond = find_col('stay in hostels')
    ho_over = find_col('overall assessment of the hostel facility')
    med_cond = find_col('service from the medical center')
    med_over = find_col('overall assessment of the medical centre')
    
    cond_cols = []
    if sp_cond != 'NOT FOUND' and sp_over != 'NOT FOUND': cond_cols.append((sp_cond, sp_over))
    if ho_cond != 'NOT FOUND' and ho_over != 'NOT FOUND': cond_cols.append((ho_cond, ho_over))
    if med_cond != 'NOT FOUND' and med_over != 'NOT FOUND': cond_cols.append((med_cond, med_over))

    # Special Needs
    sn_col = find_col('student with special needs')
    sn_q1 = find_col('accessibility of university buildings')
    sn_q2 = find_col('convenience of transportation options')
    sn_q3 = find_col('classroom environments, including access')
    sn_q4 = find_col('availability and quality of assistive technology')
    sn_q5 = find_col('effectiveness of university-provided disability')
    sn_q6 = find_col('attention to your special needs')
    sn_q7 = find_col('awareness and sensitivity of academic staff')
    sn_q8 = find_col("overall satisfaction with the university's efforts")
    
    sn_q_cols = [c for c in [sn_q1, sn_q2, sn_q3, sn_q4, sn_q5, sn_q6, sn_q7, sn_q8] if c != 'NOT FOUND']

    df = main_charts.prepare_composite_overall(df, base_cols, cond_cols)

    with ui.column().classes('w-full gap-4 p-2'):
        ui.label('University Student Satisfaction Dashboard - Home').classes('text-3xl font-bold text-[#0b1132] mb-2')
        with ui.tabs().classes('w-full border-b text-[#3B82F6]') as tabs:
            t_ov = ui.tab('Overview', icon='dashboard')
            t_ge = ui.tab('Gender Analysis', icon='wc')
            t_sn = ui.tab('Disabilities Analysis', icon='accessible')
            if selected_year.lower() == 'all': t_yr = ui.tab('Year Analysis', icon='timeline')

        with ui.tab_panels(tabs, value=t_ov).classes('w-full bg-transparent p-0'):
            # TAB 1: OVERVIEW
            with ui.tab_panel(t_ov).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_overall_satisfaction_donut(df)
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_overall_faculty_bar(df, fac_col)
                
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_first_gen_gauge(df, fgen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_ethnicity_pie(df, eth_col)
            
            # TAB 2: GENDER
            with ui.tab_panel(t_ge).classes('w-full p-0 gap-6'):
                main_charts.draw_gender_distribution(df, gen_col)
                with ui.row().classes('w-full gap-4 mt-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_gender_overall_bar(df, gen_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_clustered_faculty_gender(df, fac_col, gen_col)

            # TAB 3: SPECIAL NEEDS
            with ui.tab_panel(t_sn).classes('w-full p-0 gap-6'):
                with ui.row().classes('w-full gap-4'):
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_special_needs_gauge(df, sn_col)
                    with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_special_needs_faculty_count_bar(df, sn_col, fac_col)
                
                sn_df = main_charts.get_special_needs_composite(df, sn_col, sn_q_cols)
                if not sn_df.empty:
                    with ui.row().classes('w-full gap-4 mt-4'):
                        with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_special_needs_satisfaction_donut(sn_df)
                        with ui.column().classes('flex-1 min-w-[300px]'): main_charts.draw_special_needs_faculty_sat_bar(sn_df, fac_col)
                    
                    ui.label('Key Indicators (Special Needs Support)').classes('font-bold text-xl text-[#0b1132] mt-6')
                    
                    # 🔴 මෙතන තමයි CSV එකේ තියෙන සිංහල අකුරු සහිත සම්පූර්ණ ප්‍රශ්න 8 එකතු කළේ
                    main_charts.draw_special_needs_kpi_boxes(sn_df, {
                        'Accessibility of university buildings, including ramps, elevators, and restrooms (බෑවුම්, විදුලි සෝපාන සහ විවේකාගාර ඇතුළු විශ්වවිද්‍යාල ගොඩනැගිලිවලට ප්‍රවේශ වීමේ හැකියාව):': sn_q1,
                        'Accessibility and convenience of transportation options and parking spaces (ප්‍රවාහන විකල්ප සහ වාහන නැවැත්වීමේ ඉඩ ප්‍රවේශය සහ පහසුව):': sn_q2,
                        'Classroom environments, including access to lecture materials and seating arrangements (ඉගෙනුම් ආධාරක සඳහා ප්‍රවේශය සහ ආසන සැකසීම ඇතුළුව පන්ති කාමර පරිසරයන්):': sn_q3,
                        'Availability and quality of assistive technology such as screen readers and note-taking software (තිර කියවන සහ සටහන් ගැනීමේ මෘදුකාංග වැනි උපකාරක තාක්ෂණය ඇති බව සහ එහි ගුණාත්මකභාවය):': sn_q4,
                        'Effectiveness of university-provided disability support services such as counseling and academic accommodations (විශ්වවිද්‍යාලය විසින් සපයනු ලබන උපදේශන සහ අධ්‍යයන කාමර වැනි ආබාධිත ආධාර සේවා වල ඵලදායී බව):': sn_q5,
                        'University staff\'s attention to your special needs (ඔබේ විශේෂ අවශ්‍යතා කෙරෙහි විශ්වවිද්‍යාල කාර්ය මණ්ඩලය දක්වන අවධානය):': sn_q6,
                        'Awareness and sensitivity of academic staff regarding your special needs (ඔබේ විශේෂ අවශ්‍යතා සම්බන්ධයෙන් අධ්‍යයන කාර්ය මණ්ඩලයේ දැනුවත්භාවය සහ සංවේදීතාව):': sn_q7,
                        'Your overall satisfaction with the University\'s efforts to support and accommodate your needs as a student with special needs (විශේෂ අවශ්‍යතා සහිත ශිෂ්‍යයෙකු ලෙස ඔබගේ අවශ්‍යතා සඳහා සහය දැක්වීමට සහ ඒවාට පහසුකම් සැලසීමට විශ්වවිද්‍යාලය දරන උත්සාහයන් පිළිබඳව ඔබේ සමස්ත තෘප්තිය):': sn_q8
                    })

            # TAB 4: YEAR ANALYSIS
            if selected_year.lower() == 'all':
                with ui.tab_panel(t_yr).classes('w-full p-0 gap-6'):
                    cdf = get_combined_trend_data()
                    if not cdf.empty:
                        cdf = main_additional.prepare_trend_data(cdf, base_cols, cond_cols)
                        with ui.row().classes('w-full gap-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'): main_additional.draw_overall_trend_line(cdf)
                            with ui.column().classes('flex-1 min-w-[300px]'): main_additional.draw_faculty_trend_bar(cdf, fac_col)
                        with ui.row().classes('w-full gap-4 mt-4'):
                            with ui.column().classes('flex-1 min-w-[300px]'): main_additional.draw_gender_trend_line(cdf, gen_col)
                            with ui.column().classes('flex-1 min-w-[300px]'): main_additional.draw_first_gen_trend_line(cdf, fgen_col)