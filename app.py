import streamlit as st
import sqlite3
import hashlib
import os
import requests
import json
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw
from PIL import Image
import io

st.set_page_config(layout="wide")

# =========================
# DB (CORRIGIDO)
# =========================
@st.cache_resource
def get_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, email TEXT, senha TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS talhoes (id INTEGER PRIMARY KEY, usuario_id INTEGER, geojson TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS fazendas (id INTEGER PRIMARY KEY, usuario_id INTEGER, nome TEXT)")
    conn.commit()

    return conn

conn = get_db()
c = conn.cursor()

# =========================
# FUNÇÕES
# =========================
def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def get_token():
    try:
        url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET")
        }

        r = requests.post(url, data=data)

        if r.status_code != 200:
            return None

        return r.json().get("access_token")

    except:
        return None

@st.cache_data(ttl=3600)
def buscar_ndvi_satellite(geojson):
    token = get_token()

    if not token:
        return None

    url = "https://sh.dataspace.copernicus.eu/api/v1/process"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "input": {
            "bounds": {"geometry": geojson},
            "data": [{"type": "sentinel-2-l2a"}]
        },
        "evalscript": """
        //VERSION=3
        function setup() {
          return { input: ["B04", "B08"], output: { bands: 3 } };
        }
        function evaluatePixel(sample) {
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          if (ndvi < 0.2) return [1,0,0];
          else if (ndvi < 0.5) return [1,1,0];
          else return [0,1,0];
        }
        """,
        "output": {"width": 512, "height": 512}
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        return None

    return response.content

# =========================
# LOGIN
# =========================
st.sidebar.title("Login")

if "user_id" not in st.session_state:
    email = st.sidebar.text_input("Email")
    senha = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        senha_hash = hash_senha(senha)
        c.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha_hash))
        user = c.fetchone()

        if user:
            st.session_state["user_id"] = user[0]
            st.success("Logado!")
            st.rerun()
        else:
            st.error("Erro login")

    if st.sidebar.button("Cadastrar"):
        senha_hash = hash_senha(senha)
        c.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        if c.fetchone():
            st.error("Usuário já existe")
        else:
            c.execute("INSERT INTO usuarios (email, senha) VALUES (?,?)", (email, senha_hash))
            conn.commit()
            st.success("Usuário criado!")

else:
    st.sidebar.success("Logado")
    if st.sidebar.button("Logout"):
        del st.session_state["user_id"]
        st.rerun()

# =========================
# MENU
# =========================
menu = st.sidebar.radio("Menu", ["Dashboard", "Mapa", "NDVI Satélite"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    if "user_id" not in st.session_state:
        st.warning("Faça login")
    else:
        c.execute("SELECT COUNT(*) FROM talhoes WHERE usuario_id=?", (st.session_state["user_id"],))
        total = c.fetchone()[0]

        st.metric("🌾 Total de Talhões", total)

# =========================
# MAPA
# =========================
if menu == "Mapa":
    st.title("🗺️ Mapa")

    mapa = folium.Map(location=[-12.5, -45.0], zoom_start=13)
    Draw(export=True).add_to(mapa)

    map_data = st_folium(mapa)

    if map_data and map_data.get("last_active_drawing"):
        geojson = map_data["last_active_drawing"]
        st.session_state["talhao"] = geojson

        if "user_id" in st.session_state:
            if st.button("Salvar Talhão"):
                c.execute(
                    "INSERT INTO talhoes (usuario_id, geojson) VALUES (?, ?)",
                    (st.session_state["user_id"], json.dumps(geojson))
                )
                conn.commit()
                st.success("Talhão salvo!")

# =========================
# NDVI
# =========================
if menu == "NDVI Satélite":
    st.title("🛰️ NDVI")

    if "talhao" not in st.session_state:
        st.warning("Desenhe um talhão primeiro")
    else:
        geo = st.session_state["talhao"]["geometry"]

        with st.spinner("Buscando NDVI..."):
            img_bytes = buscar_ndvi_satellite(geo)

        if not img_bytes:
            st.error("Erro ao buscar imagem")
        else:
            imagem = Image.open(io.BytesIO(img_bytes))
            st.image(imagem, caption="NDVI Satélite")