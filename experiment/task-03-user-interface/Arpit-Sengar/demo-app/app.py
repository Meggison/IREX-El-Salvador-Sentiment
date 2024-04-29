import streamlit as st
from st_on_hover_tabs import on_hover_tabs

from utils import set_page_background
from visualizations import visualization_page
from analyse_sentiment import analyse_sentiment_page
from constants import PAGE_BANNER, PAGE_FAVICON, PAGE_BACKGROUND, ANALYSIS_REPORT_TEMPLATE

st.set_page_config(page_title='Sentiment Analysis Tool', page_icon=PAGE_FAVICON, layout='wide')
set_page_background(PAGE_BACKGROUND)



if 'disable_button' not in st.session_state:
    st.session_state['disable_button'] = False

with st.sidebar:
    st.write('<br><br><br><br>', unsafe_allow_html=True)
    selected_task = on_hover_tabs(
        tabName=['Home Page', 'Analyse Sentiment', 'Visualizations', 'About Us'],
        iconName=['home', 'engineering', 'insert_chart', 'contact_support'],
        styles = {
            'navtab': {'background-color':'#ffffff',
                        'color': '#ff0290',
                        'padding': '40px 0px 10px 0px',
                        'border-radius': '0px',
                        'font-size': '18px',
                        'transition': '.5s',
                        'white-space': 'nowrap',
                        'text-transform': 'uppercase',
            },
            'tabOptionsStyle': {':hover :hover': {'color': '#170034',
                                            'cursor': 'pointer'},
                            },
            'iconStyle':{'position':'fixed',
                        'left':'11.5px'},
            'tabStyle' : {'background-color':'rgba(0, 0, 0, 0)',
                        'list-style-type': 'none',
                        'margin-bottom': '30px',
                        },
        },
        key="1",
        default_choice=1)

if selected_task == 'Home Page':
    with st.columns([3,4,3])[1]:
        st.image(PAGE_BANNER, use_column_width="auto")
    
    st.write(open('assets/html_components/home.html', 'r').read(), unsafe_allow_html=True)

elif selected_task == 'Analyse Sentiment':
    analyse_sentiment_page()

elif selected_task == 'Visualizations':
    visualization_page()
    
elif selected_task == 'About Us':
    with open("assets/txt/contributors.txt", "r") as f:
        data = f.read().splitlines()
        full_string = ""
        
        for i in range(0, len(data), 3):
            try:
                contributor1 = data[i].split(",")[0].strip().title()
                contributor2 = data[i + 1].split(",")[0].strip().title()
                contributor3 = data[i + 2].split(",")[0].strip().title()

                contributors = f"""<tr>
                    <td>{contributor1}</td>
                    <td>{contributor2}</td>
                    <td>{contributor3}</td>
                </tr>
                """
                full_string += contributors
            
            except IndexError:
                if len(data[i:])==2:
                    full_string += f"""<tr>
                            <td>
                                {data[i:][0].split(",")[0].strip().title()}
                            </td>
                            <td>
                                {data[i:][1].split(",")[0].strip().title()}
                            </td>
                        </tr>
                    """
                elif len(data[i:])==1:
                    full_string += f"""<tr>
                            <td>
                                {data[i:][0].split(",")[0].strip().title()}
                            </td>
                        </tr>
                    """
        with open('assets/html_components/team.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
            
        st.write(html_content.format(team=full_string), unsafe_allow_html=True)