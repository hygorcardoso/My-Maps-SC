import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import json
import os
import time
import ssl
import certifi

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="My Maps SC - Filtro Rigoroso", layout="wide")

# 2. CSS PARA REMOVER BORDAS
st.markdown(
    """
    <style>
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        header, footer {
            display: none !important;
        }
        .stButton > button {
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

CACHE_FILE = "coords_cache.json"


def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                return json.loads(content) if content else {}
        except Exception:
            return {}
    return {}


# FUNÇÃO DE DETECÇÃO RIGOROSA (V3)
def detectar_coluna_v3(lista_colunas, termos_exatos, termos_contidos):
    # Passo 1: Busca EXATA (Ignora espaços e maiúsculas)
    # Isso evita pegar "NumOfcliente" quando buscamos "UF"
    for i, col in enumerate(lista_colunas):
        nome_limpo = str(col).strip().upper()
        if nome_limpo in [t.upper() for t in termos_exatos]:
            return i

    # Passo 2: Busca por PALAVRA COMPLETA dentro do nome (Usando split)
    # Evita pegar termos no meio de outras palavras
    for i, col in enumerate(lista_colunas):
        palavras = str(col).strip().upper().replace("_", " ").replace("-", " ").split()
        if any(t.upper() in palavras for t in termos_exatos):
            return i

    # Passo 3: Busca por TERMO CONTIDO (Apenas se falhar os anteriores)
    for i, col in enumerate(lista_colunas):
        nome_limpo = str(col).strip().lower()
        if any(t.lower() in nome_limpo for t in termos_contidos):
            return i

    return 0


if 'cache' not in st.session_state:
    st.session_state.cache = carregar_cache()

if 'mapa_pronto' not in st.session_state:
    st.session_state.mapa_pronto = None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("📍 My Maps SC")
    st.markdown("---")

    arquivo = st.file_uploader("Upload da Planilha Excel", type=["xlsx"])

    if arquivo:
        xl = pd.ExcelFile(arquivo)
        aba = st.selectbox("Selecione a Aba", xl.sheet_names)
        df = pd.read_excel(arquivo, sheet_name=aba)

        cols = df.columns.tolist()

        # LÓGICA RIGOROSA
        # Cidade: Tenta "Cidade", "Município" exatos primeiro.
        idx_cidade = detectar_coluna_v3(cols, ["cidade", "municipio", "localidade"], ["cid", "mun"])

        # UF: Tenta "UF" ou "ESTADO" exatos.
        # A busca por termo contido "sc" ou "est" só ocorre se não achar "UF".
        idx_uf = detectar_coluna_v3(cols, ["uf", "estado", "sigla"], ["est", "sc"])

        col_cidade = st.selectbox("Coluna Cidade", cols, index=idx_cidade)
        col_uf = st.selectbox("Coluna UF", cols, index=idx_uf)

        st.markdown("---")
        if st.button("⚡ Gerar Mapa", use_container_width=True):
            st.session_state.mapa_pronto = None

            dados = df[[col_cidade, col_uf]].dropna().drop_duplicates()

            ctx = ssl.create_default_context(cafile=certifi.where())
            geolocator = Nominatim(user_agent="mymaps_web_v10_rigorous", ssl_context=ctx)

            m = folium.Map(location=[-27.2, -50.5], zoom_start=8)

            progresso = st.progress(0)
            status_txt = st.empty()
            encontradas = 0
            cache_alterado = False

            for i, row in enumerate(dados.itertuples(index=False)):
                c, u = str(getattr(row, col_cidade)).strip(), str(getattr(row, col_uf)).strip()
                chave = f"{c}, {u}, Brasil"

                if chave in st.session_state.cache:
                    pos = st.session_state.cache[chave]
                    folium.Marker(pos, tooltip=c, popup=c).add_to(m)
                    encontradas += 1
                else:
                    status_txt.text(f"🌐 Geocodificando: {c}...")
                    try:
                        loc = geolocator.geocode(chave, timeout=10)
                        if loc:
                            pos = [loc.latitude, loc.longitude]
                            folium.Marker(pos, tooltip=c, popup=c).add_to(m)
                            st.session_state.cache[chave] = pos
                            encontradas += 1
                            cache_alterado = True
                        time.sleep(1.1)
                    except Exception:
                        continue

                progresso.progress((i + 1) / len(dados))

            if cache_alterado:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.cache, f, indent=4)

            status_txt.success(f"✅ {encontradas} pontos carregados!")
            st.session_state.mapa_pronto = m
            st.rerun()

# --- ÁREA PRINCIPAL ---
if st.session_state.mapa_pronto:
    st_folium(
        st.session_state.mapa_pronto,
        width=1800,
        height=900,
        use_container_width=True
    )
else:
    st.container().markdown("<br><br><center><h3>⬅️ Configure os dados na barra lateral</h3></center>",
                            unsafe_allow_html=True)