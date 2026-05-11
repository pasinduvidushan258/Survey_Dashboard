from nicegui import ui
import pandas as pd

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
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

# ==========================================
# 2. CHART FUNCTIONS
# ==========================================

def draw_overall_satisfaction_gauge(df, col_name):
    if col_name not in df.columns: return
    
    pct = _get_single_pct(df, col_name)

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall assessment of the Medical Centre').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'series': [
                {
                    'type': 'gauge',
                    'startAngle': 180,
                    'endAngle': 0,
                    'min': 0,
                    'max': 100,
                    'splitNumber': 2,
                    'axisLine': {
                        'lineStyle': {
                            'width': 30,
                            'color': [
                                [pct / 100, '#14B8A6'], 
                                [1, '#FFE4E6']          
                            ]
                        }
                    },
                    'pointer': {
                        'icon': 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
                        'length': '12%',
                        'width': 20,
                        'offsetCenter': [0, '-60%'],
                        'itemStyle': {
                            'color': '#F43F5E' 
                        }
                    },
                    'axisTick': {
                        'length': 12,
                        'lineStyle': {'color': 'auto', 'width': 2}
                    },
                    'splitLine': {
                        'length': 20,
                        'lineStyle': {'color': 'auto', 'width': 5}
                    },
                    'axisLabel': {
                        'color': '#464646',
                        'fontSize': 14,
                        'distance': -40,
                        'formatter': '{value}%' 
                    },
                    'detail': {
                        'fontSize': 40,
                        'offsetCenter': [0, '15%'],
                        'valueAnimation': True,
                        'formatter': '{value}%',
                        'color': '#1F2937',
                        'fontWeight': 'bold'
                    },
                    'data': [{'value': pct, 'name': 'Overall Score'}],
                    'title': {
                        'offsetCenter': [0, '-25%'],
                        'fontSize': 14,
                        'color': '#6B7280'
                    }
                }
            ]
        }).classes('w-full h-[450px]')
        ui.label('💡 This gauge chart shows the overall average satisfaction score of the medical center out of 100%.').classes('text-xs text-gray-500 mt-auto text-center pt-2')

def draw_overall_satisfaction_donut(df, col_name):
    if col_name not in df.columns: return
    
    counts = df[col_name].value_counts().to_dict()
    custom_colors = {
        'Very Good': '#10B981', 'ඉතා හොඳයි': '#10B981',          
        'Good': '#34D399', 'හොඳයි': '#34D399',                   
        'Neither good nor poor': '#FBBF24', 'හොඳ හෝ නරක නොවේ': '#FBBF24', 
        'Poor': '#F87171', 'නරකයි': '#F87171',                   
        'Very Poor': '#DC2626', 'ඉතා නරකයි': '#DC2626', 'Very poor': '#DC2626' 
    }
    
    data = []
    for k, v in counts.items():
        color = custom_colors.get(str(k).strip(), '#9CA3AF') 
        data.append({'value': v, 'name': str(k).strip(), 'itemStyle': {'color': color}})
        
    pct = _get_single_pct(df, col_name)

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall assessment of the Medical Centre').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'title': {
                'text': f'{pct}%', 
                'subtext': 'Overall Score',
                'left': 'center', 
                'top': '40%', 
                'textStyle': {'fontSize': 24, 'fontWeight': 'bold', 'color': '#1F2937'},
                'subtextStyle': {'fontSize': 10, 'color': '#6B7280'}
            },
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.value+"</b> ("+p.percent+"%)"}'},
            'legend': {'show': True, 'orient': 'horizontal', 'bottom': 0, 'type': 'scroll', 'textStyle': {'fontSize': 11}}, 
            'series': [{
                'type': 'pie',
                'radius': ['40%', '60%'], 
                'center': ['50%', '45%'],
                'avoidLabelOverlap': True,
                'minAngle': 5,
                'data': data,
                'label': {
                    'show': True, 'position': 'outside', 'formatter': '{b}\n{c} ({d}%)', 
                    'fontWeight': 'bold', 'fontSize': 11, 'color': '#374151'
                },
                'labelLine': {'show': True, 'length': 15, 'length2': 20, 'smooth': True}
            }]
        }).classes('w-full h-[450px]') 
        ui.label('💡 This chart breaks down the overall satisfaction with the medical center into 5 levels.').classes('text-xs text-gray-500 mt-auto text-center pt-2')
        
def draw_overall_faculty_col(df, col_name, fac_col):
    data = _get_multi_pct_with_count(df, [col_name], fac_col)
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    y_vals = []
    for f in target_facs:
        match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
        y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count'], 'itemStyle': {'color': COLOR_MAP[f], 'borderRadius': [3,3,0,0]}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall satisfaction in faculty wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': target_facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '50%', 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[450px]')
        ui.label('💡 This chart displays the overall average satisfaction percentage for the medical center separated by each faculty.').classes('text-xs text-gray-500 mt-auto text-center pt-2')

def draw_dynamic_faculty_bar(df, questions_dict, fac_col):
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Satisfaction of Medical Facilities by faculty wise').classes('font-bold text-xl text-[#0b1132] mb-4')
        q_select = ui.select(options=list(questions_dict.keys()), value=list(questions_dict.keys())[0]).classes('w-full mb-4').props('outlined dense')
        chart_cont = ui.column().classes('w-full h-80')
        def render(e=None):
            chart_cont.clear()
            with chart_cont:
                q_col = questions_dict[q_select.value]
                data = _get_multi_pct_with_count(df, [q_col], fac_col)
                target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
                y_vals = []
                for f in target_facs:
                    match = next((v for k, v in data.items() if _get_faculty_short(k) == f), {'pct': 0, 'count': 0})
                    y_vals.append({'value': match['pct'], 'name': f, 'count_val': match['count'], 'itemStyle': {'color': COLOR_MAP[f], 'borderRadius': [3,3,0,0]}})
                ui.echart({
                    'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
                    'xAxis': {'type': 'category', 'data': target_facs, 'axisLabel': {'fontWeight': 'bold'}},
                    'yAxis': {'max': 100},
                    'series': [{'data': y_vals, 'type': 'bar', 'label': {'show': True, 'formatter': '{c}%', 'position': 'top'}}]
                }).classes('w-full h-full')
        q_select.on_value_change(render); render()
        ui.label('💡 Select a facility from the dropdown to see how satisfaction varies across different faculties.').classes('text-xs text-gray-500 mt-auto text-center pt-2')

def draw_quick_stats_boxes(df, questions_dict):
    with ui.row().classes('w-full gap-3 flex-wrap justify-center'):
        for name, col in questions_dict.items():
            pct = _get_single_pct(df, col)
            # 🔴 සිංහල අකුරු සඳහා ඉඩ වෙන් කරලා කොටු 8ටම ගැලපෙන්න min-w හැදුවා
            with ui.card().classes('flex-1 min-w-[200px] max-w-[300px] p-4 text-center shadow-sm border rounded-xl bg-white'):
                ui.label(name).classes('text-[11px] font-bold text-gray-600 min-h-[90px]')
                ui.label(f'{pct}%').classes('text-3xl font-black text-[#3B82F6] mt-2')

def draw_gender_overall_bar(df, all_cols, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, gender_col)
    y_vals = []
    for g in ['Male', 'Female']:
        m = next((v for k, v in data.items() if str(k).strip().title() == g), {'pct': 0, 'count': 0})
        y_vals.append({'value': m['pct'], 'name': g, 'count_val': m['count'], 'itemStyle': {'color': '#3B82F6' if g=='Male' else '#E91E63', 'borderRadius': [3,3,0,0]}})
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall satisfaction').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': ['Male', 'Female'], 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'max': 100},
            'series': [{'type': 'bar', 'barWidth': '40%', 'data': y_vals, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[280px]')
        ui.label('💡 This chart compares the overall average satisfaction percentage between male and female students for medical facilities.').classes('text-xs text-gray-500 mt-auto text-center pt-2')

def draw_clustered_faculty_gender(df, all_cols, fac_col, gender_col):
    data = _get_multi_pct_with_count(df, all_cols, fac_col, gender_col)
    target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    chart_data = {fac: {'Male': {'pct':0, 'count':0}, 'Female': {'pct':0, 'count':0}} for fac in target_facs}
    
    for key, vals in data.items():
        if isinstance(key, tuple):
            f_short = _get_faculty_short(key[0])
            g_clean = str(key[1]).strip().title() 
            if f_short in chart_data and g_clean in ['Male', 'Female']:
                chart_data[f_short][g_clean] = vals

    m_data = [{'value': chart_data[f]['Male']['pct'], 'name': f, 'count_val': chart_data[f]['Male']['count'], 'itemStyle': {'borderRadius': [3,3,0,0]}} for f in target_facs]
    f_data = [{'value': chart_data[f]['Female']['pct'], 'name': f, 'count_val': chart_data[f]['Female']['count'], 'itemStyle': {'borderRadius': [3,3,0,0]}} for f in target_facs]

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Gender-wise Overall satisfaction in faculty wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'color': ['#3B82F6', '#E91E63'],
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': ['Male', 'Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': target_facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'max': 100},
            'series': [
                {'name': 'Male', 'type': 'bar', 'data': m_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}},
                {'name': 'Female', 'type': 'bar', 'data': f_data, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}
            ]
        }).classes('w-full h-[280px]')
        ui.label('💡 This chart breaks down the average satisfaction percentage by both faculty and gender. Hover over the bars to see exact counts.').classes('text-xs text-gray-500 mt-auto text-center pt-2')