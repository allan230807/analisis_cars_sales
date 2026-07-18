import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Dashboard Automotriz", layout="wide")

# Función para cargar y guardar datos
FILE_PATH = 'car_prices_clean.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(FILE_PATH)
    
    # En lugar de usar .dt, creamos el string 'YYYY-MM' usando sale_year de forma segura
    if 'sale_year' in df.columns:
        df['mes_año'] = df['sale_year'].astype(int).astype(str) + "-01"
    else:
        # Por si acaso no encuentra sale_year, un fallback seguro
        df['mes_año'] = "2026-01"
        
    return df
df = load_data()
# Navegación en la barra lateral izquierda
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["Buscador Principal", "Registro de Ventas"])

if menu == "Buscador Principal":
    st.markdown("<h1 style='text-align: center; margin-bottom: 50px;'>Bienvenido, ¿qué desea consultar hoy?</h1>", unsafe_allow_html=True)

    col_marca, col_modelo = st.columns(2)
    marcas_disponibles = sorted(df['make'].dropna().astype(str).unique())
    marca_seleccionada = col_marca.selectbox("Seleccione la Marca", marcas_disponibles)

    modelos_disponibles = sorted(df[df['make'] == marca_seleccionada]['model'].dropna().astype(str).unique())
    modelo_seleccionado = col_modelo.selectbox("Seleccione el Modelo", modelos_disponibles)

    df_filtrado = df[(df['make'] == marca_seleccionada) & (df['model'] == modelo_seleccionado)]

    st.markdown("---")
    col_img, col_kpi = st.columns([1, 1])

    with col_img:
        marca_clean = str(marca_seleccionada).replace(' ', '')
        modelo_clean = str(modelo_seleccionado).replace(' ', '')
        img_url = f"https://loremflickr.com/800/400/{marca_clean},{modelo_clean},car"
        st.image(img_url, caption=f"{marca_seleccionada.title()} {modelo_seleccionado.title()}", use_container_width=True)

    with col_kpi:
        st.subheader(f"Métricas de {marca_seleccionada.title()} {modelo_seleccionado.title()}")
        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Unidades Vendidas", len(df_filtrado))
        kpi2.metric("Precio Promedio", f"${df_filtrado['sellingprice'].mean():,.2f}")
        kpi3, kpi4 = st.columns(2)
        kpi3.metric("Margen Promedio", f"${df_filtrado['margen_usd'].mean():,.2f}")
        kpi4.metric("Kilometraje Promedio", f"{df_filtrado['odometer'].mean():,.0f}")

    st.markdown("---")
    st.subheader("Análisis Dinámico Global")
    tab1, tab2, tab3 = st.tabs(["Ventas por Marca", "Top Modelos", "Distribución de Precios"])

    with tab1:
        df_marcas = df['make'].value_counts().head(15).reset_index()
        df_marcas.columns = ['Marca', 'Ventas']
        fig_marcas = px.bar(df_marcas, x='Marca', y='Ventas', title="Top 15 Marcas de Mayor Rotación", template="plotly_white")
        st.plotly_chart(fig_marcas, use_container_width=True)

    with tab2:
        df_modelos = df['model'].value_counts().head(15).reset_index()
        df_modelos.columns = ['Modelo', 'Ventas']
        fig_modelos = px.bar(df_modelos, x='Modelo', y='Ventas', title="Top 15 Modelos más Vendidos", template="plotly_white", color='Ventas', color_continuous_scale='Blues')
        st.plotly_chart(fig_modelos, use_container_width=True)

    with tab3:
        fig_scatter = px.scatter(df.sample(min(2000, len(df)), random_state=42), x='odometer', y='sellingprice', color='categoria_mercado', title="Impacto del Kilometraje en el Precio", template="plotly_white", opacity=0.6)
        st.plotly_chart(fig_scatter, use_container_width=True)

elif menu == "Registro de Ventas":
    st.title("Base de Datos de Ventas y Rendimiento Mensual")
    
    st.subheader("Ingreso de Nuevas Operaciones")
    st.write("Edita la tabla o añade nuevas filas al final. Los cambios se pueden guardar directamente en la base de datos.")
    
    # Mostrar las últimas 100 ventas para mantener la tabla rápida y editable
    df_recent = df.tail(100).copy()
    
    # st.data_editor permite editar celdas y añadir filas si num_rows="dynamic"
    edited_df = st.data_editor(df_recent, num_rows="dynamic", use_container_width=True, key="data_editor")
    
    if st.button("Guardar Cambios en Base de Datos"):
        # Actualizar el dataframe original con los cambios y guardar el CSV
        df.update(edited_df)
        df.to_csv(FILE_PATH, index=False)
        st.success("¡Base de datos actualizada con éxito!")
        st.cache_data.clear() # Limpia el caché para recargar los datos actualizados

    st.markdown("---")
    
    # Sección de métricas mensuales
    meses_disponibles = sorted(df['mes_año'].dropna().unique(), reverse=True)
    
    col_mes, col_vacio = st.columns([1, 2])
    with col_mes:
        mes_seleccionado = st.selectbox("Seleccionar Mes de Análisis", meses_disponibles)
    
    df_mes = df[df['mes_año'] == mes_seleccionado]
    ganancia_total = df_mes['margen_usd'].sum()
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_ganancia, col_marca_fav = st.columns([2, 1])
    
    with col_ganancia:
        if ganancia_total > 0:
            st.markdown(f"<h1 style='color: #28a745; font-size: 50px;'>Ganancia: ${ganancia_total:,.2f}</h1>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='color: #dc3545; font-size: 50px;'>Pérdida: ${ganancia_total:,.2f}</h1>", unsafe_allow_html=True)
            
    with col_marca_fav:
        if not df_mes.empty:
            marca_favorita = df_mes['make'].value_counts().idxmax()
            st.markdown(f"### Marca Favorita: **{marca_favorita.upper()}**")
            marca_fav_clean = str(marca_favorita).replace(' ', '')
            st.image(f"https://loremflickr.com/300/300/{marca_fav_clean},logo,car", width=150)
        else:
            st.write("No hay ventas registradas en este mes.")