from nicegui import ui
import pandas as pd

SCORE_MAP = {
    'Very Good': 5, 'Good': 4, 'Neither good nor poor': 3, 'Poor': 2, 'Very Poor': 1,
    'Very good': 5, 'Very poor': 1, 
    'ඉතා හොඳයි': 5, 'හොඳයි': 4, 'හොඳ හෝ නරක නොවේ': 3, 'නරකයි': 2, 'ඉතා නරකයි': 1
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
    if col not in df.columns: return 0.0
    temp = df.copy()
    temp['score'] = temp[col].map(SCORE_MAP).dropna()
    if temp['score'].empty: return 0.0
    return round(temp['score'].mean() / 5 * 100, 1)

def _get_multi_pct_with_count(df, cols_list, group_col1=None, group_col2=None):
    valid_cols = [c for c in cols_list if c in df.columns]
    if not valid_cols: return {}
    temp = df.copy()
    for c in valid_cols:
        temp[c] = temp[c].map(SCORE_MAP)
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

def draw_canteen_usage_pie(df, usage_col):
    if usage_col not in df.columns: return
    usage_counts = df[usage_col].value_counts().to_dict()
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#F97316', '#64748B']
    data = [{'value': v, 'name': str(k).split('(')[0].strip(), 'itemStyle': {'color': colors[i % len(colors)]}} for i, (k, v) in enumerate(usage_counts.items())]
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Mostly Used Canteen by Students').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.value+"</b> ("+p.percent+"%)"}'},
            'legend': {'show': True, 'orient': 'horizontal', 'bottom': 0, 'type': 'scroll'}, 
            'series': [{'type': 'pie', 'radius': ['30%', '50%'], 'center': ['50%', '45%'], 'avoidLabelOverlap': True, 'minAngle': 5, 'data': data, 'label': {'show': True, 'formatter': '{b}\n{c} ({d}%)', 'fontWeight': 'bold', 'fontSize': 12, 'color': '#374151'}, 'labelLine': {'show': True, 'length': 20, 'length2': 30, 'smooth': True}}]
        }).classes('w-full h-[450px]')

def draw_overall_satisfaction_donut(df, col_name):
    if col_name not in df.columns: return
    counts = df[col_name].value_counts().to_dict()
    custom_colors = {'Very Good': '#10B981', 'ඉතා හොඳයි': '#10B981', 'Good': '#34D399', 'හොඳයි': '#34D399', 'Neither good nor poor': '#FBBF24', 'හොඳ හෝ නරක නොවේ': '#FBBF24', 'Poor': '#F87171', 'නරකයි': '#F87171', 'Very Poor': '#DC2626', 'ඉතා නරකයි': '#DC2626', 'Very poor': '#DC2626'}
    data = [{'value': v, 'name': str(k).strip(), 'itemStyle': {'color': custom_colors.get(str(k).strip(), '#9CA3AF')}} for k, v in counts.items()]
    pct = _get_single_pct(df, col_name)

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall satisfaction of Canteen facilities').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'title': {'text': f'{pct}%', 'subtext': 'Overall Score', 'left': 'center', 'top': '40%', 'textStyle': {'fontSize': 24, 'fontWeight': 'bold', 'color': '#1F2937'}, 'subtextStyle': {'fontSize': 10, 'color': '#6B7280'}},
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.value+"</b> ("+p.percent+"%)"}'},
            'legend': {'show': True, 'orient': 'horizontal', 'bottom': 0, 'type': 'scroll', 'textStyle': {'fontSize': 11}}, 
            'series': [{'type': 'pie', 'radius': ['40%', '60%'], 'center': ['50%', '45%'], 'avoidLabelOverlap': True, 'minAngle': 5, 'data': data, 'label': {'show': True, 'position': 'outside', 'formatter': '{b}\n{c} ({d}%)', 'fontWeight': 'bold', 'fontSize': 11, 'color': '#374151'}, 'labelLine': {'show': True, 'length': 15, 'length2': 20, 'smooth': True}}]
        }).classes('w-full h-[450px]') 

def draw_overall_faculty_col(df, col_name, fac_col):
    data = _get_multi_pct_with_count(df, [col_name], fac_col)
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    y_vals = [{'value': next((v['pct'] for k, v in data.items() if _get_faculty_short(k) == f), 0), 'name': f, 'count_val': next((v['count'] for k, v in data.items() if _get_faculty_short(k) == f), 0), 'itemStyle': {'color': COLOR_MAP[f], 'borderRadius': [3,3,0,0]}} for f in target_facs]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall satisfaction in faculty wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': target_facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'max': 100},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '50%', 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[280px]')

def draw_dynamic_faculty_bar(df, questions_dict, fac_col):
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Satisfaction of Canteen Facilities by faculty wise').classes('font-bold text-xl text-[#0b1132] mb-4')
        q_select = ui.select(options=list(questions_dict.keys()), value=list(questions_dict.keys())[0]).classes('w-full mb-4').props('outlined dense')
        chart_cont = ui.column().classes('w-full h-80')
        def render():
            chart_cont.clear()
            with chart_cont:
                q_col = questions_dict[q_select.value]
                data = _get_multi_pct_with_count(df, [q_col], fac_col)
                target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
                y_vals = [{'value': next((v['pct'] for k, v in data.items() if _get_faculty_short(k) == f), 0), 'name': f, 'count_val': next((v['count'] for k, v in data.items() if _get_faculty_short(k) == f), 0), 'itemStyle': {'color': COLOR_MAP[f], 'borderRadius': [3,3,0,0]}} for f in target_facs]
                ui.echart({
                    'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
                    'xAxis': {'type': 'category', 'data': target_facs, 'axisLabel': {'fontWeight': 'bold'}},
                    'yAxis': {'max': 100},
                    'series': [{'data': y_vals, 'type': 'bar', 'label': {'show': True, 'formatter': '{c}%', 'position': 'top'}}]
                }).classes('w-full h-full')
        q_select.on_value_change(render); render()

def draw_quick_stats_boxes(df, questions_dict):
    with ui.row().classes('w-full gap-3 flex-wrap justify-center'):
        for name, col in questions_dict.items():
            pct = _get_single_pct(df, col)
            with ui.card().classes('flex-1 min-w-[300px] max-w-[400px] p-4 text-center shadow-sm border rounded-xl bg-white'):
                ui.label(name).classes('text-[11px] font-bold text-gray-600 min-h-12')
                ui.label(f'{pct}%').classes('text-3xl font-black text-[#3B82F6] mt-2')

def draw_gender_overall_bar(df, all_cols, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, gender_col)
    y_vals = [{'value': next((v['pct'] for k, v in data.items() if str(k).strip().title() == g), 0), 'name': g, 'count_val': next((v['count'] for k, v in data.items() if str(k).strip().title() == g), 0), 'itemStyle': {'color': '#3B82F6' if g=='Male' else '#E91E63', 'borderRadius': [3,3,0,0]}} for g in ['Male', 'Female']]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall satisfaction').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Count: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': ['Male', 'Female']},
            'yAxis': {'max': 100},
            'series': [{'type': 'bar', 'barWidth': '40%', 'data': y_vals, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[280px]')

def draw_clustered_faculty_gender(df, all_cols, fac_col, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, fac_col, gender_col)
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    m_data = [{'value': next((v['pct'] for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Male'), 0), 'name': f, 'count_val': next((v['count'] for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Male'), 0)} for f in target_facs]
    f_data = [{'value': next((v['pct'] for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Female'), 0), 'name': f, 'count_val': next((v['count'] for k, v in data.items() if _get_faculty_short(k[0]) == f and str(k[1]).strip().title() == 'Female'), 0)} for f in target_facs]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall satisfaction in faculty wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'color': ['#3B82F6', '#E91E63'],
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Count: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': ['Male', 'Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': target_facs},
            'yAxis': {'max': 100},
            'series': [{'name': 'Male', 'type': 'bar', 'data': m_data}, {'name': 'Female', 'type': 'bar', 'data': f_data}]
        }).classes('w-full h-[280px]')