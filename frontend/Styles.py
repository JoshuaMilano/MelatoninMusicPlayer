background_colour = '#403D88'


STYLESHEET = f'''
QMainWindow {{
    background-color: {background_colour};
}}

QSlider::groove:horizontal {{
    background: #8B639B;
}}

QSlider::handle:horizontal {{
    height: 8px;
    background: transparent;
}}

QSlider::add-page:horizontal {{
    background: transparent;
}}

QSlider::sub-page:horizontal {{
    background: #AF719D;
}}
'''