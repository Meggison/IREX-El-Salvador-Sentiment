import base64
import streamlit as st
    
def set_page_background(png_file):
    @st.cache_data()
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
        <style>
        {header_css}
        .stApp {{
                background-image: url("data:image/png;base64,{bin_str}");
            }}
        </style>
    '''.format(
        header_css=open('assets/css/styles.css').read(),
        bin_str=bin_str
    )
    st.markdown(page_bg_img, unsafe_allow_html=True)