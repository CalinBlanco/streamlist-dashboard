import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

def run():
  st.title("Predicciones")
  st.subheader("Estimación de Costo del Flete")
  with st.expander("",expanded=True):
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
      price = st.number_input('Ingresar precio(R$)')
      # st.write('The current number is ', number1)
    with col2:
      product_weight_g = st.number_input('Ingresar peso(gr)')
      # st.write('The current number is ', number2)
    with col3:
      product_length_cm = st.number_input('Ingresar longitud(cm)')
      # st.write('The current number is ', number3)
    
    col4, col5 = st.columns([3,3])

    with col4:
      product_height_cm = st.number_input('Ingresar altura(cm)')
      # st.write('The current number is ', number4)
    with col5:
      product_width_cm = st.number_input('Ingresar ancho(cm)')
      # st.write('The current number is ', number5)
    
    col6, col7 = st.columns([1,5])
    
    with col6:
      boton = st.button("Calcular")
      if boton:
        prediccion = prediction(price,product_weight_g,product_length_cm,product_height_cm,product_width_cm)

    with col7:  
      if boton:
        st.subheader("R$" + str(prediccion))

# ==============================FUNCIONES======================================================
def pre_procesamiento(df_orders):
  regression = df_orders[df_orders['order_status']=='delivered'][['purchase_date', 'price', 'freight_value', 'product_weight_g', 'product_length_cm',
        'product_height_cm', 'product_width_cm',]]
  regression = regression[['price', 'freight_value', 'product_weight_g', 'product_length_cm',
        'product_height_cm', 'product_width_cm']]
  regression.drop_duplicates(inplace=True)
  regression.dropna(inplace=True)
  return regression


def training(regression):
  X = regression.drop(columns=['freight_value'], axis=1)
  Y = regression['freight_value']
  X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
  return X_train, Y_train

def random_forest(X_train,Y_train):
  model2 = RandomForestRegressor(n_estimators=100, random_state=42)
  y2 = model2.fit(X_train, Y_train)
  # y2_preds = y2.predict(X_test)
  return y2

def prediction(price,product_weight_g,product_length_cm,product_height_cm,product_width_cm):
  regression = pre_procesamiento(st.session_state.data_final)
  X_, Y_ = training(regression)
  r_forest = random_forest(X_, Y_)
  pred = r_forest.predict(pd.DataFrame({'price':price, 'product_weight_g':product_weight_g, 'product_length_cm':product_length_cm, 'product_height_cm':product_height_cm, 'product_width_cm':product_width_cm}, index=[0]))
  return pred[0].round(2)

# ====================================================================================

def ml(df):

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

  features = df_rfm.drop('customer_id',axis = 1)
  scale = StandardScaler()
  features_scaled = scale.fit_transform(features)

  features = df_rfm.drop('customer_id',axis = 1)
  scale = StandardScaler()
  features_scaled = scale.fit_transform(features)

  kmeans = KMeans(n_clusters = 4, init = 'k-means++',random_state = 1)
  kmeans.fit(features_scaled)
  df_seg_kmeans = df_rfm.copy()
  df_seg_kmeans['segments'] = kmeans.labels_

  df_analysis = df_seg_kmeans.groupby('segments').mean()
  df_analysis['#observations'] = df_seg_kmeans[['segments','f_score']].groupby(['segments']).count()
  df_analysis['Percentage'] = df_analysis['#observations'] / df_analysis['#observations'].sum()
