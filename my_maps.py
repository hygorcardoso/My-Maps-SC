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
st.set_page_config(page_title="My Maps SC", layout="wide")

# 2. CSS GLOBAL
st.markdown(
    """
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        button[kind="headerNoPadding"] {
            color: #FFFFFF !important; background-color: #1E1E1E !important;
            border: 1px solid #333333 !important; border-radius: 5px !important;
            visibility: visible !important; z-index: 1000001 !important; margin-left: 5px !important;
        }
        header[data-testid="stHeader"] { background-color: transparent !important; z-index: 1000000 !important; }
        #MainMenu, footer {visibility: hidden;}
        .map-container { margin-left: 20px !important; margin-right: 20px !important; }
        .stButton > button { width: 100%; }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. LÓGICA DE CACHE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "coords_cache.json")


def carregar_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # AJUSTE CRUCIAL: Remove ", BRASIL" das chaves antigas ao carregar
                novo_cache = {}
                for k, v in data.items():
                    chave_limpa = str(k).upper().replace(", BRASIL", "").strip()
                    novo_cache[chave_limpa] = v
                return novo_cache
        except:
            return {}
    return {}


def salvar_cache(cache_data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=4, ensure_ascii=False)


if 'cache' not in st.session_state:
    st.session_state.cache = carregar_cache()
if 'mapa_pronto' not in st.session_state:
    st.session_state.mapa_pronto = None


def detectar_coluna(cols, exatos, contidos):
    for i, col in enumerate(cols):
        c_up = str(col).strip().upper()
        if c_up in [t.upper() for t in exatos]: return i
    for i, col in enumerate(cols):
        c_low = str(col).strip().lower()
        if any(t.lower() in c_low for t in contidos): return i
    return 0


# --- BARRA LATERAL ---
with st.sidebar:
    st.title("📍 My Maps SC")
    st.caption(f"Cidades em cache: {len(st.session_state.cache)}")
    st.markdown("---")
    arquivo = st.file_uploader("Upload Excel", type=["xlsx"])

    if arquivo:
        xl = pd.ExcelFile(arquivo)
        aba = st.selectbox("Aba", xl.sheet_names)
        df = pd.read_excel(arquivo, sheet_name=aba)
        cols = df.columns.tolist()

        col_cidade = st.selectbox("Cidade", cols, index=detectar_coluna(cols, ["cidade", "municipio"], ["cid", "mun"]))
        col_uf = st.selectbox("UF", cols, index=detectar_coluna(cols, ["uf", "estado"], ["uf", "sc"]))

        if st.button("⚡ Gerar Mapa"):
            st.session_state.mapa_pronto = None
            dados = df[[col_cidade, col_uf]].dropna().drop_duplicates()

            ctx = ssl.create_default_context(cafile=certifi.where())
            geolocator = Nominatim(user_agent="mymaps_sc_v5", ssl_context=ctx)
            m = folium.Map(location=[-27.2, -50.5], zoom_start=8)

            prog = st.progress(0)
            status = st.empty()
            encontradas = 0
            alterado = False

            for i, row in enumerate(dados.itertuples(index=False)):
                c = str(getattr(row, col_cidade)).strip()
                u = str(getattr(row, col_uf)).strip()

                # Busca apenas por "CIDADE, UF"
                chave_busca = f"{c.upper()}, {u.upper()}"

                if chave_busca in st.session_state.cache:
                    pos = st.session_state.cache[chave_busca]
                    folium.Marker(pos, tooltip=c, popup=c).add_to(m)
                    encontradas += 1
                else:
                    status.text(f"🌐 Geocodificando: {c}...")
                    try:
                        # O Nominatim continua recebendo ", Brasil" para precisão na busca
                        loc = geolocator.geocode(f"{c}, {u}, Brasil", timeout=10)
                        if loc:
                            pos = [loc.latitude, loc.longitude]
                            folium.Marker(pos, tooltip=c, popup=c).add_to(m)
                            st.session_state.cache[chave_busca] = pos
                            encontradas += 1
                            alterado = True
                        time.sleep(1.1)
                    except:
                        continue
                prog.progress((i + 1) / len(dados))

            if alterado: salvar_cache(st.session_state.cache)
            status.success(f"✅ {encontradas} pontos carregados!")
            st.session_state.mapa_pronto = m
            st.rerun()

# --- ÁREA PRINCIPAL ---
if st.session_state.mapa_pronto:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(st.session_state.mapa_pronto, width=1800, height=900, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.container().markdown("<br><br><center><h3>⬅️ Configure os dados na barra lateral</h3></center>",
                            unsafe_allow_html=True)