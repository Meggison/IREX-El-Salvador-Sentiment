import streamlit as st
from constants import ANALYSIS_REPORT_TEMPLATE


def analyse_sentiment_page():
    st.write("""
            <div style='text-align:center;'>
                <h1 style='text-align:center; font-size: 300%;'>Analyse Sentiment</h1>
                <p style=' color: #9c9d9f'>Paste the text to get the analysis report.</p>
                <hr>
            </div>
             """
    , unsafe_allow_html=True)
    
    user_text_input = st.text_area('Paste your text here', key='text')
    
    with st.columns(4)[-1]:
        submit_button_container = st.empty()

    submit_button = submit_button_container.button('Submit', key='submit_button', use_container_width=True)
    if user_text_input and submit_button:
        submit_button_container.empty()
        st.write(ANALYSIS_REPORT_TEMPLATE.format(sentiment_score="N/A", sentiment="N/A", sentiment_category="N/A"))

    elif user_text_input is None and submit_button is not None:
        st.toast("Text area cannot be empty.", icon="⚠️")