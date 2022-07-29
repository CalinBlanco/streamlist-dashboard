import streamlit as st
from kpi_names import ST_KPI

from application import utils, session_state_vars as ssv, routes, conn_aws as cn



def run(selected_option = 'ventas'):
    st.sidebar.caption(ST_KPI[selected_option.capitalize()]['texto'])
    # SESSION STATE INITIALIZE
    cn.run()
    ssv.run()

    anios = utils.get_years()
    meses = utils.get_month()

    if st.session_state.mostrar_filtros:
        with st.expander("Opciones de Filtrado",expanded=True):
            f1, f2= st.columns([4,4])
            f1.checkbox('Todos los años', key="all_option_year", on_change=ssv.check_change_year)
            if st.session_state.all_option_year == False:
                f1.multiselect('Años:', anios,key="selected_options_year", on_change=ssv.multi_change_year, \
                    disabled=st.session_state.disabled_year)

            f2.checkbox('Todos los Meses', key="all_option_month", on_change=ssv.check_change_month)
            if st.session_state.all_option_month == False:
                f2.multiselect('Meses:', meses,key="selected_options_month", on_change=ssv.multi_change_month, \
                    disabled=st.session_state.disabled_month)
            
        result = st.button('Filtrar resultados')
        if result:
            routes.run()
    else:
        routes.run()

          
  # f3, f4 = st.columns(2)
  # f3.select_slider("Años", options=(['2016','2017','2018']), value="2016", disabled=False)
  # st.title("Principales Indicadores de Olist")


