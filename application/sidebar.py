import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image

from kpi_names import ST_KPI

## ******** Diccionario que me permite llamar a las funciones de las páginas
page_names_to_funcs = {
    "ventas": "ventas",
    "pagos": "pagos",
    "distribución": "distribución",
    "tiempos": "tiempos",
    "vendedores": "vendedores",
    "geolocalización": "geolocalización",
    "predicciones":"predicciones",
    "segmentación":"segmentación"
}


def run():
  kpi_icon = []
  kpi_funtion = []
  logo = Image.open('assets/logo.png')
  kpi_menu = list(ST_KPI.keys())
  for x in kpi_menu:
    kpi_icon.append(ST_KPI[x]['icon'])

  for x in kpi_funtion:
    kpi_funtion.append(ST_KPI[x]['fun'])

  # kpi_icon = kpi_icon
  # kpi_funtion = kpi_funtion

  with st.sidebar:
    st.title("Análisis de Mercados E-Commerce")
    st.image(logo)
    selected = option_menu("Dashboard", kpi_menu, 
        default_index=0,menu_icon="speedometer",icons=kpi_icon)
        
  ## ******** Aquí enviamos a la función
  st.session_state.pagina = page_names_to_funcs[selected.lower() if selected else 'ventas']
  
  if st.session_state.pagina in ['geolocalización','predicciones','segmentación']:
    st.session_state.mostrar_filtros = False
  else:
    st.session_state.mostrar_filtros = True
  # llamar_pagina = page_names_to_funcs[selected.lower() if selected else 'ventas']
  # print("FUNCION:",funcion_pagina)
  return st.session_state.pagina
