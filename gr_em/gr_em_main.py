"""
Graduate Employability Dashboard
─────────────────────────────────
Student Satisfaction page pattern එකටම.
Real DB data (survey.db / graduate_employability_{year} tables).
ECharts graphs - matplotlib නෑ.

CHANGES:
  - All Years: combines ALL graduate_employability_{year} tables, adds '__year' column
  - New "YEAR ANALYSIS" tab (visible only in All Years mode) with trend graphs
"""

from nicegui import ui
import sidebar
from settings_dialog import create_settings_dialog
import pandas as pd
import sqlite3
import numpy as np

# ══════════════════════════════════════════════════════════════════════════════
# LABEL MAPS
# ══════════════════════════════════════════════════════════════════════════════

FACULTY_LABELS    = {1: 'FCMS', 2: 'FCT', 3: 'FHU', 4: 'FMED', 5: 'FSC', 6: 'FSS'}
GENDER_LABELS     = {1: 'Male', 2: 'Female'}
EMP_STATUS_LABELS = {1: 'Employed', 2: 'Unemployed'}
TIMING_LABELS     = {
    1: 'After A/L / During Uni',
    2: 'Immediately / Within 3 months',
    3: 'After 6 months or more',
}
EMP_SECTOR_LABELS = {
    1: 'Public Sector', 2: 'Private Sector', 3: 'Semi-Government',
    4: 'Self-Employed',  5: 'NGO / Non-Profit', 6: 'Informal Sector',
    7: 'Military / Defence', 8: 'Gig Economy', 10: 'Other',
}
RANK_LABELS = {
    1: 'Staff', 2: 'Executive',
    3: 'Junior Manager', 4: 'Middle Manager', 5: 'Senior Manager',
}
SALARY_LABELS = {
    67: '< 25k', 68: '25k–49k', 69: '50k–74k', 70: '75k–99k', 73: '100k+',
}
CLASS_LABELS       = {1: 'First Class', 2: 'Second Upper', 3: 'Second Lower', 4: 'Ordinary Pass'}
DEGREE_TYPE_LABELS = {1: 'General (3yr)', 2: 'Special (4yr)', 4: 'Special (5yr)'}
MEDIUM_LABELS      = {1: 'English', 2: 'Sinhala', 3: 'Both'}
RELATION_LABELS    = {
    1: 'Very Related', 2: 'Somewhat Related', 3: 'Neutral',
    4: 'Somewhat Unrelated', 5: 'Very Unrelated',
}
SATISFACTION_LABELS = {
    1: 'Very Satisfied', 2: 'Somewhat Satisfied', 3: 'Neutral',
    4: 'Somewhat Dissatisfied', 5: 'Very Dissatisfied',
}
EMP_TYPE_LABELS = {
    1: 'Permanent', 2: 'Temporary/Contract', 3: 'Self-Employed',
    4: 'Entrepreneur', 5: 'Foreign Employment', 6: 'Other',
}
UNEMP_REASON_COLS = {
    'reason_unemployment___1': 'Not Looking',
    'reason_unemployment___2': 'Cont. Studies',
    'reason_unemployment___3': 'Still Searching',
    'reason_unemployment___4': 'Rejected Offers',
    'reason_unemployment___5': 'Quit/Resigned',
    'reason_unemployment___6': 'Other',
}
JOB_ASPECTS_COLS = {
    'job_aspects___1':  'Degree',          'job_aspects___2':  'Class of Degree',
    'job_aspects___3':  'Uni Reputation',  'job_aspects___4':  'Field of Study',
    'job_aspects___5':  'Research Exp.',   'job_aspects___6':  'Personal Contacts',
    'job_aspects___7':  'Work Experience', 'job_aspects___8':  'English',
    'job_aspects___9':  'Prof. Quals',     'job_aspects___10': 'Personality',
    'job_aspects___11': 'Computer Lit.',   'job_aspects___12': 'Other',
}
JOB_FINDING_COLS = {
    'job_finding_method___1': 'Newspaper',
    'job_finding_method___2': 'Online/Social Media',
    'job_finding_method___3': 'Personal Contact',
    'job_finding_method___4': 'Same Job During Uni',
    'job_finding_method___5': 'Via Internship',
    'job_finding_method___6': 'Uni Contact',
    'job_finding_method___7': 'Job Fair',
    'job_finding_method___8': 'Other',
}

# ══════════════════════════════════════════════════════════════════════════════
# COLOUR CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

ALL_FACS = ['FCMS', 'FCT', 'FHU', 'FMED', 'FSC', 'FSS']
FAC_COLORS = {
    'FCMS': '#E81E29', 'FCT': '#F05323', 'FHU': '#3A7B43',
    'FMED': '#2F97BB', 'FSC': '#2B3A89', 'FSS': '#5A2F83',
}
PALETTE = ['#1a3a6b','#f5a623','#6baed6','#4caf50','#e53935',
           '#9e9e9e','#bc119d','#16a085','#d35400','#2980b9']
SAT_COLORS = {
    'Very Good':'#10B981','Good':'#34D399','Neutral':'#FBBF24',
    'Poor':'#F87171','Very Poor':'#DC2626',
}

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _amap(series, mapping):
    return series.map(mapping).fillna('Unknown')

def _pct(num, den):
    return round(num / den * 100, 1) if den > 0 else 0

def _fac_col(df):
    df = df.copy()
    df['__fac'] = _amap(df['faculty'], FACULTY_LABELS)
    return df

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def _get_years() -> list[str]:
    try:
        conn = sqlite3.connect('survey.db')
        cur  = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name LIKE 'graduate_employability_%'"
        )
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return sorted([t.replace('graduate_employability_', '') for t in tables], reverse=True)
    except Exception:
        return []


def _load_data(year: str) -> pd.DataFrame | None:
    """
    year == 'All'  →  concat ALL graduate_employability_{y} tables,
                      add '__year' column = survey year string (e.g. '2022')
    year == '2025' →  single table, '__year' column filled with '2025'
    """
    try:
        conn = sqlite3.connect('survey.db')

        if year == 'All':
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name LIKE 'graduate_employability_%'"
            )
            tables = [r[0] for r in cur.fetchall()]
            frames = []
            for tbl in tables:
                y = tbl.replace('graduate_employability_', '')
                try:
                    df_y = pd.read_sql(f'SELECT * FROM "{tbl}"', conn)
                    if not df_y.empty:
                        df_y['__year'] = y
                        frames.append(df_y)
                except Exception:
                    pass
            conn.close()
            if not frames:
                return None
            # align columns (fill missing with NaN)
            df = pd.concat(frames, ignore_index=True, sort=False)
            return df if not df.empty else None

        else:
            tbl = f'graduate_employability_{year}'
            df  = pd.read_sql(f'SELECT * FROM "{tbl}"', conn)
            conn.close()
            if df.empty:
                return None
            df['__year'] = year
            return df

    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
# CHART COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

# ── KPI ROW ───────────────────────────────────────────────────────────────────
def _kpi_row(df):
    total = len(df)
    emp   = int((df['employment_status'] == 1).sum())
    unemp = int((df['employment_status'] == 2).sum())
    kpis  = [
        ('👩‍🎓 Total Graduates', str(total),       '#3B82F6'),
        ('✅ Employed',          str(emp),          '#10B981'),
        ('❌ Unemployed',        str(unemp),        '#F87171'),
        ('📊 Employment Rate',  f'{_pct(emp,total)}%', '#8B5CF6'),
    ]
    with ui.row().classes('w-full gap-4 mb-2 flex-wrap'):
        for lbl, val, color in kpis:
            with ui.card().classes('flex-1 min-w-[140px] p-4 rounded-xl shadow-sm border bg-white text-center'):
                ui.label(lbl).classes('text-xs font-bold text-gray-500 uppercase')
                ui.label(val).classes('text-3xl font-black mt-1').style(f'color:{color}')

# ── OVERVIEW ──────────────────────────────────────────────────────────────────
def _employment_status_donut(df):
    d     = _amap(df['employment_status'], EMP_STATUS_LABELS)
    counts = d.value_counts().to_dict()
    total  = sum(counts.values())
    emp_n  = counts.get('Employed', 0)
    pct    = _pct(emp_n, total)
    data   = [{'value': v, 'name': k,
                'itemStyle': {'color': '#10B981' if k=='Employed' else '#F87171'}}
               for k, v in counts.items()]
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Overall Employability').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'title': {'text': f'{pct}%', 'subtext': 'Employment Rate',
                      'left': 'center', 'top': 'center',
                      'textStyle': {'fontSize': 26, 'fontWeight': 'bold', 'color': '#1F2937'},
                      'subtextStyle': {'fontSize': 11, 'color': '#6B7280'}},
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'series': [{'type': 'pie', 'radius': ['50%', '72%'], 'center': ['50%', '50%'],
                        'avoidLabelOverlap': True,
                        'itemStyle': {'borderRadius': 4, 'borderColor': '#fff', 'borderWidth': 2},
                        'label': {'show': True, 'position': 'outside',
                                  'formatter': '{b}\n{c}', 'fontSize': 12, 'fontWeight': 'bold'},
                        'labelLine': {'show': True, 'smooth': True},
                        'data': data}]
        }).classes('w-full h-[300px]')

def _gender_pie(df):
    counts = _amap(df['gender'], GENDER_LABELS).value_counts().to_dict()
    colors = {'Male': '#3B82F6', 'Female': '#EC4899'}
    data   = [{'name': k, 'value': v, 'itemStyle': {'color': colors.get(k, '#9CA3AF')}}
               for k, v in counts.items()]
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Sample by Gender').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'series': [{'type': 'pie', 'radius': ['40%', '68%'], 'center': ['50%', '50%'],
                        'itemStyle': {'borderRadius': 5, 'borderColor': '#fff', 'borderWidth': 2},
                        'label': {'show': True, 'formatter': '{b}\n{d}%', 'fontWeight': 'bold'},
                        'data': data}]
        }).classes('w-full h-[300px]')

def _faculty_employment_bar(df):
    df2 = _fac_col(df)
    cats, y_vals = [], []
    for f in ALL_FACS:
        sub = df2[df2['__fac'] == f]
        if sub.empty: continue
        total = len(sub); emp = int((sub['employment_status']==1).sum())
        cats.append(f)
        y_vals.append({'value': _pct(emp, total), 'name': f, 'count_val': total,
                       'itemStyle': {'color': FAC_COLORS.get(f,'#9CA3AF'), 'borderRadius':[4,4,0,0]}})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Employment Rate by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Total: <b>"+p.data.count_val+"</b><br/>Rate: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': cats, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'name': 'Employment Rate (%)'},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%',
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[320px]')

def _timing_bar(df):
    sub = df.dropna(subset=['timing'])
    counts = _amap(sub['timing'], TIMING_LABELS).value_counts().to_dict()
    cats  = list(TIMING_LABELS.values())
    vals  = [counts.get(c, 0) for c in cats]
    clrs  = ['#3B82F6', '#10B981', '#F59E0B']
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Timing of First Employment').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': cats,
                      'axisLabel': {'fontSize': 10, 'fontWeight': 'bold', 'interval': 0}},
            'yAxis': {'type': 'value', 'name': 'Graduates'},
            'series': [{'type': 'bar', 'barWidth': '40%',
                        'data': [{'value': v, 'itemStyle': {'color': clrs[i], 'borderRadius':[4,4,0,0]}}
                                  for i, v in enumerate(vals)],
                        'label': {'show': True, 'position': 'top'}}]
        }).classes('w-full h-[300px]')

# ── EMPLOYMENT CHARACTERISTICS ─────────────────────────────────────────────────
def _emp_type_donut(df):
    sub    = df.dropna(subset=['current_status_your_employment'])
    counts = _amap(sub['current_status_your_employment'], EMP_TYPE_LABELS).value_counts().to_dict()
    data   = [{'value': v, 'name': k, 'itemStyle': {'color': PALETTE[i % len(PALETTE)]}}
               for i, (k,v) in enumerate(counts.items())]
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Employment Type').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'legend': {'bottom': '0%', 'left': 'center', 'textStyle': {'fontSize': 9}},
            'series': [{'type': 'pie', 'radius': '58%', 'center': ['50%', '44%'],
                        'label': {'show': True, 'formatter': '{b}\n{c}', 'fontSize': 9},
                        'data': data}]
        }).classes('w-full h-[320px]')

def _sector_bar(df):
    sub = df.dropna(subset=['employment_sector'])
    counts = _amap(sub['employment_sector'], EMP_SECTOR_LABELS).value_counts().to_dict()
    items  = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    cats, vals = zip(*items) if items else ([], [])
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Employment Sector').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'value', 'name': 'Graduates'},
            'yAxis': {'type': 'category', 'data': list(cats)[::-1],
                      'axisLabel': {'fontSize': 9, 'fontWeight': 'bold'}},
            'series': [{'type': 'bar', 'data': list(vals)[::-1],
                        'itemStyle': {'color': '#3B82F6', 'borderRadius':[0,4,4,0]},
                        'label': {'show': True, 'position': 'right'}}]
        }).classes('w-full h-[320px]')

def _rank_faculty_stacked(df):
    sub = df.dropna(subset=['rank_position','faculty']).copy()
    sub = _fac_col(sub)
    sub['rank'] = _amap(sub['rank_position'], RANK_LABELS)
    rank_order   = ['Staff','Executive','Junior Manager','Middle Manager','Senior Manager']
    facs = [f for f in ALL_FACS if f in sub['__fac'].values]
    series = []
    for i, r in enumerate(rank_order):
        vals = []
        for f in facs:
            grp = sub[sub['__fac']==f]; total=len(grp)
            vals.append(_pct(int((grp['rank']==r).sum()), total))
        series.append({'name': r, 'type': 'bar', 'stack': 'total', 'data': vals,
                       'itemStyle': {'color': PALETTE[i]},
                       'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9}})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Position Rank by Faculty (%)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': rank_order, 'top': 0, 'textStyle': {'fontSize': 10}},
            'xAxis': {'type': 'category', 'data': facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[350px]')

def _salary_faculty_stacked(df):
    sub = df.dropna(subset=['salary','faculty']).copy()
    sub = _fac_col(sub)
    sub['sal'] = _amap(sub['salary'], SALARY_LABELS)
    sal_order  = ['< 25k','25k–49k','50k–74k','75k–99k','100k+']
    sal_colors = ['#F87171','#FBBF24','#34D399','#3B82F6','#8B5CF6']
    facs = [f for f in ALL_FACS if f in sub['__fac'].values]
    series = []
    for i, s in enumerate(sal_order):
        vals = []
        for f in facs:
            grp = sub[sub['__fac']==f]; total=len(grp)
            vals.append(_pct(int((grp['sal']==s).sum()), total))
        series.append({'name': s, 'type': 'bar', 'stack': 'total', 'data': vals,
                       'itemStyle': {'color': sal_colors[i]},
                       'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9}})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Salary Distribution by Faculty (%)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': sal_order, 'top': 0, 'textStyle': {'fontSize': 10}},
            'xAxis': {'type': 'category', 'data': facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[350px]')

# ── EMPLOYABILITY FACTORS ──────────────────────────────────────────────────────
def _job_aspects_bar(df):
    total = len(df)
    items = [(lbl, int(df[col].sum())) for col, lbl in JOB_ASPECTS_COLS.items() if col in df.columns]
    items.sort(key=lambda x: x[1], reverse=True)
    cats = [i[0] for i in items]
    pcts = [_pct(i[1], total) for i in items]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Influential Factors in Finding Employment (% selected)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': cats,
                      'axisLabel': {'fontSize': 9, 'interval': 0, 'rotate': 30}},
            'yAxis': {'type': 'value', 'name': '% Graduates', 'max': 100},
            'series': [{'type': 'bar', 'barWidth': '60%',
                        'data': [{'value': p, 'itemStyle':{'color': PALETTE[i%len(PALETTE)], 'borderRadius':[4,4,0,0]}}
                                  for i, p in enumerate(pcts)],
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%', 'fontSize': 9}}]
        }).classes('w-full h-[350px]')

def _job_finding_bar(df):
    emp   = df[df['employment_status']==1]
    total = len(emp)
    items = [(lbl, int(emp[col].sum())) for col, lbl in JOB_FINDING_COLS.items() if col in emp.columns]
    items.sort(key=lambda x: x[1], reverse=True)
    cats = [i[0] for i in items]
    pcts = [_pct(i[1], total) for i in items]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Method of Finding Employment (% of Employed)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': cats,
                      'axisLabel': {'fontSize': 9, 'interval': 0, 'rotate': 20}},
            'yAxis': {'type': 'value', 'name': '% Employed', 'max': 100},
            'series': [{'type': 'bar', 'barWidth': '55%',
                        'data': [{'value': p, 'itemStyle':{'color':'#1a3a6b','borderRadius':[4,4,0,0]}}
                                  for p in pcts],
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%', 'fontSize': 9}}]
        }).classes('w-full h-[320px]')

def _edu_class_bar(df):
    sub = df.dropna(subset=['class_received','employment_status']).copy()
    sub['cls'] = _amap(sub['class_received'], CLASS_LABELS)
    sub['st']  = _amap(sub['employment_status'], EMP_STATUS_LABELS)
    order = ['First Class','Second Upper','Second Lower','Ordinary Pass']
    cats  = [c for c in order if c in sub['cls'].values]
    emp_v, unemp_v = [], []
    for c in cats:
        grp = sub[sub['cls']==c]; total=len(grp)
        emp_v.append(_pct(int((grp['st']=='Employed').sum()), total))
        unemp_v.append(_pct(int((grp['st']=='Unemployed').sum()), total))
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Academic Class vs Employability (%)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': ['Employed','Unemployed'], 'top': 0},
            'xAxis': {'type': 'category', 'data': cats, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel': {'formatter': '{value}%'}},
            'series': [
                {'name':'Employed','type':'bar','stack':'total','data': emp_v,
                 'itemStyle':{'color':'#10B981'},'label':{'show':True,'formatter':'{c}%'}},
                {'name':'Unemployed','type':'bar','stack':'total','data': unemp_v,
                 'itemStyle':{'color':'#F87171'},'label':{'show':True,'formatter':'{c}%'}},
            ]
        }).classes('w-full h-[320px]')

# ── UNEMPLOYMENT ANALYSIS ──────────────────────────────────────────────────────
def _unemp_reasons_bar(df):
    unemp = df[df['employment_status']==2]
    total = len(unemp)
    items = [(lbl, int(unemp[col].sum())) for col, lbl in UNEMP_REASON_COLS.items() if col in unemp.columns]
    items.sort(key=lambda x: x[1], reverse=True)
    cats, vals = zip(*items) if items else ([], [])
    pcts = [_pct(v, total) for v in vals]
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Reasons for Unemployment (% of Unemployed)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': list(cats),
                      'axisLabel': {'fontWeight': 'bold', 'interval': 0}},
            'yAxis': {'type': 'value', 'name': '%', 'max': 100},
            'series': [{'type': 'bar', 'barWidth': '45%',
                        'data': [{'value': p, 'itemStyle':{'color':'#F87171','borderRadius':[4,4,0,0]}}
                                  for p in pcts],
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')

def _unemp_by_faculty_bar(df):
    df2 = _fac_col(df)
    cats, y_vals = [], []
    for f in ALL_FACS:
        sub = df2[df2['__fac']==f]
        if sub.empty: continue
        total = len(sub); u = int((sub['employment_status']==2).sum())
        cats.append(f)
        y_vals.append({'value': _pct(u, total), 'name': f, 'count_val': u,
                       'itemStyle': {'color': FAC_COLORS.get(f,'#9CA3AF'), 'borderRadius':[4,4,0,0]}})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Unemployment Rate by Faculty (%)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Unemployed: <b>"+p.data.count_val+"</b><br/>Rate: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': cats, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100},
            'series': [{'data': y_vals, 'type': 'bar', 'barWidth': '45%',
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[320px]')

# ── GRADUATE PERCEPTIONS ───────────────────────────────────────────────────────
def _degree_relevance(df):
    sub    = df.dropna(subset=['relation_to_job'])
    counts = _amap(sub['relation_to_job'], RELATION_LABELS).value_counts().to_dict()
    order  = ['Very Related','Somewhat Related','Neutral','Somewhat Unrelated','Very Unrelated']
    colors = ['#10B981','#34D399','#FBBF24','#F87171','#DC2626']
    data   = [{'value': counts.get(k,0), 'name': k, 'itemStyle':{'color': colors[i]}}
               for i, k in enumerate(order) if counts.get(k,0)>0]
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Degree Relevance to Employment').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'legend': {'bottom': '0%', 'left': 'center', 'textStyle': {'fontSize': 9}},
            'series': [{'type': 'pie', 'radius': '58%', 'center': ['50%', '44%'],
                        'label': {'show': True, 'formatter': '{d}%', 'fontWeight': 'bold'},
                        'data': data}]
        }).classes('w-full h-[320px]')

def _job_satisfaction_bar(df):
    sub    = df.dropna(subset=['job_satisfaction'])
    counts = _amap(sub['job_satisfaction'], SATISFACTION_LABELS).value_counts().to_dict()
    order  = ['Very Satisfied','Somewhat Satisfied','Neutral','Somewhat Dissatisfied','Very Dissatisfied']
    colors = ['#10B981','#34D399','#FBBF24','#F87171','#DC2626']
    vals   = [{'value': counts.get(c,0),
                'itemStyle': {'color': colors[i], 'borderRadius':[4,4,0,0]}}
               for i, c in enumerate(order)]
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Job Satisfaction (Employed Graduates)').classes('font-bold text-[#0b1132] mb-2 text-center')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'xAxis': {'type': 'category', 'data': order,
                      'axisLabel': {'fontSize': 9, 'interval': 0, 'rotate': 15}},
            'yAxis': {'type': 'value', 'name': 'Graduates'},
            'series': [{'type': 'bar', 'data': vals, 'barWidth': '55%',
                        'label': {'show': True, 'position': 'top'}}]
        }).classes('w-full h-[320px]')

# ── GENDER ANALYSIS ────────────────────────────────────────────────────────────
def _gender_employment_rate_bar(df):
    df2 = df.copy()
    df2['gl'] = _amap(df2['gender'], GENDER_LABELS)
    genders   = ['Male','Female']
    colors    = {'Male':'#3B82F6','Female':'#EC4899'}
    vals = []
    for g in genders:
        grp = df2[df2['gl']==g]; total=len(grp)
        emp = int((grp['employment_status']==1).sum())
        vals.append({'value': _pct(emp, total), 'name': g, 'count_val': total,
                     'itemStyle':{'color': colors[g],'borderRadius':[4,4,0,0]}})
    with ui.card().classes('flex-1 min-w-[300px] p-4 shadow-sm border rounded-xl bg-white'):
        ui.label('Employment Rate by Gender').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.name+"</b><br/>Total: <b>"+p.data.count_val+"</b><br/>Rate: <b>"+p.value+"%</b>"}'},
            'xAxis': {'type': 'category', 'data': genders},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel':{'formatter':'{value}%'}},
            'series': [{'type': 'bar', 'barWidth': '40%', 'data': vals,
                        'label': {'show': True, 'position': 'top', 'formatter': '{c}%'}}]
        }).classes('w-full h-[300px]')

def _gender_faculty_clustered(df):
    df2 = _fac_col(df.copy())
    df2['gl'] = _amap(df2['gender'], GENDER_LABELS)
    facs = [f for f in ALL_FACS if f in df2['__fac'].values]
    m_data, f_data = [], []
    for fac in facs:
        for gender, lst in [('Male', m_data),('Female', f_data)]:
            grp = df2[(df2['__fac']==fac)&(df2['gl']==gender)]
            total=len(grp); emp=int((grp['employment_status']==1).sum())
            lst.append({'value': _pct(emp, total), 'count_val': total})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Employment Rate by Gender & Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'item', ':formatter': 'function(p){return p.marker+" <b>"+p.seriesName+" – "+p.name+"</b><br/>Total: <b>"+p.data.count_val+"</b><br/>Rate: <b>"+p.value+"%</b>"}'},
            'color': ['#3B82F6','#EC4899'],
            'legend': {'data': ['Male','Female'], 'top': 0},
            'xAxis': {'type': 'category', 'data': facs, 'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel':{'formatter':'{value}%'}},
            'series': [
                {'name':'Male','type':'bar','data': m_data,'label':{'show':True,'position':'top','formatter':'{c}%','fontSize':9}},
                {'name':'Female','type':'bar','data': f_data,'label':{'show':True,'position':'top','formatter':'{c}%','fontSize':9}},
            ]
        }).classes('w-full h-[350px]')

def _gender_salary_stacked(df):
    sub = df.dropna(subset=['salary','gender']).copy()
    sub['gl']  = _amap(sub['gender'], GENDER_LABELS)
    sub['sal'] = _amap(sub['salary'], SALARY_LABELS)
    sal_order  = ['< 25k','25k–49k','50k–74k','75k–99k','100k+']
    sal_colors = ['#F87171','#FBBF24','#34D399','#3B82F6','#8B5CF6']
    genders    = ['Male','Female']
    series = []
    for i, s in enumerate(sal_order):
        vals = []
        for g in genders:
            grp = sub[sub['gl']==g]; total=len(grp)
            vals.append(_pct(int((grp['sal']==s).sum()), total))
        series.append({'name': s,'type':'bar','stack':'total','data': vals,
                       'itemStyle':{'color':sal_colors[i]},
                       'label':{'show':True,'formatter':'{c}%','fontSize':10}})
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Salary Distribution by Gender').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': sal_order, 'top': 0, 'textStyle':{'fontSize':10}},
            'xAxis': {'type': 'category', 'data': genders},
            'yAxis': {'type': 'value', 'max': 100, 'axisLabel':{'formatter':'{value}%'}},
            'series': series,
        }).classes('w-full h-[320px]')


# ══════════════════════════════════════════════════════════════════════════════
# YEAR ANALYSIS TAB  (All Years mode only)
# ══════════════════════════════════════════════════════════════════════════════

def _year_kpi_summary(df):
    """Small KPI cards showing per-year totals."""
    years = sorted(df['__year'].dropna().unique())
    with ui.row().classes('w-full gap-3 flex-wrap mb-2'):
        for y in years:
            sub   = df[df['__year'] == y]
            total = len(sub)
            emp   = int((sub['employment_status'] == 1).sum())
            rate  = _pct(emp, total)
            with ui.card().classes('flex-1 min-w-[120px] p-3 rounded-xl shadow-sm border bg-white text-center'):
                ui.label(str(y)).classes('text-xs font-bold text-gray-500 uppercase')
                ui.label(f'{rate}%').classes('text-2xl font-black mt-1').style('color:#8B5CF6')
                ui.label(f'{emp} / {total}').classes('text-xs text-gray-400 mt-0.5')


def _overall_emp_rate_over_years(df):
    """Overall employment rate trend – bar + line combo."""
    years = sorted(df['__year'].dropna().unique())
    rates, totals, emp_counts = [], [], []
    for y in years:
        sub   = df[df['__year'] == y]
        total = len(sub)
        emp   = int((sub['employment_status'] == 1).sum())
        rates.append(_pct(emp, total))
        totals.append(total)
        emp_counts.append(emp)

    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Overall Employability Rate Over Years').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'cross'}},
            'legend': {'data': ['Total Graduates', 'Employed', 'Employment Rate (%)'], 'top': 0},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': [
                {'type': 'value', 'name': 'Graduates', 'position': 'left'},
                {'type': 'value', 'name': 'Rate (%)', 'position': 'right',
                 'max': 100, 'axisLabel': {'formatter': '{value}%'}},
            ],
            'series': [
                {'name': 'Total Graduates', 'type': 'bar', 'data': totals,
                 'itemStyle': {'color': '#6baed6', 'borderRadius': [4,4,0,0]},
                 'label': {'show': True, 'position': 'top', 'fontSize': 10}},
                {'name': 'Employed', 'type': 'bar', 'data': emp_counts,
                 'itemStyle': {'color': '#10B981', 'borderRadius': [4,4,0,0]},
                 'label': {'show': True, 'position': 'top', 'fontSize': 10}},
                {'name': 'Employment Rate (%)', 'type': 'line', 'yAxisIndex': 1,
                 'data': rates, 'smooth': True,
                 'lineStyle': {'color': '#8B5CF6', 'width': 3},
                 'itemStyle': {'color': '#8B5CF6'},
                 'symbol': 'circle', 'symbolSize': 8,
                 'label': {'show': True, 'formatter': '{c}%', 'fontSize': 10,
                           'color': '#8B5CF6', 'fontWeight': 'bold'}},
            ],
        }).classes('w-full h-[380px]')


def _emp_rate_by_faculty_over_years(df):
    """Line chart – one line per faculty, x-axis = survey year."""
    years = sorted(df['__year'].dropna().unique())
    df2   = _fac_col(df)
    facs  = [f for f in ALL_FACS if f in df2['__fac'].values]
    series = []
    for fac in facs:
        rates = []
        for y in years:
            sub   = df2[(df2['__fac'] == fac) & (df2['__year'] == y)]
            total = len(sub)
            emp   = int((sub['employment_status'] == 1).sum())
            rates.append(_pct(emp, total) if total > 0 else None)
        series.append({
            'name': fac, 'type': 'line', 'data': rates, 'smooth': True,
            'connectNulls': True,
            'lineStyle': {'color': FAC_COLORS.get(fac, '#9CA3AF'), 'width': 2},
            'itemStyle': {'color': FAC_COLORS.get(fac, '#9CA3AF')},
            'symbol': 'circle', 'symbolSize': 7,
            'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9},
        })
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Employability Rate Over Years by Faculty').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': facs, 'top': 0, 'textStyle': {'fontSize': 10}},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'name': 'Employment Rate (%)', 'max': 100,
                      'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[380px]')


def _unemp_rate_gender_over_years(df):
    """Grouped bar – Male vs Female unemployment rate per year."""
    years  = sorted(df['__year'].dropna().unique())
    df2    = df.copy()
    df2['gl'] = _amap(df2['gender'], GENDER_LABELS)
    genders   = ['Male', 'Female']
    colors    = {'Male': '#3B82F6', 'Female': '#EC4899'}
    series = []
    for g in genders:
        rates = []
        for y in years:
            sub   = df2[(df2['gl'] == g) & (df2['__year'] == y)]
            total = len(sub)
            unemp = int((sub['employment_status'] == 2).sum())
            rates.append(_pct(unemp, total) if total > 0 else 0)
        series.append({
            'name': g, 'type': 'bar',
            'data': [{'value': r, 'itemStyle': {'color': colors[g], 'borderRadius': [4,4,0,0]}}
                     for r in rates],
            'label': {'show': True, 'position': 'top', 'formatter': '{c}%', 'fontSize': 9},
        })
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Unemployment Rate by Gender Over Years').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': genders, 'top': 0},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'name': 'Unemployment Rate (%)', 'max': 100,
                      'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[350px]')


def _emp_sector_over_years(df):
    """Stacked bar – top sectors share per year."""
    years   = sorted(df['__year'].dropna().unique())
    sub     = df.dropna(subset=['employment_sector']).copy()
    sub['sec'] = _amap(sub['employment_sector'], EMP_SECTOR_LABELS)
    top_secs = sub['sec'].value_counts().head(6).index.tolist()
    sec_colors = ['#1a3a6b','#f5a623','#6baed6','#4caf50','#e53935','#9e9e9e']
    series = []
    for i, sec in enumerate(top_secs):
        vals = []
        for y in years:
            grp   = sub[sub['__year'] == y]
            total = len(grp)
            cnt   = int((grp['sec'] == sec).sum())
            vals.append(_pct(cnt, total) if total > 0 else 0)
        series.append({
            'name': sec, 'type': 'bar', 'stack': 'total', 'data': vals,
            'itemStyle': {'color': sec_colors[i % len(sec_colors)]},
            'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9},
        })
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Employment Sector Distribution Over Years (% of all graduates)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': top_secs, 'top': 0, 'textStyle': {'fontSize': 9}},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'name': '%', 'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[380px]')


def _salary_trend_over_years(df):
    """Stacked bar – salary band distribution per year."""
    years      = sorted(df['__year'].dropna().unique())
    sub        = df.dropna(subset=['salary']).copy()
    sub['sal'] = _amap(sub['salary'], SALARY_LABELS)
    sal_order  = ['< 25k','25k–49k','50k–74k','75k–99k','100k+']
    sal_colors = ['#F87171','#FBBF24','#34D399','#3B82F6','#8B5CF6']
    series = []
    for i, s in enumerate(sal_order):
        vals = []
        for y in years:
            grp   = sub[sub['__year'] == y]
            total = len(grp)
            cnt   = int((grp['sal'] == s).sum())
            vals.append(_pct(cnt, total) if total > 0 else 0)
        series.append({
            'name': s, 'type': 'bar', 'stack': 'total', 'data': vals,
            'itemStyle': {'color': sal_colors[i]},
            'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9},
        })
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Salary Band Distribution Over Years (% of employed)').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': sal_order, 'top': 0, 'textStyle': {'fontSize': 9}},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'name': '%', 'max': 100,
                      'axisLabel': {'formatter': '{value}%'}},
            'series': series,
        }).classes('w-full h-[380px]')


def _gender_ratio_over_years(df):
    """Line chart showing Male/Female ratio change per year."""
    years = sorted(df['__year'].dropna().unique())
    df2   = df.copy()
    df2['gl'] = _amap(df2['gender'], GENDER_LABELS)
    male_pcts, female_pcts = [], []
    for y in years:
        grp   = df2[df2['__year'] == y]
        total = len(grp)
        m = int((grp['gl'] == 'Male').sum())
        f = int((grp['gl'] == 'Female').sum())
        male_pcts.append(_pct(m, total))
        female_pcts.append(_pct(f, total))
    with ui.card().classes('w-full p-4 shadow-sm border rounded-xl bg-white mt-4'):
        ui.label('Gender Composition of Respondents Over Years').classes('font-bold text-[#0b1132] mb-2')
        ui.echart({
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['Male %','Female %'], 'top': 0},
            'xAxis': {'type': 'category', 'data': [str(y) for y in years],
                      'axisLabel': {'fontWeight': 'bold'}},
            'yAxis': {'type': 'value', 'max': 100, 'name': '%',
                      'axisLabel': {'formatter': '{value}%'}},
            'series': [
                {'name': 'Male %', 'type': 'line', 'data': male_pcts, 'smooth': True,
                 'lineStyle': {'color': '#3B82F6', 'width': 2},
                 'itemStyle': {'color': '#3B82F6'}, 'symbol': 'circle', 'symbolSize': 7,
                 'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9},
                 'areaStyle': {'color': 'rgba(59,130,246,0.1)'}},
                {'name': 'Female %', 'type': 'line', 'data': female_pcts, 'smooth': True,
                 'lineStyle': {'color': '#EC4899', 'width': 2},
                 'itemStyle': {'color': '#EC4899'}, 'symbol': 'circle', 'symbolSize': 7,
                 'label': {'show': True, 'formatter': '{c}%', 'fontSize': 9},
                 'areaStyle': {'color': 'rgba(236,72,153,0.1)'}},
            ],
        }).classes('w-full h-[320px]')


# ══════════════════════════════════════════════════════════════════════════════
# TAB RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def _tab_overview(df):
    _kpi_row(df)
    with ui.row().classes('w-full gap-4 flex-wrap'):
        _employment_status_donut(df)
        _gender_pie(df)
    _faculty_employment_bar(df)
    _timing_bar(df)

def _tab_emp_char(df):
    with ui.row().classes('w-full gap-4 flex-wrap'):
        _emp_type_donut(df)
        _sector_bar(df)
    _rank_faculty_stacked(df)
    _salary_faculty_stacked(df)

def _tab_emp_factors(df):
    _job_aspects_bar(df)
    _job_finding_bar(df)
    _edu_class_bar(df)

def _tab_unemp(df):
    _kpi_row(df)
    _unemp_reasons_bar(df)
    _unemp_by_faculty_bar(df)

def _tab_perceptions(df):
    with ui.row().classes('w-full gap-4 flex-wrap'):
        _degree_relevance(df)
        _job_satisfaction_bar(df)

def _tab_gender(df):
    with ui.row().classes('w-full gap-4 flex-wrap'):
        _gender_pie(df)
        _gender_employment_rate_bar(df)
    _gender_faculty_clustered(df)
    _gender_salary_stacked(df)

def _tab_year_analysis(df):
    """Year-over-year trend analysis. Only shown in All Years mode."""
    _year_kpi_summary(df)
    _overall_emp_rate_over_years(df)
    _emp_rate_by_faculty_over_years(df)
    _unemp_rate_gender_over_years(df)
    _emp_sector_over_years(df)
    _salary_trend_over_years(df)
    _gender_ratio_over_years(df)


# Base tabs (always shown)
BASE_TABS = [
    ('overview',    'OVERVIEW',                  _tab_overview),
    ('emp_char',    'EMPLOYMENT CHARACTERISTICS', _tab_emp_char),
    ('emp_factors', 'EMPLOYABILITY FACTORS',     _tab_emp_factors),
    ('unemp',       'UNEMPLOYMENT ANALYSIS',     _tab_unemp),
    ('perceptions', 'GRADUATE PERCEPTIONS',      _tab_perceptions),
    ('gender',      'GENDER ANALYSIS',           _tab_gender),
]

# Extra tab only in All Years mode
YEAR_TAB = ('year_analysis', 'YEAR ANALYSIS', _tab_year_analysis)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD RENDERER
# ══════════════════════════════════════════════════════════════════════════════

# Tab icons matching image-2 style
TAB_ICONS = {
    'overview':      '🏠',
    'emp_char':      '💼',
    'emp_factors':   '🔑',
    'unemp':         '📉',
    'perceptions':   '💬',
    'gender':        '👥',
    'year_analysis': '📅',
}

def _render_dashboard(df, selected_year, show_year_fn, load_fn, container):
    container.clear()

    is_all = (selected_year == 'All')
    tabs_to_show = BASE_TABS + ([YEAR_TAB] if is_all else [])

    TAB_TITLES = {
        'overview':      'Overview',
        'emp_char':      'Employment Characteristics',
        'emp_factors':   'Employability Factors',
        'unemp':         'Unemployment Analysis',
        'perceptions':   'Graduate Perceptions',
        'gender':        'Gender Analysis',
        'year_analysis': 'Year Analysis',
    }

    state = {'active': 'overview'}

    with container:
        # ── CSS (inject once) ─────────────────────────────────────────────────
        ui.add_head_html('''
        <style>
          .ge-tabbar  { display:flex; gap:6px; overflow-x:auto; padding:6px 8px;
                        background:#fff; border-radius:14px;
                        box-shadow:0 1px 4px rgba(0,0,0,.10); }
          .ge-tabbar::-webkit-scrollbar { height:4px; }
          .ge-tabbar::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }
          .ge-pill    { display:flex; align-items:center; gap:5px; white-space:nowrap;
                        padding:7px 14px; border-radius:9px; cursor:pointer;
                        font-size:11px; font-weight:700; letter-spacing:.4px;
                        color:#475569; background:transparent;
                        border:none; transition:background .18s,color .18s; }
          .ge-pill:hover  { background:#f1f5f9; color:#1e293b; }
          .ge-pill.active { background:#3b82f6; color:#fff; }
          .ge-panel       { display:none; }
          .ge-panel.active{ display:block; }
          .ge-back-btn    { display:inline-flex; align-items:center; gap:6px;
                            background:#fff; border:1px solid #d1d5db;
                            color:#374151; font-weight:700; font-size:13px;
                            padding:8px 18px; border-radius:8px; cursor:pointer;
                            box-shadow:0 1px 3px rgba(0,0,0,.08);
                            transition:background .15s; }
          .ge-back-btn:hover { background:#f9fafb; }
        </style>
        ''')

        # ── Header row ────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center justify-between mb-3 flex-wrap gap-2'):

            # BACK button as plain HTML element (avoids NiceGUI button quirks)
            back_btn = ui.element('button').classes('ge-back-btn').on('click', show_year_fn)
            with back_btn:
                ui.element('span').props('innerHTML="&#8592;"')   # ← arrow
                ui.element('span').props('innerHTML="BACK"')

            with ui.row().classes('items-center gap-2'):
                ui.label('🎓').classes('text-3xl')
                ui.label('Overall Graduate Employability').classes('text-2xl font-bold text-[#0b1132]')

            # Year dropdown
            years = _get_years()
            opts  = {'All': 'All Years', **{y: y for y in years}}
            cur_val = 'All' if selected_year == 'All' else selected_year
            sel = ui.select(
                opts,
                value=cur_val,
                on_change=lambda e: load_fn(e.value)
            ).classes('w-36')

        # ── Welcome heading — ABOVE tabs ──────────────────────────────────────
        welcome_label = ui.label(
            f'Welcome to Graduate Employability {TAB_TITLES["overview"]}'
        ).classes('text-2xl font-bold text-[#0b1132] mb-2')

        # ── Pill-tab navigation bar ───────────────────────────────────────────
        tab_bar    = ui.element('div').classes('ge-tabbar w-full mb-3')
        panel_host = ui.element('div').classes('w-full')

        # Build content panels
        panels = {}
        with panel_host:
            for key, _, renderer in tabs_to_show:
                with ui.element('div').classes(
                    'ge-panel' + (' active' if key == 'overview' else '')
                ) as panel:
                    renderer(df)
                panels[key] = panel

        # Build pill buttons + switcher
        btn_refs = {}

        def _make_switcher(target_key):
            def _switch():
                old = state['active']
                btn_refs[old].classes(remove='active')
                panels[old].classes(remove='active')
                btn_refs[target_key].classes(add='active')
                panels[target_key].classes(add='active')
                state['active'] = target_key
                welcome_label.text = (
                    f'Welcome to Graduate Employability '
                    f'{TAB_TITLES.get(target_key, target_key.replace("_"," ").title())}'
                )
            return _switch

        with tab_bar:
            for key, label, _ in tabs_to_show:
                icon = TAB_ICONS.get(key, '📋')
                btn = ui.element('button').classes(
                    'ge-pill' + (' active' if key == 'overview' else '')
                ).on('click', _make_switcher(key))
                with btn:
                    ui.element('span').props(f'innerHTML="{icon} "')
                    ui.element('span').props(f'innerHTML="{label}"')
                btn_refs[key] = btn

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE ROUTE
# ══════════════════════════════════════════════════════════════════════════════

@ui.page('/graduate_employability')
def graduate_employability_page():
    ui.query('body').style('background-color:#d3dae0;')
    settings_dialog = create_settings_dialog()
    sidebar.create_sidebar(settings_dialog, active_page='/graduate_employability')

    main_container = ui.column().classes('p-2 w-full')

    def load_dashboard(selected_year: str):
        df = _load_data(selected_year)
        if df is None or df.empty:
            main_container.clear()
            with main_container:
                with ui.card().classes('w-full p-8 bg-white rounded-2xl shadow-sm'):
                    ui.label('⚠️ Data not found').classes('text-xl font-bold text-red-500')
                    ui.label(
                        f'Table "graduate_employability_{selected_year}" not found in survey.db. '
                        'Database Management ෙකින් data import කරන්න.'
                    ).classes('text-gray-500 mt-2')
                    ui.button('BACK', icon='arrow_back', on_click=show_year_selection)\
                        .props('flat')\
                        .classes('text-black bg-white border border-[#3b82f6] rounded-md px-4 shadow-sm')\
                        .style('height: 38px;')
            return
        _render_dashboard(df, selected_year, show_year_selection, load_dashboard, main_container)

    def show_year_selection():
        main_container.clear()
        with main_container:
            with ui.card().classes('w-full p-8 shadow-sm border border-gray-100 rounded-2xl bg-white'):
                ui.label('🎓 Graduate Employability').classes('text-4xl font-bold text-[#0b1132]')
                ui.label('Centre for Strategic Planning & University Statistics').classes('text-lg mt-2 ml-6')
                ui.label('Welcome to the Graduate Employability Survey').classes('text-gray-500 ml-6 mt-1 mb-8')

                with ui.card().classes(
                    'w-64 p-3 ml-6 cursor-pointer hover:bg-gray-100 border transition-all'
                ).on('click', lambda: load_dashboard('All')):
                    ui.label('All Years').classes('text-lg font-bold text-[#0b1132] text-center w-full')

                years = _get_years()
                for year in years:
                    with ui.card().classes(
                        'w-64 p-3 ml-6 mt-3 cursor-pointer hover:bg-gray-100 border transition-all'
                    ).on('click', lambda e, y=year: load_dashboard(y)):
                        ui.label(year).classes('text-lg font-bold text-[#0b1132] text-center w-full')

                if not years:
                    ui.label(
                        'ℹ️ No data found. Database Management ෙකින් data import කරන්න.'
                    ).classes('text-sm text-gray-400 ml-6 mt-4')

    show_year_selection()