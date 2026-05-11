from nicegui import ui
from st_sa.washroom_charts import _get_multi_pct_with_count, _get_faculty_short, COLOR_MAP

def draw_year_comparison_bar(df, all_cols, year_col):
    """Line Chart එක (අවුරුදු 2කට වඩා තියෙනවා නම් Line එකක්, නැත්නම් තනි කණුවක් පෙන්වයි)"""
    try:
        data = _get_multi_pct_with_count(df, all_cols, year_col)
        
        cleaned_data = {}
        for k, v in data.items():
            if str(k).lower() != 'nan':
                yr_str = str(k).replace('.0', '').strip() 
                cleaned_data[yr_str] = v
                
        target_years = sorted(list(cleaned_data.keys()))
        
        y_vals = []
        for yr in target_years:
            match_val = cleaned_data[yr]
            y_vals.append({
                'value': match_val['pct'],
                'name': yr,
                'count_val': match_val['count']
            })

        chart_type = 'line' if len(target_years) > 1 else 'bar'

        with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
            ui.label('Overall student satisfaction percentage timeline').classes('font-bold text-[#0b1132] mb-2')
            ui.echart({
                'tooltip': {
                    'trigger': 'item',
                    ':formatter': 'function(params) { return params.marker + " <b>Year: " + params.name + "</b><br/>Total Responses: <b>" + params.data.count_val + " Students</b><br/>Percentage: <b>" + params.value + "%</b>"; }'
                },
                'xAxis': {
                    'type': 'category', 
                    'data': target_years, 
                    'axisLabel': {'fontWeight': 'bold'},
                    'boundaryGap': True if chart_type == 'bar' else False 
                },
                'yAxis': {'type': 'value', 'max': 100},
                'series': [{
                    'type': chart_type, 
                    'barWidth': '40%', 
                    'data': y_vals, 
                    'smooth': True, 
                    'symbolSize': 10, 
                    'itemStyle': {'color': '#3B82F6', 'borderRadius': [4,4,0,0]}, 
                    'areaStyle': { 
                        'color': {
                            'type': 'linear', 'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                            'colorStops': [{'offset': 0, 'color': 'rgba(59, 130, 246, 0.5)'}, {'offset': 1, 'color': 'rgba(59, 130, 246, 0.0)'}]
                        }
                    } if chart_type == 'line' else None,
                    'label': {'show': True, 'position': 'top', 'formatter': '{c}%', 'fontWeight': 'bold'}
                }]
            }).classes('w-full h-80')
            ui.label('💡 How to read this chart: It shows the trend of overall satisfaction across different years.').classes('text-xs text-gray-500 mt-auto text-center pt-2')
    except Exception as e:
        ui.label(f"Chart Error: {str(e)}").classes('text-red-500')


def draw_clustered_faculty_year(df, all_cols, fac_col, year_col):
    """පීඨ 6ට අදාළව අවුරුද්දෙන් අවුරුද්දට වෙනස් වෙන Bar Chart එක"""
    try:
        data = _get_multi_pct_with_count(df, all_cols, year_col, fac_col)
        
        target_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
        
        unique_years = set()
        for key in data.keys():
            if isinstance(key, tuple):
                yr_raw, fac_raw = key
                if str(yr_raw).lower() != 'nan':
                    unique_years.add(str(yr_raw).replace('.0', '').strip())
        
        target_years = sorted(list(unique_years))
        chart_data = {yr: {fac: {'pct':0.0, 'count':0} for fac in target_facs} for yr in target_years}
        
        for key, vals in data.items():
            if isinstance(key, tuple):
                yr_raw, fac_raw = key
                yr_clean = str(yr_raw).replace('.0', '').strip()
                fac_short = _get_faculty_short(fac_raw)
                
                if yr_clean in target_years and fac_short in target_facs:
                    chart_data[yr_clean][fac_short] = vals

        series_data = []
        for fac in target_facs:
            fac_data = [
                {
                    'value': chart_data[yr][fac]['pct'], 
                    'name': yr, 
                    'count_val': chart_data[yr][fac]['count'],
                    'itemStyle': {'borderRadius': [3,3,0,0]} 
                } 
                for yr in target_years
            ]
            
            series_data.append({
                'name': fac, 
                'type': 'bar', 
                'data': fac_data,
                'itemStyle': {'color': COLOR_MAP.get(fac, '#000000')}, 
                'label': {'show': False} 
            })

        with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
            ui.label('Faculty-wise overall satisfaction percentage in year wise').classes('font-bold text-[#0b1132] mb-2')
            ui.echart({
                'tooltip': {
                    'trigger': 'item', 
                    ':formatter': 'function(params) { return params.marker + " <b>" + params.seriesName + " (" + params.name + ")</b><br/>Total Responses: <b>" + params.data.count_val + " Students</b><br/>Percentage: <b>" + params.value + "%</b>"; }'
                },
                'legend': {'data': target_facs, 'top': '0%'},
                'xAxis': {'type': 'category', 'data': target_years, 'axisLabel': {'fontWeight': 'bold', 'interval': 0}},
                'yAxis': {'type': 'value', 'max': 100},
                'series': series_data
            }).classes('w-full h-80')
            ui.label('💡 How to read this chart: It breaks down the satisfaction percentage by each faculty, grouped by the calendar year.').classes('text-xs text-gray-500 mt-auto text-center pt-2')
    except Exception as e:
        ui.label(f"Chart Error: {str(e)}").classes('text-red-500')