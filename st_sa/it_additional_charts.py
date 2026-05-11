from nicegui import ui
from st_sa.it_charts import _get_multi_pct_with_count, COLOR_MAP, _get_faculty_short

def draw_year_comparison_bar(df, all_cols, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col)
    years = sorted([str(k) for k in data.keys() if str(k) != 'nan'])
    y_vals = [{'value': data[y]['pct'], 'name': y, 'count_val': data[y]['count']} for y in years]
    ctype = 'line' if len(years) > 1 else 'bar'

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall student satisfaction percentage timeline').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>Year: "+p.name+"</b><br/>Total Responses: <b>"+p.data.count_val+"</b><br/>Percentage: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': years, 'boundaryGap': (ctype == 'bar'), 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'max': 100},
            'series': [{'type': ctype, 'barWidth': '40%', 'data': y_vals, 'smooth': True, 'itemStyle': {'color': '#3B82F6', 'borderRadius': [4,4,0,0]}, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')
        ui.label('💡 This chart shows the trend of overall IT satisfaction across different years.').classes('text-xs text-gray-500 mt-auto text-center pt-2')

def draw_clustered_faculty_year(df, all_cols, fac_col, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col, fac_col)
    facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    years = sorted(list(set([str(k[0]) for k in data.keys() if str(k[0]) != 'nan'])))
    
    series = []
    for f in facs:
        f_data = []
        for y in years:
            # 🔴 මෙතනදී අපි 'value' එක විතරක් නෙවෙයි 'count_val' එකත් ගන්නවා
            match = next((v for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), {'pct': 0, 'count': 0})
            f_data.append({'value': match['pct'], 'name': y, 'count_val': match['count']})
        
        series.append({
            'name': f, 
            'type': 'bar', 
            'data': f_data, 
            'itemStyle': {'color': COLOR_MAP.get(f, '#000000'), 'borderRadius': [3,3,0,0]}, 
            'label': {'show': False}
        })

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Faculty-wise overall satisfaction percentage in year wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            # 🔴 මෙන්න Mouse එක ගෙනිච්චම පේන Tooltip එක
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': facs, 'top': 0, 'type': 'scroll'},
            'xAxis': {'type': 'category', 'data': years, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'max': 100},
            'series': series
        }).classes('w-full h-[300px]')
        ui.label('💡 This chart breaks down the IT satisfaction percentage by each faculty, grouped by year.').classes('text-xs text-gray-500 mt-auto text-center pt-2')