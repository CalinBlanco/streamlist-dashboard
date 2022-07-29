import streamlit as st
from application import conn_aws as cn
## ******** Extrayendo meses del dataset(data_final.csv) y los muestra ordenado

# data_final = con.run()
if "data_final" not in st.session_state:
    # st.session_state.data_final = cn.connection()
    cn.run()
    # print("DATA_FINAL DESDE UTILS",st.session_state.data_final)

data_final = st.session_state.data_final
# print(data_final)


def get_month():
  # data_final = st.session_state.data_final
  # data_final = con.run()
  # print("TIPO DE DATO data_final:",type(data_final))
  meses = data_final.groupby(['purchase_month','purchase_month_name'])['purchase_month_name'].agg('count').to_frame()
  meses.drop(['purchase_month_name'],axis=1,inplace=True)
  meses.reset_index(inplace=True)
  meses.rename(columns={'purchase_month':'nro_mes','purchase_month_name':'nombre_mes'}, inplace=True)
  meses['nombre_mes'].to_list()
  meses = meses['nombre_mes'].to_list()
  return meses

## ******** Extrayendo años del dataset(data_final.csv) y los muestra ordenado

def get_years():
  # data_final = st.session_state.data_final
  # data_final = con.run()
  anios = sorted(list(data_final['purchase_year'].unique()))
  return anios

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')