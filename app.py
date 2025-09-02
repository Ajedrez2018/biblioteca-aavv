import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Archivos CSV
LIBROS_CSV = "libros.csv"
USUARIOS_CSV = "usuarios.csv"
PRESTAMOS_CSV = "prestamos.csv"

# Cargar datos
def cargar_datos(path, columnas):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=columnas)

# Guardar datos
def guardar_datos(df, path):
    df.to_csv(path, index=False)

# Inicializar
libros = cargar_datos(LIBROS_CSV, [
    "ISBN","Título","Autor","Editorial","Año de publicación","Categoría",
    "Número de ejemplares","Estado de conservación","Ubicación","Notas"
])
usuarios = cargar_datos(USUARIOS_CSV, [
    "Id_usuario","Nombre","Apellidos","Teléfono","Correo","Dirección","Notas"
])
prestamos = cargar_datos(PRESTAMOS_CSV, [
    "ISBN","Id_usuario","Fecha préstamo","Fecha devolución",
    "Fecha devolución real","Estado devolución","Fuera de plazo","Notas"
])

# Config
st.set_page_config(page_title="AAVV el Pla - Biblioteca", page_icon="📚", layout="wide")
st.title("📖 Biblioteca AAVV el Pla")

# Tabs
tabs = st.tabs(["Libros", "Usuarios", "Préstamos"])

# ========================= LIBROS =========================
with tabs[0]:
    st.subheader("📚 Libros")
    accion = st.radio("Acción", ["Consultar","Alta","Modificar","Baja"], key="radio_libros", horizontal=True)

    if accion == "Consultar":
        filtro_titulo = st.text_input("Título (contiene)")
        filtro_autor = st.text_input("Autor (contiene)")
        filtro_cat = st.text_input("Categoría (contiene)")
        df = libros.copy()
        if filtro_titulo:
            df = df[df["Título"].str.contains(filtro_titulo, case=False, na=False)]
        if filtro_autor:
            df = df[df["Autor"].str.contains(filtro_autor, case=False, na=False)]
        if filtro_cat:
            df = df[df["Categoría"].str.contains(filtro_cat, case=False, na=False)]
        st.dataframe(df, use_container_width=True)

# ========================= USUARIOS =========================
with tabs[1]:
    st.subheader("👤 Usuarios")
    accion = st.radio("Acción", ["Consultar","Alta","Modificar","Baja"], key="radio_usuarios", horizontal=True)

    if accion == "Consultar":
        filtro_nombre = st.text_input("Nombre (contiene)")
        filtro_tel = st.text_input("Teléfono (contiene)")
        filtro_email = st.text_input("Correo (contiene)")
        df = usuarios.copy()
        if filtro_nombre:
            df = df[df["Nombre"].str.contains(filtro_nombre, case=False, na=False)]
        if filtro_tel:
            df = df[df["Teléfono"].str.contains(filtro_tel, case=False, na=False)]
        if filtro_email:
            df = df[df["Correo"].str.contains(filtro_email, case=False, na=False)]
        st.dataframe(df, use_container_width=True)

# ========================= PRÉSTAMOS =========================
with tabs[2]:
    st.subheader("📑 Préstamos")
    accion = st.radio("Acción", ["Consultar","Alta","Modificar","Baja"], key="radio_prestamos", horizontal=True)

    if accion == "Consultar":
        filtro_fecha = st.date_input("Mostrar préstamos con fecha devolución >= ...", value=None)
        df = prestamos.copy()
        if filtro_fecha:
            filtro_fecha = pd.to_datetime(filtro_fecha)
            df["Fecha devolución"] = pd.to_datetime(df["Fecha devolución"], errors="coerce")
            df = df[df["Fecha devolución"] >= filtro_fecha]
        st.dataframe(df, use_container_width=True)
