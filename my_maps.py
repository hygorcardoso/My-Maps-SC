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
st.set_page_config(page_title="My Maps BR", layout="wide")


# --- FUNÇÃO AUXILIAR DE CONFIGURAÇÃO SEGURA ---
def obter_config(chave, valor_padrao=True):
    try:
        return st.secrets.get(chave, valor_padrao)
    except:
        return valor_padrao


# Lendo as permissões do arquivo secreto
CONSEGUI_VER_LISTA = obter_config("HABILITAR_LISTA_CHAMADOS", True)
CONSEGUI_VER_ROTAS = obter_config("HABILITAR_ABA_ROTAS", True)

# 2. CSS GLOBAL (LARGURA DA SIDEBAR EM 240PX EXPANDIDA E 20PX RECOLHIDA COM BOTÃO ATIVO)
st.markdown(
    """
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }

        /* --- TRAVA A LARGURA DA SIDEBAR EM 240PX QUANDO EXPANDIDA --- */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: 240px !important;
            min-width: 240px !important;
            max-width: 240px !important;
        }

        /* --- MANTÉM UMA FAIXA MINIMALISTA DE 20PX QUANDO RECOLHIDA --- */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            width: 20px !important;
            min-width: 20px !important;
            max-width: 20px !important;
            background-color: #1E1E24 !important;
        }

        /* Oculta os elementos internos da barra quando fechada para não quebrar o layout */
        section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarUserContent"] {
            display: none !important;
        }

        /* --- OCULTA APENAS A TOOLBAR DA DIREITA (Share, Star, GitHub, Menus) --- */
        [data-testid="stHeaderToolbar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Mantém o fundo do cabeçalho transparente para não criar blocos vazios no topo */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Destaca o botão nativo de expandir/recolher (setinhas) para ficar sempre visível e clicável */
        button[data-testid="baseButton-headerNoPadding"],
        button[aria-label="Expand sidebar"],
        button[aria-label="Collapse sidebar"] {
            background-color: #262730 !important;
            color: #FFFFFF !important;
            border: 1px solid #464855 !important;
            border-radius: 4px !important;
            z-index: 999999 !important;
        }

        /* --- REMOVE O BOTÃO 'MANAGE APP' DO CANTO INFERIOR DIREITO --- */
        div[data-testid="stManageAppButton"], 
        div[class*="stManageAppButton"],
        button[id*="manage-app"],
        iframe[title="manage-app"] {
            display: none !important;
            visibility: hidden !important;
        }

        #MainMenu, footer { visibility: hidden !important; }
        .map-container { margin-left: 20px !important; margin-right: 20px !important; }

        .lista-chamados-container {
            max-height: 400px;
            overflow-y: auto;
            background-color: #262730;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #464855;
        }

        /* --- SELETORES PARA OS BOTÕES NATIVOS --- */
        div[data-testid="stButton"] button,
        div[data-testid="stSidebar"] button,
        div[data-testid="stHorizontalBlock"] button,
        .lista-chamados-container button {
            min-height: 55px !important;
            height: 55px !important;
            line-height: 55px !important;
            font-size: 14px !important;
            font-weight: bold !important;
            display: inline-flex !important;
            align-items: center !important;
            border-radius: 8px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 10px 10px !important;
        }

        /* Botões específicos da lista de chamados */
        .lista-chamados-container button {
            justify-content: flex-start !important;
            text-align: left !important;
            font-family: monospace !important;
            background-color: #1E1E24 !important;
            border: 1px solid #3e404f !important;
            color: #E0E0E0 !important;
            margin-bottom: 8px !important;
        }

        .lista-chamados-container button:hover {
            border-color: #007BFF !important;
            background-color: #2d2f3a !important;
            color: #FFFFFF !important;
        }

        /* Alinhamento do bloco horizontal do botão calcular rota */
        div[data-testid="stHorizontalBlock"] div[data-testid="element-container"] {
            padding-top: 10px !important;
        }

        div[data-testid="stHorizontalBlock"] button {
            background-color: #007BFF !important;
            color: white !important;
            border: none !important;
            margin-top: 14px !important;
            justify-content: center !important;
            box-shadow: 0px 4px 12px rgba(0, 123, 255, 0.3) !important;
        }

        div[data-testid="stHorizontalBlock"] button:hover {
            background-color: #0056b3 !important;
            box-shadow: 0px 6px 16px rgba(0, 123, 255, 0.5) !important;
        }

        /* --- PREPARA O CONTAINER INTERNO DA SIDEBAR --- */
        div[data-testid="stSidebarUserContent"], 
        .st-emotion-cache-1r1cntt, 
        .eelgd2m1 {
            position: relative !important;
            min-height: calc(100vh - 30px) !important;
            display: flex !important;
            flex-direction: column !important;
        }

        /* --- INJETA A TAG DE VERSÃO APENAS QUANDO A SIDEBAR ESTIVER EXPANDIDA --- */
        section[data-testid="stSidebar"][aria-expanded="true"] div[data-testid="stSidebarUserContent"]::after,
        section[data-testid="stSidebar"][aria-expanded="true"] .st-emotion-cache-1r1cntt::after, 
        section[data-testid="stSidebar"][aria-expanded="true"] .eelgd2m1::after {
            content: "v0.2.1" !important;
            position: absolute !important;
            bottom: 15px !important;
            right: 15px !important;
            z-index: 999999 !important;
            color: #888c99 !important;
            font-family: monospace !important;
            font-size: 11px !important;
            font-weight: bold !important;
            background-color: #1E1E24 !important;
            padding: 4px 10px !important;
            border-radius: 5px !important;
            border: 1px solid #3e404f !important;
            pointer-events: none !important;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.5) !important;
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
    st.session_state.map_center = [-14.2350, -51.9253]
if 'map_zoom' not in st.session_state:
    st.session_state.map_zoom = 4
if 'map_bounds' not in st.session_state:
    st.session_state.map_bounds = None

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
    st.title("📍 My Maps BR")
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
            col_cliente = mapear_coluna_flexivel(df_aba.columns.tolist(),
                                                 ["LocalAtendimento", "Local Atendimento", "Cliente", "NomeCliente"])
            col_sla = mapear_coluna_flexivel(df_aba.columns.tolist(),
                                             ["limiteAtendimento", "limite", "dataFimGarantia", "SLA"])

            if col_os and col_cidade and col_uf and col_rua:
                colunas_alvo = [col_os, col_cidade, col_uf, col_rua]
                if col_cliente:
                    colunas_alvo.append(col_cliente)
                if col_sla:
                    colunas_alvo.append(col_sla)

                df_limpo = df_aba[colunas_alvo].dropna(subset=[col_os, col_rua])

                dicionario_renomear = {
                    col_os: 'CodOS',
                    col_cidade: 'Cidade',
                    col_uf: 'SiglaUF',
                    col_rua: 'Endereco'
                }
                if col_cliente:
                    dicionario_renomear[col_cliente] = 'Cliente'
                if col_sla:
                    dicionario_renomear[col_sla] = 'SLA_Original'

                df_limpo = df_limpo.rename(columns=dicionario_renomear)

                if 'Cliente' not in df_limpo.columns:
                    df_limpo['Cliente'] = 'Não Identificado'

                hoje = pd.Timestamp.now().normalize()

                if 'SLA_Original' in df_limpo.columns:
                    df_limpo['SLA_Data'] = pd.to_datetime(df_limpo['SLA_Original'], errors='coerce')
                    df_limpo['SLA'] = df_limpo['SLA_Data'].dt.strftime('%d/%m/%Y').fillna('Não Informado')
                else:
                    df_limpo['SLA_Data'] = pd.NaT
                    df_limpo['SLA'] = 'Não Informado'


                def definir_peso_prioridade(data_limite):
                    if pd.isna(data_limite):
                        return 0
                    dias_restantes = (data_limite.normalize() - hoje).days
                    if dias_restantes <= 2:
                        return 3
                    elif dias_restantes <= 4:
                        return 2
                    return 1


                df_limpo['Peso_Prioridade'] = df_limpo['SLA_Data'].apply(definir_peso_prioridade)

                df_limpo['CodOS'] = df_limpo['CodOS'].astype(str).str.split('.').str[0].str.strip()
                df_limpo = df_limpo.drop_duplicates(subset=['CodOS'], keep='first')

                st.session_state.df_final = df_limpo
                st.session_state.ultimo_arquivo = arquivo.name
                st.session_state.chamado_selecionado = None

                st.session_state.map_center = [-14.2350, -51.9253]
                st.session_state.map_zoom = 4
                st.session_state.map_bounds = None

                st.session_state.expander_aberto = False
                st.session_state.coords_sessao = {}

                if 'dados_rota_ativa' in st.session_state:
                    del st.session_state.dados_rota_ativa

                st.session_state.mapa_pronto = "solicitar_geracao"
                st.rerun()
            else:
                st.error("❌ Não foi possível encontrar todas as colunas (OS, Cidade, UF, Endereco) nesta aba.")

# --- PROCESSAMENTO DO MAPA AUTOMÁTICO ---
if st.session_state.df_final is not None:
    df = st.session_state.df_final
    dados_mapa = df.dropna(subset=['Endereco', 'Cidade', 'SiglaUF'])

    grupo_pontos = dados_mapa.groupby(['Endereco', 'Cidade', 'SiglaUF']).agg(
        qtd=('CodOS', 'size'),
        clientes=('Cliente', lambda x: " / ".join(x.astype(str).unique())),
        slas=('SLA', lambda x: " / ".join(x.astype(str).unique())),
        max_peso=('Peso_Prioridade', 'max')
    ).reset_index()

    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Photon(ssl_context=ctx, user_agent="mymaps_br_fast")

    pontos_para_buscar = []
    EXCECOES_CIDADES = {"ZORTEA": [-27.4514, -51.5542]}
    mapeamento_cores = {3: '#FF4B4B', 2: '#FFAA00', 1: '#2E7D32', 0: '#007BFF'}

    for row in grupo_pontos.itertuples(index=False):
        rua_limpa = str(row.Endereco).strip()
        cid_limpa = str(row.Cidade).strip()
        uf_limpa = str(row.SiglaUF).strip()
        endereco_completo_busca = f"{rua_limpa}, {cid_limpa} - {uf_limpa}, Brasil"
        chave_busca = endereco_completo_busca.upper().strip()

        cid_upper = cid_limpa.upper().strip()
        if cid_upper in EXCECOES_CIDADES and uf_limpa.upper().strip() == "SC":
            st.session_state.coords_sessao[chave_busca] = EXCECOES_CIDADES[cid_upper]

        if chave_busca not in st.session_state.coords_sessao:
            cor_marcador = mapeamento_cores.get(row.max_peso, '#FF4B4B')
            linha_sla = f"<b>⏱️ SLA:</b> {str(row.slas).strip()}<br>" if row.max_peso != 0 else ""
            pontos_para_buscar.append((row, endereco_completo_busca, chave_busca, cor_marcador, linha_sla))

    if pontos_para_buscar:
        prog = st.sidebar.progress(0)
        status = st.sidebar.empty()

        for idx, (row, endereco_completo_busca, chave_busca, cor_marcador, linha_sla) in enumerate(pontos_para_buscar):
            rua = str(row.Endereco).strip()
            cid = str(row.Cidade).strip()
            uf_val = str(row.SiglaUF).strip()

            status.text(f"🌐 Buscando locais: {cid}-{uf_val} ({idx + 1}/{len(pontos_para_buscar)})...")
            pos = None
            try:
                loc = geolocator.geocode(endereco_completo_busca, timeout=3)
                if loc:
                    pos = [loc.latitude, loc.longitude]
                    st.session_state.coords_sessao[chave_busca] = pos
                else:
                    loc_fallback = geolocator.geocode(f"{rua.split(',')[0]}, {cid} - {uf_val}, Brasil", timeout=2)
                    if loc_fallback:
                        pos = [loc_fallback.latitude, loc_fallback.longitude]
                        st.session_state.coords_sessao[chave_busca] = pos
            except:
                pos = None

            prog.progress((idx + 1) / len(pontos_para_buscar))

        status.empty()
        prog.empty()

    if st.session_state.coords_sessao:
        coordenadas_validas = list(st.session_state.coords_sessao.values())
        lats = [c[0] for c in coordenadas_validas]
        lngs = [c[1] for c in coordenadas_validas]
        st.session_state.map_bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]

        if st.session_state.map_center == [-14.2350, -51.9253] and st.session_state.map_zoom == 4:
            st.session_state.map_center = [sum(lats) / len(lats), sum(lngs) / len(lngs)]
            max_delta = max(max(lats) - min(lats), max(lngs) - min(lngs))

            if max_delta == 0:
                st.session_state.map_zoom = 16
            elif max_delta < 0.05:
                st.session_state.map_zoom = 14
            elif max_delta < 0.4:
                st.session_state.map_zoom = 11
            elif max_delta < 1.2:
                st.session_state.map_zoom = 9
            elif max_delta < 4.5:
                st.session_state.map_zoom = 8
            elif max_delta < 10.0:
                st.session_state.map_zoom = 6
            else:
                st.session_state.map_zoom = 5

    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

    for row in grupo_pontos.itertuples(index=False):
        rua_limpa = str(row.Endereco).strip()
        cid_limpa = str(row.Cidade).strip()
        uf_limpa = str(row.SiglaUF).strip()
        cliente_limpo = str(row.clientes).strip()
        sla_limpo = str(row.slas).strip()

        cor_marcador = mapeamento_cores.get(row.max_peso, '#FF4B4B')
        linha_sla = f"<b>⏱️ SLA:</b> {sla_limpo}<br>" if row.max_peso != 0 else ""
        endereco_completo_busca = f"{rua_limpa}, {cid_limpa} - {uf_limpa}, Brasil"
        chave_busca = endereco_completo_busca.upper().strip()

        if chave_busca in st.session_state.coords_sessao:
            pos = st.session_state.coords_sessao[chave_busca]
            qtd_chamados = int(row.qtd)
            raio_marcador = min(9 + (qtd_chamados * 0.2), 28)
            diametro = int(raio_marcador * 2)
            tamanho_fonte = max(8, min(12, int(raio_marcador * 0.65)))

            texto_exibicao = f"<b>🏢 {cliente_limpo}</b><br>{linha_sla}<b>{cid_limpa} - {uf_limpa}</b><br><small>{rua_limpa}</small><br>Chamados no local: {qtd_chamados}"
            html_icone = f"""<div style="background-color: {cor_marcador}; color: white; border: 1px solid #1E1E1E; border-radius: 50%; width: {diametro}px; height: {diametro}px; display: flex; align-items: center; justify-content: center; font-size: {tamanho_fonte}px; font-weight: bold; box-shadow: 0px 0px 8px {cor_marcador};">{qtd_chamados}</div>"""

            folium.Marker(location=pos, icon=folium.DivIcon(html=html_icone, icon_size=(diametro, diametro),
                                                            icon_anchor=(raio_marcador, raio_marcador)),
                          tooltip=texto_exibicao, popup=texto_exibicao).add_to(m)

    st.session_state.mapa_pronto = m

# --- RENDERIZAÇÃO DA SIDEBAR CONDICIONAL ---
if st.session_state.df_final is not None and CONSEGUI_VER_LISTA:
    with st.sidebar:
        df = st.session_state.df_final
        df_botoes = df.copy()
        df_botoes['OS_Num'] = pd.to_numeric(df_botoes['CodOS'], errors='coerce')
        df_botoes = df_botoes.sort_values(by=['SiglaUF', 'Cidade', 'OS_Num', 'CodOS'])

        st.markdown("---")
        with st.expander(f"📋 Lista de Chamados ({len(df_botoes)})", expanded=st.session_state.expander_aberto):
            busca = st.text_input("🔍 Pesquisar por OS, Cidade ou UF:", placeholder="Ex: PR...")

            if busca:
                st.session_state.expander_aberto = True
                busca_normalizada = str(busca).strip().lower()
                df_botoes = df_botoes[
                    df_botoes['CodOS'].astype(str).str.lower().str.contains(busca_normalizada) |
                    df_botoes['Cidade'].astype(str).str.lower().str.contains(busca_normalizada) |
                    df_botoes['SiglaUF'].astype(str).str.lower().str.contains(busca_normalizada)
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
                    label_botao = f"{prefixo} [{cid}-{uf_val}] OS: {cham}"

                    if st.button(label_botao, key=f"btn_os_{cham}_{idx}"):
                        st.session_state.chamado_selecionado = cham
                        st.session_state.expander_aberto = True

                        busca_endereco = f"{rua_completa.strip()}, {cid.strip()} - {uf_val.strip()}, Brasil".upper().strip()
                        if busca_endereco not in st.session_state.coords_sessao:
                            busca_endereco = " ".join(busca_endereco.split())

                        if busca_endereco in st.session_state.coords_sessao:
                            st.session_state.map_center = st.session_state.coords_sessao[busca_endereco]
                            st.session_state.map_zoom = 17
                            st.session_state.map_bounds = None
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA PRINCIPAL COM CONTROLE DE ABAS ---
if st.session_state.mapa_pronto:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)

    lista_abas_nome = ["🗺️ Visão Geral"]
    if CONSEGUI_VER_ROTAS:
        lista_abas_nome.append("🚗 Traçar Rotas")

    abas_renderizadas = st.tabs(lista_abas_nome)

    with abas_renderizadas[0]:
        saída_mapa_geral = st_folium(
            st.session_state.mapa_pronto,
            width=1800,
            height=850,
            use_container_width=True,
            returned_objects=["last_object_clicked"],
            center=st.session_state.map_center,
            zoom=st.session_state.map_zoom,
            key=f"mapa_geral_lat_{st.session_state.map_center[0]}_lng_{st.session_state.map_center[1]}_zoom_{st.session_state.map_zoom}_bnd_{len(st.session_state.coords_sessao)}"
        )

        if saída_mapa_geral and saída_mapa_geral.get("last_object_clicked"):
            lat_clicada = saída_mapa_geral["last_object_clicked"]["lat"]
            lng_clicada = saída_mapa_geral["last_object_clicked"]["lng"]
            nova_posicao = [lat_clicada, lng_clicada]
            if nova_posicao != st.session_state.map_center or st.session_state.map_zoom != 17:
                st.session_state.map_center = nova_posicao
                st.session_state.map_zoom = 17
                st.session_state.map_bounds = None
                st.rerun()

    if CONSEGUI_VER_ROTAS:
        with abas_renderizadas[1]:
            df_rotas = st.session_state.df_final

            # Formata os labels de cada chamado para o menu multiselect conforme imagem
            df_rotas['Label_Selecao'] = "OS: " + df_rotas['CodOS'] + " | " + df_rotas['Cliente'] + " (" + df_rotas[
                'Cidade'] + "-" + df_rotas['SiglaUF'] + ")"
            lista_opcoes_chamados = sorted(df_rotas['Label_Selecao'].tolist())

            # RESTAURAÇÃO EXATA DO LAYOUT SOLICITADO (IMAGE_7DF2F1.PNG)
            col1, col2 = st.columns([2.5, 2.5])
            with col1:
                endereco_partida_livre = st.text_input(
                    "📍 Endereço de Partida Livre (Ex: Rua, Cidade - Estado)",
                    placeholder="Digite a base, hotel ou local inicial...",
                    key="partida_livre_input"
                )
            with col2:
                chamados_escolhidos_labels = st.multiselect(
                    "📌 Selecione os chamados para incluir nesta rota:",
                    options=lista_opcoes_chamados,
                    key="chamados_manuais_rota"
                )

            calcular = st.button("🚀 Gerar Itinerário por Prioridade", use_container_width=True)

            m_rota = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
            for child in st.session_state.mapa_pronto._children.values():
                if isinstance(child, folium.Marker):
                    child.add_to(m_rota)

            # Processa e calcula as coordenadas da rota ordenada por prioridade
            if calcular:
                if not endereco_partida_livre:
                    st.error("❌ Por favor, digite um endereço válido no ponto de partida.")
                elif not chamados_escolhidos_labels:
                    st.error("❌ Selecione ao menos 1 chamado para traçar o trajeto.")
                else:
                    ctx = ssl.create_default_context(cafile=certifi.where())
                    geolocator_livre = Photon(ssl_context=ctx, user_agent="mymaps_br_free_start")

                    pos_partida = None
                    try:
                        loc_partida = geolocator_livre.geocode(f"{endereco_partida_livre}, Brasil", timeout=4)
                        if loc_partida:
                            pos_partida = [loc_partida.latitude, loc_partida.longitude]
                        else:
                            loc_fallback = geolocator_livre.geocode(endereco_partida_livre, timeout=3)
                            if loc_fallback:
                                pos_partida = [loc_fallback.latitude, loc_fallback.longitude]
                    except:
                        pos_partida = None

                    if pos_partida:
                        # Filtra os chamados que o usuário escolheu no multiselect
                        df_selecionados = df_rotas[df_rotas['Label_Selecao'].isin(chamados_escolhidos_labels)].copy()

                        # Ordena de forma automática por urgência (Peso_Prioridade descendo, SLA subindo)
                        df_ordenado_prioridade = df_selecionados.sort_values(
                            by=['Peso_Prioridade', 'SLA_Data'],
                            ascending=[False, True]
                        )

                        st.session_state.dados_rota_ativa = {
                            'ponto_partida': pos_partida,
                            'origem_nome': endereco_partida_livre,
                            'chamados': df_ordenado_prioridade.to_dict('records')
                        }
                        st.rerun()
                    else:
                        st.error(
                            "❌ Não conseguimos localizar as coordenadas do endereço de partida. Tente incluir a Cidade e o Estado.")

            # Renderização persistente com suporte avançado a 3 rotas alternativas
            if 'dados_rota_ativa' in st.session_state:
                dados = st.session_state.dados_rota_ativa
                ponto_partida = dados['ponto_partida']

                st.write("### 🧭 Itinerário Otimizado Ativo:")
                st.markdown(f"**🛫 Ponto de Partida Livre:** {dados['origem_nome']}")

                coords_rota = [f"{ponto_partida[1]},{ponto_partida[0]}"]
                dados_para_bounds = [ponto_partida]

                folium.Marker(
                    location=ponto_partida,
                    icon=folium.Icon(color='purple', icon='play', prefix='fa'),
                    tooltip="🛫 Ponto Inicial Customizado",
                    popup=f"<b>Origem da Rota:</b><br>{dados['origem_nome']}"
                ).add_to(m_rota)

                for idx, chamado in enumerate(dados['chamados']):
                    key_chamado = f"{str(chamado['Endereco']).strip()}, {str(chamado['Cidade']).strip()} - {str(chamado['SiglaUF']).strip()}, Brasil".upper().strip()

                    if key_chamado in st.session_state.coords_sessao:
                        pos_chamado = st.session_state.coords_sessao[key_chamado]
                        coords_rota.append(f"{pos_chamado[1]},{pos_chamado[0]}")
                        dados_para_bounds.append(pos_chamado)

                        selo = "🔴 CRÍTICO" if chamado['Peso_Prioridade'] == 3 else (
                            "🟡 ALERTA" if chamado['Peso_Prioridade'] == 2 else "🟢 NORMAL")
                        data_sla = chamado['SLA'] if chamado['Peso_Prioridade'] != 0 else "Sem SLA"

                        st.markdown(
                            f"**📌 {idx + 1}ª Parada:** OS: `{chamado['CodOS']}` | {chamado['Cliente']} — *{chamado['Cidade']}* | **[{selo} — SLA: {data_sla}]**")

                # Conecta as paradas gerando os trajetos alternativos estáveis do OSRM
                if len(coords_rota) > 1:
                    try:
                        url_osrm = f"http://router.project-osrm.org/route/v1/driving/{';'.join(coords_rota)}?overview=full&geometries=geojson&alternatives=true"
                        res = requests.get(url_osrm).json()

                        if res.get('routes'):
                            rotas_retornadas = res['routes']
                            cores_linhas = ['#007BFF', '#9400D3', '#FF8C00']
                            labels_linhas = ['🚀 Rota Principal (Mais Rápida)', '🔄 Caminho Alternativo 1',
                                             '🔄 Caminho Alternativo 2']

                            st.markdown("<br><b>📊 Comparativo de Trajetos (Disponíveis pelo servidor):</b>",
                                        unsafe_allow_html=True)
                            cols_metricas = st.columns(min(3, len(rotas_retornadas)))

                            for idx_r, rota in enumerate(rotas_retornadas[:3]):
                                dist_km = rota['distance'] / 1000.0
                                dur_min = rota['duration'] / 60.0

                                if dur_min >= 60:
                                    texto_tempo = f"{int(dur_min // 60)}h {int(dur_min % 60)}min"
                                else:
                                    texto_tempo = f"{int(dur_min)}min"

                                with cols_metricas[idx_r]:
                                    st.markdown(
                                        f"""
                                        <div style="background-color: #262730; padding: 12px; border-radius: 6px; border: 1px solid #464855; border-left: 5px solid {cores_linhas[idx_r]};">
                                            <span style="color: {cores_linhas[idx_r]}; font-weight: bold;">{labels_linhas[idx_r]}</span><br>
                                            📏 <b>{dist_km:.2f} km</b><br>
                                            ⏱️ <b>{texto_tempo}</b>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                geometria_rota = rota['geometry']['coordinates']
                                lista_coordenadas_folium = [[point[1], point[0]] for point in geometria_rota]

                                espessura = 6 if idx_r == 0 else 4
                                opacidade = 0.85 if idx_r == 0 else 0.55

                                folium.PolyLine(
                                    lista_coordenadas_folium,
                                    color=cores_linhas[idx_r],
                                    weight=espessura,
                                    opacity=opacidade,
                                    tooltip=f"{labels_linhas[idx_r]} ({dist_km:.1f} km)"
                                ).add_to(m_rota)

                    except Exception as e:
                        st.error(f"Erro ao calcular as alternativas OSRM: {e}")

                lats_r = [c[0] for c in dados_para_bounds]
                lngs_r = [c[1] for c in dados_para_bounds]
                m_rota.fit_bounds([[min(lats_r), min(lngs_r)], [max(lats_r), max(lngs_r)]], padding=(40, 40))

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Limpar Itinerário Escolhido", use_container_width=True):
                    del st.session_state.dados_rota_ativa
                    st.rerun()

            saída_mapa_rotas = st_folium(
                m_rota,
                width=1800,
                height=700,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=f"mapa_rotas_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}_active_{'dados_rota_ativa' in st.session_state}"
            )

            if saída_mapa_rotas and saída_mapa_rotas.get("last_object_clicked"):
                lat_clicada = saída_mapa_rotas["last_object_clicked"]["lat"]
                lng_clicada = saída_mapa_rotas["last_object_clicked"]["lng"]
                if [lat_clicada, lng_clicada] != st.session_state.map_center or st.session_state.map_zoom != 17:
                    st.session_state.map_center = [lat_clicada, lng_clicada]
                    st.session_state.map_zoom = 17
                    st.session_state.map_bounds = None
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.container().markdown("<br><br><center><h3>⬅️ Insira a planilha para renderizar os endereços</h3></center>",
                            unsafe_allow_html=True)