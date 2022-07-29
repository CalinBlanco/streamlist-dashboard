import streamlit as st
from application import conn_aws as cn
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from application import utils as util


def run():
  st.subheader("Segmentación de características basado en el comportamiento")
  st.text("Se ha utilizado datos de clientes, valor de compras, compras recientes.")
  preprocesamiento(st.session_state.data_final)
  grafico1()
  with st.expander("Más Descripción", expanded=False):
    st.caption("Compara los resultados a través de diferentes valores de K que indica la distancia media entre los puntos de datos y el centroide de su clúster, se traza la distancia media al centroide en función de K para lo cual se utiliza el método de codo, donde la tasa de disminución se desplaza brúscamente, para determinar aproximadamente el valor K.")
  grafico2()
  with st.expander("Más Descripción", expanded=False):
    st.text("Se ha utilizado features_scaled para la normalización de datos previo a la generación de los segmentos, los cuales serán utilizados en los próximos cuadros.")
    st.text("•	Segmento 0 = Clientes con mayor frecuencia de compras.")
    st.text("•	Segmento 1 = Clientes con compras con menos de 300 días de antigüedad y bajo valor monetario.")
    st.text("•	Segmento 2 = Clientes con compras de mayor valor monetario.")
    st.text("•	Segmento 3 = Clientes con compras con más de 300 días de antigüedad y bajo valor monetario.")
  grafico3()
  grafico4()

def preprocesamiento(df):
  df_status = df[df['order_status'] == 'delivered']
  df_status['order_status'].value_counts()

  Q1 = df['payment_value'].quantile(0.25)
  Q3 = df['payment_value'].quantile(0.75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5*IQR
  upper_bound = Q3 + 1.5*IQR
  out_list = df.index[(df['payment_value'] < lower_bound) | (df['payment_value'] > upper_bound)]
  out_list = sorted(set(out_list))

  order_mes = df.rename(columns = {'order_approved_at': 'num_of_orders'})
  df_clean  = order_mes.drop(out_list, axis = 0)

  max_date = df_clean.groupby('customer_id')['num_of_orders'].max().reset_index()
  max_date = max_date.rename({'num_of_orders':'most_recent'},axis = 1)
  max_date['r_score'] = (max_date['most_recent'].max() - max_date['most_recent']).dt.days

  n_transaction = df_clean.groupby('customer_id')['order_id'].count().reset_index()
  n_transaction = n_transaction.rename({'order_id':'f_score'},axis = 1)

  avg_purchase = df_clean.groupby('customer_id')['payment_value'].mean().reset_index()
  avg_purchase = avg_purchase.rename({'payment_value':'m_score'},axis = 1)

  merge = max_date.merge(n_transaction, how = 'left', on = 'customer_id')
  merge = merge.merge(avg_purchase, how = 'left', on = 'customer_id')

  df_rfm = merge[['customer_id','r_score','f_score','m_score']]
  df_rfm.dropna(inplace=True)

  if "features_scaled" not in st.session_state:
    features = df_rfm.drop('customer_id',axis = 1)
    scale = StandardScaler()
    st.session_state.features_scaled = scale.fit_transform(features)
  
  if "df_seg_kmeans" not in st.session_state:
    kmeans = KMeans(n_clusters = 4, init = 'k-means++',random_state = 1)
    kmeans.fit(st.session_state.features_scaled)
    df_seg_kmeans = df_rfm.copy()
    df_seg_kmeans['segments'] = kmeans.labels_
    st.session_state.df_seg_kmeans = df_seg_kmeans

  if "df_analysis" not in st.session_state:
    df_analysis = df_seg_kmeans.groupby('segments').mean()
    df_analysis['#observaciones'] = df_seg_kmeans[['segments','f_score']].groupby(['segments']).count()
    df_analysis['Porcentaje'] = df_analysis['#observaciones'] / df_analysis['#observaciones'].sum()*100
    df_analysis['r_score'] = df_analysis['r_score'].round(2)
    df_analysis['f_score'] = df_analysis['f_score'].round(2)
    df_analysis['m_score'] = df_analysis['m_score'].round(2)
    df_analysis['Porcentaje'] = df_analysis['Porcentaje'].round(2)
    st.session_state.df_analysis = df_analysis


def grafico1():
  wcss = []
  dict_kmeans = {}
  for i in range(1,11):
      kmeans = KMeans(n_clusters=  i,init = 'k-means++', random_state = 1)
      kmeans.fit(st.session_state.features_scaled)
      wcss.append(kmeans.inertia_)
      dict_kmeans[str(i)]=str(kmeans.inertia_)
  
  # data_kmeans = pd.DataFrame.from_dict(dict_kmeans)

  figure = make_subplots(rows=1, cols=1)
  figure.add_trace(
      go.Scatter(x=list(range(1,11)), y=wcss, mode="lines+markers",marker=dict(size=10, color="LightSeaGreen")),
      secondary_y=False,
  )
  # Set x-axis title
  figure.update_xaxes(title_text="Número de Clúster",tickangle=-30)

  # Set y-axis title
  figure.update_yaxes(title_text="Suma de cuadrados dentro del grupo (WCSS)", secondary_y=False)

  figure['layout']['xaxis1']['showgrid'] = False

  # Add figure title
  figure.update_layout(
      title_text="K óptimo o un número óptimo de Cluster",
      hovermode="x unified",
      plot_bgcolor= 'rgba(0, 0, 0, 0)',
      paper_bgcolor= 'rgba(0, 0, 0, 0)',
      font_color='black',
      hoverlabel=dict(
          bgcolor="white",
          font_size=12,
          font_color="black"
          # font_family="Rockwell"
      )
  )

  st.plotly_chart(figure, use_container_width=True)



def grafico2():
  x_axis = st.session_state.df_seg_kmeans['m_score']
  y_axis = st.session_state.df_seg_kmeans['r_score']
  segment = st.session_state.df_seg_kmeans['segments']
  df_csv = st.session_state.df_seg_kmeans[['segments','m_score','r_score']]

  plt.figure(figsize = (10,8))
  plt.title("Agrupamiento de Clientes por Segmentos")
  plt.xlabel('m_score = Valor Promedio de la Compra (R$)') 
  plt.ylabel('f_score = Frecuencia de compras del cliente') 
  sns.scatterplot(x = x_axis, y = y_axis, hue = segment,
                  palette = 'Set2', legend = 'full')
  st.pyplot(plt)
  tabla_2_csv = util.convert_df(df_csv)
  st.download_button(
      label="Descargar dataset en CSV",
      data=tabla_2_csv,
      file_name='agrupamiento_por_segmentos.csv',
      mime='text/csv',
      key="2"
  )

def grafico3():
  x_axis = st.session_state.df_seg_kmeans['m_score']
  y_axis = st.session_state.df_seg_kmeans['f_score']
  df_csv = st.session_state.df_seg_kmeans[['segments','m_score','r_score']]
  plt.figure(figsize = (10,8))
  sns.scatterplot(x = x_axis, y = y_axis, hue = st.session_state.df_seg_kmeans['segments'],
                  palette = 'Set2', legend = 'full')
  plt.title("Comportamiento por Segmentos de Compras y el Valor Promedio")
  plt.ylabel('f_score = Frecuencia de compras del cliente') 
  plt.xlabel('m_score = Valor Promedio de la Compra (R$)') 
  st.pyplot(plt)
  tabla_3_csv = util.convert_df(df_csv)
  st.download_button(
      label="Descargar dataset en CSV",
      data=tabla_3_csv,
      file_name='comportamiento_por_segmentos_compras_y_valor.csv',
      mime='text/csv',
      key="3"
  )

def grafico4():
  x_axis = st.session_state.df_seg_kmeans['f_score']
  y_axis = st.session_state.df_seg_kmeans['r_score']
  df_csv = st.session_state.df_seg_kmeans[['segments','m_score','r_score']]
  plt.figure(figsize = (10,8))
  sns.scatterplot(x = x_axis, y = y_axis, hue = st.session_state.df_seg_kmeans['segments'],
                  palette = 'Set2', legend = 'full')
  plt.title("Comportamiento de Frecuencia de Compras recientes")
  plt.ylabel('r_score = Días de la última compra') 
  plt.xlabel('f_score = Frecuencia de compras del cliente') 
  st.pyplot(plt)
  tabla_4_csv = util.convert_df(df_csv)
  st.download_button(
      label="Descargar dataset en CSV",
      data=tabla_4_csv,
      file_name='comportamiento_por_segmentos_de_compras_y_valor.csv',
      mime='text/csv',
      key="4"
  )