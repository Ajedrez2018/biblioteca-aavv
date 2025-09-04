# app.py — AAVV el Pla · Biblioteca (Home + módulos)
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- Config y estilo ----------
st.set_page_config(page_title="AAVV el Pla - Biblioteca", page_icon="assets/logo.png", layout="wide")
st.markdown("""
<style>
@media (max-width: 724px){
  .block-container{padding:10px 8px;}
  .stTabs [role="tablist"] button {font-size:.95rem; padding:6px 8px;}
  .bottom-bar{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #e6e6e6;padding:8px;z-index:9999;}
  .page-spacer{height:72px;}
  .bar-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
}
@media (min-width: 725px){
  .bottom-bar{margin-top:8px;}
  .bar-grid{display:grid;grid-template-columns:repeat(6,max-content);gap:8px;}
}
.home-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:18px 0;}
.home-card{border:1px solid #e6e6e6;border-radius:12px;padding:18px;text-align:center;}
.home-card h3{margin:6px 0 0 0;}
.home-card p{color:#666;margin:6px 0 0 0;}
@media (max-width:724px){ .home-grid{grid-template-columns:1fr;}}
</style>
""", unsafe_allow_html=True)
st.title("📚 AAVV el Pla - Biblioteca")

# ---------- Helpers de datos ----------
LIBROS_COLS = ["ISBN","Título","Autor","Editorial","Año de publicación","Categoría",
               "Número de ejemplares","Estado de conservación","Ubicación","Notas"]
USUARIOS_COLS = ["Id_usuario","Nombre o mote","Apellidos","Teléfono","Correo electrónico","Dirección","Notas"]
PRESTAMOS_COLS = ["ISBN","Id_usuario","Fecha del préstamo","Fecha de devolución",
                  "Fecha de devolución real","Estado en que se devuelve","Fuera de plazo","Notas"]

def load_csv(path, cols):
    try: return pd.read_csv(path)
    except: return pd.DataFrame(columns=cols)

def save_csv(df, path): df.to_csv(path, index=False)

def df_to_pdf_bytes(title, df):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1,8)]
    data = [list(df.columns)] + [[str(r.get(c,"")) for c in df.columns] for _, r in df.iterrows()]
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                           ('GRID',(0,0),(-1,-1),0.25,colors.grey),
                           ('FONT',(0,0),(-1,0),'Helvetica-Bold'),
                           ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.whitesmoke,colors.white])]))
    story.append(t); doc.build(story); buf.seek(0); return buf

def export_section(title, df):
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ CSV", df.to_csv(index=False), file_name=f"{title.lower().replace(' ','_')}.csv")
    c2.download_button("🖨️ PDF", data=df_to_pdf_bytes(title, df),
                       file_name=f"{title.lower().replace(' ','_')}.pdf", mime="application/pdf")

# ---------- Carga inicial ----------
libros    = load_csv("libros.csv", LIBROS_COLS)
usuarios  = load_csv("usuarios.csv", USUARIOS_COLS)
prestamos = load_csv("prestamos.csv", PRESTAMOS_COLS)

# ---------- Estado y router ----------
st.session_state.setdefault("page", "Inicio")
st.session_state.setdefault("accion_Libros","Consultar")
st.session_state.setdefault("accion_Usuarios","Consultar")
st.session_state.setdefault("accion_Préstamos","Consultar")
st.session_state.setdefault("trigger_export", False)

def go(dest): st.session_state["page"] = dest

# ---------- Home ----------
def home_screen(libros_df, usuarios_df, prestamos_df):
    st.subheader("🏠 Inicio")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Libros", len(libros_df))
    with c2: st.metric("Usuarios", len(usuarios_df))
    with c3:
        v = 0
        if not prestamos_df.empty:
            df = prestamos_df.copy()
            df["Fecha de devolución"] = pd.to_datetime(df["Fecha de devolución"], errors="coerce")
            v = int((df["Fecha de devolución"].dropna() < pd.Timestamp.today()).sum())
        st.metric("Préstamos (vencidos)", v)

    st.markdown('<div class="home-grid">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="home-card">📘<h3>Libros</h3><p>Altas, bajas, modificación, consultas e impresión.</p></div>', unsafe_allow_html=True)
        st.button("Entrar a Libros", use_container_width=True, on_click=go, args=("Libros",))
    with col2:
        st.markdown('<div class="home-card">👤<h3>Usuarios</h3><p>Gestión de lectores y consultas.</p></div>', unsafe_allow_html=True)
        st.button("Entrar a Usuarios", use_container_width=True, on_click=go, args=("Usuarios",))
    with col3:
        st.markdown('<div class="home-card">🔁<h3>Préstamos</h3><p>Alta, devolución, vencidos y exportación.</p></div>', unsafe_allow_html=True)
        st.button("Entrar a Préstamos", use_container_width=True, on_click=go, args=("Préstamos",))
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Barra superior ----------
st.markdown("---")
cA, cB, cC, cD = st.columns(4)
with cA:
    if st.button("🏠 Inicio", use_container_width=True): go("Inicio")
with cB:
    if st.button("📘 Libros", use_container_width=True): go("Libros")
with cC:
    if st.button("👤 Usuarios", use_container_width=True): go("Usuarios")
with cD:
    if st.button("🔁 Préstamos", use_container_width=True): go("Préstamos")
st.markdown("---")

# ---------- Acciones inferiores ----------
def acciones_inferiores(modulo):
    st.markdown('<div class="page-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="bottom-bar"><div class="bar-grid">', unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        if st.button("➕ Alta", key=f"a_{modulo}"): st.session_state[f"accion_{modulo}"]="Alta"
    with c2:
        if st.button("🗑️ Baja", key=f"b_{modulo}"): st.session_state[f"accion_{modulo}"]="Baja"
    with c3:
        if st.button("✏️ Modificar", key=f"m_{modulo}"): st.session_state[f"accion_{modulo}"]="Modificar"
    with c4:
        if st.button("🔎 Consultar", key=f"c_{modulo}"): st.session_state[f"accion_{modulo}"]="Consultar"
    with c5:
        if st.button("🖨️ Exportar", key=f"e_{modulo}"): st.session_state["trigger_export"]=True
    with c6:
        if st.button("🏠 Inicio", key=f"v_{modulo}"): go("Inicio")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Módulo: Libros ----------
def render_libros():
    global libros
    st.subheader("📘 Libros")
    accion = st.radio("Acción (Libros)", ["Consultar","Alta","Modificar","Baja"],
                      index=["Consultar","Alta","Modificar","Baja"].index(st.session_state.get("accion_Libros","Consultar")),
                      horizontal=True, key="radio_libros")
    st.session_state["accion_Libros"]=accion

    if accion=="Consultar":
        c1,c2,c3=st.columns(3)
        f1=c1.text_input("Título (contiene)")
        f2=c2.text_input("Autor (contiene)")
        f3=c3.text_input("Categoría (contiene)")
        df=libros.copy()
        if f1: df=df[df["Título"].str.contains(f1,case=False,na=False)]
        if f2: df=df[df["Autor"].str.contains(f2,case=False,na=False)]
        if f3: df=df[df["Categoría"].str.contains(f3,case=False,na=False)]
        st.dataframe(df, use_container_width=True)
        if st.session_state.get("trigger_export", False):
            export_section("Libros", df); st.session_state["trigger_export"]=False

    elif accion=="Alta":
        with st.form("alta_libro"):
            c1,c2,c3=st.columns(3); isbn=c1.text_input("ISBN *"); titulo=c2.text_input("Título *"); autor=c3.text_input("Autor *")
            c4,c5,c6=st.columns(3); editorial=c4.text_input("Editorial *"); anio=c5.number_input("Año de publicación *",1800,2100,2024); cat=c6.text_input("Categoría *")
            c7,c8,c9=st.columns(3); ej=c7.number_input("Número de ejemplares *",1,999,1); estado=c8.selectbox("Estado *",["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"],index=2); ubi=c9.text_input("Ubicación *")
            notas=st.text_area("Notas (opcional)")
            if st.form_submit_button("Guardar libro"):
                if any([str(x).strip()=="" for x in [isbn,titulo,autor,editorial,cat,ubi]]):
                    st.error("Faltan campos obligatorios.")
                else:
                    row={"ISBN":isbn,"Título":titulo,"Autor":autor,"Editorial":editorial,"Año de publicación":anio,
                         "Categoría":cat,"Número de ejemplares":ej,"Estado de conservación":estado,"Ubicación":ubi,"Notas":notas}
                    libros=pd.concat([libros,pd.DataFrame([row])], ignore_index=True); save_csv(libros,"libros.csv"); st.success("Libro dado de alta.")

    elif accion=="Modificar":
        if libros.empty: st.info("No hay libros.")
        else:
            sel=st.selectbox("ISBN a modificar", libros["ISBN"].tolist())
            r=libros[libros["ISBN"]==sel].iloc[0]
            with st.form("mod_libro"):
                c1,c2,c3=st.columns(3); titulo=c1.text_input("Título *",r["Título"]); autor=c2.text_input("Autor *",r["Autor"]); editorial=c3.text_input("Editorial *",r["Editorial"])
                c4,c5,c6=st.columns(3); anio=c4.number_input("Año de publicación *",1800,2100,int(r["Año de publicación"])); cat=c5.text_input("Categoría *",r["Categoría"]); ej=c6.number_input("Número de ejemplares *",1,999,int(r["Número de ejemplares"]))
                c7,c8=st.columns(2); estado=c7.selectbox("Estado *",["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"],
                        index=["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"].index(r["Estado de conservación"]) if r["Estado de conservación"] in ["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"] else 2)
                ubi=c8.text_input("Ubicación *",r["Ubicación"]); notas=st.text_area("Notas", r.get("Notas",""))
                if st.form_submit_button("Guardar cambios"):
                    libros.loc[libros["ISBN"]==sel,["Título","Autor","Editorial","Año de publicación","Categoría","Número de ejemplares","Estado de conservación","Ubicación","Notas"]] = \
                    [titulo,autor,editorial,anio,cat,ej,estado,ubi,notas]
                    save_csv(libros,"libros.csv"); st.success("Libro modificado.")

    elif accion=="Baja":
        if libros.empty: st.info("No hay libros.")
        else:
            sel=st.selectbox("ISBN a eliminar", libros["ISBN"].tolist())
            if st.button("Eliminar libro"):
                libros=libros[libros["ISBN"]!=sel]; save_csv(libros,"libros.csv"); st.success("Libro eliminado.")
    acciones_inferiores("Libros")

# ---------- Módulo: Usuarios ----------
def render_usuarios():
    global usuarios
    st.subheader("👤 Usuarios")
    accion = st.radio("Acción (Usuarios)", ["Consultar","Alta","Modificar","Baja"],
                      index=["Consultar","Alta","Modificar","Baja"].index(st.session_state.get("accion_Usuarios","Consultar")),
                      horizontal=True, key="radio_usuarios")
    st.session_state["accion_Usuarios"]=accion

    if accion=="Consultar":
        c1,c2,c3=st.columns(3); f1=c1.text_input("Nombre/Apellidos (contiene)"); f2=c2.text_input("Teléfono (contiene)"); f3=c3.text_input("Correo (contiene)")
        df=usuarios.copy()
        if f1: df=df[df["Nombre o mote"].str.contains(f1,case=False,na=False) | df["Apellidos"].str.contains(f1,case=False,na=False)]
        if f2: df=df[df["Teléfono"].astype(str).str.contains(f2,na=False)]
        if f3: df=df[df["Correo electrónico"].str.contains(f3,case=False,na=False)]
        st.dataframe(df, use_container_width=True)
        if st.session_state.get("trigger_export", False):
            export_section("Usuarios", df); st.session_state["trigger_export"]=False

    elif accion=="Alta":
        with st.form("alta_usuario"):
            nombre=st.text_input("Nombre o mote *"); apellidos=st.text_input("Apellidos"); tel=st.text_input("Teléfono")
            mail=st.text_input("Correo electrónico"); dirc=st.text_input("Dirección"); notas=st.text_area("Notas (opcional)")
            if st.form_submit_button("Guardar usuario"):
                if str(nombre).strip()=="": st.error("El nombre es obligatorio.")
                else:
                    new_id = 1 if usuarios.empty else int(usuarios["Id_usuario"].max())+1
                    row={"Id_usuario":new_id,"Nombre o mote":nombre,"Apellidos":apellidos,"Teléfono":tel,"Correo electrónico":mail,"Dirección":dirc,"Notas":notas}
                    usuarios=pd.concat([usuarios,pd.DataFrame([row])], ignore_index=True); save_csv(usuarios,"usuarios.csv"); st.success(f"Usuario creado (Id {new_id}).")

    elif accion=="Modificar":
        if usuarios.empty: st.info("No hay usuarios.")
        else:
            uid=st.selectbox("Id_usuario a modificar", usuarios["Id_usuario"].astype(int).tolist())
            r=usuarios[usuarios["Id_usuario"]==uid].iloc[0]
            with st.form("mod_usuario"):
                nombre=st.text_input("Nombre o mote *", r["Nombre o mote"]); apellidos=st.text_input("Apellidos", r["Apellidos"])
                tel=st.text_input("Teléfono", r["Teléfono"]); mail=st.text_input("Correo electrónico", r["Correo electrónico"])
                dirc=st.text_input("Dirección", r["Dirección"]); notas=st.text_area("Notas", r.get("Notas",""))
                if st.form_submit_button("Guardar cambios"):
                    if str(nombre).strip()=="": st.error("El nombre es obligatorio.")
                    else:
                        usuarios.loc[usuarios["Id_usuario"]==uid, ["Nombre o mote","Apellidos","Teléfono","Correo electrónico","Dirección","Notas"]] = \
                        [nombre,apellidos,tel,mail,dirc,notas]
                        save_csv(usuarios,"usuarios.csv"); st.success("Usuario modificado.")

    elif accion=="Baja":
        if usuarios.empty: st.info("No hay usuarios.")
        else:
            uid=st.selectbox("Id_usuario a eliminar", usuarios["Id_usuario"].astype(int).tolist())
            if st.button("Eliminar usuario"):
                usuarios=usuarios[usuarios["Id_usuario"]!=uid]; save_csv(usuarios,"usuarios.csv"); st.success("Usuario eliminado.")
    acciones_inferiores("Usuarios")

# ---------- Módulo: Préstamos ----------
def render_prestamos():
    global prestamos, libros, usuarios
    st.subheader("🔁 Préstamos")
    accion = st.radio("Acción (Préstamos)", ["Consultar","Alta","Modificar","Baja","Registrar devolución"],
                      index=["Consultar","Alta","Modificar","Baja","Registrar devolución"].index(st.session_state.get("accion_Préstamos","Consultar")),
                      horizontal=True, key="radio_prestamos")
    st.session_state["accion_Préstamos"]=accion

    if not prestamos.empty:
        prestamos["Fecha del préstamo"]      = pd.to_datetime(prestamos["Fecha del préstamo"], errors="coerce")
        prestamos["Fecha de devolución"]     = pd.to_datetime(prestamos["Fecha de devolución"], errors="coerce")
        prestamos["Fecha de devolución real"]= pd.to_datetime(prestamos["Fecha de devolución real"], errors="coerce")
        hoy = pd.to_datetime(date.today())
        prestamos["Fuera de plazo"] = prestamos.apply(
            lambda r: (pd.isna(r["Fecha de devolución real"]) and pd.notna(r["Fecha de devolución"]) and hoy > r["Fecha de devolución"]) or
                      (pd.notna(r["Fecha de devolución real"]) and pd.notna(r["Fecha de devolución"]) and r["Fecha de devolución real"] > r["Fecha de devolución"]),
            axis=1
        )

    if accion=="Consultar":
        c1, c2 = st.columns(2)
        modo = c1.selectbox("Filtrar por fecha de préstamo", ["Todos","Antes de","En","Después de"])
        fref = c2.date_input("Fecha de referencia", value=date.today())

        df = prestamos.copy()

        if not df.empty:
            # Asegurar tipos de fecha y la columna booleana
            df["Fecha del préstamo"]       = pd.to_datetime(df["Fecha del préstamo"], errors="coerce")
            df["Fecha de devolución"]      = pd.to_datetime(df["Fecha de devolución"], errors="coerce")
            df["Fecha de devolución real"] = pd.to_datetime(df["Fecha de devolución real"], errors="coerce")
            df["Fuera de plazo"] = df["Fuera de plazo"].fillna(False).astype(bool)

            # Filtro por fecha de préstamo
            if modo == "Antes de":
                df = df[df["Fecha del préstamo"] < pd.to_datetime(fref)]
            elif modo == "En":
                df = df[df["Fecha del préstamo"] == pd.to_datetime(fref)]
            elif modo == "Después de":
                df = df[df["Fecha del préstamo"] > pd.to_datetime(fref)]

            # Columna visual en lugar de Styler
            df_mostrar = df.copy()
            df_mostrar["⚠️ Fuera de plazo"] = df_mostrar["Fuera de plazo"].map(lambda v: "Sí" if bool(v) else "—")

            # Orden opcional de columnas
            cols = [
                "ISBN","Id_usuario","Fecha del préstamo","Fecha de devolución",
                "Fecha de devolución real","Estado en que se devuelve","Notas","⚠️ Fuera de plazo"
            ]
            # Mantén solo columnas que existan
            cols = [c for c in cols if c in df_mostrar.columns]
            df_mostrar = df_mostrar[cols]

            st.dataframe(df_mostrar, use_container_width=True)

            # Exportación
            if st.session_state.get("trigger_export", False):
                export_section("Préstamos", df)  # exporta el DF real (incluye booleano)
                st.session_state["trigger_export"] = False
        else:
            st.info("No hay préstamos.")


    elif accion=="Alta":
        with st.form("alta_prestamo"):
            isbn=st.selectbox("ISBN *", libros["ISBN"].tolist() if not libros.empty else [])
            uid=st.selectbox("Id_usuario *", usuarios["Id_usuario"].astype(int).tolist() if not usuarios.empty else [])
            f_p=st.date_input("Fecha del préstamo *", value=date.today()); f_dev=f_p+timedelta(days=30)
            st.info(f"Fecha de devolución: {f_dev} (30 días naturales)")
            notas=st.text_area("Notas (opcional)")
            if st.form_submit_button("Guardar préstamo"):
                if not isbn or not uid: st.error("Faltan campos obligatorios.")
                else:
                    row={"ISBN":isbn,"Id_usuario":uid,"Fecha del préstamo":f_p,"Fecha de devolución":f_dev,
                         "Fecha de devolución real":"","Estado en que se devuelve":"","Fuera de plazo":False,"Notas":notas}
                    prestamos=pd.concat([prestamos,pd.DataFrame([row])], ignore_index=True); save_csv(prestamos,"prestamos.csv"); st.success("Préstamo creado.")

    elif accion=="Modificar":
        if prestamos.empty: st.info("No hay préstamos.")
        else:
            idx=st.number_input("Índice de fila a modificar", min_value=0, max_value=len(prestamos)-1, value=0)
            r=prestamos.iloc[idx]
            with st.form("mod_prestamo"):
                isbn_list = libros["ISBN"].tolist() if not libros.empty else []
                user_list = usuarios["Id_usuario"].astype(int).tolist() if not usuarios.empty else []
                isbn=st.selectbox("ISBN *", isbn_list, index=max(0, isbn_list.index(r["ISBN"]) if r["ISBN"] in isbn_list else 0))
                uid =st.selectbox("Id_usuario *", user_list, index=max(0, user_list.index(int(r["Id_usuario"])) if int(r["Id_usuario"]) in user_list else 0))
                f_p=st.date_input("Fecha del préstamo *", value=pd.to_datetime(r["Fecha del préstamo"]).date() if pd.notna(r["Fecha del préstamo"]) else date.today())
                f_dev=st.date_input("Fecha de devolución *", value=pd.to_datetime(r["Fecha de devolución"]).date() if pd.notna(r["Fecha de devolución"]) else f_p+timedelta(days=30))
                notas=st.text_area("Notas", value=r.get("Notas",""))
                if st.form_submit_button("Guardar cambios"):
                    prestamos.loc[idx, ["ISBN","Id_usuario","Fecha del préstamo","Fecha de devolución","Notas"]] = [isbn,uid,f_p,f_dev,notas]
                    save_csv(prestamos,"prestamos.csv"); st.success("Préstamo actualizado.")

    elif accion=="Baja":
        if prestamos.empty: st.info("No hay préstamos.")
        else:
            idx=st.number_input("Índice de fila a eliminar", min_value=0, max_value=len(prestamos)-1, value=0)
            if st.button("Eliminar préstamo"):
                prestamos=prestamos.drop(prestamos.index[idx]).reset_index(drop=True); save_csv(prestamos,"prestamos.csv"); st.success("Préstamo eliminado.")

    elif accion=="Registrar devolución":
        if prestamos.empty: st.info("No hay préstamos.")
        else:
            idx=st.number_input("Índice (devolución)", min_value=0, max_value=len(prestamos)-1, value=0)
            r=prestamos.iloc[idx]
            with st.form("devolver"):
                f_real=st.date_input("Fecha de devolución real *", value=date.today())
                estado_dev=st.selectbox("Estado en que se devuelve *", ["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"], index=2)
                notas=st.text_area("Notas", value=r.get("Notas",""))
                if st.form_submit_button("Registrar devolución"):
                    f_prev = pd.to_datetime(r["Fecha de devolución"]).date() if pd.notna(r["Fecha de devolución"]) else (pd.to_datetime(r["Fecha del préstamo"]).date()+timedelta(days=30))
                    fuera = f_real > f_prev
                    prestamos.loc[idx, ["Fecha de devolución real","Estado en que se devuelve","Fuera de plazo","Notas"]] = [f_real, estado_dev, fuera, notas]
                    save_csv(prestamos,"prestamos.csv")
                    # actualizar estado del libro si empeora
                    libro_row = libros[libros["ISBN"]==r["ISBN"]]
                    order = ["Nuevo","Muy bueno","Bueno","Aceptable","Dañado","Perdido"]
                    if not libro_row.empty:
                        actual = libro_row.iloc[0]["Estado de conservación"]
                        if actual in order and estado_dev in order and order.index(estado_dev) > order.index(actual):
                            libros.loc[libros["ISBN"]==r["ISBN"], "Estado de conservación"] = estado_dev
                            save_csv(libros,"libros.csv")
                    st.success("Devolución registrada y estado verificado/actualizado.")
    acciones_inferiores("Préstamos")

# ---------- Router ----------
if st.session_state["page"] == "Inicio":
    home_screen(libros, usuarios, prestamos)
elif st.session_state["page"] == "Libros":
    render_libros()
elif st.session_state["page"] == "Usuarios":
    render_usuarios()
elif st.session_state["page"] == "Préstamos":
    render_prestamos()
