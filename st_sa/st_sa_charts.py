from nicegui import ui
import pandas as pd

def draw_gender_donut_chart(df):
    """Gender column එක පාවිච්චි කරලා Donut Chart එක අඳිනවා"""
    
    # Column එකේ නම හරියටම database එකේ තියෙන විදිහට දෙන්න ඕනේ. 
    # (උදා: 'Gender:  (ස්ත්‍රී පුරුෂ භාවය):' හෝ 'Gender')
    # අපි දැනට 'Gender' කියලා හිතමු, ඔයාගේ DB එකේ තියෙන නමට මේක වෙනස් කරන්න.
    gender_column = 'Gender:  (ස්ත්‍රී පුරුෂ භාවය):' 
    
    if gender_column not in df.columns:
        ui.label(f"'{gender_column}' තීරුව දත්ත ගබඩාවේ සොයාගැනීමට නොහැක.").classes('text-red-500')
        return

    # Pandas වලින් Male/Female ගණන හොයාගැනීම
    gender_counts = df[gender_column].value_counts()
    
    # ECharts වලට ඕන විදිහට Data ටික සකස් කිරීම
    chart_data = []
    for index, value in gender_counts.items():
        # පාට වෙනස් කරන්න පුළුවන් (Female = රෝස, Male = නිල් වගේ)
        color = '#E91E63' if str(index).strip().lower() == 'female' else '#3B82F6'
        chart_data.append({'value': int(value), 'name': str(index), 'itemStyle': {'color': color}})

    # NiceGUI EChart එක ඇඳීම (Donut Chart)
    with ui.card().classes('p-6 border shadow-sm rounded-xl bg-white w-full max-w-md mx-auto'):
        ui.label('Gender Distribution').classes('text-xl font-bold mb-4 text-[#0b1132] text-center')
        
        ui.echart({
            'tooltip': {'trigger': 'item'},
            'legend': {'bottom': '0%', 'left': 'center'},
            'series': [
                {
                    'name': 'Gender',
                    'type': 'pie',
                    'radius': ['40%', '70%'], # මේ අගයන් දෙක නිසා තමයි මැද හිස්වෙලා Donut එකක් හැදෙන්නේ
                    'avoidLabelOverlap': False,
                    'itemStyle': {'borderRadius': 10, 'borderColor': '#fff', 'borderWidth': 2},
                    'label': {'show': False, 'position': 'center'},
                    'data': chart_data
                }
            ]
        }).classes('w-full h-72')