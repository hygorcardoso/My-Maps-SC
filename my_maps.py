import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Photon
import ssl
import certifi

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

# 2. CSS GLOBAL
st.markdown(
    """
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }

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
            font-size: 15px !important;
            font-weight: bold !important;
            display: inline-flex !important;
            align-items: center !important;
            border-radius: 8px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 10px 15px !important;
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

        /* --- AJUSTE DA SIDEBAR PARA PERMITIR ANCORAGEM NO RODAPÉ --- */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            position: relative !important;
            min-height: calc(100vh - 20px) !important;
            display: flex !important;
            flex-direction: column !important;
        }

        /* --- ESTILO DA VERSÃO NO CANTO INFERIOR DIREITO DA SIDEBAR --- */
        .version-tag-sidebar {
            position: absolute !important;
            bottom: 10px !important;
            right: auto !important;
            left: auto !important;
            top: auto !important;
            z-index: 1000 !important;
            color: #888c99 !important;
            font-family: monospace !important;
            font-size: 12px !important;
            font-weight: bold !important;
            background-color: rgba(38, 39, 48, 0.95) !important;
            padding: 4px 10px !important;
            border-radius: 5px !important;
            border: 1px solid #464855 !important;
            pointer-events: none !important;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.5) !important;
        }

        /* 🔒 Sidebar sempre visível */
        section[data-testid="stSidebar"] {
            transform: none !important;
            width: 300px !important;
            min-width: 300px !important;
        }

        /* 🔒 Impede qualquer tentativa de esconder */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: none !important;
            width: 300px !important;
        }

        /* 🔒 Remove botão nativo de vez */
        button[data-testid="collapsedControl"],
        button[kind="header"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializa estados globais
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
if 'dados_agrupados_marcador' not in st.session_state:
    st.session_state.dados_agrupados_marcador = []


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
    st.markdown('<div class="version-tag-sidebar">v0.3.3</div>', unsafe_allow_html=True)

    st.title("📍 My Maps BR")
    st.caption("Modo de Geocodificação Nacional (Tempo Real)")
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

        # --- CONTAINER DE FILTROS DINÂMICOS ---
        st.markdown("---")
        with st.expander("⏳ Filtros", expanded=False):
            if st.session_state.df_final is not None:
                # Dropdown 1: Intervenção
                opcoes_intervencao = ["Todos"] + sorted(
                    st.session_state.df_final['Intervencao'].dropna().astype(str).unique().tolist())
                intervencao_selecionada = st.selectbox("Filtrar por Intervenção:", opcoes_intervencao,
                                                       key="filtro_intervencao_dropdown")

                # Dropdown 2: Cliente
                opcoes_cliente = ["Todos"] + sorted(
                    st.session_state.df_final['Cliente'].dropna().astype(str).unique().tolist())
                cliente_selecionado = st.selectbox("Filtrar por Cliente:", opcoes_cliente,
                                                   key="filtro_cliente_dropdown")

                # Dropdown 3: Região
                opcoes_regiao = ["Todos"] + sorted(
                    st.session_state.df_final['Regiao'].dropna().astype(str).unique().tolist())
                regiao_selecionada = st.selectbox("Filtrar por Região:", opcoes_regiao, key="filtro_regiao_dropdown")
            else:
                st.selectbox("Filtrar por Intervenção:", ["Nenhuma planilha carregada"], disabled=True,
                             key="filtro_intervencao_disabled")
                st.selectbox("Filtrar por Cliente:", ["Nenhuma planilha carregada"], disabled=True,
                             key="filtro_cliente_disabled")
                st.selectbox("Filtrar por Região:", ["Nenhuma planilha carregada"], disabled=True,
                             key="filtro_regiao_disabled")
                st.caption("💡 Carregue uma planilha e clique em gerar mapa para liberar os filtros.")

        if is_novo_arquivo or st.session_state.df_final is None or st.sidebar.button("⚡ Gerar / Atualizar Mapa",
                                                                                     key="btn_gerar"):
            df_aba = pd.read_excel(arquivo, sheet_name=aba_selecionada)

            col_os = mapear_coluna_flexivel(df_aba.columns.tolist(), ["CodOS", "Chamado", "ID", "Ticket"])
            col_cidade = mapear_coluna_flexivel(df_aba.columns.tolist(), ["Cidade", "Municipio", "Cid"])
            col_uf = mapear_coluna_flexivel(df_aba.columns.tolist(), ["SiglaUF", "UF", "Estado"])
            col_rua = mapear_coluna_flexivel(df_aba.columns.tolist(), ["Endereco", "Endereço", "Logradouro", "Rua"])
            col_intervencao = mapear_coluna_flexivel(df_aba.columns.tolist(), ["Intervencao", "Intervenção", "Tipo"])
            col_cliente = mapear_coluna_flexivel(df_aba.columns.tolist(),
                                                 ["Cliente", "NomeCliente", "RazaoSocial", "Aba Cliente", "Empresa"])
            col_regiao = mapear_coluna_flexivel(df_aba.columns.tolist(),
                                                ["Regiao", "Região", "Distrito", "Area", "Zona"])

            if col_os and col_cidade and col_uf and col_rua:
                colunas_para_copiar = [col_os, col_cidade, col_uf, col_rua]
                if col_intervencao:
                    colunas_para_copiar.append(col_intervencao)
                if col_cliente:
                    colunas_para_copiar.append(col_cliente)
                if col_regiao:
                    colunas_para_copiar.append(col_regiao)

                df_limpo = df_aba[colunas_para_copiar].dropna(subset=[col_os, col_rua])

                nomes_colunas = {
                    col_os: 'CodOS',
                    col_cidade: 'Cidade',
                    col_uf: 'SiglaUF',
                    col_rua: 'Endereco'
                }
                if col_intervencao:
                    nomes_colunas[col_intervencao] = 'Intervencao'
                if col_cliente:
                    nomes_colunas[col_cliente] = 'Cliente'
                if col_regiao:
                    nomes_colunas[col_regiao] = 'Regiao'

                df_limpo = df_limpo.rename(columns=nomes_colunas)

                if 'Intervencao' not in df_limpo.columns:
                    df_limpo['Intervencao'] = "Não Informado"
                if 'Cliente' not in df_limpo.columns:
                    df_limpo['Cliente'] = "Não Informado"
                if 'Regiao' not in df_limpo.columns:
                    df_limpo['Regiao'] = "Não Informado"

                df_limpo['CodOS'] = df_limpo['CodOS'].astype(str).str.split('.').str[0].str.strip()
                df_limpo = df_limpo.drop_duplicates(subset=['CodOS'], keep='first')

                st.session_state.df_final = df_limpo
                st.session_state.ultimo_arquivo = arquivo.name
                st.session_state.chamado_selecionado = None

                st.session_state.expander_aberto = False
                st.session_state.coords_sessao = {}
                st.session_state.dados_agrupados_marcador = []

                st.session_state.map_center = [-14.2350, -51.9253]
                st.session_state.map_zoom = 4
                st.session_state.map_bounds = None
                st.rerun()
            else:
                st.error(
                    "❌ Não foi possível encontrar todas as colunas obrigatórias (OS, Cidade, UF, Endereço) nesta aba.")

# --- PROCESSAMENTO E GEOLOCALIZAÇÃO ---
if st.session_state.df_final is not None and not st.session_state.dados_agrupados_marcador:
    df = st.session_state.df_final
    dados_mapa = df.dropna(subset=['Endereco', 'Cidade', 'SiglaUF'])

    grupo_pontos = dados_mapa.groupby(
        ['Endereco', 'Cidade', 'SiglaUF', 'Intervencao', 'Cliente', 'Regiao']).size().reset_index(name='qtd')

    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Photon(ssl_context=ctx, user_agent="mymaps_br_fast")

    pontos_para_buscar = []

    # --- DICIONÁRIO DE COORDENADAS CORRIGIDAS (EXCEÇÕES NACIONAIS) ---
    EXCECOES_CIDADES = {
        "ZORTEA": [-27.4514, -51.5542],
        "CHAPECO": [-27.1004, -52.6152],
        "CHAPECÓ": [-27.1004, -52.6152],
        "NAVEGANTES": [-26.8914, -48.6548],
        "SAO JOSE": [-27.6146, -48.6353],  # Força São José - SC na Região Metropolitana de Florianópolis (Litoral)
        "SÃO JOSÉ": [-27.6146, -48.6353]
    }

    for row in grupo_pontos.itertuples(index=False):
        rua_limpa = str(row.Endereco).strip()
        cid_limpa = str(row.Cidade).strip()
        uf_limpa = str(row.SiglaUF).strip()
        interv_limpa = str(row.Intervencao).strip()
        cli_limpa = str(row.Cliente).strip()
        reg_limpa = str(row.Regiao).strip()

        endereco_completo_busca = f"{rua_limpa}, {cid_limpa} - {uf_limpa}, Brasil"
        chave_busca = endereco_completo_busca.upper().strip()

        cid_upper = cid_limpa.upper().strip()

        # Intercepta se a cidade estiver cadastrada na tabela de amarras geográficas do estado (SC)
        if cid_upper in EXCECOES_CIDADES and uf_limpa.upper().strip() == "SC":
            st.session_state.coords_sessao[chave_busca] = EXCECOES_CIDADES[cid_upper]

        if chave_busca in st.session_state.coords_sessao:
            pos = st.session_state.coords_sessao[chave_busca]
            st.session_state.dados_agrupados_marcador.append({
                "pos": pos, "qtd": int(row.qtd), "cid": cid_limpa, "uf": uf_limpa, "rua": rua_limpa,
                "interv": interv_limpa, "cli": cli_limpa, "reg": reg_limpa
            })
        else:
            pontos_para_buscar.append((row, endereco_completo_busca, chave_busca, interv_limpa, cli_limpa, reg_limpa))

    if pontos_para_buscar:
        prog = st.sidebar.progress(0)
        status = st.sidebar.empty()

        for idx, (row, endereco_completo_busca, chave_busca, interv_limpa, cli_limpa, reg_limpa) in enumerate(
                pontos_para_buscar):
            rua = str(row.Endereco).strip()
            cid = str(row.Cidade).strip()
            uf_val = str(row.SiglaUF).strip()

            status.text(f"🌐 Buscando locais: {cid}-{uf_val} ({idx + 1}/{len(pontos_para_buscar)})...")
            pos = None
            try:
                loc = geolocator.geocode(endereco_completo_busca, timeout=3)
                if loc:
                    pos = [loc.latitude, loc.longitude]
                else:
                    loc_fallback = geolocator.geocode(f"{rua.split(',')[0]}, {cid} - {uf_val}, Brasil", timeout=2)
                    if loc_fallback:
                        pos = [loc_fallback.latitude, loc_fallback.longitude]
            except:
                pos = None

            if pos:
                st.session_state.coords_sessao[chave_busca] = pos
                st.session_state.dados_agrupados_marcador.append({
                    "pos": pos, "qtd": int(row.qtd), "cid": cid, "uf": uf_val, "rua": rua, "interv": interv_limpa,
                    "cli": cli_limpa, "reg": reg_limpa
                })

            prog.progress((idx + 1) / len(pontos_para_buscar))

        status.empty()
        prog.empty()

    if st.session_state.coords_sessao:
        coordenadas_validas = list(st.session_state.coords_sessao.values())
        lats = [c[0] for c in coordenadas_validas]
        lngs = [c[1] for c in coordenadas_validas]

        center_lat = (min(lats) + max(lats)) / 2
        center_lng = (min(lngs) + max(lngs)) / 2
        st.session_state.map_center = [center_lat, center_lng]

        lat_delta = max(lats) - min(lats)
        lng_delta = max(lngs) - min(lngs)
        delta_max = max(lat_delta, lng_delta)
        if delta_max < 0.05:
            zoom_calc = 14
        elif delta_max < 0.2:
            zoom_calc = 12
        elif delta_max < 0.5:
            zoom_calc = 11
        elif delta_max < 1.0:
            zoom_calc = 10
        elif delta_max < 2.0:
            zoom_calc = 9
        elif delta_max < 4.0:
            zoom_calc = 8
        elif delta_max < 8.0:
            zoom_calc = 7
        else:
            zoom_calc = 6
        st.session_state.map_zoom = zoom_calc
        st.rerun()


# --- CONSTRUTOR DINÂMICO DO MAPA ---
def construir_mapa_geral():
    filtro_interv = st.session_state.get("filtro_intervencao_dropdown", "Todos")
    filtro_cliente = st.session_state.get("filtro_cliente_dropdown", "Todos")
    filtro_regiao = st.session_state.get("filtro_regiao_dropdown", "Todos")

    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

    dados_filtrados = []
    for p in st.session_state.dados_agrupados_marcador:
        if filtro_interv != "Todos" and p["interv"] != filtro_interv:
            continue
        if filtro_cliente != "Todos" and p["cli"] != filtro_cliente:
            continue
        if filtro_regiao != "Todos" and p["reg"] != filtro_regiao:
            continue
        dados_filtrados.append(p)

    df_agrupamento_mapa = pd.DataFrame(dados_filtrados)
    if not df_agrupamento_mapa.empty:
        df_agrupamento_mapa['lat'] = df_agrupamento_mapa['pos'].apply(lambda x: x[0])
        df_agrupamento_mapa['lng'] = df_agrupamento_mapa['pos'].apply(lambda x: x[1])

        res_agrupado = df_agrupamento_mapa.groupby(['lat', 'lng', 'cid', 'uf', 'rua'])['qtd'].sum().reset_index()

        for p in res_agrupado.itertuples():
            raio_marcador = min(9 + (p.qtd * 0.2), 28)
            diametro = int(raio_marcador * 2)
            tamanho_fonte = max(8, min(12, int(raio_marcador * 0.65)))
            texto_exibicao = f"<b>{p.cid} - {p.uf}</b><br><small>{p.rua}</small><br>Chamados: {p.qtd}"

            html_icone = f"""<div style="background-color: #FF4B4B; color: white; border: 1px solid #1E1E1E; border-radius: 50%; width: {diametro}px; height: {diametro}px; display: flex; align-items: center; justify-content: center; font-size: {tamanho_fonte}px; font-weight: bold; box-shadow: 0px 0px 8px #FF4B4B;">{p.qtd}</div>"""

            folium.Marker(
                location=[p.lat, p.lng],
                icon=folium.DivIcon(html=html_icone, icon_size=(diametro, diametro),
                                    icon_anchor=(raio_marcador, raio_marcador)),
                tooltip=texto_exibicao,
                popup=texto_exibicao
            ).add_to(m)

    return m


# --- RENDERIZAÇÃO DA SIDEBAR CONDICIONAL ---
if st.session_state.df_final is not None and CONSEGUI_VER_LISTA:
    with st.sidebar:
        df = st.session_state.df_final.copy()

        filtro_interv = st.session_state.get("filtro_intervencao_dropdown", "Todos")
        filtro_cliente = st.session_state.get("filtro_cliente_dropdown", "Todos")
        filtro_regiao = st.session_state.get("filtro_regiao_dropdown", "Todos")

        if filtro_interv != "Todos":
            df = df[df['Intervencao'] == filtro_interv]
        if filtro_cliente != "Todos":
            df = df[df['Cliente'] == filtro_cliente]
        if filtro_regiao != "Todos":
            df = df[df['Regiao'] == filtro_regiao]

        df_botoes = df.copy()
        df_botoes['OS_Num'] = pd.to_numeric(df_botoes['CodOS'], errors='coerce')
        df_botoes = df_botoes.sort_values(by=['SiglaUF', 'Cidade', 'OS_Num', 'CodOS'])

        st.markdown("---")
        with st.expander(f"📋 Lista de Chamados ({len(df_botoes)})", expanded=st.session_state.expander_aberto):
            busca = st.text_input("🔍 Pesquisar por OS, Cidade ou UF:", placeholder="Ex: PR ou Curitiba...")

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

# --- ÁREA PRINCIPAL COM CONTROLE DE ABAS REMOTO ---
if st.session_state.df_final is not None and st.session_state.dados_agrupados_marcador:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)

    lista_abas_nome = ["🗺️ Visão Geral"]
    if CONSEGUI_VER_ROTAS:
        lista_abas_nome.append("🚗 Traçar Rotas")

    abas_renderizadas = st.tabs(lista_abas_nome)

    with abas_renderizadas[0]:
        mapa_atualizado = construir_mapa_geral()

        saída_mapa_geral = st_folium(
            mapa_atualizado,
            width=1800,
            height=850,
            use_container_width=True,
            returned_objects=["last_object_clicked"],
            center=st.session_state.map_center,
            zoom=st.session_state.map_zoom,
            key=f"mapa_geral_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}"
        )

        if saída_mapa_geral and saída_mapa_geral.get("last_object_clicked"):
            clique = saída_mapa_geral["last_object_clicked"]
            lat_clicada = clique["lat"]
            lng_clicada = clique["lng"]

            distancia_lat = abs(lat_clicada - st.session_state.map_center[0])
            distancia_lng = abs(lng_clicada - st.session_state.map_center[1])

            if (distancia_lat > 0.0001 or distancia_lng > 0.0001) or st.session_state.map_zoom != 17:
                st.session_state.map_center = [lat_clicada, lng_clicada]
                st.session_state.map_zoom = 17
                st.session_state.map_bounds = None

                for chave_busca, pos in st.session_state.coords_sessao.items():
                    if abs(pos[0] - lat_clicada) < 0.001 and abs(pos[1] - lng_clicada) < 0.001:
                        df_filtro = st.session_state.df_final
                        for r in df_filtro.itertuples():
                            busca_end = f"{str(r.Endereco).strip()}, {str(r.Cidade).strip()} - {str(r.SiglaUF).strip()}, Brasil".upper().strip()
                            if busca_end == chave_busca:
                                st.session_state.chamado_selecionado = str(r.CodOS)
                                st.session_state.expander_aberto = True
                                break
                        break
                st.rerun()

    if CONSEGUI_VER_ROTAS:
        with abas_renderizadas[1]:
            filtro_interv = st.session_state.get("filtro_intervencao_dropdown", "Todos")
            filtro_cliente = st.session_state.get("filtro_cliente_dropdown", "Todos")
            filtro_regiao = st.session_state.get("filtro_regiao_dropdown", "Todos")

            df_rotas = st.session_state.df_final.copy()
            if filtro_interv != "Todos":
                df_rotas = df_rotas[df_rotas['Intervencao'] == filtro_interv]
            if filtro_cliente != "Todos":
                df_rotas = df_rotas[df_rotas['Cliente'] == filtro_cliente]
            if filtro_regiao != "Todos":
                df_rotas = df_rotas[df_rotas['Regiao'] == filtro_regiao]

            df_rotas['Cidade_UF'] = df_rotas['Cidade'] + " - " + df_rotas['SiglaUF']
            lista_cidades_br = sorted(df_rotas['Cidade_UF'].unique().tolist())

            if not lista_cidades_br:
                st.warning("⚠️ Nenhuma cidade disponível para rotas com os filtros aplicados.")
            else:
                col1, col2, col3 = st.columns([2, 2, 1.2])
                with col1:
                    origem = st.selectbox("📍 Cidade de Origem", lista_cidades_br, key="origem_rota")
                with col2:
                    def_idx = min(1, len(lista_cidades_br) - 1)
                    destino = st.selectbox("🏁 Cidade de Destino", lista_cidades_br, index=def_idx, key="destino_rota")
                with col3:
                    calcular = st.button("🚀 Calcular Rota", use_container_width=True)

                m_rota = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
                for p in st.session_state.dados_agrupados_marcador:
                    if filtro_interv != "Todos" and p["interv"] != filtro_interv:
                        continue
                    if filtro_cliente != "Todos" and p["cli"] != filtro_cliente:
                        continue
                    if filtro_regiao != "Todos" and p["reg"] != filtro_regiao:
                        continue

                    raio_marcador = min(9 + (p["qtd"] * 0.2), 28)
                    diametro = int(raio_marcador * 2)
                    tamanho_fonte = max(8, min(12, int(raio_marcador * 0.65)))
                    texto_exibicao = f"<b>{p['cid']} - {p['uf']}</b><br><small>{p['rua']}</small><br>Chamados no local: {p['qtd']}"
                    html_icone = f"""<div style="background-color: #FF4B4B; color: white; border: 1px solid #1E1E1E; border-radius: 50%; width: {diametro}px; height: {diametro}px; display: flex; align-items: center; justify-content: center; font-size: {tamanho_fonte}px; font-weight: bold; box-shadow: 0px 0px 8px #FF4B4B;">{p['qtd']}</div>"""
                    folium.Marker(location=p["pos"],
                                  icon=folium.DivIcon(html=html_icone, icon_size=(diametro, diametro),
                                                      icon_anchor=(raio_marcador, raio_marcador)),
                                  tooltip=texto_exibicao, popup=texto_exibicao).add_to(m_rota)

                if calcular:
                    lin_origem = df_rotas[df_rotas['Cidade_UF'] == origem].iloc[0]
                    lin_destino = df_rotas[df_rotas['Cidade_UF'] == destino].iloc[0]

                    key_origem = f"{str(lin_origem['Endereco']).strip()}, {str(lin_origem['Cidade']).strip()} - {str(lin_origem['SiglaUF']).strip()}, Brasil".upper().strip()
                    key_destino = f"{str(lin_destino['Endereco']).strip()}, {str(lin_destino['Cidade']).strip()} - {str(lin_destino['SiglaUF']).strip()}, Brasil".upper().strip()

                    if key_origem in st.session_state.coords_sessao and key_destino in st.session_state.coords_sessao:
                        ponto_A = st.session_state.coords_sessao[key_origem]
                        ponto_B = st.session_state.coords_sessao[key_destino]

                        st.write("### 🔄 Rota Dinâmica Ativada")
                        st.info(
                            "💡 **Como usar:** Passe o mouse sobre a rota para ver o ponto de controle. Clique e arraste qualquer parte da linha azul para mudar o caminho!")

                        m_rota.get_root().header.add_child(folium.Element(
                            '<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" />'))
                        m_rota.get_root().header.add_child(folium.Element(
                            '<script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.js"></script>'))

                        script_rota_arrastavel = f"""
                        <script>
                        (function() {{
                            function inicializarRota() {{
                                var mapInstance = null;
                                if (typeof L !== 'undefined' && L.Map && L.Map._maps) {{
                                    var mapas_ativos = Object.values(L.Map._maps);
                                    if (mapas_ativos.length > 0) {{ mapInstance = mapas_ativos[0]; }}
                                }}
                                if (!mapInstance && typeof L !== 'undefined') {{
                                    var layers = L.Map.prototype._layers;
                                    for (var id in layers) {{
                                        if (layers[id]._container && layers[id]._container.id) {{
                                            mapInstance = layers[id];
                                            break;
                                        }}
                                    }}
                                }}
                                if (mapInstance) {{
                                    L.Routing.control({{
                                        waypoints: [
                                            L.latLng({ponto_A[0]}, {ponto_A[1]}),
                                            L.latLng({ponto_B[0]}, {ponto_B[1]})
                                        ],
                                        routeWhileDragging: true,
                                        showAlternatives: true,
                                        altLineOptions: {{ styles: [[{{color: '#9400D3', opacity: 0.6, weight: 4}}]] }},
                                        lineOptions: {{ styles: [{{color: '#007BFF', opacity: 0.85, weight: 6}}] }},
                                        createMarker: function(i, wp, nWps) {{
                                            var label = i === 0 ? "Início" : (i === nWps - 1 ? "Fim" : "Ponto de Desvio");
                                            return L.marker(wp.latLng, {{ draggable: true }}).bindPopup(label);
                                        }}
                                    }}).addTo(mapInstance);
                                }} else {{
                                    setTimeout(inicializarRota, 300);
                                }}
                            }}
                            setTimeout(inicializarRota, 600);
                        }})();
                        </script>
                        """
                        m_rota.get_root().html.add_child(folium.Element(script_rota_arrastavel))
                        m_rota.fit_bounds([ponto_A, ponto_B])
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

                    dist_lat_r = abs(lat_clicada - st.session_state.map_center[0])
                    dist_lng_r = abs(lng_clicada - st.session_state.map_center[1])

                    if (dist_lat_r > 0.0001 or dist_lng_r > 0.0001) or st.session_state.map_zoom != 17:
                        st.session_state.map_center = [lat_clicada, lng_clicada]
                        st.session_state.map_zoom = 17
                        st.session_state.map_bounds = None
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.container().markdown("<br><br><center><h3>⬅️ Insira a planilha para renderizar os endereços</h3></center>",
                            unsafe_allow_html=True)