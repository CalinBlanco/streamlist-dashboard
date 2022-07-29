from matplotlib.pyplot import xlabel
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import altair as alt

from application import session_state_vars as ssv, conn_aws as cn, utils as util

# from application import conn_aws as cn


def run():
    data_final = st.session_state.data_final

    ## ******** Filtramos del dataset el Total de Ingresos
    total_ingresos = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month) & (data_final['order_status'] == 'delivered')].groupby("order_id")["payment_value"].sum().sum()
    ## ******** Filtramos del dataset el Total de Órdenes
    total_ordenes = len(data_final['order_id'].loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].unique())
    ## ******** Filtramos del dataset el Total de Clientes
    total_clientes = len(data_final['customer_id'].loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].unique())
    ## ******** Filtramos del dataset el Total de Vendedores
    total_vendedores = len(data_final['seller_id'].loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].unique())
    ## ******** Filtramos del dataset el Total de productos
    total_productos = len(data_final['product_id'].loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].unique())

    # Fila 1
    ## ******** Damos formato en la salida de las métricas
    total_revenue = "$R " + str(round(total_ingresos/1000000,2)) + "M"
    num_customer = str(round(total_clientes/1000,2)) + "K"
    num_order = str(round(total_ordenes/1000,2)) + "K"
    num_seller = str(round(total_vendedores/1000,2)) + "K"
    num_product = str(round(total_productos/1000,2)) + "K"

    ## ******** Insertamos cada métrica en su componente
    a1, a2, a3, a4, a5= st.columns(5)
    a1.metric("Total de Ingresos", total_revenue)
    a2.metric("Total de Clientes", num_customer)
    a3.metric("Total de Órdenes", num_order)
    a4.metric("Total de Vendedores", num_seller)
    a5.metric("Total de Productos", num_product)

    # Fila 2
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["order_id"].count().reset_index().sort_values("order_id", ascending=False)
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["order_id"].count().reset_index().sort_values("order_id", ascending=False)
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["price"].agg(["count","sum"], axis="columns").reset_index().sort_values("order_purchase_year_month", ascending=False)
    
    col1, col2 = st.columns([4, 2])
    col3 = st.columns(1)
    col4, col5 = st.columns([4, 4])

    ## ! Gráfico 1: Ingresos Mensuales vs Número de Órdenes Mensuales
    
    tabla_1 = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)&(data_final['order_status']=='delivered')].groupby("purchase_year_month")["payment_value"].agg(["count","sum"], axis="columns").reset_index().sort_values("purchase_year_month", ascending=False)
        
    fig_1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add figure title
    fig_1.update_layout(
        title_text="Ingresos Mensuales vs Número de Órdenes Mensuales",
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
    # Add traces
    fig_1.add_trace(
        go.Scatter(x=list(tabla_1['purchase_year_month']), y=list(tabla_1['sum']), name="Ingresos",mode="lines+markers",marker=dict(size=5, color="#d4ad00")),
        secondary_y=False,
    )
    fig_1.add_trace(
        go.Scatter(x=list(tabla_1['purchase_year_month']), y=list(tabla_1['count']), name="Ódenes",mode="lines+markers",marker=dict(size=5, color="LightSeaGreen")),
        secondary_y=True,
    )
    fig_1['layout']['yaxis1']['showgrid'] = False
    fig_1['layout']['xaxis1']['showgrid'] = False
    # Set x-axis title
    fig_1.update_xaxes(title_text="Meses",tickangle=-30)
    # Set y-axis title
    fig_1.update_yaxes(title_text="Ingresos(R$)", secondary_y=False)
    fig_1.update_yaxes(title_text="# Órdenes", secondary_y=True)
    # fig_1.show()
    col1.plotly_chart(fig_1, use_container_width=True)

    tabla_1_csv = util.convert_df(tabla_1)
    col1.download_button(
        label="Descargar dataset en CSV",
        data=tabla_1_csv,
        file_name='ingresos_mensuales_vs_numero_de_ordenes_mensuales.csv',
        mime='text/csv',
        key="1"
    )

    # Fila 3
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["order_id"].count().reset_index().sort_values("order_id", ascending=False)
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["order_id"].count().reset_index().sort_values("order_id", ascending=False)
    # df_1 = data_final.loc[(data_final.order_purchase_year.isin(st.session_state.selected_options_year)) & data_final.order_purchase_month_name.isin(st.session_state.selected_options_month)].groupby("order_purchase_year_month")["price"].agg(["count","sum"], axis="columns").reset_index().sort_values("order_purchase_year_month", ascending=False)
    
    ## ! Gráfico 2: Porcentaje de Estados de Órdenes

    tabla_2 = data_final['order_status'].loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].value_counts(normalize=True)#.to_frame().rename(columns={'order_id':'conteo'})
    tabla_2 = tabla_2.to_frame().reset_index()
    tabla_2.rename(columns = {'index':'status', 'order_status':'percentage'}, inplace = True)
    tabla_2['status'] = tabla_2['status'].apply(lambda x: 'delivered' if (x == 'delivered') else 'otro')
    tabla_2 = tabla_2.groupby('status')['percentage'].sum().to_frame().reset_index()

    fig_2 = go.Figure(data=[go.Pie(labels=tabla_2['status'], values=tabla_2['percentage'])])

    fig_2.update_layout(
        # title="Rating de Productos",
        title="Porcentaje de Estados de Órdenes",
        # annotations=[dict(text='Avg. Rating<br><b>'+str(avg_rating)+'</b>', font_size=15, showarrow=False)],
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='black',
        legend_title_text="Estado",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black"
            # font_family="Rockwell"
        )
    )

    col2.plotly_chart(fig_2, use_container_width=True)
    tabla_2_csv = util.convert_df(tabla_2)
    col2.download_button(
        label="Descargar dataset en CSV",
        data=tabla_2_csv,
        file_name='estado_de_ordenes.csv',
        mime='text/csv',
        key="2"
    )

    # Fila 4
    ## ! Gráfico 3: Nro de Órdenes por Día de la Semana y Hora del Día

    byWkdHr = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].groupby(["delivered_customer_dayofweek", "delivered_customer_hour"]).count()["order_id"].unstack()

    fig_3 = px.imshow(byWkdHr, text_auto=True, height = 400, zmin=250, zmax=0,color_continuous_scale='YlGn')
    fig_3.update_layout(
        font_size=12,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black"
            # font_family="Rockwell"
        ),
        title="Nro de Órdenes por Día de la Semana y Hora del Día",
        yaxis = dict(
            tickmode = 'array',
            tickvals = ["6", "5", "4", "3", "2", "1", "0"],
            ticktext = ['Sun', 'Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon']
        ),
        font_color='black',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    fig_3.update_traces(
        hovertemplate= "Hour: %{x} <br> Day: %{y} <br> Orders counts: %{z}"
    )
    fig_3.update_xaxes(title_text="Horas")
    fig_3.update_yaxes(title_text="Días")

    col3[0].plotly_chart(fig_3, use_container_width=True, sharing="streamlit")

    tabla_3_csv = util.convert_df(byWkdHr)
    col3[0].download_button(
        label="Descargar dataset en CSV",
        data=tabla_3_csv,
        file_name='ordenes_por_dia_de_semana_y_hora_del_dia.csv',
        mime='text/csv',
        key="3"
    )
    

    # Fila 5
    ## ! Gráfico 4: Ingresos de los Top 10 Categoría de Productos
    top_categ_by_revenue = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].groupby("product_category_name").agg({'order_id':'nunique','payment_value':'sum'}).sort_values("payment_value", ascending=False)
    top_categ_by_revenue.rename(columns={"order_id":"NumOfOrders", "payment_value":"Revenues"}, inplace=True)
    top_categ_by_revenue = top_categ_by_revenue[:5].reset_index()
    top_categ_by_revenue = top_categ_by_revenue.sort_values('Revenues',ascending=True)
    top_categ_by_revenue['product_category_name'] = top_categ_by_revenue['product_category_name'].apply(lambda x : x.capitalize().replace('_'," "))

    fig_4 = make_subplots(rows=1, cols=1)
    fig_4.append_trace(go.Bar(
        x=top_categ_by_revenue['Revenues'],
        y=top_categ_by_revenue['product_category_name'],
        marker=dict(
            color='LightSeaGreen',
        ),
        orientation='h'
    ),1,1)

    fig_4.update_xaxes(title_text="Ingresos(R$)")
    fig_4.update_yaxes(title_text="Categorías")

    fig_4.update_layout(
        title='Ingresos de los Top 5 Categoría de Productos',
        hovermode='y unified',
        # xlabel="Ingresos(R$)",
        # ylabel="Categorías",
        legend=dict(x=0.029, y=1.038, font_size=50),
        margin=dict(l=150, r=20, t=60, b=50),
        plot_bgcolor= 'rgba(0, 0, 0, 0)',
        paper_bgcolor= 'rgba(0, 0, 0, 0)',
        font_color='black',
        font_size=12,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black"
        )
    )
    col4.plotly_chart(fig_4, use_container_width=True, sharing="streamlit")

    tabla_4_csv = util.convert_df(top_categ_by_revenue)
    col4.download_button(
        label="Descargar dataset en CSV",
        data=tabla_4_csv,
        file_name='ingresos_top_10_categoría_de_productos.csv',
        mime='text/csv',
        key="4"
    )

    ## ! Gráfico 5: Calificación de Satisfacción del Cliente
    product_rating = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)].groupby("review_score").agg({'order_id':'count'}).sort_values("order_id", ascending=False).reset_index()
    product_rating['percentage'] = product_rating['order_id']/product_rating['order_id'].sum()

    sum_rating = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)]['review_score'].sum()
    count_rating = data_final.loc[(data_final.purchase_year.isin(st.session_state.selected_options_year)) & data_final.purchase_month_name.isin(st.session_state.selected_options_month)]['review_score'].count()
    avg_rating = round(sum_rating/count_rating,2)

    fig_13 = go.Figure(data=[go.Pie(labels=product_rating['review_score'], values=product_rating['percentage'], hole=.5)])

    fig_13.update_layout(
        # title="Rating de Productos",
        title="Calificación de Satisfacción del Cliente",
        annotations=[dict(text='Avg. Rating<br><b>'+str(avg_rating)+'</b>', font_size=15, showarrow=False)],
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='black',
        legend_title_text="Puntaje",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_color="black"
            # font_family="Rockwell"
        )
    )

    col5.plotly_chart(fig_13, use_container_width=True, sharing="streamlit")

    tabla_5_csv = util.convert_df(product_rating)
    col5.download_button(
        label="Descargar dataset en CSV",
        data=tabla_5_csv,
        file_name='calificación_satisfaccion_del_cliente.csv',
        mime='text/csv',
        key="5"
    )

    col6, col7 = st.columns([4, 4])

    ## ! Gráfico 6: 


    # st.write(st.session_state)

    value_and_freight(st.session_state.data_final)

    # st.altair_chart(grafico_6, use_container_width=True)
    
    sells_total_and_seller(st.session_state.data_final)
    
    total_value(st.session_state.data_final)




# ==================== GENERAR NUEVAS COLUMNAS

def filter(df):
    # ssv.run()
    # cn.run()
    df = df.loc[(df.purchase_year.isin(st.session_state.selected_options_year)) & (df.purchase_month_name.isin(st.session_state.selected_options_month))]
    # df = df[df['order_purchase_timestamp'].astype('datetime64[ns]').apply(lambda x: int(x.strftime('%Y'))).isin(st.session_state.selected_options_year)]
    # df = df[df['order_purchase_timestamp'].astype('datetime64[ns]').apply(lambda x: x.strftime('%b')).isin(st.session_state.selected_options_month)]
    return df

def value_and_freight(df):

    df = filter(df)

    value, freight, merge_value_freight = value_freight_1(df)
# ======================================================================= 
    fig_1 = make_subplots(specs=[[{"secondary_y": True}]])
    # Add figure title
    fig_1.update_layout(
        title_text="Comportamiento de Ventas con Costo de Distribución",
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
    # Add traces
    fig_1.add_trace(
        go.Scatter(x=list(freight['order_purchase_timestamp']), y=list(freight['freight_value']), name="Total freight(R$)",mode="lines+markers",marker=dict(size=5, color="#d4ad00")),
        secondary_y=False,
    )
    fig_1.add_trace(
        go.Scatter(x=list(value['order_purchase_timestamp']), y=list(value['payment_value']), name="Total sells(R$)",mode="lines+markers",marker=dict(size=5, color="LightSeaGreen")),
        secondary_y=True,
    )
    fig_1['layout']['yaxis1']['showgrid'] = False
    fig_1['layout']['xaxis1']['showgrid'] = False
    # Set x-axis title
    fig_1.update_xaxes(title_text="Meses",tickangle=-30)
    # Set y-axis title
    fig_1.update_yaxes(title_text="Total freight(R$)", secondary_y=False)
    fig_1.update_yaxes(title_text="Total sells(R$)", secondary_y=True)
    # fig_1.show()
    st.plotly_chart(fig_1, use_container_width=True)

    tabla_6_csv = util.convert_df(merge_value_freight)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_6_csv,
        file_name='comportamiento_de_ventas_con_costo_de_distribucion.csv',
        mime='text/csv',
        key="6"
    )


# ======================================================================= 


def sells_total_and_seller(df):
    
    df = filter(df)

    orders = df.loc[:,['order_id', 'order_item_id', 'seller_id', 'seller_state','seller_state_name', 'price', 'customer_id']].drop_duplicates()
    sellers_by_state = orders.loc[:,['seller_id', 'seller_state','seller_state_name']].drop_duplicates().groupby(['seller_state','seller_state_name']).count().reset_index()
    sellers_by_state.rename(columns={'seller_id':'total_sellers'}, inplace=True)
    sells_by_state = orders.loc[:,['price', 'seller_state','seller_state_name']].groupby(['seller_state','seller_state_name']).sum().reset_index()
    sells_by_state.rename(columns={'price':'total_sells'}, inplace=True)
    total_orders_by_seller_by_state = orders.loc[:,['seller_state','seller_state_name', 'order_id']].groupby(['seller_state','seller_state_name']).count().reset_index()
    total_orders_by_seller_by_state.rename(columns={'order_id':'total_orders'}, inplace=True)
    sells_by_state_seller = pd.merge(sellers_by_state, sells_by_state, on='seller_state')
    sells_by_state_seller = pd.merge(sells_by_state_seller, total_orders_by_seller_by_state, on='seller_state')
    sells_by_state_seller.drop(columns=['seller_state_name_x','seller_state_name_y'], inplace=True)
    sells_by_state_seller['sells_by_seller'] = sells_by_state_seller['total_sells']/sells_by_state_seller['total_sellers']
    sells_by_state_seller['sells_by_seller'] = sells_by_state_seller['sells_by_seller'].apply(lambda x: round(x,2))
    sells_by_state_seller

    base = alt.Chart(sells_by_state_seller).encode(
    alt.X('seller_state_name:O', axis=alt.Axis(title='State'))
)

    line1 = base.mark_bar(opacity=0.5).encode(
        alt.Y('sells_by_seller:Q', axis=alt.Axis(title='Sells by Seller(R$)')),
        tooltip=[alt.Tooltip('seller_state_name', title='Seller State'), alt.Tooltip('total_sells', title='Total Sells'), alt.Tooltip('sells_by_seller', title='Sells by Seller'), alt.Tooltip('total_sellers', title='Total Sellers')]
    )

    line2 = base.mark_bar(color='red', opacity=0.3).encode(
        alt.Y('total_sells:Q', axis=alt.Axis(title='Total Sells(R$)')),
        tooltip=[alt.Tooltip('seller_state_name', title='Seller State'), alt.Tooltip('total_sells', title='Total Sells'), alt.Tooltip('sells_by_seller', title='Sells by Seller'), alt.Tooltip('total_sellers', title='Total Sellers')]
    )

    grafico_7 = alt.layer(line2, line1, background="transparent").resolve_scale(y='independent').interactive().properties(title="Comparativa de Igresos por Estado y Promedio de Ingresos por Vendedor")

    st.altair_chart(grafico_7, use_container_width=True)

    tabla_7_csv = util.convert_df(sells_by_state_seller)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_7_csv,
        file_name='comparativa_igresos_estado_y_promedio_ingresos_vendedor.csv',
        mime='text/csv',
        key="7"
    )

def total_value(df):

    df = filter(df)

    value = value_freight(df)[0]

    grafico_8 = alt.Chart(value, background="transparent").mark_line().encode(
        alt.X('order_purchase_timestamp:T', axis=alt.Axis(title='Date')),
        alt.Y('payment_value:Q', axis=alt.Axis(title='Total Sales(R$)')),
        color='seller_state_name',
        strokeDash='seller_state_name',
        tooltip='seller_state_name'
    ).interactive().properties(title="Evolución de Ventas por Estado")

    st.altair_chart(grafico_8, use_container_width=True)
    
    tabla_8_csv = util.convert_df(value)
    st.download_button(
        label="Descargar dataset en CSV",
        data=tabla_8_csv,
        file_name='evolución_ventas_por_estado.csv',
        mime='text/csv',
        key="8"
    )

def value_freight(df):
    # df = filter(df)
    sales_state = df.loc[:,['order_id', 'payment_value', 'freight_value', 'seller_state','seller_state_name', 'order_purchase_timestamp', 'order_status']]
    sales_state = sales_state[sales_state['order_status'] == 'delivered']
    sales_state.drop_duplicates(inplace=True)
    sales_state['order_purchase_timestamp'] = sales_state['order_purchase_timestamp'].apply(lambda x: x.strftime('%Y-%m'))
    total_value = sales_state.loc[:,['order_purchase_timestamp', 'seller_state','seller_state_name', 'payment_value']].groupby(['order_purchase_timestamp', 'seller_state','seller_state_name']).sum().reset_index().sort_values('order_purchase_timestamp')
    total_freight = sales_state.loc[:,['order_purchase_timestamp', 'seller_state','seller_state_name', 'freight_value']].groupby(['order_purchase_timestamp', 'seller_state','seller_state_name']).sum().reset_index().sort_values('order_purchase_timestamp')
    return total_value, total_freight

def value_freight_1(df):
    # df = filter(df)
    sales_state = df.loc[:,['order_id', 'payment_value', 'freight_value', 'seller_state','seller_state_name', 'order_purchase_timestamp', 'order_status']]
    sales_state = sales_state[sales_state['order_status'] == 'delivered']
    sales_state.drop_duplicates(inplace=True)
    sales_state['order_purchase_timestamp'] = sales_state['order_purchase_timestamp'].apply(lambda x: x.strftime('%Y-%m'))
    total_value = sales_state.groupby(['order_purchase_timestamp'])['payment_value'].sum().reset_index().sort_values('order_purchase_timestamp')
    total_freight = sales_state.groupby(['order_purchase_timestamp'])['freight_value'].sum().reset_index().sort_values('order_purchase_timestamp')
    merge_value_freight = pd.merge(total_value,total_freight, on='order_purchase_timestamp', how='left')
    return total_value, total_freight, merge_value_freight
