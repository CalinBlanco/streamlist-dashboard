import streamlit as st


def run():
    st.set_page_config(
        page_title="Dashboard OLIST",
        page_icon=":chart_with_upwards_trend:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    with open('style/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)