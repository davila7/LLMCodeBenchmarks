import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Participantes", layout="wide")

# Función para cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv('data_hack.csv')
    return df

# Cargar los datos
df = load_data()

# Título principal
st.title("Dashboard de Participantes")

# Crear dos columnas para los gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Clasificación por País")
    # Contar participantes por país
    pais_counts = df['País'].value_counts()
    # Crear gráfico de barras
    fig_pais = px.bar(
        x=pais_counts.index,
        y=pais_counts.values,
        labels={'x': 'País', 'y': 'Cantidad de Participantes'}
    )
    st.plotly_chart(fig_pais)

with col2:
    st.subheader("Clasificación por Actividad")
    # Contar participantes por actividad
    actividad_counts = df['¿En que actividades participarás?'].value_counts()
    # Crear gráfico de torta
    fig_actividad = px.pie(
        values=actividad_counts.values,
        names=actividad_counts.index,
        title='Distribución de Actividades'
    )
    st.plotly_chart(fig_actividad)

# Filtros
st.subheader("Filtros")
col_filtro1, col_filtro2 = st.columns(2)

with col_filtro1:
    # Filtro por correo electrónico
    correos = df['Correo electrónico'].dropna().unique()
    correo_seleccionado = st.selectbox('Filtrar por correo electrónico:', ['Todos'] + list(correos))

with col_filtro2:
    # Filtro por nombre
    nombres = df['Nombre'].dropna().unique()
    nombre_seleccionado = st.selectbox('Filtrar por nombre:', ['Todos'] + list(nombres))

# Aplicar filtros
df_filtrado = df.copy()
if correo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Correo electrónico'] == correo_seleccionado]
if nombre_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Nombre'] == nombre_seleccionado]

# Mostrar tabla de datos filtrada
st.subheader("Tabla de Datos")
st.dataframe(df_filtrado)
