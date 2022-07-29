import streamlit as st
import numpy as np
import pandas as pd
import boto3
from fastparquet import ParquetFile

## ================================================================================================================
## Leyendo la fuente de datos

def run():
  if "data_final" not in st.session_state:
    # ssv.run()
    st.session_state.data_final = connection()
    st.session_state.mostrar_filtros = True

def connection():
  session = boto3.Session(
      aws_access_key_id='AKIAVIHI23JPR2BQFWRX',
      aws_secret_access_key='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',
      region_name='us-east-2'
  )
  s3_resource = session.resource("s3")

  file_path='olist/66f54897-7830-496a-a252-872f76e2a188'
  file_name = file_path.split("/")[-1]
  s3_resource.meta.client.download_file('olist-data-wh',file_path, f'/tmp/{file_name}')
  pf= ParquetFile(f'/tmp/{file_name}')
  df = pf.to_pandas()
  df_final = transform_timestamp_columns(df)

  return df_final

def transform_timestamp_columns(df):
    df.drop(columns=['purchase_date','delivered_customer_date','estimated_delivery_date','purchase_hour','delivered_customer_hour','purchase_time_day','delvered_customer_time_day'],axis=1, inplace=True)
    
    timestamp_cols = ['order_purchase_timestamp','order_delivered_customer_date','order_delivered_carrier_date','order_estimated_delivery_date']

    for col in timestamp_cols:
        df[col] = pd.to_datetime(df[col])
        column_split = df[col].name.split("_")
        if column_split[1] in ["purchase","approved"]:
            column_split = column_split[1]
        else:
            column_split = "_".join(column_split[1:3])
        
        # Agregando columnas con Año y Mes
        df[column_split+'_year'] = df[col].apply(lambda x: x.year).apply(lambda x:np.nan if np.isnan(x) else int(x))
        df[column_split+'_month'] = df[col].apply(lambda x: x.month)
        df[column_split+'_month_name'] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%b')
        df[column_split+'_year_month'] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m')
        df[column_split+'_date'] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

        # # Agregando columnas con Día y Día de la semana
        df[column_split+'_day'] = pd.to_datetime(df[col], errors='coerce').dt.day
        # df[column_split+'_day'] = df[col].astype('datetime64[ns]').apply(lambda x: x.day) # FALTA NUMERO DEL DIA
        df[column_split+'_dayofweek'] = pd.to_datetime(df[col], errors='coerce').dt.dayofweek
        # df[column_split+'_dayofweek'] = df[col].astype('datetime64[ns]').apply(lambda x: x.dayofweek) #
        df[column_split+'_dayofweek_name'] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%a')
        # df[column_split+'_dayofweek_name'] = df[col].astype('datetime64[ns]').apply(lambda x: x.strftime('%a'))
    
        # # Agregando columnas con Hora y si es de día o noche
        df[column_split+'_hour'] = pd.to_datetime(df[col], errors='coerce').dt.hour
        # df[column_split+'_hour'] = df[col].astype('datetime64[ns]').apply(lambda x: x.hour)
        hours_bins = [-0.001, 6, 12, 18, 23]
        hours_labels = ['Dawn', 'Morning', 'Afternoon', 'Night']
        df[column_split+'_time_day'] = pd.cut(df[column_split+'_hour'], hours_bins, labels=hours_labels)
    return df
      
