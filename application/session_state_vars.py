import streamlit as st
from application import utils as util

# print("INICIANDO MODULO SESSION STATE")
## *================================================================================================================
## Definimos los valores iniciales de la sesión de estado y monitoreamos los cambios de los componentes checkbob y multiselect

def run():
    if "all_option_year" not in st.session_state:
        st.session_state.all_option_year = True
        st.session_state.selected_options_year = util.get_years()
        st.session_state.disabled_year = True

    if "all_option_month" not in st.session_state:
        st.session_state.all_option_month = True
        st.session_state.selected_options_month = util.get_month()
        st.session_state.disabled_month = True

def check_change_year():
    if st.session_state.all_option_year:
        st.session_state.disabled_year = True
        st.session_state.selected_options_year = util.get_years()
    else:
        st.session_state.disabled_year = False
        st.session_state.selected_options_year = util.get_years()
        st.session_state.disabled_month = False

def check_change_month():
    if st.session_state.all_option_month:
        st.session_state.disabled_month = True
        st.session_state.selected_options_month = util.get_month()
    else:
        st.session_state.disabled_month = False
        st.session_state.selected_options_month = util.get_month()
    st.session_state.disabled_month = True if st.session_state.all_option_month else False

def multi_change_year():
    if len(st.session_state.selected_options_year) !=0:
        st.session_state.all_option_year = True

    st.session_state.all_option_year = True if len(st.session_state.selected_options_year) == 3 else False
    st.session_state.disabled_year = True if len(st.session_state.selected_options_year) == 3 else False

def multi_change_month():
    st.session_state.all_option_month = True if len(st.session_state.selected_options_month) == 12 else False
    st.session_state.disabled_month = True if len(st.session_state.selected_options_month) == 12 else False