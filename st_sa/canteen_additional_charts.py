from nicegui import ui
from st_sa.canteen_charts import _get_multi_pct_with_count, COLOR_MAP, _get_faculty_short

def draw_year_comparison_bar(df, all_cols, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col)
    years = sorted([str(k) for k in data.keys() if str(k) != 'nan'])
    y_vals = [{'value': data[y]['pct'], 'name': y, 'count_val': data[y]['count']} for y in years]
    ctype = 'line' if len(years) > 1 else 'bar'

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall student satisfaction percentage timeline').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>Year: "+p.name+"</b><br/>Total Responses: <b>"+p.data.count_val+"</b><br/>Percentage: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': [{'type': ctype, 'data': y_vals, 'smooth': True, 'itemStyle': {'color': '#3B82F6'}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')

def draw_clustered_faculty_year(df, all_cols, fac_col, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col, fac_col)
    facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    years = sorted(list(set([str(k[0]) for k in data.keys() if str(k[0]) != 'nan'])))
    series = []
    for f in facs:
        f_data = [
            {'value': next((v['pct'] for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), 0),
             'count_val': next((v['count'] for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), 0)}
            for y in years
        ]
        series.append({'name': f, 'type': 'bar', 'data': f_data, 'itemStyle': {'color': COLOR_MAP.get(f, '#000000'), 'borderRadius': [3,3,0,0]}})
    
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Faculty-wise overall satisfaction percentage in year wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': facs, 'top': 0, 'type': 'scroll'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': series
        }).classes('w-full h-[300px]')