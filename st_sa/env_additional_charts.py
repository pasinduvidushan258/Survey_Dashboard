from nicegui import ui
from st_sa.env_charts import _get_multi_pct_with_count, COLOR_MAP, _get_faculty_short

def draw_year_comparison_bar(df, all_cols, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col)
    years = sorted([str(k) for k in data.keys() if str(k) != 'nan'])
    y_vals = []
    for y in years:
        y_vals.append({'value': data[y]['pct'], 'name': y, 'count_val': data[y]['count']})
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Overall satisfaction percentage timeline').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>Year: "+p.name+"</b><br/>Total Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': [{'type': 'line', 'data': y_vals, 'smooth': True, 'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')

def draw_clustered_faculty_year(df, all_cols, fac_col, year_col):
    data = _get_multi_pct_with_count(df, all_cols, year_col, fac_col)
    all_facs = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
    years = sorted(list(set([str(k[0]) for k in data.keys() if str(k[0]) != 'nan'])))
    
    active_facs = [f for f in all_facs if any((str(k[0]) in years and _get_faculty_short(k[1]) == f) for k in data.keys())]
    
    series = []
    for f in active_facs:
        f_data = []
        for y in years:
            match = next((v for k, v in data.items() if str(k[0])==y and _get_faculty_short(k[1])==f), {'pct': 0, 'count': 0})
            f_data.append({'value': match['pct'], 'name': y, 'count_val': match['count']})
        
        series.append({
            'name': f, 
            'type': 'bar', 
            'data': f_data, 
            'itemStyle': {'color': COLOR_MAP.get(f, '#9CA3AF'), 'borderRadius': [3,3,0,0]},
            'label': {'show': False}
        })

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Faculty-wise satisfaction year wise').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': active_facs, 'top': 0, 'type': 'scroll'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': series
        }).classes('w-full h-[300px]')

# 🔴 1 වෙනි අලුත් ග්‍රාෆ් එක (Individual Work vs Team Work)
def draw_spaces_year_comparison(df, ind_col, team_col, year_col):
    years = sorted([str(y) for y in df[year_col].dropna().unique() if str(y) != 'nan'])
    
    series_data = []
    # කලින් පාවිච්චි නොකළ අලුත් පාට 2ක් (Teal සහ Orange)
    labels = [('Individual Work', ind_col, '#14B8A6'), ('Team Work', team_col, '#F97316')]
    
    for name, col, color in labels:
        data_dict = _get_multi_pct_with_count(df, [col], year_col)
        y_vals = []
        for y in years:
            match = data_dict.get(y, {'pct': 0, 'count': 0})
            y_vals.append({'value': match['pct'], 'name': y, 'count_val': match['count']})
        
        series_data.append({
            'name': name,
            'type': 'bar',
            'data': y_vals,
            'itemStyle': {'color': color, 'borderRadius': [3,3,0,0]},
            'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}
        })
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Adequacy of Spaces (Year-wise)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': ['Individual Work', 'Team Work'], 'top': 0},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': series_data
        }).classes('w-full h-[300px]')

# 🔴 2 වෙනි අලුත් ග්‍රාෆ් එක (Staff & Senior Student Support)
def draw_support_year_comparison(df, acad_col, temp_col, admin_col, senior_col, year_col):
    years = sorted([str(y) for y in df[year_col].dropna().unique() if str(y) != 'nan'])
    
    series_data = []
    # අලුත් පාට 4ක් (Purple, Indigo, Cyan, Amber)
    labels = [
        ('Academic Staff', acad_col, '#8B5CF6'), 
        ('Temp. Academic Staff', temp_col, '#6366F1'),
        ('Admin/Non-Academic', admin_col, '#06B6D4'),
        ('Senior Students', senior_col, '#F59E0B')
    ]
    
    for name, col, color in labels:
        data_dict = _get_multi_pct_with_count(df, [col], year_col)
        y_vals = []
        for y in years:
            match = data_dict.get(y, {'pct': 0, 'count': 0})
            y_vals.append({'value': match['pct'], 'name': y, 'count_val': match['count']})
        
        series_data.append({
            'name': name,
            'type': 'bar',
            'data': y_vals,
            'itemStyle': {'color': color, 'borderRadius': [3,3,0,0]},
            'label': {'show': False} # බාර් 4ක් තියෙන නිසා අකුරු එකපිට වැටෙන එක නවත්තන්න ලේබල් එක හැංගුවා (Mouse එක ගෙනිච්චම පෙනේවි)
        })
        
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white h-full flex flex-col'):
        ui.label('Staff & Student Support (Year-wise)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" ("+p.name+")</b><br/>Students: <b>"+p.data.count_val+"</b><br/>Pct: <b>"+p.value+"%</b>"}'},
            'legend': {'data': [l[0] for l in labels], 'top': 0, 'type': 'scroll'},
            'xAxis': {'type': 'category', 'data': years},
            'yAxis': {'max': 100},
            'series': series_data
        }).classes('w-full h-[300px]')