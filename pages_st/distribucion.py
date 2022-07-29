from matplotlib.pyplot import title
import streamlit as st
import pandas as pd
# from application import conn_aws as cn
import altair as alt
from geopy import distance as dis

from application import utils as util

def run():
  # st.markdown("## Página Distribución")
  df = st.session_state.data_final

  ## ******** Insertamos cada métrica en su componente
  a1, a2, a3, a4, a5, a6= st.columns(6)

  delivery = load_delivery(df)

#   a1.metric('Promedio de diferencia entre estimado y real', '{0:.2g}'.format(delivery['delta_estimated_real'].mean()))
#   a2.metric('Tiempo de entregas a tiempo promedio', '{0:.2g}'.format(delivery[delivery['delta_estimated_real'] >= 0]['delta_estimated_real'].mean()))
#   a3.metric('Cantidad de retrasos', delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].count())
#   a4.metric('Porcentaje de retrasos', '{0:.2g}'.format((delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].count()/delivery['delta_estimated_real'].count())*100)+'%')
#   a5.metric('Tiempo de retraso promedio', '{0:.2g}'.format(delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].mean()))
#   a6.metric('Promedio de entrega total', '{0:.2g}'.format(delivery['delta_purchase_delivered'].mean()))

  a1.metric('Estimado-Entregado', '{0:.2g}'.format(delivery['delta_estimated_real'].mean())+" d.")
  a2.metric('Tiempo de entrega', '{0:.2g}'.format(delivery[delivery['delta_estimated_real'] >= 0]['delta_estimated_real'].mean())+" d.")
  a3.metric('Cantidad de retrasos', delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].count())
  a4.metric('% de retrasos', '{0:.2g}'.format((delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].count()/delivery['delta_estimated_real'].count())*100))
  a5.metric('Tiempo de retraso', '{0:.0g}'.format(delivery[delivery['delta_estimated_real'] < 0]['delta_estimated_real'].mean()*-1)+" d.")
  a6.metric('Tiempo entrega total', '{0:.2g}'.format(delivery['delta_purchase_delivered'].mean())+" d.")


  distance(st.session_state.data_final)

  total_freight(st.session_state.data_final)

  average_delivery(st.session_state.data_final)


def filter(df):
    # df = df.loc[(df.purchase_year.isin(st.session_state.selected_options_year)) & (df.purchase_month_name.isin(st.session_state.selected_options_month))]
    df = df[df['order_purchase_timestamp'].astype('datetime64[ns]').apply(lambda x: int(x.strftime('%Y'))).isin(st.session_state.selected_options_year)]
    df = df[df['order_purchase_timestamp'].astype('datetime64[ns]').apply(lambda x: x.strftime('%B')).isin(st.session_state.selected_options_month)]
    return df

def value_freight(df):
    df = filter(df)
    sales_state = df.loc[:,['order_id', 'payment_value', 'freight_value', 'seller_state', 'order_purchase_timestamp', 'order_status']]
    sales_state = sales_state[sales_state['order_status'] == 'delivered']
    sales_state.drop_duplicates(inplace=True)
    sales_state['order_purchase_timestamp'] = sales_state['order_purchase_timestamp'].astype('datetime64[ns]').apply(lambda x: x.strftime('%Y-%m'))
    total_value = sales_state.loc[:,['order_purchase_timestamp', 'seller_state', 'payment_value']].groupby(['order_purchase_timestamp', 'seller_state']).sum().reset_index().sort_values('order_purchase_timestamp')
    total_freight = sales_state.loc[:,['order_purchase_timestamp', 'seller_state', 'freight_value']].groupby(['order_purchase_timestamp', 'seller_state']).sum().reset_index().sort_values('order_purchase_timestamp')
    return total_value, total_freight

def review_state(df, state):
    df = filter(df)
    reviews = df[['review_score', 'seller_state', 'order_id']].drop_duplicates()
    reviews = reviews[(reviews['review_score'] > 0) & (reviews['seller_state'] == state)]
    reviews['review_name'] = reviews['review_score'].apply(lambda x: 'Buena' if (x > 3) else ('Mala' if x < 3 else 'Neutral'))
    return reviews


def distance(df):
    
    df = filter(df)

    sellers_customers = df.loc[:,['seller_id', 'seller_state', 'seller_geolocation_lat', 'seller_geolocation_lng', 'customer_id', 'customer_state_name', 'customer_geoloction_lat', 'customer_geolocation_lng']].drop_duplicates()
    sellers_customers = sellers_customers[sellers_customers['seller_state'] != sellers_customers['customer_state_name']].dropna()
    sellers_customers['distance'] = sellers_customers.loc[:,['seller_geolocation_lat', 'seller_geolocation_lng', 'customer_geoloction_lat', 'customer_geolocation_lng']].apply(lambda x: dis.distance((x[0], x[1]), (x[2], x[3])), axis=1)
    sellers_customers['distance'] = sellers_customers['distance'].apply(lambda x: round(x.km,2))
    sellers_customers_by_state = sellers_customers.loc[:,['seller_state', 'distance']]
    sellers_customers_by_state = sellers_customers_by_state[sellers_customers_by_state['distance'] < 4000]
    
    alt.data_transformers.disable_max_rows()
    boxplot = alt.Chart(sellers_customers_by_state, background="transparent").mark_boxplot(outliers={'size':3}).encode(
        alt.X('seller_state:O', axis=alt.Axis(title='State')),
        alt.Y('distance:Q'),
        color=alt.Color('seller_state', legend=None)
    ).properties(
        width=800,
        title="Distancias de Entrega Entre Estados"
    )

    violin = alt.Chart(sellers_customers_by_state, background="transparent").transform_density(
        'distance',
        as_=['Distance(Km)', 'density'],
        extent=[0, 4000],
        groupby=['seller_state']
    ).mark_area(orient='horizontal').encode(
        y='Distance(Km):Q',
        color='seller_state:N',
        x=alt.X(
            'density:Q',
            stack='center',
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, values=[0],grid=False, ticks=True),
        ),
        column=alt.Column(
            'seller_state:N',
            header=alt.Header(
                titleOrient='bottom',
                labelOrient='bottom',
                labelPadding=0,
            ),
        )
    ).properties(
        # width=50,
        title="Distancias de Entrega Entre Estados"
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )
    st.altair_chart(boxplot, use_container_width=True)

    tabla_9_csv = util.convert_df(sellers_customers_by_state)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_9_csv,
        file_name='distancias_entrega_entre_estados.csv',
        mime='text/csv',
        key="9"
    )

def total_freight(df):

    df = filter(df)

    freight = value_freight(df)[1]

    grafico_2 = alt.Chart(freight, background="transparent").mark_line().encode(
        alt.X('order_purchase_timestamp:T', axis=alt.Axis(title='Date')),
        alt.Y('freight_value:Q', axis=alt.Axis(title='Total Freight')),
        color='seller_state',
        strokeDash='seller_state',
        tooltip=['seller_state']
    ).interactive().properties(title="Evolución de Gastos de Flete por Estado")
    st.altair_chart(grafico_2, use_container_width=True)
    tabla_10_csv = util.convert_df(freight)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_10_csv,
        file_name='evolución_gastos_de_flete_por_estado.csv',
        mime='text/csv',
        key="10"
    )

def average_delivery(df):

    df_delivered = load_delivery(df)
    total_delivered_real = df_delivered.loc[:,['seller_state', 'delta_estimated_real']].groupby('seller_state').count().reset_index()
    total_delivered_real.rename(columns={'delta_estimated_real':'total_delivered_real'}, inplace=True)
    ontime_delivered_real = df_delivered[df_delivered['delta_estimated_real'] > 1].loc[:,['seller_state', 'delta_estimated_real']].groupby('seller_state').count().reset_index()
    delivered_real = pd.merge(ontime_delivered_real, total_delivered_real, on='seller_state', how='left')
    delivered_real.rename(columns={'delta_estimated_real':'ontime_delivered_real'}, inplace=True)
    delivered_real['delivered_real_percentage'] = (delivered_real['ontime_delivered_real']/delivered_real['total_delivered_real'])*100
    delivered_real['delivered_real_percentage'] = delivered_real['delivered_real_percentage'].apply(lambda x: round(x,2))
    
    points = alt.Chart(delivered_real).mark_point(filled=True, size=80, color='black').encode(
        alt.X('seller_state', title='Seller State'),
        alt.Y('delivered_real_percentage', title='On time delivery (%)', scale=alt.Scale(zero=False)),
    ).interactive()

    line = alt.Chart(delivered_real).mark_line(stroke='red').transform_joinaggregate(
        mean_delivered_real='mean(delivered_real_percentage)'
    ).encode(
        alt.X('seller_state', title='Seller State'),
        alt.Y('mean_delivered_real:Q', title='On time delivery (%)', scale=alt.Scale(zero=False)),
    )

    grafico_3 = alt.layer(points, line, background="transparent").properties(title="Porcentaje de Entregas a Tiempo")
    st.altair_chart(grafico_3, use_container_width=True)

    tabla_11_csv = util.convert_df(delivered_real)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_11_csv,
        file_name='porcentaje_de_entregas_a_tiempo.csv',
        mime='text/csv',
        key="11"
    )


def load_delivery(df):
    df = filter(df)
    df_delivery = df.loc[:,['order_id', 'seller_state', 'order_status', 'order_purchase_timestamp', 'purchase_date', 'order_delivered_carrier_date', 'delivered_carrier_date', 'order_delivered_customer_date', 'delivered_customer_date', 'order_estimated_delivery_date', 'estimated_delivery_date']]
    df_delivered = df_delivery[df_delivery['order_status']=='delivered']
    df_delivered.loc[:,'delta_estimated_real'] = df_delivered.loc[:,'estimated_delivery_date'].astype('datetime64[ns]') - df_delivered.loc[:,'delivered_customer_date'].astype('datetime64[ns]')
    df_delivered.loc[:,'delta_purchase_delivered'] = df_delivered.loc[:,'delivered_customer_date'].astype('datetime64[ns]') - df_delivered.loc[:,'purchase_date'].astype('datetime64[ns]')
    df_delivered['delta_estimated_real'] = df_delivered['delta_estimated_real'].apply(lambda x: x.days)
    df_delivered['delta_purchase_delivered'] = df_delivered['delta_purchase_delivered'].apply(lambda x: x.days)
    return df_delivered