from nicegui import ui
import pandas as pd
import numpy as np

SCORE_MAP = {
    'Totally agree': 5, 'Very Good': 5, 'Very good': 5, 'ඉතා හොඳයි': 5,
    'Somewhat agree': 4, 'Good': 4, 'හොඳයි': 4,
    'Neither disagree nor agree': 3, 'Neither good nor poor': 3, 'Neither Good nor Poor': 3, 'හොඳ හෝ නරක නොවේ': 3,
    'somewhat disagree': 2, 'Somewhat disagree': 2, 'Poor': 2, 'නරකයි': 2,
    'Totally disagree': 1, 'Very Poor': 1, 'Very poor': 1, 'ඉතා නරකයි': 1
}

COLOR_MAP = {
    'FCMS': '#E81E29', 'FCT': '#F05323', 'FHU': '#3A7B43',
    'FMED': '#2F97BB', 'FSC': '#2B3A89', 'FSS': '#5A2F83'
}

def _get_faculty_short(fac_str):
    fac_str = str(fac_str).lower()
    if 'commerce' in fac_str or 'fcms' in fac_str: return 'FCMS'
    if 'computing' in fac_str or 'fct' in fac_str: return 'FCT'
    if 'humanities' in fac_str or 'fhu' in fac_str: return 'FHU'
    if 'medicine' in fac_str or 'fmed' in fac_str: return 'FMED'
    if 'science' in fac_str and 'social' not in fac_str: return 'FSC'
    if 'social' in fac_str or 'fss' in fac_str: return 'FSS'
    return 'Other'

def prepare_composite_overall(df, base_cols, cond_cols):
    if df.empty: return df
    
    def calc_row(row):
        scores = []
        for c in base_cols:
            if c in row and pd.notna(row[c]):
                val = SCORE_MAP.get(str(row[c]).strip())
                if val: scores.append(val)
                
        for cond_c, val_c in cond_cols:
            if cond_c in row and val_c in row:
                if str(row[cond_c]).strip().lower() == 'yes':
                    if pd.notna(row[val_c]):
                        val = SCORE_MAP.get(str(row[val_c]).strip())
                        if val: scores.append(val)
        
        if not scores: return np.nan
        return sum(scores) / len(scores)

    df['Composite_Score'] = df.apply(calc_row, axis=1)
    
    def map_category(score):
        if pd.isna(score): return np.nan
        score = round(score)
        if score == 5: return 'Very Good'
        elif score == 4: return 'Good'
        elif score == 3: return 'Neither good nor poor'
        elif score == 2: return 'Poor'
        else: return 'Very Poor'
        
    df['Composite_Category'] = df['Composite_Score'].apply(map_category)
    return df

def draw_overall_satisfaction_donut(df):
    counts = df['Composite_Category'].dropna().value_counts().to_dict()
    if not counts: return
    
    overall_pct = round((df['Composite_Score'].dropna().mean() / 5) * 100, 1)
    
    colors = {'Very Good': '#10B981', 'Good': '#34D399', 'Neither good nor poor': '#FBBF24', 'Poor': '#F87171', 'Very Poor': '#DC2626'}
    data = [{'value': v, 'name': k, 'itemStyle': {'color': colors.get(k, '#3B82F6')}} for k, v in counts.items()]
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Overall University Satisfaction').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'title': {'text': f'{overall_pct}%', 'subtext': 'University Score', 'left': 'center', 'top': 'center', 'textStyle': {'fontSize': 28, 'fontWeight': 'bold', 'color': '#1F2937'}, 'subtextStyle': {'fontSize': 12, 'color': '#6B7280'}},
            'tooltip': {'trigger': 'item', ':formatter': "function(p){return p.marker+\" <b style='font-size:13px;'>\"+p.name+\"</b><br/>Students: <b>\"+p.value+\"</b> (\"+p.percent+\")%\"}"},
            'series': [{
                'type': 'pie', 'radius': ['50%', '75%'], 'center': ['50%', '50%'], 'avoidLabelOverlap': True,
                'itemStyle': {'borderRadius': 4, 'borderColor': '#fff', 'borderWidth': 2},
                'label': {'show': True, 'position': 'outside', 'formatter': '{b}\nStudents: {c}', 'fontSize': 12, 'fontWeight': 'bold', 'color': '#1F2937'},
                'labelLine': {'show': True, 'length': 12, 'length2': 18, 'smooth': True, 'lineStyle': {'width': 1.5}},
                'data': data
            }]
        }).classes('w-full h-[350px]')

def draw_overall_faculty_bar(df, fac_col):
    if 'Composite_Score' not in df.columns: return
    
    grouped = df.dropna(subset=['Composite_Score']).groupby(fac_col)['Composite_Score'].agg(['mean', 'count'])
    data = {k: {'pct': round((v['mean']/5)*100, 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    active_facs = [f for f in all_facs if any(_get_faculty_short(k) == f for k in data.keys())]
    
    y_vals = []
    for f in active_facs:
        match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
        y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count'], 'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [4,4,0,0]}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Overall Satisfaction by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': active_facs, 'axisLabel': {'fontSize': 10, 'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%', 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[350px]')

def draw_first_gen_gauge(df, col_name):
    if col_name not in df.columns or df.empty: return
    counts = df[col_name].value_counts().to_dict()
    yes_count = counts.get('Yes', 0)
    total = sum(counts.values())
    pct = round((yes_count / total * 100), 1) if total > 0 else 0
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col items-center'):
        ui.label('First-Generation Students').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'formatter': '{b} : {c}%'},
            'series': [{
                'type': 'gauge', 'startAngle': 225, 'endAngle': -45, 'min': 0, 'max': 100, 'radius': '90%', 'center': ['50%', '55%'],
                'axisLine': {'lineStyle': {'width': 20, 'color': [[pct/100, '#8B5CF6'], [1, '#EDE9FE']]}},
                'pointer': {'show': True, 'length': '60%', 'width': 6},
                'axisLabel': {'distance': 30, 'color': '#464646', 'fontSize': 10, 'formatter': '{value}%'},
                'detail': {'fontSize': 24, 'offsetCenter': [0, '75%'], 'formatter': '{value}%', 'fontWeight': 'bold'},
                'data': [{'value': pct, 'name': 'First-Gen'}]
            }]
        }).classes('w-full h-[300px]')
        ui.label(f'💡 Total: {yes_count} Students').classes('text-xs text-gray-500 text-center mt-auto pt-2')

def draw_ethnicity_pie(df, col_name):
    if col_name not in df.columns or df.empty: return
    
    counts = df[col_name].dropna().value_counts().to_dict()
    main_ethnicities = ['Sinhala', 'Tamil', 'Moor']
    grouped_counts = {'Sinhala': 0, 'Tamil': 0, 'Moor': 0, 'Other': 0}
    
    for k, v in counts.items():
        matched = False
        for m in main_ethnicities:
            if m.lower() in str(k).lower():
                grouped_counts[m] += v
                matched = True
                break
        if not matched: grouped_counts['Other'] += v
        
    data = []
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#6B7280']
    for i, (k, v) in enumerate(grouped_counts.items()):
        if v > 0: data.append({'name': k, 'value': v, 'itemStyle': {'color': colors[i]}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full'):
        ui.label('Ethnicity Distribution').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'legend': {'bottom': '0%', 'left': 'center'},
            'series': [{
                'type': 'pie', 'radius': '60%', 'center': ['50%', '45%'],
                'label': {'show': True, 'formatter': '{b}\n{c}', 'fontWeight': 'bold'},
                'data': data
            }]
        }).classes('w-full h-[300px]')

def draw_gender_distribution(df, col_name):
    if col_name not in df.columns or df.empty: return
    counts = df[col_name].dropna().value_counts().to_dict()
    data = []
    colors = {'Male': '#3B82F6', 'Female': '#EC4899'}
    for k, v in counts.items():
        gender = str(k).strip().title()
        data.append({'name': gender, 'value': v, 'itemStyle': {'color': colors.get(gender, '#9CA3AF')}})
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Gender Distribution').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'series': [{
                'type': 'pie', 'radius': ['40%', '70%'], 'center': ['50%', '50%'],
                'itemStyle': {'borderRadius': 5, 'borderColor': '#fff', 'borderWidth': 2},
                'label': {'show': True, 'formatter': '{b}\n{d}%', 'fontWeight': 'bold', 'fontSize': 12},
                'data': data
            }]
        }).classes('w-full h-[300px]')

def draw_special_needs_gauge(df, sn_col):
    if sn_col not in df.columns or df.empty: return
    counts = df[sn_col].value_counts().to_dict()
    yes_count = counts.get('Yes', 0)
    total = sum(counts.values())
    pct = round((yes_count / total * 100), 1) if total > 0 else 0
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col items-center'):
        ui.label('Students with Special Needs').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'formatter': '{b} : {c}%'},
            'series': [{
                'type': 'gauge', 'startAngle': 225, 'endAngle': -45, 'min': 0, 'max': 100, 'radius': '90%', 'center': ['50%', '55%'],
                'axisLine': {'lineStyle': {'width': 20, 'color': [[pct/100, '#EAB308'], [1, '#FEF08A']]}},
                'pointer': {'show': True, 'length': '60%', 'width': 6},
                'axisLabel': {'distance': 30, 'color': '#464646', 'fontSize': 10, 'formatter': '{value}%'},
                'detail': {'fontSize': 24, 'offsetCenter': [0, '75%'], 'formatter': '{value}%', 'fontWeight': 'bold'},
                'data': [{'value': pct, 'name': 'Special Needs'}]
            }]
        }).classes('w-full h-[300px]')
        ui.label(f'💡 Total: {yes_count} Students').classes('text-xs text-gray-500 text-center mt-auto pt-2')

def draw_special_needs_faculty_count_bar(df, sn_col, fac_col):
    if sn_col not in df.columns or df.empty: return
    sn_df = df[df[sn_col] == 'Yes']
    counts = sn_df[fac_col].value_counts().to_dict()
    
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    y_vals = []
    active_facs = [f for f in all_facs if any(_get_faculty_short(k) == f for k in counts.keys())]
    
    for f in active_facs:
        count = sum([v for k, v in counts.items() if _get_faculty_short(k) == f])
        y_vals.append({'value': count, 'name': f, 'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [4,4,0,0]}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full'):
        ui.label('Special Needs Students by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'xAxis': {'type': 'category', 'data': active_facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'name': 'Student Count'},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%', 'label': {'show': True, 'position': 'top'}}]
        }).classes('w-full h-[300px]')

def get_special_needs_composite(df, sn_col, q_cols):
    sn_df = df[df[sn_col] == 'Yes'].copy()
    if sn_df.empty: return sn_df
    
    def calc_sn(row):
        scores = [SCORE_MAP.get(str(row[c]).strip()) for c in q_cols if c in row and pd.notna(row[c])]
        scores = [s for s in scores if s]
        return sum(scores)/len(scores) if scores else np.nan
        
    sn_df['SN_Score'] = sn_df.apply(calc_sn, axis=1)
    
    def map_cat(score):
        if pd.isna(score): return np.nan
        score = round(score)
        cats = {5: 'Very Good', 4: 'Good', 3: 'Neither good nor poor', 2: 'Poor', 1: 'Very Poor'}
        return cats.get(score)
        
    sn_df['SN_Category'] = sn_df['SN_Score'].apply(map_cat)
    return sn_df

def draw_special_needs_satisfaction_donut(sn_df):
    if 'SN_Category' not in sn_df.columns or sn_df.empty: return
    counts = sn_df['SN_Category'].dropna().value_counts().to_dict()
    if not counts: return
    pct = round((sn_df['SN_Score'].dropna().mean() / 5) * 100, 1)
    
    colors = {'Very Good': '#10B981', 'Good': '#34D399', 'Neither good nor poor': '#FBBF24', 'Poor': '#F87171', 'Very Poor': '#DC2626'}
    data = [{'value': v, 'name': k, 'itemStyle': {'color': colors.get(k, '#3B82F6')}} for k, v in counts.items()]
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Special Needs Support Satisfaction').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'title': {'text': f'{pct}%', 'subtext': 'Overall Score', 'left': 'center', 'top': 'center', 'textStyle': {'fontSize': 28, 'fontWeight': 'bold', 'color': '#1F2937'}, 'subtextStyle': {'fontSize': 12, 'color': '#6B7280'}},
            'tooltip': {'trigger': 'item', ':formatter': "function(p){return p.marker+\" <b style='font-size:13px;'>\"+p.name+\"</b><br/>Students: <b>\"+p.value+\"</b> (\"+p.percent+\")%\"}"},
            'series': [{
                'type': 'pie', 'radius': ['50%', '75%'], 'center': ['50%', '50%'], 'avoidLabelOverlap': True,
                'itemStyle': {'borderRadius': 4, 'borderColor': '#fff', 'borderWidth': 2},
                'label': {'show': True, 'position': 'outside', 'formatter': '{b}\nStudents: {c}', 'fontSize': 12, 'fontWeight': 'bold', 'color': '#1F2937'},
                'labelLine': {'show': True, 'length': 12, 'length2': 18, 'smooth': True, 'lineStyle': {'width': 1.5}},
                'data': data
            }]
        }).classes('w-full h-[350px]')

def draw_special_needs_faculty_sat_bar(sn_df, fac_col):
    if 'SN_Score' not in sn_df.columns or sn_df.empty: return
    grouped = sn_df.dropna(subset=['SN_Score']).groupby(fac_col)['SN_Score'].agg(['mean', 'count'])
    data = {k: {'pct': round((v['mean']/5)*100, 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    active_facs = [f for f in all_facs if any(_get_faculty_short(k) == f for k in data.keys())]
    
    y_vals = []
    for f in active_facs:
        match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
        y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count'], 'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [4,4,0,0]}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Satisfaction by Faculty (Special Needs)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': active_facs, 'axisLabel': {'fontSize': 10, 'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%', 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[350px]')

def draw_special_needs_kpi_boxes(sn_df, questions_dict):
    def get_sn_pct(col):
        if col not in sn_df.columns or sn_df.empty: return 0.0
        scores = sn_df[col].map(SCORE_MAP).dropna()
        return round(scores.mean() / 5 * 100, 1) if not scores.empty else 0.0

    with ui.row().classes('w-full gap-3 flex-wrap justify-center mt-4'):
        for name, col in questions_dict.items():
            pct = get_sn_pct(col)
            with ui.card().classes('flex-1 min-w-[400px] max-w-[500px] p-3 text-center shadow-sm border rounded-xl bg-gray-50'):
                ui.label(name).classes('text-[10px] font-bold text-gray-500 uppercase h-10 line-clamp-2')
                ui.label(f'{pct}%').classes('text-2xl font-black text-[#EAB308] mt-2')

def draw_gender_overall_bar(df, gender_col):
    if 'Composite_Score' not in df.columns: return
    grouped = df.dropna(subset=['Composite_Score']).groupby(gender_col)['Composite_Score'].agg(['mean', 'count'])
    y_vals = []
    genders = ['Male', 'Female']
    for g in genders:
        match = next((v for k, v in grouped.iterrows() if str(k).strip().title() == g), None)
        if match is not None:
            y_vals.append({'value': round((match['mean']/5)*100, 1), 'name': g, 'count_val': int(match['count'])})
        else:
            y_vals.append({'value': 0, 'name': g, 'count_val': 0})
            
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall Satisfaction').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': genders},
            'yAxis': {'max': 100},
            'series': [{'type': 'bar', 'barWidth': '40%', 'data': y_vals, 'itemStyle': {'color': '#3B82F6'}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[350px]')

def draw_clustered_faculty_gender(df, fac_col, gender_col):
    if 'Composite_Score' not in df.columns: return
    grouped = df.dropna(subset=['Composite_Score']).groupby([fac_col, gender_col])['Composite_Score'].agg(['mean', 'count'])
    data = {k: {'pct': round((v['mean']/5)*100, 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    active_facs = [f for f in target_facs if any(_get_faculty_short(k[0]) == f for k in data.keys())]
    
    m_data, f_data = [], []
    for f in active_facs:
        m_match = next((v for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Male'), {'pct': 0, 'count': 0})
        f_match = next((v for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Female'), {'pct': 0, 'count': 0})
        m_data.append({'value': m_match['pct'], 'count_val': m_match['count']})
        f_data.append({'value': f_match['pct'], 'count_val': f_match['count']})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col mt-4'):
        ui.label('Gender-wise Satisfaction by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'color': ['#3B82F6', '#EC4899'],
            'legend': {'data': ['Male', 'Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': active_facs},
            'yAxis': {'max': 100},
            'series': [
                {'name': 'Male', 'type': 'bar', 'data': m_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}},
                {'name': 'Female', 'type': 'bar', 'data': f_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}
            ]
        }).classes('w-full h-[350px]')