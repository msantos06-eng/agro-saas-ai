import streamlit as st
import requests

API_URL = "https://SEU-BACKEND.onrender.com"

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ======================
# LOGIN
# ======================
if not st.session_state.user_id:

    st.title("🌱 Agro SaaS")

    aba = st.radio("Acesso", ["Login", "Cadastro"])

    if aba == "Cadastro":
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            requests.post(f"{API_URL}/register", params={"usuario": u, "senha": s})
            st.success("Criado")

    if aba == "Login":
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            r = requests.post(f"{API_URL}/login", params={"usuario": u, "senha": s})
            if r.status_code == 200:
                st.session_state.user_id = r.json()["user_id"]
                st.rerun()
            else:
                st.error("Erro login")

# ======================
# APP
# ======================
else:

    st.sidebar.button("Sair", on_click=lambda: st.session_state.update(user_id=None))

    menu = st.sidebar.radio("Menu", ["Fazendas", "Talhões"])

    if menu == "Fazendas":

        nome = st.text_input("Nome fazenda")

        if st.button("Salvar"):
            requests.post(f"{API_URL}/fazenda",
                          params={"nome": nome, "user_id": st.session_state.user_id})

        dados = requests.get(f"{API_URL}/fazendas/{st.session_state.user_id}").json()

        for f in dados:
            st.write("🌾", f["nome"])

    elif menu == "Talhões":

        fazendas = requests.get(f"{API_URL}/fazendas/{st.session_state.user_id}").json()

        nomes = [f["nome"] for f in fazendas]
        escolha = st.selectbox("Fazenda", nomes)

        fid = [f["id"] for f in fazendas if f["nome"] == escolha][0]

        nome = st.text_input("Talhão")
        area = st.number_input("Área")

        if st.button("Salvar"):
            requests.post(f"{API_URL}/talhao",
                          params={"nome": nome, "area": area, "fazenda_id": fid})

        dados = requests.get(f"{API_URL}/talhoes/{fid}").json()

        for t in dados:
            st.write("📍", t["nome"], "-", t["area"], "ha")