import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="My Maps BR",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo para deixar em tela cheia sem margens do Streamlit
st.markdown(
    """
    <style>
        #MainMenu, header, footer { visibility: hidden; }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
            overflow: hidden !important;
        }
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw !important;
            height: 100vh !important;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Procura o arquivo HTML na mesma pasta do my_maps.py
diretorio_atual = Path(__file__).parent
arquivo_html = None

# Tenta encontrar o arquivo HTML pelo nome comum
for nome in ["mymaps.html", "index.html"]:
    caminho = diretorio_atual / nome
    if caminho.exists():
        arquivo_html = caminho
        break

if arquivo_html:
    with open(arquivo_html, "r", encoding="utf-8") as f:
        conteudo_html = f.read()
    components.html(conteudo_html, height=900, scrolling=False)
else:
    st.error("❌ Arquivo 'mymaps.html' ou 'index.html' não foi encontrado na pasta do projeto.")