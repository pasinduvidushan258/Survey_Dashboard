from nicegui import ui
import pandas as pd
import numpy as np
from st_sa.main_charts import prepare_composite_overall, COLOR_MAP, _get_faculty_short

def prepare_trend_data(cdf, base_cols, cond_cols):
    return prepare_composite_overall(cdf, base_cols, cond_cols)

def draw_overall_trend_line(cdf):
    if 'Composite_Score' not in cdf.columns: return
    grouped = cdf.dropna(subset=['Composite_Score']).groupby('Trend_Year')['Composite_Score'].agg(['mean', 'count'])
    years = sorted([str(k) for k in grouped.index])
    y_vals = [{'value': round((grouped.loc[y, 'mean']/5)*100, 1), 'name': y, 'count_val': int(grouped.loc[y, 'count'])} for y in years]
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('1. Overall Satisfaction Timeline').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>Year: "+p.name+"</b><br/>Total Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': [{'type': 'line', 'data': y_vals, 'smooth': True, 'itemStyle': {'color': '#3B82F6'}, 'lineStyle': {'width': 3}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')

def draw_faculty_trend_bar(cdf, fac_col):
    if 'Composite_Score' not in cdf.columns: return
    grouped = cdf.dropna(subset=['Composite_Score']).groupby(['Trend_Year', fac_col])['Composite_Score'].agg(['mean', 'count'])
    data = {k: {'pct': round((v['mean']/5)*100, 1), 'count': int(v['count'])} for k, v in grouped.iterrows()}
    
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    years = sorted(list(set([str(k[0]) for k in data.keys() if str(k[0]) != 'nan'])))
    active_facs = [f for f in all_facs if any((str(k[0]) in years and _get_faculty_short(k[1]) == f) for k in data.keys())]
    
    series = []
    for f in active_facs:
        f_data = [{'value': next((v['pct'] for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), 0), 'name': y, 'count_val': next((v['count'] for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), 0)} for y in years]
        series.append({'name': f, 'type': 'bar', 'data': f_data, 'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [3,3,0,0]}, 'label': {'show': False}})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('2. Faculty-wise Satisfaction Year over Year').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': active_facs, 'top': 0, 'type': 'scroll'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': series
        }).classes('w-full h-[300px]')

def draw_gender_trend_line(cdf, gender_col):
    if 'Composite_Score' not in cdf.columns: return
    grouped = cdf.dropna(subset=['Composite_Score']).groupby(['Trend_Year', gender_col])['Composite_Score'].agg(['mean', 'count'])
    years = sorted(list(set([str(k[0]) for k in grouped.index])))
    
    m_data = [{'value': round((grouped.loc[(y, k), 'mean']/5)*100, 1) if (y, k) in grouped.index else 0, 'name': y, 'count_val': int(grouped.loc[(y, k), 'count']) if (y, k) in grouped.index else 0} for y in years for k in grouped.index.get_level_values(1) if str(k).strip().title() == 'Male']
    f_data = [{'value': round((grouped.loc[(y, k), 'mean']/5)*100, 1) if (y, k) in grouped.index else 0, 'name': y, 'count_val': int(grouped.loc[(y, k), 'count']) if (y, k) in grouped.index else 0} for y in years for k in grouped.index.get_level_values(1) if str(k).strip().title() == 'Female']

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('3. Gender-wise Satisfaction Trend').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': ['Male', 'Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': [
                {'name': 'Male', 'type': 'line', 'data': m_data, 'smooth': True, 'itemStyle': {'color': '#3B82F6'}, 'lineStyle': {'width': 3}},
                {'name': 'Female', 'type': 'line', 'data': f_data, 'smooth': True, 'itemStyle': {'color': '#EC4899'}, 'lineStyle': {'width': 3}}
            ]
        }).classes('w-full h-[300px]')

def draw_first_gen_trend_line(cdf, fgen_col):
    if fgen_col not in cdf.columns: return
    
    years = sorted(list(set(cdf['Trend_Year'].dropna().astype(str))))
    y_vals = []
    for y in years:
        y_df = cdf[cdf['Trend_Year'] == y]
        counts = y_df[fgen_col].value_counts().to_dict()
        yes = counts.get('Yes', 0)
        tot = sum(counts.values())
        pct = round((yes/tot)*100, 1) if tot > 0 else 0
        y_vals.append({'value': pct, 'name': y, 'count_val': yes})

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('4. First-Generation Students Trend (%)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>Year: "+p.name+"</b><br/>First-Gen Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': [{'type': 'line', 'data': y_vals, 'smooth': True, 'itemStyle': {'color': '#8B5CF6'}, 'lineStyle': {'width': 3}, 'areaStyle': {'opacity': 0.2, 'color': '#8B5CF6'}}]
        }).classes('w-full h-[300px]')