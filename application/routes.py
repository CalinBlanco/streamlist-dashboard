import streamlit as st
from pages_st import segmentacion, ventas, distribucion, geolocalizacion, machine_learning


def run():
  selected_option = st.session_state.pagina
  if selected_option == 'ventas':
    ventas.run()
  elif selected_option == 'distribución':
    distribucion.run()
  elif selected_option == 'geolocalización':
    geolocalizacion.run()
  elif selected_option == 'predicciones':
    machine_learning.run()
  elif selected_option == 'segmentación':
    segmentacion.run()

  