import streamlit as st
from PIL import Image

def run():
  st.subheader("Segmentación de características basado en el comportamiento")
  st.write("Se ha utilizado datos de clientes, valor de compras, compras recientes.")
  grafico1()
  with st.expander("Más Descripción", expanded=False):
    st.write("Compara los resultados a través de diferentes valores de K que indica la distancia media entre los puntos de datos y el centroide de su clúster, se traza la distancia media al centroide en función de K para lo cual se utiliza el método de codo, donde la tasa de disminución se desplaza brúscamente, para determinar aproximadamente el valor K.")
  grafico2()
  with st.expander("Más Descripción", expanded=False):
    st.write("Se ha utilizado features_scaled para la normalización de datos previo a la generación de los segmentos,\nlos cuales serán utilizados en los próximos cuadros.")
    st.write("•	Segmento 0 = Clientes con mayor frecuencia de compras.")
    st.write("•	Segmento 1 = Clientes con compras con menos de 300 días de antigüedad y bajo valor monetario.")
    st.write("•	Segmento 2 = Clientes con compras de mayor valor monetario.")
    st.write("•	Segmento 3 = Clientes con compras con más de 300 días de antigüedad y bajo valor monetario.")
  grafico3()
  grafico4()

def grafico1():
  grafico_1 = Image.open('assets/k_optimo_codo.png')
  st.image(grafico_1)

def grafico2():
  grafico_2 = Image.open('assets/grafico_2.png')
  st.image(grafico_2)

def grafico3():
  grafico_3 = Image.open('assets/grafico_3.png')
  st.image(grafico_3)

def grafico4():
  grafico_4 = Image.open('assets/grafico_4.png')
  st.image(grafico_4)