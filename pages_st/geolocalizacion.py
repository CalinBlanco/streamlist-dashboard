import streamlit as st
import folium
import geopandas as gpd
from application import conn_aws as cn
from streamlit_folium import folium_static

import altair as alt
import pandas as pd

def run():
    cn.run()
    st.markdown("## Mapa de Georeferenciación")
    data_final = st.session_state.data_final
    # data_final = st.session_state.data_final_csv
#   print("TIPO DE DATO DF: ",type(df))
#   df[['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']] = df[['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']].apply(lambda y: y.apply(lambda x: pd.to_datetime(x.split(' ')[0]) if not isinstance(x, float) else x))
#   df['delta_estimated_real'] = df['order_estimated_delivery_date'] - df['order_delivered_customer_date']
#   df['delta_purchase_delivered'] = df['order_delivered_customer_date'] - df['order_purchase_timestamp']
#   df['delta_estimated_real'] = df['delta_estimated_real'].apply(lambda x: x.days)
#   df['delta_purchase_delivered'] = df['delta_purchase_delivered'].apply(lambda x: x.days)

#   df_definitivo = df[['order_id','customer_id','customer_state','nombre_estado_customer','lat_customer','lng_customer','seller_id','lat_seller','lng_seller','seller_state','nombre_estado_seller']]
#   df_seller = df_definitivo[['order_id','seller_id','lat_seller','lng_seller','seller_state']]
#   df_customer = df_definitivo[['order_id','customer_id','customer_state','lat_customer','lng_customer']]

  # Promediamos las coordenadas de Customer para obtener las coordenadas de cada estado de Brasil
#   state_lat_lon = df_customer.groupby('customer_state').agg({'lat_customer':'mean','lng_customer':'mean'}).reset_index()

    state_mean_customer = data_final.groupby(['customer_state','customer_state_name']).agg({'customer_geoloction_lat':'mean','customer_geolocation_lng':'mean'}).reset_index()
    state_revenue_seller= data_final.groupby(['seller_state']).agg({'payment_value':'sum'}).reset_index()

    state_revenue_map = pd.merge(state_mean_customer,state_revenue_seller, left_on='customer_state', right_on="seller_state", how="outer")
    state_revenue_map.drop(columns=['seller_state'], axis=1, inplace=True)
    state_revenue_map.rename(columns={'customer_state':'seller_state','customer_state_name':'nombre_estado','customer_geoloction_lat':'latitud','customer_geolocation_lng':'longitud'}, inplace=True)
    state_revenue_map.loc[state_revenue_map.payment_value.isna(),'payment_value'] = 0.0
    state_revenue_map['percentage'] = (state_revenue_map['payment_value']/state_revenue_map['payment_value'].sum() * 100).round(2)
    state_revenue_map.sort_values(by='percentage',ascending=False)


    my_map = folium.Map(location=[-15,-50],
                zoom_start=4,
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
                attr='My Data Attribution')

    states = gpd.read_file("data/brazil-states.geojson")
    state_poly = states[['sigla','geometry']]
    df_definitivo = state_poly.merge(state_revenue_map, left_on='sigla', right_on='seller_state', how='outer')
    df_definitivo.loc[df_definitivo['percentage'].isna(),'percentage'] = 0.0
    df_definitivo.drop(columns=['seller_state'],axis=1, inplace=True)
    # df_definitivo.rename(columns={'seller_lat':'latitud','seller_lng':'longitud'}, inplace=True)
    df_definitivo.rename(columns={'lat_seller':'latitud','lng_seller':'longitud'}, inplace=True)

    df_definitivo['state_position']=df_definitivo['sigla'].apply(lambda x : str(get_state_position(data_final,x,top_sellers)))
    df_definitivo['average_review']=df_definitivo['sigla'].apply(lambda x : str(average_review(data_final,x)))

    df_total=df_definitivo
    for x in df_definitivo['sigla']:
        if df_definitivo.loc[df_definitivo['sigla']==x,'payment_value'].values[0]==0.0:
            continue
        generar_marker(x,df_total,data_final).add_to(my_map)
    

    style_function = lambda x: {'fillColor': '#c0c0c0', 
                                'color':'#000000', 
                                'fillOpacity': 0.5,
                                'weight': 0.2}
    highlight_function = lambda x: {'fillColor': '#000000', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.50, 
                                    'weight': 0.2}

    myscale = (df_definitivo['percentage'].quantile((0,0.1,0.75,0.9,0.98,1))).tolist()
    # colormap = m.linear.YlGnBu_09.to_step(data=df_definitivo['percentage'], method='quant', quantiles=[0,0.1,0.75,0.9,0.98,1])
    # colormap.caption='Revenue by State in %'
    
    my_map.choropleth(
    geo_data=df_definitivo,
    name='Choropleth',
    data=df_definitivo,
    columns=['nombre_estado','percentage'],
    key_on="feature.properties.nombre_estado",
    fill_color='YlGn',
    threshold_scale=myscale,
    fill_opacity=1,
    line_opacity=0.2,
    legend_name='Revenue by State in %',
    smooth_factor=0
    )

    datos = folium.features.GeoJson(
                        data=df_definitivo,
                        
                        style_function=style_function, 
                        control=True,
                        highlight_function=highlight_function,
                        tooltip=folium.features.GeoJsonTooltip(
                            fields=['nombre_estado',
                                    'sigla',
                                    'state_position',
                                    'average_review'
                                    ],
                            aliases=['Estado',
                                    'Sigla',
                                    'Ranking Actual',
                                    'Promedio de Reviews'
                                    ], 
                            
                            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    my_map.add_child(datos)

    # folium_static(my_map, width=1738, height=1000)
    # col1 = st.columns(1)
    folium_static(my_map, width=950, height=600)

#--------------------------------------------------METRICAS--------------------------------------------------

def top_sellers(df):
    
    # df = filter(df)

    sells_by_state = df.loc[:,['price', 'seller_state', 'order_purchase_timestamp']].groupby('seller_state').sum().sort_values('price', ascending=False).reset_index()
    sells_by_state.rename(columns={'price':'total_sells'}, inplace=True)
    return sells_by_state

def get_state_position(df, state, function):
    top = function(df)
    ranking = top[top['seller_state'] == state]
    if ranking.empty:
        return 'Not avaliable'
    else:
        return ranking.index[0] + 1

def average_review(df, state):
    
    # df = filter(df)

    reviews = df[['review_score', 'seller_state']].groupby('seller_state').mean().reset_index()
    review_state = reviews[reviews['seller_state'] == state]
    if review_state.empty:
        return 'Not avaliable'
    else:
        return round(review_state.iloc[0]['review_score'], 2)

# Pop-up window for the map

def graph_review(df, state):
    reviews = review_state(df, state)
    reviews = reviews.groupby('review_name').count().reset_index()
    reviews = reviews.loc[:,['review_name', 'review_score']]
    reviews['percentage'] = reviews['review_score']/reviews['review_score'].sum()
    bar = alt.Chart(reviews).mark_bar(size=20).encode(
    alt.X('review_name:N', axis=alt.Axis(title='Review')),
    alt.Y('percentage:Q', axis=alt.Axis(title='Count', format='.0%')),
    color=alt.Color('review_name', legend=None)
    )
    return bar

def top_categories(df, state):
    # df = filter(df)
    df = df[df['seller_state'] == state]
    categories = df.groupby(['product_category_name','seller_state'])['payment_value'].sum().to_frame().reset_index().sort_values(by=['payment_value'],ascending=False)
    categories['percentage'] = categories['payment_value']/categories['payment_value'].sum()
    categories = categories.head(3)
    categories['product_category_name'] = categories['product_category_name'].apply(lambda x : x.capitalize().replace('_'," "))
    return alt.Chart(categories).mark_bar(size=20).encode(
        alt.Y('product_category_name:N', axis=alt.Axis(title='Category')),
        alt.X('percentage:Q', axis=alt.Axis(title='Revenue', format='.0%')),
        color=alt.Color('product_category_name', legend=None)
        )




def generar_marker(state,df_total,df):
#   order_amount, total_value = sells_by_state(df, state)
#   lines = alt.Chart(total_value).mark_line(stroke='#AD1010').encode(
#         x='order_purchase_timestamp:T',y='payment_value:Q')

#   bars = alt.Chart(order_amount).mark_bar(color='#57A44C').encode(
#         x='order_purchase_timestamp:T', y='order_id:Q')

#   fig1 = alt.layer(bars,lines).resolve_scale(y='independent').properties(width=120,height=120,title='Ventas')

#   customers = customers_by_state(df, state)
#   fig2 = alt.Chart(customers).mark_bar().encode(
#         x='customer_id:Q', y='customer_state:N').properties(width=120,height=120,title='Clientes por Estado')


#   category = category_by_state(df, state)
#   fig3 = alt.Chart(category).mark_bar().encode(
#         x='order_id:Q', y='product_category_name:N').properties(width=120,height=120,title='Cat. más Vendidas')


#   payment = payment_type_by_state(df, state)
#   fig4 = alt.Chart(payment).mark_bar().encode(
#         x='payment_type:N', y ='order_id:Q').properties(width=120,height=120,title='Tipos de Pagos')

    fig1 = graph_review(df,state).properties(width=120,height=120,title='Ratio de Reviews')
    fig2 = top_categories(df,state).properties(width=120,height=120,title='Cat. más Vendidas')
  
    estado = df_total[df_total['sigla']==state]
    lat = estado['latitud']
    lon = estado['longitud']
    
    marker = folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(max_width=500).add_child(
            #   folium.VegaLite(fig1 & fig2 | fig3 & fig4 )),
            folium.VegaLite(fig1 & fig2 )),
    )
    return marker



#---------------------Funciones de Carga de Datos---------------------#

# def sells_by_state(df, state):
#     sales_state = df.loc[:,['order_id', 'payment_value', 'seller_state', 'order_purchase_timestamp', 'order_status']]
#     sales_state = sales_state[sales_state['order_status'] == 'delivered']
#     sells_by_state = sales_state[sales_state['seller_state'] == state]
#     sells_by_state['order_purchase_timestamp'] = sells_by_state['order_purchase_timestamp'].apply(lambda x: x.strftime('%Y-%m'))
#     orders_amount = sells_by_state.loc[:,['order_purchase_timestamp', 'order_id']].groupby(['order_purchase_timestamp']).count().reset_index().sort_values('order_purchase_timestamp')
#     total_value = sells_by_state.loc[:,['order_purchase_timestamp', 'payment_value']].groupby(['order_purchase_timestamp']).sum().reset_index().sort_values('order_purchase_timestamp')
#     return orders_amount, total_value

# def customers_by_state(df, state):
#     customers_state = df.loc[:,['customer_id','customer_state', 'seller_state']]
#     customers_state.drop_duplicates(inplace=True)
#     customers_by_state = customers_state[customers_state['seller_state'] == state]
#     answ = customers_by_state.loc[:,['customer_id', 'customer_state']].groupby(['customer_state']).count().sort_values('customer_id', ascending=True).reset_index()
#     return answ.head(5)

# def category_by_state(df, state):
#     category_state = df.loc[:,['order_id','product_category_name', 'seller_state']]
#     category_state.drop_duplicates(inplace=True)
#     category_by_state = category_state[category_state['seller_state'] == state]
#     to_bar_cat = category_by_state.loc[:,['product_category_name', 'order_id']].groupby(['product_category_name']).count().sort_values('order_id', ascending=True).reset_index().head(5)
#     return to_bar_cat

# def payment_type_by_state(df, state):
#     payment_type = df.loc[:,['order_id','payment_type', 'seller_state']]
#     payment_type.drop_duplicates(inplace=True)
#     payment_by_state = payment_type[payment_type['seller_state'] == state]
#     to_pie_payment = payment_by_state.loc[:,['payment_type', 'order_id']].groupby(['payment_type']).count().reset_index()
#     return to_pie_payment

# #---------------------Funciones de métricas---------------------#

# def delays_by_state(df, state):
#     delays = df.loc[:,['order_id','delta_estimated_real', 'seller_state']]
#     delays.drop_duplicates(inplace=True)
#     delays_by_state = delays[delays['seller_state'] == state]
#     delays_by_state = delays_by_state[~delays_by_state['delta_estimated_real'].isna()]
#     delays_by_state = delays_by_state[delays_by_state['delta_estimated_real'] < 0]
#     average_delay  = delays_by_state['delta_estimated_real'].mean()
#     return average_delay

# def sellers_by_state(df, state):
#     sellers_quantity = df.loc[:,['seller_id', 'seller_state']]
#     sellers_quantity_by_state = sellers_quantity[sellers_quantity['seller_state'] == state]['seller_id'].unique().shape[0]
#     return sellers_quantity_by_state

# #--------------------------------------------------METRICAS--------------------------------------------------

# def top_sellers(df):
    
#     df = filter(df)

#     sells_by_state = df.loc[:,['price', 'seller_state', 'order_purchase_timestamp']].groupby('seller_state').sum().sort_values('price', ascending=False).reset_index()
#     sells_by_state.rename(columns={'price':'total_sells'}, inplace=True)
#     return sells_by_state

# def get_state_position(df, state, function):
#     top = function(df)
#     ranking = top[top['seller_state'] == state]
#     if ranking.empty:
#         return 'Not avaliable'
#     else:
#         return ranking.index[0] + 1

# def average_review(df, state):
    
#     df = filter(df)

#     reviews = df[['review_score', 'seller_state']].groupby('seller_state').mean().reset_index()
#     review_state = reviews[reviews['seller_state'] == state]
#     if review_state.empty:
#         return 'Not avaliable'
#     else:
#         return round(review_state.iloc[0]['review_score'], 2)

# # Pop-up window for the map

# def graph_review(df, state):
#     reviews = review_state(df, state)
#     reviews = reviews.groupby('review_name').count().reset_index()
#     reviews = reviews.loc[:,['review_name', 'review_score']]
#     reviews['percentage'] = reviews['review_score']/reviews['review_score'].sum()
#     bar = alt.Chart(reviews).mark_bar(size=100).encode(
#     alt.X('review_name:N', axis=alt.Axis(title='Review')),
#     alt.Y('percentage:Q', axis=alt.Axis(title='Count', format='.0%')),
#     color=alt.Color('review_name', legend=None)
#     ).properties(
#         width=500
#     )
#     return bar

# def top_categories(df, state):
#     df = filter(df)
#     df = df[df['seller_state'] == state]
#     categories = df.loc[:,['product_category_name', 'category_id']].drop_duplicates()
#     categories = df.groupby('product_category_name').count().reset_index()
#     return alt.Chart(categories).mark_bar(size=100).encode(
#         alt.Y('product_category_name:N', axis=alt.Axis(title='Category')),
#         alt.X('category_id:Q', axis=alt.Axis(title='Count')),
#         color=alt.Color('product_category_name', legend=None)
#         ).properties(
#             width=500
#         )
    

def review_state(df, state):
    # df = filter(df)
    reviews = df[['review_score', 'seller_state', 'order_id']].drop_duplicates()
    reviews = reviews[(reviews['review_score'] > 0) & (reviews['seller_state'] == state)]
    reviews['review_name'] = reviews['review_score'].apply(lambda x: 'Buena' if (x > 3) else ('Mala' if x < 3 else 'Neutral'))
    return reviews