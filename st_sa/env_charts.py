from nicegui import ui
import pandas as pd

SCORE_MAP = {
    'Very Good': 5, 'Good': 4, 'Neither good nor poor': 3, 'Poor': 2, 'Very Poor': 1,
    'Very good': 5, 'Very poor': 1, 'Neither Good nor Poor': 3,
    'ඉතා හොඳයි': 5, 'හොඳයි': 4, 'හොඳ හෝ නරක නොවේ': 3, 'නරකයි': 2, 'ඉතා නරකයි': 1,
    'Totally agree': 5, 'Somewhat agree': 4, 'Neither disagree nor agree': 3, 'Somewhat disagree': 2, 'somewhat disagree': 2, 'Totally disagree': 1
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

def _get_single_pct(df, col):
    if col not in df.columns or df.empty: return 0.0
    temp = df.copy()
    temp['score'] = temp[col].map(SCORE_MAP)
    valid_scores = temp['score'].dropna()
    return round(valid_scores.mean() / 5 * 100, 1) if not valid_scores.empty else 0.0

def _get_multi_pct_with_count(df, cols_list, group_col1=None, group_col2=None):
    valid_cols = [c for c in cols_list if c in df.columns]
    if not valid_cols or df.empty: return {}
    temp = df.copy()
    for c in valid_cols: temp[c] = temp[c].map(SCORE_MAP)
    temp['total'] = temp[valid_cols].sum(axis=1)
    temp['max'] = temp[valid_cols].notna().sum(axis=1) * 5
    temp = temp[temp['max'] > 0]
    if temp.empty: return {}
    temp['pct'] = (temp['total'] / temp['max']) * 100
    if group_col1 and group_col2:
        grouped = temp.groupby([group_col1, group_col2])['pct'].agg(['mean', 'count'])
        return {k: {'pct': round(v['mean'], 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    elif group_col1:
        grouped = temp.groupby(group_col1)['pct'].agg(['mean', 'count'])
        return {k: {'pct': round(v['mean'], 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    return {}

def draw_overall_satisfaction_gauge_only(df, col_name):
    if col_name not in df.columns or df.empty: return
    
    counts = df[col_name].value_counts().to_dict()
    pct = _get_single_pct(df, col_name)
    
    custom_colors = {
        'Totally agree': '#10B981', 'Very Good': '#10B981', 'Very good': '#10B981', 'ඉතා හොඳයි': '#10B981',
        'Somewhat agree': '#34D399', 'Good': '#34D399', 'හොඳයි': '#34D399',
        'Neither disagree nor agree': '#FBBF24', 'Neither good nor poor': '#FBBF24', 'Neither Good nor Poor': '#FBBF24', 'හොඳ හෝ නරක නොවේ': '#FBBF24',
        'somewhat disagree': '#F87171', 'Somewhat disagree': '#F87171', 'Poor': '#F87171', 'නරකයි': '#F87171',
        'Totally disagree': '#DC2626', 'Very Poor': '#DC2626', 'Very poor': '#DC2626', 'ඉතා නරකයි': '#DC2626'
    }
    
    data = []
    for k, v in counts.items():
        color = custom_colors.get(str(k).strip(), '#3B82F6')
        data.append({'value': v, 'name': str(k).strip(), 'itemStyle': {'color': color}})
        
    ui.echart({
        'title': {
            'text': f'{pct}%',
            'subtext': 'Overall Score',
            'left': 'center',
            'top': 'center',
            'textStyle': {'fontSize': 26, 'fontWeight': 'bold', 'color': '#1F2937'},
            'subtextStyle': {'fontSize': 11, 'color': '#6B7280'}
        },
        'tooltip': {
            'trigger': 'item', 
            ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.value+"</b> ("+p.percent+"%)"}'
        },
        'series': [{
            'type': 'pie',
            'radius': ['55%', '80%'],
            'center': ['50%', '50%'],
            'avoidLabelOverlap': True,
            'itemStyle': {
                'borderRadius': 4,
                'borderColor': '#fff',
                'borderWidth': 2
            },
            'label': {
                'show': True,
                'position': 'outside',
                'formatter': '{b}\nStudents: {c}',
                'fontSize': 10,
                'fontWeight': 'bold',
                'color': '#4B5563'
            },
            'labelLine': {
                'show': True,
                'length': 10,
                'length2': 15,
                'smooth': True
            },
            'data': data
        }]
    }).classes('w-full h-[320px]')

def draw_overall_faculty_bar_only(df, col_name, fac_col):
    data = _get_multi_pct_with_count(df, [col_name], fac_col)
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    active_facs = [f for f in all_facs if any(_get_faculty_short(k) == f for k in data.keys())]
    
    y_vals = []
    for f in active_facs:
        match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
        y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count'], 'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [4,4,0,0]}})

    ui.echart({
        'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
        'xAxis': {'type': 'category', 'data': active_facs, 'axisLabel': {'fontSize': 10, 'fontWeight': 'bold'}},
        'yAxis': {'type': 'value', 'max': 100},
        'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%', 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
    }).classes('w-full h-[320px]')

def draw_dynamic_faculty_bar(df, questions_dict, fac_col):
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Satisfaction of Learning Environment by Faculty').classes('font-bold text-xl text-[#0b1132] mb-4')
        q_select = ui.select(options=list(questions_dict.keys()), value=list(questions_dict.keys())[0]).classes('w-full mb-4')
        chart_cont = ui.column().classes('w-full h-[300px]')
        def update():
            chart_cont.clear()
            with chart_cont:
                q_col = questions_dict[q_select.value]
                data = _get_multi_pct_with_count(df, [q_col], fac_col)
                all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
                active_facs = [f for f in all_facs if any(_get_faculty_short(k) == f for k in data.keys())]
                
                y_vals = []
                for f in active_facs:
                    match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
                    y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count']})
                
                ui.echart({
                    'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
                    'xAxis': {'type': 'category', 'data': active_facs, 'axisLabel': {'fontWeight': 'bold'}},
                    'yAxis': {'max': 100},
                    'series': [{'data': y_vals, 'type': 'bar', 'itemStyle': {'color': '#3B82F6'}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
                }).classes('w-full h-full')
        q_select.on_value_change(update); update()

def draw_quick_stats_boxes(df, questions_dict):
    with ui.row().classes('w-full gap-3 flex-wrap justify-center'):
        for name, col in questions_dict.items():
            pct = _get_single_pct(df, col)
            with ui.card().classes('flex-1 min-w-[400px] max-w-[500px] p-3 text-center shadow-sm border rounded-xl'):
                ui.label(name).classes('text-[11px] font-bold text-gray-500 uppercase h-10 line-clamp-2')
                ui.label(f'{pct}%').classes('text-3xl font-black text-[#3B82F6] mt-2')

def draw_gender_overall_bar(df, all_cols, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, gender_col)
    y_vals = []
    genders = ['Male', 'Female']
    for g in genders:
        m = next((v for k, v in data.items() if str(k).strip().title() == g), {'pct': 0, 'count': 0})
        y_vals.append({'value': m['pct'], 'name': g, 'count_val': m['count']})
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall satisfaction').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': genders},
            'yAxis': {'max': 100},
            'series': [{'type': 'bar', 'barWidth': '40%', 'data': y_vals, 'itemStyle': {'color': '#3B82F6'}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[280px]')

def draw_clustered_faculty_gender(df, all_cols, fac_col, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, fac_col, gender_col)
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    active_facs = [f for f in target_facs if any(_get_faculty_short(k[0]) == f for k in data.keys() if isinstance(k, tuple))]
    
    m_data = []
    f_data = []
    for f in active_facs:
        m_match = next((v for k, v in data.items() if isinstance(k, tuple) and _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Male'), {'pct': 0, 'count': 0})
        f_match = next((v for k, v in data.items() if isinstance(k, tuple) and _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Female'), {'pct': 0, 'count': 0})
        m_data.append({'value': m_match['pct'], 'count_val': m_match['count']})
        f_data.append({'value': f_match['pct'], 'count_val': f_match['count']})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Satisfaction by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'color': ['#3B82F6', '#E91E63'],
            'legend': {'data': ['Male', 'Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': active_facs},
            'yAxis': {'max': 100},
            'series': [
                {'name': 'Male', 'type': 'bar', 'data': m_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}},
                {'name': 'Female', 'type': 'bar', 'data': f_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}
            ]
        }).classes('w-full h-[280px]')