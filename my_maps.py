import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Photon
import json
import os
import time
import ssl
import certifi
import requests

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="My Maps SC", layout="wide")


# --- FUNÇÃO AUXILIAR DE CONFIGURAÇÃO SEGURA ---
def obter_config(chave, valor_padrao=True):
    """Busca a configuração no st.secrets. Se não existir (local), usa o padrão."""
    try:
        return st.secrets.get(chave, valor_padrao)
    except:
        return valor_padrao


# Lendo as permissões do arquivo secreto (se não existirem, iniciam como True)
CONSEGUI_VER_LISTA = obter_config("HABILITAR_LISTA_CHAMADOS", True)
CONSEGUI_VER_ROTAS = obter_config("HABILITAR_ABA_ROTAS", True)

# 2. CSS GLOBAL
st.markdown(
    """
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }

        button[kind="headerNoPadding"] {
            color: #FFFFFF !important; 
            background-color: #1E1E1E !important;
            border: 1px solid #333333 !important; 
            border-radius: 5px !important;
            visibility: visible !important; 
            z-index: 1000001 !important; 
            margin-left: 5px !important;
        }

        header[data-testid="stHeader"] { 
            background-color: transparent !important; 
            z-index: 1000000 !important; 
        }

        #MainMenu, footer {visibility: hidden;}

        .map-container { 
            margin-left: 20px !important; 
            margin-right: 20px !important; 
        }

        .lista-chamados-container {
            max-height: 400px;
            overflow-y: auto;
            background-color: #262730;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #464855;
        }

        .lista-chamados-container div[data-testid="stButton"] button {
            padding: 4px 10px !important;
            font-family: monospace;
            text-align: left;
            margin-bottom: -5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 11px !important;
        }

        div[data-testid="stHorizontalBlock"] button {
            margin-top: 4px !important;
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializa estados globais
if 'mapa_pronto' not in st.session_state:
    st.session_state.mapa_pronto = None
if 'df_final' not in st.session_state:
    st.session_state.df_final = None
if 'chamado_selecionado' not in st.session_state:
    st.session_state.chamado_selecionado = None
if 'map_center' not in st.session_state:
    st.session_state.map_center = [-27.2, -50.5]
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 8
if 'ultimo_arquivo' not in st.session_state:
    st.session_state.ultimo_arquivo = None
if 'expander_aberto' not in st.session_state:
    st.session_state.expander_aberto = False
if 'coords_sessao' not in st.session_state:
    st.session_state.coords_sessao = {}


def mapear_coluna_flexivel(lista_colunas, alvos):
    for col in lista_colunas:
        if str(col).strip().upper() in [t.upper() for t in alvos]:
            return col
    for col in lista_colunas:
        for t in alvos:
            if t.lower() in str(col).strip().lower():
                return col
    return None


# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("📍 My Maps SC")
    st.caption("Modo de Geocodificação em Tempo Real (Sem Cache Local)")
    st.markdown("---")

    arquivo = st.file_uploader("Upload da Planilha Excel", type=["xlsx"])

    if arquivo:
        is_novo_arquivo = (st.session_state.ultimo_arquivo != arquivo.name)
        xl = pd.ExcelFile(arquivo)
        abas_disponiveis = xl.sheet_names

        aba_alvo = None
        for prioridade in ["unificado", "rat's", "rats", "chamados"]:
            for name in abas_disponiveis:
                if name.strip().lower() == prioridade:
                    aba_alvo = name
                    break
            if aba_alvo:
                break

        if aba_alvo:
            st.caption(f"📖 Aba carregada: **{aba_alvo}**")
            aba_selecionada = aba_alvo
        else:
            st.warning("⚠️ Aba padrão não encontrada.")
            aba_selecionada = st.selectbox("Selecione a aba manualmente", abas_disponiveis)

        if is_novo_arquivo or st.session_state.df_final is None or st.sidebar.button("⚡ Gerar / Atualizar Mapa",
                                                                                     key="btn_gerar"):
            df_aba = pd.read_excel(arquivo, sheet_name=aba_selecionada)

            col_os = mapear_coluna_flexivel(df_aba.columns.tolist(), ["CodOS", "Chamado", "ID", "Ticket"])
            col_cidade = mapear_coluna_flexivel(df_aba.columns.tolist(), ["Cidade", "Municipio", "Cid"])
            col_uf = mapear_coluna_flexivel(df_aba.columns.tolist(), ["SiglaUF", "UF", "Estado"])
            col_rua = mapear_coluna_flexivel(df_aba.columns.tolist(), ["Endereco", "Endereço", "Logradouro", "Rua"])

            if col_os and col_cidade and col_uf and col_rua:
                df_limpo = df_aba[[col_os, col_cidade, col_uf, col_rua]].dropna(subset=[col_os, col_rua])

                df_limpo = df_limpo.rename(columns={
                    col_os: 'CodOS',
                    col_cidade: 'Cidade',
                    col_uf: 'SiglaUF',
                    col_rua: 'Endereco'
                })

                df_limpo['CodOS'] = df_limpo['CodOS'].astype(str).str.split('.').str[0].str.strip()
                df_limpo = df_limpo.drop_duplicates(subset=['CodOS'], keep='first')

                st.session_state.df_final = df_limpo
                st.session_state.ultimo_arquivo = arquivo.name
                st.session_state.chamado_selecionado = None
                st.session_state.map_center = [-27.2, -50.5]
                st.session_state.map_zoom = 8
                st.session_state.expander_aberto = False
                st.session_state.coords_sessao = {}

                st.session_state.mapa_pronto = "solicitar_geracao"
                st.rerun()
            else:
                st.error("❌ Não foi possível encontrar todas as colunas (OS, Cidade, UF, Endereco) nesta aba.")

# --- PROCESSAMENTO DO MAPA AUTOMÁTICO ---
if st.session_state.df_final is not None:
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

    df = st.session_state.df_final
    dados_mapa = df.dropna(subset=['Endereco', 'Cidade', 'SiglaUF'])
    grupo_pontos = dados_mapa.groupby(['Endereco', 'Cidade', 'SiglaUF']).size().reset_index(name='qtd')

    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Photon(ssl_context=ctx, user_agent="mymaps_sc_fast")

    pontos_para_buscar = []
    EXCECOES_CIDADES = {"ZORTEA": [-27.4514, -51.5542]}

    for row in grupo_pontos.itertuples(index=False):
        rua_limpa = str(row.Endereco).strip()
        cid_limpa = str(row.Cidade).strip()
        uf_limpa = str(row.SiglaUF).strip()

        endereco_completo_busca = f"{rua_limpa}, {cid_limpa} - {uf_limpa}, Brasil"
        chave_busca = endereco_completo_busca.upper().strip()

        cid_upper = cid_limpa.upper().strip()
        if cid_upper in EXCECOES_CIDADES:
            st.session_state.coords_sessao[chave_busca] = EXCECOES_CIDADES[cid_upper]

        if chave_busca in st.session_state.coords_sessao:
            pos = st.session_state.coords_sessao[chave_busca]
            qtd_chamados = int(row.qtd)
            raio_marcador = min(9 + (qtd_chamados * 0.2), 28)
            diametro = int(raio_marcador * 2)
            tamanho_fonte = max(8, min(12, int(raio_marcador * 0.65)))
            texto_exibicao = f"<b>{cid_limpa} - {uf_limpa}</b><br><small>{rua_limpa}</small><br>Chamados no local: {qtd_chamados}"

            html_icone = f"""<div style="background-color: #FF4B4B; color: white; border: 1px solid #1E1E1E; border-radius: 50%; width: {diametro}px; height: {diametro}px; display: flex; align-items: center; justify-content: center; font-size: {tamanho_fonte}px; font-weight: bold; box-shadow: 0px 0px 8px #FF4B4B;">{qtd_chamados}</div>"""

            folium.Marker(location=pos, icon=folium.DivIcon(html=html_icone, icon_size=(diametro, diametro),
                                                            icon_anchor=(raio_marcador, raio_marcador)),
                          tooltip=texto_exibicao, popup=texto_exibicao).add_to(m)
        else:
            pontos_para_buscar.append((row, endereco_completo_busca, chave_busca))

    if pontos_para_buscar:
        prog = st.sidebar.progress(0)
        status = st.sidebar.empty()

        for idx, (row, endereco_completo_busca, chave_busca) in enumerate(pontos_para_buscar):
            rua = str(row.Endereco).strip()
            cid = str(row.Cidade).strip()
            qtd_chamados = int(row.qtd)

            raio_marcador = min(9 + (qtd_chamados * 0.2), 28)
            diametro = int(raio_marcador * 2)
            tamanho_fonte = max(8, min(12, int(raio_marcador * 0.65)))
            texto_exibicao = f"<b>{cid} - {row.SiglaUF}</b><br><small>{rua}</small><br>Chamados no local: {qtd_chamados}"

            html_icone = f"""<div style="background-color: #FF4B4B; color: white; border: 1px solid #1E1E1E; border-radius: 50%; width: {diametro}px; height: {diametro}px; display: flex; align-items: center; justify-content: center; font-size: {tamanho_fonte}px; font-weight: bold; box-shadow: 0px 0px 8px #FF4B4B;">{qtd_chamados}</div>"""

            status.text(f"🌐 Buscando novos locais: {cid} ({idx + 1}/{len(pontos_para_buscar)})...")
            pos = None
            try:
                loc = geolocator.geocode(endereco_completo_busca, timeout=3)
                if loc:
                    pos = [loc.latitude, loc.longitude]
                    st.session_state.coords_sessao[chave_busca] = pos
                else:
                    loc_fallback = geolocator.geocode(f"{rua.split(',')[0]}, {cid}, Brasil", timeout=2)
                    if loc_fallback:
                        pos = [loc_fallback.latitude, loc_fallback.longitude]
                        st.session_state.coords_sessao[chave_busca] = pos
            except:
                pos = None

            if pos:
                folium.Marker(location=pos, icon=folium.DivIcon(html=html_icone, icon_size=(diametro, diametro),
                                                                icon_anchor=(raio_marcador, raio_marcador)),
                              tooltip=texto_exibicao, popup=texto_exibicao).add_to(m)

            prog.progress((idx + 1) / len(pontos_para_buscar))

        status.empty()
        prog.empty()

    st.session_state.mapa_pronto = m

# --- RENDERIZAÇÃO DA SIDEBAR CONDICIONAL ---
if st.session_state.df_final is not None and CONSEGUI_VER_LISTA:
    with st.sidebar:
        df = st.session_state.df_final
        df_botoes = df.copy()
        df_botoes['OS_Num'] = pd.to_numeric(df_botoes['CodOS'], errors='coerce')
        df_botoes = df_botoes.sort_values(by=['Cidade', 'OS_Num', 'CodOS'])

        st.markdown("---")
        with st.expander(f"📋 Lista de Chamados ({len(df_botoes)})", expanded=st.session_state.expander_aberto):
            busca = st.text_input("🔍 Pesquisar por OS ou Cidade:", placeholder="Ex: Capinzal...")

            if busca:
                st.session_state.expander_aberto = True
                busca_normalizada = str(busca).strip().lower()
                df_botoes = df_botoes[
                    df_botoes['CodOS'].astype(str).str.lower().str.contains(busca_normalizada) |
                    df_botoes['Cidade'].astype(str).str.lower().str.contains(busca_normalizada)
                    ]

            st.markdown('<div class="lista-chamados-container">', unsafe_allow_html=True)

            if df_botoes.empty:
                st.caption("⚠️ Nenhum chamado encontrado.")
            else:
                for idx, row in enumerate(df_botoes.itertuples(index=False)):
                    cham = str(row.CodOS)
                    cid = str(row.Cidade)
                    uf_val = str(row.SiglaUF)
                    rua_completa = str(row.Endereco)

                    is_selecionado = (str(st.session_state.chamado_selecionado) == cham)
                    prefixo = "🔷" if is_selecionado else "🔵"
                    label_botao = f"{prefixo} [{cid}] OS: {cham}"

                    if st.button(label_botao, key=f"btn_os_{cham}_{idx}"):
                        st.session_state.chamado_selecionado = cham
                        st.session_state.expander_aberto = True

                        busca_endereco = f"{rua_completa.strip()}, {cid.strip()} - {uf_val.strip()}, Brasil".upper().strip()
                        if busca_endereco not in st.session_state.coords_sessao:
                            busca_endereco = " ".join(busca_endereco.split())

                        if busca_endereco in st.session_state.coords_sessao:
                            st.session_state.map_center = st.session_state.coords_sessao[busca_endereco]
                            st.session_state.map_zoom = 17
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA PRINCIPAL COM CONTROLE DE ABAS REMOTO ---
if st.session_state.mapa_pronto:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)

    # Monta as abas baseadas nas flags secretas do arquivo TOML
    lista_abas_nome = ["🗺️ Visão Geral"]
    if CONSEGUI_VER_ROTAS:
        lista_abas_nome.append("🚗 Traçar Rotas")

    abas_renderizadas = st.tabs(lista_abas_nome)

    # Aba 1 sempre fixa
    with abas_renderizadas[0]:
        saída_mapa_geral = st_folium(
            st.session_state.mapa_pronto,
            width=1800,
            height=850,
            use_container_width=True,
            returned_objects=["last_object_clicked"],
            center=st.session_state.map_center,
            zoom=st.session_state.map_zoom,
            key=f"mapa_geral_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}"
        )

        if saída_mapa_geral and saída_mapa_geral.get("last_object_clicked"):
            lat_clicada = saída_mapa_geral["last_object_clicked"]["lat"]
            lng_clicada = saída_mapa_geral["last_object_clicked"]["lng"]
            nova_posicao = [lat_clicada, lng_clicada]
            if nova_posicao != st.session_state.map_center or st.session_state.map_zoom != 17:
                st.session_state.map_center = nova_posicao
                st.session_state.map_zoom = 17
                st.rerun()

    # Aba 2 (Rotas) condicional
    if CONSEGUI_VER_ROTAS:
        with abas_renderizadas[1]:
            df_rotas = st.session_state.df_final
            lista_cidades = sorted(df_rotas['Cidade'].unique().tolist())

            col1, col2, col3 = st.columns([2, 2, 1.2])
            with col1:
                origem = st.selectbox("📍 Cidade de Origem", lista_cidades, key="origem_rota")
            with col2:
                def_idx = min(1, len(lista_cidades) - 1)
                destino = st.selectbox("🏁 Cidade de Destino", lista_cidades, index=def_idx, key="destino_rota")
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                calcular = st.button("🚀 Calcular Rota", use_container_width=True)

            m_rota = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
            for child in st.session_state.mapa_pronto._children.values():
                if isinstance(child, folium.Marker):
                    child.add_to(m_rota)

            if calcular:
                lin_origem = df_rotas[df_rotas['Cidade'] == origem].iloc[0]
                lin_destino = df_rotas[df_rotas['Cidade'] == destino].iloc[0]

                key_origem = f"{str(lin_origem['Endereco']).strip()}, {str(lin_origem['Cidade']).strip()} - {str(lin_origem['SiglaUF']).strip()}, Brasil".upper().strip()
                key_destino = f"{str(lin_destino['Endereco']).strip()}, {str(lin_destino['Cidade']).strip()} - {str(lin_destino['SiglaUF']).strip()}, Brasil".upper().strip()

                if key_origem in st.session_state.coords_sessao and key_destino in st.session_state.coords_sessao:
                    ponto_A = st.session_state.coords_sessao[key_origem]
                    ponto_B = st.session_state.coords_sessao[key_destino]
                    url_osrm = f"http://router.project-osrm.org/route/v1/driving/{ponto_A[1]},{ponto_A[0]};{ponto_B[1]},{ponto_B[0]}?overview=full&geometries=geojson"

                    try:
                        res = requests.get(url_osrm, timeout=5).json()
                        if "routes" in res and len(res["routes"]) > 0:
                            coordenadas_linha = res["routes"][0]["geometry"]["coordinates"]
                            trajeto_folium = [[coord[1], coord[0]] for coord in coordenadas_linha]
                            folium.PolyLine(locations=trajeto_folium, color="#007BFF", weight=6, opacity=0.8,
                                            tooltip=f"Rota: {origem} ➡️ {destino}").add_to(m_rota)
                            folium.Marker(location=ponto_A, popup="Início",
                                          icon=folium.Icon(color='green', icon='play')).add_to(m_rota)
                            folium.Marker(location=ponto_B, popup="Fim",
                                          icon=folium.Icon(color='black', icon='stop')).add_to(m_rota)
                            m_rota.location = [(ponto_A[0] + ponto_B[0]) / 2, (ponto_A[1] + ponto_B[1]) / 2]
                            m_rota.zoom_start = 10
                        else:
                            st.error("Não foi possível calcular o traçado.")
                    except:
                        st.error("Erro de conexão ao servidor de rotas.")
                else:
                    st.error("Coordenadas não encontradas no mapa atual.")

            saída_mapa_rotas = st_folium(
                m_rota,
                width=1800,
                height=700,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=f"mapa_rotas_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}"
            )

            if saída_mapa_rotas and saída_mapa_rotas.get("last_object_clicked"):
                lat_clicada = saída_mapa_rotas["last_object_clicked"]["lat"]
                lng_clicada = saída_mapa_rotas["last_object_clicked"]["lng"]
                if [lat_clicada, lng_clicada] != st.session_state.map_center or st.session_state.map_zoom != 17:
                    st.session_state.map_center = [lat_clicada, lng_clicada]
                    st.session_state.map_zoom = 17
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.container().markdown("<br><br><center><h3>⬅️ Insira a planilha para renderizar os endereços</h3></center>",
                            unsafe_allow_html=True)