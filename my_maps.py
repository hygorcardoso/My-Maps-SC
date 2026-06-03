import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Photon
import ssl
import certifi

# --- CACHE DE GEOCODIFICAÇÕES ---
import os
import json
from pathlib import Path

CACHE_FILE = Path.home() / ".streamlit" / "geocodificacao_cache.json"


def carregar_cache_geocodificacao():
    """Carrega o cache de coordenadas do arquivo JSON."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def salvar_cache_geocodificacao(cache):
    """Salva o cache atualizado no arquivo JSON."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[CACHE WARNING] Não foi possível salvar cache: {e}")


def obter_coordenadas_com_cache(endereco_completo, chave_busca, cliente, cidade, uf):
    """
    Busca coordenadas: primeiro no cache, depois na API.
    Atualiza o cache se encontrado na API.

    Args:
        endereco_completo: endereço formatado para busca (ex: "Rua X, Cidade - UF, Brasil")
        chave_busca: chave em caixa alta (ex: "RUA X, CIDADE - UF, BRASIL")
        cliente: nome do cliente
        cidade: nome da cidade
        uf: sigla do estado

    Returns:
        tuple: (lat, lng) ou (None, None) se não encontrado
    """
    cache = carregar_cache_geocodificacao()

    # Buscar no cache
    if chave_busca in cache:
        entrada = cache[chave_busca]
        return (entrada["lat"], entrada["lng"])

    # Se não estiver no cache, retorna None para buscar na API depois
    return None, None


def _corrigir_coords_se_necessario(cidade, lat, lng):
    """Corrige coordenadas de cidades conhecidas com geocodificação errada.
    Se lat/lng forem None, retorna as coordenadas fixas se existirem, senão (None, None)."""
    import unicodedata
    cidade_norm = unicodedata.normalize('NFKD', str(cidade)).encode('ASCII', 'ignore').decode('ASCII').upper()
    correcoes_norm = {unicodedata.normalize('NFKD', k).encode('ASCII', 'ignore').decode('ASCII').upper(): v
                      for k, v in CORRECOES_COORDENADAS.items()}
    if cidade_norm in correcoes_norm:
        return correcoes_norm[cidade_norm]
    return lat, lng


def adicionar_ao_cache(chave_busca, cliente, cidade, uf, lat, lng):
    """Adiciona uma entrada ao cache de geocodificações."""
    cache = carregar_cache_geocodificacao()
    cache[chave_busca] = {
        "cliente": cliente.upper(),
        "cidade": cidade.upper(),
        "estado": uf.upper(),
        "lat": lat,
        "lng": lng
    }
    salvar_cache_geocodificacao(cache)


# Coordenadas corretas para cidades que o Photon geocodifica errado
CORRECOES_COORDENADAS = {
    "SAO CRISTOVAO DO SUL": (-27.2666, -50.4388),
    "SÃO CRISTÓVÃO DO SUL": (-27.2666, -50.4388),
    "LUZERNA": (-27.1304, -51.4682),
}

# Carrega JSON local com todas as cidades de SC
import unicodedata as _ud, os as _os

_JSON_CIDADES_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "cidades.json")
_CIDADES = {}
try:
    with open(_JSON_CIDADES_PATH, "r", encoding="utf-8") as _f:
        _CIDADES = json.load(_f)
except Exception:
    _CIDADES = {}


def _buscar_cidade_sc(cidade):
    """Retorna (lat, lng) do JSON local se cidade de SC for encontrada, senão (None, None)."""
    nome_norm = _ud.normalize('NFKD', str(cidade)).encode('ASCII', 'ignore').decode('ASCII').upper().strip()
    entrada = _CIDADES.get(nome_norm)
    if entrada:
        return entrada["lat"], entrada["lng"]
    return None, None


def _normalizar(s):
    import unicodedata
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').upper()


def aplicar_correcoes_cache():
    """Garante que cidades com geocodificação errada sejam corrigidas no cache."""
    cache = carregar_cache_geocodificacao()
    alterado = False
    correcoes_norm = {_normalizar(k): v for k, v in CORRECOES_COORDENADAS.items()}
    for chave, entrada in cache.items():
        cidade_norm = _normalizar(entrada.get("cidade", ""))
        if cidade_norm in correcoes_norm:
            lat_corr, lng_corr = correcoes_norm[cidade_norm]
            if abs(entrada.get("lat", 0) - lat_corr) > 0.5:
                entrada["lat"] = lat_corr
                entrada["lng"] = lng_corr
                alterado = True
    if alterado:
        salvar_cache_geocodificacao(cache)


# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="My Maps BR", layout="wide")
aplicar_correcoes_cache()

# DICIONÁRIO GLOBAL DE CORES POR TIPO DE INTERVENÇÃO
CORES_INTERVENCAO = {
    "Alteração de engenharia": "#4B0082",  # Indigo
    "Autorização de deslocamento": "#4682B4",  # SteelBlue
    "Cofre": "#708090",  # SlateGray
    "Corretiva": "#FF4B4B",  # Vermelho
    "Corretiva POS reincidentes": "#B22222",  # FireBrick
    "Desinstalação": "#FF8C00",  # DarkOrange
    "Helpdesk": "#008B8B",  # DarkCyan
    "Inspeção técnica": "#9ACD32",  # YellowGreen
    "Instalação": "#2E8B57",  # SeaGreen
    "Laudo técnico": "#8B008B",  # DarkMagenta
    "Manutenção gerencial": "#5F9EA0",  # CadetBlue
    "Orçamento": "#FFD700",  # Gold
    "Orçamento aprovado": "#32CD32",  # LimeGreen
    "Orçamento pendente da filial detalhar motivo": "#FFA500",  # Orange
    "Orçamento pendente de aprovação do cliente": "#DAA520",  # GoldenRod
    "Orçamento reprovado": "#8B0000",  # DarkRed
    "Preventiva": "#007BFF",  # Azul
    "Preventiva gerencial": "#1E90FF",  # DodgerBlue
    "Reinstalação": "#20B2AA",  # LightSeaGreen
    "Treinamento": "#9370DB",  # MediumPurple
    "Troca de Veloh C": "#8B4513",  # SaddleBrown
    "Não Informado": "#464855"  # Cinza
}


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
        .block-container { padding-top: 1rem !important; padding-left: 0rem !important; padding-right: 0rem 
        !important; padding-bottom: 0rem !important; max-width: 100% !important; }

        /* --- CONTROLE DO CABEÇALHO SUPERIOR --- */
        button[data-testid="stHeaderShareButton"],
        a[data-testid="stHeaderGithubLink"],
        button[data-testid="stHeaderStarButton"] {
            display: none !important;
            visibility: hidden !important;
        }

        ul[data-testid="main-menu-list"] li:not(:nth-child(3)):not(:nth-child(4)) {
            display: none !important;
            visibility: hidden !important;
        }

        .map-container { margin-left: 20px !important; margin-right: 20px !important; }

        .lista-chamados-container {
            max-height: 4000px;
            overflow-y: auto;
            background-color: #262730;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #464855;
        }

        /* --- SELETORES GERAIS PARA BOTÕES DE FLUXO/FORMULÁRIO --- */
        div[data-testid="stButton"] button,
        div[data-testid="stSidebar"] button[disabled="false"],
        div[data-testid="stHorizontalBlock"] button,
        .lista-chamados-container button {
            min-height: 55px !important;
            height: 55px !important;
            line-height: 35px !important;
            font-size: 15px !important;
            font-weight: bold !important;
            display: inline-flex !important;
            align-items: center !important;
            border-radius: 8px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 10px 15px !important;
        }

        /* BOTÕES DA LISTA DE CHAMADOS SE AJUSTAREM AO TEXTO */
        .lista-chamados-container button {
            min-height: 45px !important;
            height: auto !important;
            line-height: 1.4 !important;
            font-size: 13px !important;
            font-weight: bold !important;
            display: block !important;
            text-align: left !important;
            font-family: monospace !important;
            margin-bottom: 8px !important;
            width: 100% !important;
            box-sizing: border-box !important;
            padding: 12px 14px !important;
            white-space: normal !important;
            word-wrap: break-word !important;
        }

        /* Alinhamento do bloco horizontal do botão calcular rota e formulários */
        div[data-testid="stHorizontalBlock"] div[data-testid="element-container"] {
            padding-top: 10px !important;
        }

        div[data-testid="stHorizontalBlock"] button,
        div[data-testid="stForm"] button {
            background-color: #007BFF !important;
            color: white !important;
            border: none !important;
            justify-content: center !important;
            box-shadow: 0px 4px 12px rgba(0, 123, 255, 0.3) !important;
        }

        div[data-testid="stHorizontalBlock"] button:hover,
        div[data-testid="stForm"] button:hover {
            background-color: #0056b3 !important;
            box-shadow: 0px 6px 16px rgba(0, 123, 255, 0.5) !important;
        }

        /* --- ABAS DE NAVEGAÇÃO SUPERIOR --- */
        div[data-testid="stTabs"] {
            background-color: #1E1E24 !important;
            padding: 6px 8px !important;
            border-radius: 8px !important;
            border: 1px solid #3e404f !important;
            margin-bottom: 20px !important;
            margin-left: 20px !important;
            margin-right: 20px !important;
            margin-top: 10px !important;
            overflow: visible !important;
        }

        div[data-testid="stTabs"] div[role="tablist"] {
            border-bottom: none !important;
            gap: 6px !important;
            min-height: 36px !important;
            height: auto !important;
            display: flex !important;
            align-items: center !important;
            flex-wrap: nowrap !important;
            overflow: visible !important;
        }

        div[data-testid="stTabs"] div[role="tablist"] button[data-baseweb="tab"] {
            min-height: 36px !important;
            height: 36px !important;
            width: auto !important;
            min-width: 100px !important;
            background-color: transparent !important;
            border: none !important;
            color: #E0E0E0 !important;
            font-size: 13px !important;
            font-weight: bold !important;
            padding: 0px 20px !important;
            border-radius: 6px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: normal !important;
            margin: 0 !important;
            overflow: visible !important;
            white-space: nowrap !important;
        }

        /* Aba Ativa (Selecionada) */
        div[data-testid="stTabs"] div[role="tablist"] button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #007BFF !important;
            color: #FFFFFF !important;
            box-shadow: 0px 2px 8px rgba(0, 123, 255, 0.3) !important;
        }

        /* Hover nas Abas */
        div[data-testid="stTabs"] div[role="tablist"] button[data-baseweb="tab"]:hover {
            color: #FFFFFF !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }

        div[data-testid="stTabs"] button[data-baseweb="tab"] div,
        div[data-testid="stTabs"] button[data-baseweb="tab"] p,
        div[data-testid="stTabs"] button[data-baseweb="tab"] span {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: normal !important;
            height: auto !important;
            overflow: visible !important;
            white-space: nowrap !important;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-border"],
        div[data-testid="stTabs"] [class*="StyledTabBorder"],
        div[data-testid="stTabs"] [class*="StyledTabHighlight"] {
            display: none !important;
            height: 0px !important;
        }

        /* --- SIDEBAR CONFIGS --- */
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            position: relative !important;
            min-height: calc(100vh - 20px) !important;
            display: flex !important;
            flex-direction: column !important;
        }

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

        div[data-testid="stForm"] {
            border: none !important;
            padding: 0rem !important;
        }

        /* --- ESTILO DA LEGENDA DE CORES --- */
        .legenda-container {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            background-color: #1E1E24;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #3e404f;
            margin-top: 15px;
        }

        .legenda-item {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 500;
            color: #E0E0E0;
            font-family: sans-serif;
        }

        .legenda-cor {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 1px solid #1E1E1E;
            flex-shrink: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicializa estados globais padrão
if 'df_final' not in st.session_state: st.session_state.df_final = None
if 'chamado_selecionado' not in st.session_state: st.session_state.chamado_selecionado = None
if 'map_center' not in st.session_state: st.session_state.map_center = [-14.2350, -51.9253]
if 'map_zoom' not in st.session_state: st.session_state.map_zoom = 4
if 'ultimo_arquivo' not in st.session_state: st.session_state.ultimo_arquivo = None
if 'expander_aberto' not in st.session_state: st.session_state.expander_aberto = False
if 'coords_sessao' not in st.session_state: st.session_state.coords_sessao = {}
if 'dados_agrupados_marcador' not in st.session_state: st.session_state.dados_agrupados_marcador = []

# Retenção do formulário
if 'f_interv' not in st.session_state: st.session_state.f_interv = "Todos"
if 'f_clie' not in st.session_state: st.session_state.f_clie = "Todos"
if 'f_regi' not in st.session_state: st.session_state.f_regi = "Todos"


def mapear_coluna_flexivel(lista_colunas, alvos):
    for col in lista_colunas:
        if str(col).strip().upper() in [t.upper() for t in alvos]:
            return col
    for col in lista_colunas:
        for t in alvos:
            if t.lower() in str(col).strip().lower():
                return col
    return None


# --- FUNÇÃO PARA GERAR O BLOCO HTML DA LEGENDA DINAMICAMENTE COM FILTROS ---
def renderizar_legenda_dinamica_html(df_filtrado):
    if df_filtrado is None or df_filtrado.empty:
        return ""

    intervencoes_ativas = set(df_filtrado["Intervencao"].dropna().astype(str).unique().tolist())

    itens = []
    for nome_tipo, cor_hex in CORES_INTERVENCAO.items():
        if nome_tipo in intervencoes_ativas and nome_tipo != "Não Informado":
            itens.append(
                f'<div style="display:inline-flex;align-items:center;gap:6px;font-size:12px;'
                f'font-weight:500;color:#E0E0E0;font-family:sans-serif;">'
                f'<div style="width:14px;height:14px;border-radius:50%;border:1px solid #1E1E1E;'
                f'flex-shrink:0;background-color:{cor_hex};box-shadow:0px 0px 4px {cor_hex};"></div>'
                f'<span>{nome_tipo}</span>'
                f'</div>'
            )

    if not itens:
        return ""

    container = (
            '<div style="display:flex;flex-wrap:wrap;gap:12px;background-color:#1E1E24;'
            'padding:15px;border-radius:8px;border:1px solid #3e404f;margin-top:15px;">'
            + "".join(itens)
            + "</div>"
    )
    return container


# --- FUNÇÃO PARA DEFINIR A COR PRIORITÁRIA DE UM AGRUPAMENTO ---
def obter_cor_prioritaria(lista_intervencoes):
    interv_set = {str(i).strip() for i in lista_intervencoes}

    if "Corretiva" in interv_set: return CORES_INTERVENCAO["Corretiva"]
    if "Corretiva POS reincidentes" in interv_set: return CORES_INTERVENCAO["Corretiva POS reincidentes"]

    if "Preventiva" in interv_set: return CORES_INTERVENCAO["Preventiva"]
    if "Preventiva gerencial" in interv_set: return CORES_INTERVENCAO["Preventiva gerencial"]

    PRIORITY_ORCAMENTO = [
        "Orçamento aprovado",
        "Orçamento pendente de aprovação do cliente",
        "Orçamento pendente da filial detalhar motivo",
        "Orçamento reprovado",
        "Orçamento",
    ]
    for key in PRIORITY_ORCAMENTO:
        if key in interv_set:
            return CORES_INTERVENCAO.get(key, "#FFD700")

    if "Instalação" in interv_set: return CORES_INTERVENCAO["Instalação"]
    if "Reinstalação" in interv_set: return CORES_INTERVENCAO["Reinstalação"]

    return CORES_INTERVENCAO.get(list(interv_set)[0], "#FF4B4B")


# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown('<div class="version-tag-sidebar">v0.4.1</div>', unsafe_allow_html=True)

    st.title("📍 My Maps BR")
    st.markdown("---")

    arquivo = st.file_uploader("Upload da Planilha Excel", type=["xlsx"])

    # Lógica de detecção do "X" (Remover arquivo) ou Novo arquivo
    if arquivo is None and st.session_state.ultimo_arquivo is not None:
        st.session_state.df_final = None
        st.session_state.chamado_selecionado = None
        st.session_state.dados_agrupados_marcador = []
        st.session_state.coords_sessao = {}
        st.session_state.ultimo_arquivo = None
        st.session_state.f_interv, st.session_state.f_clie, st.session_state.f_regi = "Todos", "Todos", "Todos"
        st.session_state.map_center = [-14.2350, -51.9253]
        st.session_state.map_zoom = 4
        st.rerun()

    if arquivo:
        is_novo_arquivo = (st.session_state.ultimo_arquivo != arquivo.name)

        if is_novo_arquivo:
            st.session_state.dados_agrupados_marcador = []
            st.session_state.coords_sessao = {}
            st.session_state.chamado_selecionado = None
            st.session_state.f_interv, st.session_state.f_clie, st.session_state.f_regi = "Todos", "Todos", "Todos"

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

        # --- FORMULÁRIO DE FILTROS ---
        st.markdown("---")
        with st.expander("⏳ Filtros", expanded=False):
            if st.session_state.df_final is not None:
                with st.form("form_filtros_sidebar"):
                    op_interv = ["Todos"] + sorted(
                        st.session_state.df_final['Intervencao'].dropna().astype(str).unique().tolist())
                    idx_interv = op_interv.index(
                        st.session_state.f_interv) if st.session_state.f_interv in op_interv else 0
                    intervencao_sel = st.selectbox("Filtrar por Intervenção:", op_interv, index=idx_interv)

                    op_clie = ["Todos"] + sorted(
                        st.session_state.df_final['Cliente'].dropna().astype(str).unique().tolist())
                    idx_clie = op_clie.index(st.session_state.f_clie) if st.session_state.f_clie in op_clie else 0
                    cliente_sel = st.selectbox("Filtrar por Cliente:", op_clie, index=idx_clie)

                    op_regi = ["Todos"] + sorted(
                        st.session_state.df_final['Regiao'].dropna().astype(str).unique().tolist())
                    idx_regi = op_regi.index(st.session_state.f_regi) if st.session_state.f_regi in op_regi else 0
                    regiao_sel = st.selectbox("Filtrar por Região:", op_regi, index=idx_regi)

                    col_aplicar, col_limpar = st.columns(2)
                    with col_aplicar:
                        submeteu = st.form_submit_button("⚡ Aplicar Filtros", use_container_width=True)
                    with col_limpar:
                        limpar = st.form_submit_button("🧹 Limpar Filtros", use_container_width=True)
                    if submeteu:
                        st.session_state.f_interv = intervencao_sel
                        st.session_state.f_clie = cliente_sel
                        st.session_state.f_regi = regiao_sel
                        st.rerun()
                    if limpar:
                        st.session_state.f_interv = "Todos"
                        st.session_state.f_clie = "Todos"
                        st.session_state.f_regi = "Todos"
                        st.rerun()
            else:
                st.selectbox("Filtrar por Intervenção:", ["Nenhuma planilha carregada"], disabled=True, key="ds1")
                st.selectbox("Filtrar por Cliente:", ["Nenhuma planilha carregada"], disabled=True, key="ds2")
                st.selectbox("Filtrar por Região:", ["Nenhuma planilha carregada"], disabled=True, key="ds3")
                st.caption("💡 Carregue uma planilha para liberar os filtros.")

        # --- INFO DA ROTA NA SIDEBAR ---
        if st.session_state.get('rota_info'):
            st.markdown("---")
            info = st.session_state.rota_info
            origem_display = info.get("origem", "")
            destino_display = info.get("destino", "")
            rotas = info.get("rotas", [])

            st.markdown("**🗺️ Última Rota Calculada**")

            st.markdown(
                f'<div style="background:#1E1E24;border:1px solid #3e404f;border-radius:8px;padding:12px;font-size:13px;color:#E0E0E0;">'
                f'<div style="margin-bottom:4px;">🏠 <b>Saída:</b> {origem_display}</div>'
                f'<div style="margin-bottom:10px;">🏁 <b>Destino:</b> {destino_display}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            for r in rotas:
                label = r.get("label", "Rota")
                cor_borda = "#007BFF" if "🔵" in label else ("#2E8B57" if "🟢" in label else "#555")
                cor_bg = "#007BFF11" if "🔵" in label else ("#2E8B5711" if "🟢" in label else "#22222211")
                dist = r.get("distancia_km", "—")
                dur = r.get("duracao_str", "—")
                st.markdown(
                    f'<div style="background:{cor_bg};border:1px solid {cor_borda};border-radius:6px;padding:8px 10px;margin-top:6px;font-size:13px;color:#E0E0E0;">'
                    f'<div style="font-weight:bold;margin-bottom:4px;">{label}</div>'
                    f'<div>📍 <b>{dist} km</b> &nbsp; ⏱️ <b>{dur}</b></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            if st.button("🗑️ Limpar Rota", use_container_width=True, key="btn_limpar_rota"):
                st.session_state.rota_ponto_A = None
                st.session_state.rota_ponto_B = None
                st.session_state.rota_info = None
                st.rerun()

        if is_novo_arquivo or st.session_state.df_final is None:
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
            col_sla = mapear_coluna_flexivel(df_aba.columns.tolist(),
                                             ["LimiteAtendimento", "LimiteAtend", "Limite Atendimento", "SLA", "Prazo"])

            if col_os and col_cidade and col_uf and col_rua:
                colunas_para_copiar = [col_os, col_cidade, col_uf, col_rua]
                if col_intervencao: colunas_para_copiar.append(col_intervencao)
                if col_cliente: colunas_para_copiar.append(col_cliente)
                if col_regiao: colunas_para_copiar.append(col_regiao)
                if col_sla: colunas_para_copiar.append(col_sla)

                df_limpo = df_aba[colunas_para_copiar].dropna(subset=[col_os, col_rua])

                nomes_colunas = {col_os: 'CodOS', col_cidade: 'Cidade', col_uf: 'SiglaUF', col_rua: 'Endereco'}
                if col_intervencao: nomes_colunas[col_intervencao] = 'Intervencao'
                if col_cliente: nomes_colunas[col_cliente] = 'Cliente'
                if col_regiao: nomes_colunas[col_regiao] = 'Regiao'
                if col_sla: nomes_colunas[col_sla] = 'SLA'

                df_limpo = df_limpo.rename(columns=nomes_colunas)

                if 'Intervencao' not in df_limpo.columns: df_limpo['Intervencao'] = "Não Informado"
                if 'Cliente' not in df_limpo.columns: df_limpo['Cliente'] = "Não Informado"
                if 'Regiao' not in df_limpo.columns: df_limpo['Regiao'] = "Não Informado"
                if 'SLA' not in df_limpo.columns: df_limpo['SLA'] = ""

                df_limpo['CodOS'] = df_limpo['CodOS'].astype(str).str.split('.').str[0].str.strip()
                df_limpo = df_limpo.drop_duplicates(subset=['CodOS'], keep='first')

                st.session_state.df_final = df_limpo
                st.session_state.ultimo_arquivo = arquivo.name
                st.session_state.chamado_selecionado = None

                st.session_state.expander_aberto = False
                st.session_state.coords_sessao = {}
                st.session_state.dados_agrupados_marcador = []
                st.session_state.f_interv, st.session_state.f_clie, st.session_state.f_regi = "Todos", "Todos", "Todos"

                st.session_state.map_center = [-14.2350, -51.9253]
                st.session_state.map_zoom = 4
                st.rerun()
            else:
                st.error("❌ Não foi possível encontrar todas as colunas obrigatórias nesta aba.")

# --- PROCESSAMENTO E GEOLOCALIZAÇÃO ---
if st.session_state.df_final is not None and not st.session_state.dados_agrupados_marcador:
    df = st.session_state.df_final
    dados_mapa = df.dropna(subset=['Endereco', 'Cidade', 'SiglaUF'])
    grupo_pontos = dados_mapa.groupby(
        ['Endereco', 'Cidade', 'SiglaUF', 'Intervencao', 'Cliente', 'Regiao', 'CodOS', 'SLA']).size().reset_index(
        name='qtd')

    ctx = ssl.create_default_context(cafile=certifi.where())
    geolocator = Photon(ssl_context=ctx, user_agent="mymaps_br_fast")

    pontos_para_buscar = []
    EXCECOES_CIDADES = {
        ("ZORTEA", "SC"): [-27.4514, -51.5542],
        ("CHAPECO", "SC"): [-27.1004, -52.6152],
        ("CHAPECÓ", "SC"): [-27.1004, -52.6152],
        ("NAVEGANTES", "SC"): [-26.8914, -48.6548],
        ("SAO JOSE", "SC"): [-27.6146, -48.6353],
        ("SÃO JOSÉ", "SC"): [-27.6146, -48.6353],
        ("CAMPO GRANDE", "MS"): [-20.4697, -54.6201],
        ("CAMPO GRANDO", "MS"): [-20.4697, -54.6201],  # typo comum na planilha
        ("PARANAIBA", "MS"): [-19.7942, -51.1809],
        ("PARANAÍBA", "MS"): [-19.7942, -51.1809],
    }

    for row in grupo_pontos.itertuples(index=False):
        rua_limpa, cid_limpa, uf_limpa = str(row.Endereco).strip(), str(row.Cidade).strip(), str(row.SiglaUF).strip()
        interv_limpa, cli_limpa, reg_limpa = str(row.Intervencao).strip(), str(row.Cliente).strip(), str(
            row.Regiao).strip()
        os_limpa, sla_limpa = str(row.CodOS).strip(), str(row.SLA).strip()

        endereco_completo_busca = f"{rua_limpa}, {cid_limpa} - {uf_limpa}, Brasil"
        chave_busca = endereco_completo_busca.upper().strip()
        cid_upper = cid_limpa.upper().strip()

        pos = None

        # 1. Verificar EXCEÇÕES (cidades com problemas conhecidos)
        chave_excecao = (cid_upper, uf_limpa.upper().strip())
        if chave_excecao in EXCECOES_CIDADES:
            pos = EXCECOES_CIDADES[chave_excecao]
            st.session_state.coords_sessao[chave_busca] = pos
            adicionar_ao_cache(chave_busca, cli_limpa, cid_limpa, uf_limpa, pos[0], pos[1])

        # 2. Verificar CACHE se não foi encontrado em exceções
        if pos is None:
            lat_cache, lng_cache = obter_coordenadas_com_cache(endereco_completo_busca, chave_busca, cli_limpa,
                                                               cid_limpa, uf_limpa)
            if lat_cache is not None and lng_cache is not None:
                pos = [lat_cache, lng_cache]
                st.session_state.coords_sessao[chave_busca] = pos

        # 3. Verificar coords_sessao (de runs anteriores)
        if pos is None and chave_busca in st.session_state.coords_sessao:
            pos = st.session_state.coords_sessao[chave_busca]

        if pos is not None:
            st.session_state.dados_agrupados_marcador.append({
                "pos": pos, "qtd": int(row.qtd), "cid": cid_limpa, "uf": uf_limpa, "rua": rua_limpa,
                "interv": interv_limpa, "cli": cli_limpa, "reg": reg_limpa, "os": os_limpa, "sla": sla_limpa
            })
        else:
            pontos_para_buscar.append(
                (row, endereco_completo_busca, chave_busca, interv_limpa, cli_limpa, reg_limpa, os_limpa, sla_limpa))

    if pontos_para_buscar:
        prog = st.sidebar.progress(0)
        status = st.sidebar.empty()

        for idx, (row, endereco_completo_busca, chave_busca, interv_limpa, cli_limpa, reg_limpa, os_limpa,
                  sla_limpa) in enumerate(pontos_para_buscar):
            rua, cid, uf_val = str(row.Endereco).strip(), str(row.Cidade).strip(), str(row.SiglaUF).strip()
            status.text(f"🌐 Buscando locais: {cid}-{uf_val} ({idx + 1}/{len(pontos_para_buscar)})...")
            pos = None
            # 1. Tenta JSON local de cidades de SC (sem API)
            if uf_val.upper() == "SC":
                lat_sc, lng_sc = _buscar_cidade_sc(cid)
                if lat_sc is not None:
                    pos = [lat_sc, lng_sc]

            # 2. Fallback: correção manual conhecida
            if not pos:
                coords_fixas = _corrigir_coords_se_necessario(cid, None, None)
                if coords_fixas[0] is not None:
                    pos = list(coords_fixas)

            # 3. Fallback: geocodificação via API (outros estados ou não encontrado no JSON)
            if not pos:
                try:
                    loc = geolocator.geocode(endereco_completo_busca, timeout=3)
                    if loc:
                        pos = [loc.latitude, loc.longitude]
                    else:
                        loc_fallback = geolocator.geocode(f"{rua.split(',')[0]}, {cid} - {uf_val}, Brasil", timeout=2)
                        if loc_fallback:
                            pos = [loc_fallback.latitude, loc_fallback.longitude]
                    if not pos:
                        loc_cidade = geolocator.geocode(f"{cid}, {uf_val}, Brasil", timeout=3)
                        if loc_cidade:
                            pos = [loc_cidade.latitude, loc_cidade.longitude]
                except Exception as e:
                    print(f"[GEOCODE ERROR] {endereco_completo_busca}: {e}")
                    pos = None

            if pos:
                # Corrige cidades com geocodificação conhecidamente errada
                pos[0], pos[1] = _corrigir_coords_se_necessario(cid, pos[0], pos[1])
                st.session_state.coords_sessao[chave_busca] = pos
                # Salvar no cache para próximas execuções
                adicionar_ao_cache(chave_busca, cli_limpa, cid, uf_val, pos[0], pos[1])
                st.session_state.dados_agrupados_marcador.append({
                    "pos": pos, "qtd": int(row.qtd), "cid": cid, "uf": uf_val, "rua": rua,
                    "interv": interv_limpa, "cli": cli_limpa, "reg": reg_limpa, "os": os_limpa, "sla": sla_limpa
                })
            prog.progress((idx + 1) / len(pontos_para_buscar))

        status.empty()
        prog.empty()

    if st.session_state.coords_sessao:
        coordenadas_validas = list(st.session_state.coords_sessao.values())
        lats, lngs = [c[0] for c in coordenadas_validas], [c[1] for c in coordenadas_validas]
        st.session_state.map_center = [(min(lats) + max(lats)) / 2, (min(lngs) + max(lngs)) / 2]

        delta_max = max(max(lats) - min(lats), max(lngs) - min(lngs))
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


# --- FUNÇÃO COMPARTILHADA: ADICIONA MARCADORES AO MAPA ---
def adicionar_marcadores_ao_mapa(m, df_agrupamento):
    """Adiciona marcadores em um folium.Map a partir de um DataFrame filtrado."""
    if df_agrupamento.empty:
        return
    df = df_agrupamento.copy()
    df['lat'] = df['pos'].apply(lambda x: x[0])
    df['lng'] = df['pos'].apply(lambda x: x[1])

    for (lat, lng), group_local in df.groupby(['lat', 'lng']):
        total_chamados = len(group_local)
        primeiro = group_local.iloc[0]
        intervencoes = group_local['interv'].tolist()
        cor = obter_cor_prioritaria(intervencoes)

        texto = f"""
            <div style='font-family: Arial, sans-serif; min-width: 240px;'>
                <span style='font-size: 14px; font-weight: bold; color: #FF4B4B;'>📍 {primeiro['cid']} - {primeiro['uf']}</span><br>
                <small style='color: #666;'>{primeiro['rua']}</small><br>
                <hr style='margin: 8px 0; border: 0; border-top: 1px solid #ddd;'>
            """
        for chamado in group_local.itertuples():
            texto += f"<b>Intervenção:</b> {chamado.interv}<br>"
            texto += f"<b>Cliente:</b> {chamado.cli}<br><b>Nº Chamado:</b> {chamado.os}<br>"
            sla_val = str(chamado.sla).strip()
            if sla_val and sla_val.upper() not in ("S/N", "NAN"):
                texto += f"<b>SLA:</b> {sla_val}<br>"
            if len(group_local) > 1:
                texto += "<hr style='margin: 6px 0; border: 0; border-top: 1px dashed #eee;'>"
        texto += f"<span style='font-size: 11px; font-weight: bold; color: #333;'>Total de chamados: {total_chamados}</span></div>"

        raio = min(9 + (total_chamados * 0.2), 28)
        diam = int(raio * 2)
        fonte = max(8, min(12, int(raio * 0.65)))
        html_icone = (
            f'<div style="background-color: {cor}; color: white; border: 1px solid #1E1E1E; '
            f'border-radius: 50%; width: {diam}px; height: {diam}px; display: flex; '
            f'align-items: center; justify-content: center; font-size: {fonte}px; '
            f'font-weight: bold; box-shadow: 0px 0px 8px {cor};">{total_chamados}</div>'
        )
        folium.Marker(
            location=[lat, lng],
            icon=folium.DivIcon(html=html_icone, icon_size=(diam, diam), icon_anchor=(raio, raio)),
            tooltip=texto, popup=texto
        ).add_to(m)


# --- CONSTRUTOR DINÂMICO DO MAPA ---
def construir_mapa_geral():
    m = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)
    dados_filtrados = []
    for p in st.session_state.dados_agrupados_marcador:
        if st.session_state.f_interv != "Todos" and p["interv"] != st.session_state.f_interv: continue
        if st.session_state.f_clie != "Todos" and p["cli"] != st.session_state.f_clie: continue
        if st.session_state.f_regi != "Todos" and p["reg"] != st.session_state.f_regi: continue
        dados_filtrados.append(p)

    adicionar_marcadores_ao_mapa(m, pd.DataFrame(dados_filtrados))
    return m


# --- RENDERIZAÇÃO DA SIDEBAR CONDICIONAL ---
if st.session_state.df_final is not None and CONSEGUI_VER_LISTA:
    with st.sidebar:
        df = st.session_state.df_final.copy()
        if st.session_state.f_interv != "Todos": df = df[df['Intervencao'] == st.session_state.f_interv]
        if st.session_state.f_clie != "Todos": df = df[df['Cliente'] == st.session_state.f_clie]
        if st.session_state.f_regi != "Todos": df = df[df['Regiao'] == st.session_state.f_regi]

        df_botoes = df.copy()
        df_botoes['OS_Num'] = pd.to_numeric(df_botoes['CodOS'], errors='coerce')
        df_botoes = df_botoes.sort_values(by=['SiglaUF', 'Cidade', 'OS_Num', 'CodOS'])

        st.markdown("---")
        with st.expander(f"📋 Lista de Chamados ({len(df_botoes)})", expanded=st.session_state.expander_aberto):
            busca = st.text_input("🔍 Pesquisar chamado:", placeholder="Ex: PR ou Curitiba...")
            if busca:
                st.session_state.expander_aberto = True
                bn = str(busca).strip().lower()
                df_botoes = df_botoes[
                    df_botoes['CodOS'].astype(str).str.lower().str.contains(bn) | df_botoes['Cidade'].astype(
                        str).str.lower().str.contains(bn) | df_botoes['SiglaUF'].astype(str).str.lower().str.contains(
                        bn)]

            st.markdown('<div class="lista-chamados-container">', unsafe_allow_html=True)
            if df_botoes.empty:
                st.caption("⚠️ Nenhum chamado encontrado.")
            else:
                # Gera um único bloco <style> consolidado (evita centenas de tags no DOM)
                regras_css = []
                for idx_css, row_css in enumerate(df_botoes.itertuples(index=False)):
                    cham_css = str(row_css.CodOS)
                    cor_css = CORES_INTERVENCAO.get(str(row_css.Intervencao), "#3e404f")
                    regras_css.append(
                        f'div[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type({idx_css + 1}) button'
                        f' {{ border-left: 6px solid {cor_css} !important; }}'
                    )
                if regras_css:
                    st.markdown(f"<style>{''.join(regras_css)}</style>", unsafe_allow_html=True)

                for idx, row in enumerate(df_botoes.itertuples(index=False)):
                    cham, cid, uf_val, rua_completa, interv = str(row.CodOS), str(row.Cidade), str(row.SiglaUF), str(
                        row.Endereco), str(row.Intervencao)
                    is_sel = (str(st.session_state.chamado_selecionado) == cham)
                    prefixo = "🔷" if is_sel else "🔵"
                    label_botao = f"{prefixo} [{cid}-{uf_val}] OS: {cham}"

                    if st.button(label_botao, key=f"btn_os_{cham}_{idx}"):
                        st.session_state.chamado_selecionado = cham
                        st.session_state.expander_aberto = True
                        busca_end = f"{rua_completa.strip()}, {cid.strip()} - {uf_val.strip()}, Brasil".upper().strip()
                        if busca_end not in st.session_state.coords_sessao: busca_end = " ".join(busca_end.split())
                        if busca_end in st.session_state.coords_sessao:
                            st.session_state.map_center = st.session_state.coords_sessao[busca_end]
                            st.session_state.map_zoom = 17
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- ÁREA PRINCIPAL COM CONTROLE DE ABAS REMOTO ---
if st.session_state.df_final is not None and st.session_state.dados_agrupados_marcador:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)

    lista_abas_nome = ["🗺️ Visão Geral"]
    if CONSEGUI_VER_ROTAS: lista_abas_nome.append("🚗 Traçar Rotas")

    abas_renderizations = st.tabs(lista_abas_nome)

    df_atual_filtrado = st.session_state.df_final.copy()
    if st.session_state.f_interv != "Todos": df_atual_filtrado = df_atual_filtrado[
        df_atual_filtrado['Intervencao'] == st.session_state.f_interv]
    if st.session_state.f_clie != "Todos": df_atual_filtrado = df_atual_filtrado[
        df_atual_filtrado['Cliente'] == st.session_state.f_clie]
    if st.session_state.f_regi != "Todos": df_atual_filtrado = df_atual_filtrado[
        df_atual_filtrado['Regiao'] == st.session_state.f_regi]

    with abas_renderizations[0]:
        mapa_atualizado = construir_mapa_geral()
        saída_mapa_geral = st_folium(
            mapa_atualizado, width=1800, height=850, use_container_width=True,
            returned_objects=["last_object_clicked"], center=st.session_state.map_center,
            zoom=st.session_state.map_zoom,
            key=f"mapa_geral_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}"
        )

        st.markdown(renderizar_legenda_dinamica_html(df_atual_filtrado), unsafe_allow_html=True)

        if saída_mapa_geral and saída_mapa_geral.get("last_object_clicked"):
            clique = saída_mapa_geral["last_object_clicked"]
            lat_clicada, lng_clicada = clique["lat"], clique["lng"]
            if (abs(lat_clicada - st.session_state.map_center[0]) > 0.0001 or abs(
                    lng_clicada - st.session_state.map_center[1]) > 0.0001) or st.session_state.map_zoom != 17:
                st.session_state.map_center = [lat_clicada, lng_clicada]
                st.session_state.map_zoom = 17
                for cb, pos in st.session_state.coords_sessao.items():
                    if abs(pos[0] - lat_clicada) < 0.001 and abs(pos[1] - lng_clicada) < 0.001:
                        for r in st.session_state.df_final.itertuples():
                            if f"{str(r.Endereco).strip()}, {str(r.Cidade).strip()} - {str(r.SiglaUF).strip()}, Brasil".upper().strip() == cb:
                                st.session_state.chamado_selecionado = str(r.CodOS)
                                st.session_state.expander_aberto = True
                                break
                        break
                st.rerun()

    if CONSEGUI_VER_ROTAS:
        with abas_renderizations[1]:
            df_rotas = df_atual_filtrado.copy()
            df_rotas['Cidade_UF'] = df_rotas['Cidade'] + " - " + df_rotas['SiglaUF']
            lista_cidades_br = sorted(df_rotas['Cidade_UF'].unique().tolist())

            if not lista_cidades_br:
                st.warning("⚠️ Nenhuma cidade disponível para rotas com os filtros aplicados.")
            else:
                # Inicializa estado da cidade de saída do técnico
                if 'cidade_saida_tecnico' not in st.session_state:
                    st.session_state.cidade_saida_tecnico = ""
                if 'coords_saida_tecnico' not in st.session_state:
                    st.session_state.coords_saida_tecnico = None

                col_saida, col_destino, col_btn = st.columns([2, 2, 1.2])
                with col_saida:
                    cidade_saida_input = st.text_input(
                        "🏠 Cidade de Saída do Técnico",
                        value=st.session_state.cidade_saida_tecnico,
                        placeholder="Ex: Videira - SC",
                        key="cidade_saida_tecnico_input"
                    )
                with col_destino:
                    destino = st.selectbox("🏁 Cidade de Destino (Chamado)", lista_cidades_br,
                                           index=0, key="destino_rota")
                with col_btn:
                    calcular = st.button("🚀 Calcular Rota", use_container_width=True)

                # Inicializa estado dos pontos de rota
                if 'rota_ponto_A' not in st.session_state:
                    st.session_state.rota_ponto_A = None
                if 'rota_ponto_B' not in st.session_state:
                    st.session_state.rota_ponto_B = None
                if 'rota_info' not in st.session_state:
                    st.session_state.rota_info = None

                m_rota = folium.Map(location=st.session_state.map_center, zoom_start=st.session_state.map_zoom)

                dados_filtrados_rota = []
                for p in st.session_state.dados_agrupados_marcador:
                    if st.session_state.f_interv != "Todos" and p["interv"] != st.session_state.f_interv: continue
                    if st.session_state.f_clie != "Todos" and p["cli"] != st.session_state.f_clie: continue
                    if st.session_state.f_regi != "Todos" and p["reg"] != st.session_state.f_regi: continue
                    dados_filtrados_rota.append(p)

                df_agrupamento_rota = pd.DataFrame(dados_filtrados_rota)
                adicionar_marcadores_ao_mapa(m_rota, df_agrupamento_rota)

                if calcular:
                    # --- GEOCODIFICAR CIDADE DE SAÍDA DO TÉCNICO ---
                    cidade_saida_str = cidade_saida_input.strip()
                    ponto_A = None

                    if not cidade_saida_str:
                        st.error("❌ Informe a cidade de saída do técnico antes de calcular a rota.")
                    else:
                        st.session_state.cidade_saida_tecnico = cidade_saida_str
                        chave_saida = f"{cidade_saida_str}, Brasil".upper().strip()

                        # Verificar cache ou coords_sessao primeiro
                        if chave_saida in st.session_state.coords_sessao:
                            ponto_A = st.session_state.coords_sessao[chave_saida]
                        else:
                            cache = carregar_cache_geocodificacao()
                            if chave_saida in cache:
                                entrada = cache[chave_saida]
                                ponto_A = [entrada["lat"], entrada["lng"]]
                                st.session_state.coords_sessao[chave_saida] = ponto_A
                            else:
                                # Geocodificar via API — cria instância local do geolocator
                                with st.spinner(f"📡 Buscando coordenadas de '{cidade_saida_str}'..."):
                                    cidade_apenas = cidade_saida_str.split("-")[0].split(",")[0].strip()
                                    queries_saida = [cidade_apenas, f"{cidade_apenas} Brasil"]
                                    loc_saida = None
                                    ultimo_erro = None
                                    try:
                                        ctx_local = ssl.create_default_context(cafile=certifi.where())
                                        geo_local = Photon(ssl_context=ctx_local, user_agent="mymaps_br_fast")
                                        for q in queries_saida:
                                            try:
                                                loc_saida = geo_local.geocode(q, timeout=5)
                                                if loc_saida:
                                                    break
                                            except Exception as e:
                                                ultimo_erro = e
                                                continue
                                    except Exception as e:
                                        ultimo_erro = e
                                    if loc_saida:
                                        ponto_A = [loc_saida.latitude, loc_saida.longitude]
                                        st.session_state.coords_sessao[chave_saida] = ponto_A
                                        cache[chave_saida] = {
                                            "cliente": "TECNICO",
                                            "cidade": cidade_saida_str.upper(),
                                            "estado": "",
                                            "lat": ponto_A[0],
                                            "lng": ponto_A[1]
                                        }
                                        salvar_cache_geocodificacao(cache)
                                    else:
                                        detalhe = f": {ultimo_erro}" if ultimo_erro else ""
                                        st.error(
                                            f"❌ Não foi possível encontrar '{cidade_saida_str}'. Tente apenas o nome da cidade, ex: Videira{detalhe}")

                    # --- OBTER COORDENADAS DO DESTINO (CHAMADO) ---
                    lin_destino = df_rotas[df_rotas['Cidade_UF'] == destino].iloc[0]
                    key_destino = f"{str(lin_destino['Endereco']).strip()}, {str(lin_destino['Cidade']).strip()} - {str(lin_destino['SiglaUF']).strip()}, Brasil".upper().strip()

                    if ponto_A is not None and key_destino in st.session_state.coords_sessao:
                        ponto_B = st.session_state.coords_sessao[key_destino]
                        st.session_state.rota_ponto_A = ponto_A
                        st.session_state.rota_ponto_B = ponto_B
                    elif ponto_A is not None and key_destino not in st.session_state.coords_sessao:
                        st.error("❌ Coordenadas do destino não encontradas. Tente recarregar a planilha.")

                # Aplica a rota no mapa sempre que os pontos estiverem salvos
                if st.session_state.rota_ponto_A and st.session_state.rota_ponto_B:
                    pA = st.session_state.rota_ponto_A
                    pB = st.session_state.rota_ponto_B

                    import urllib.request, json as _json

                    # API key ORS — lê do secrets se disponível, senão usa a padrão
                    try:
                        ORS_KEY = st.secrets.get("ORS_API_KEY",
                                                 "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjBlNWFhOTZkNTQ5OTQ3M2I5ZTM3MTc0ZDc4OTdmZDcxIiwiaCI6Im11cm11cjY0In0=")
                    except Exception:
                        ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjBlNWFhOTZkNTQ5OTQ3M2I5ZTM3MTc0ZDc4OTdmZDcxIiwiaCI6Im11cm11cjY0In0="


                    def _buscar_rota_ors(lat1, lng1, lat2, lng2, avoid_unpaved=False):
                        """Chama OpenRouteService e retorna (coords, dist_km, dur_str) ou None."""
                        url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
                        body = {
                            "coordinates": [[lng1, lat1], [lng2, lat2]],
                            "instructions": False,
                            "preference": "recommended"
                        }
                        if avoid_unpaved:
                            body["options"] = {
                                "avoid_features": ["unpavedroads", "ferries"]
                            }
                        payload = _json.dumps(body).encode("utf-8")
                        req = urllib.request.Request(
                            url,
                            data=payload,
                            headers={
                                "Authorization": ORS_KEY,
                                "Content-Type": "application/json",
                                "Accept": "application/json"
                            },
                            method="POST"
                        )
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            dados = _json.loads(resp.read())
                        feat = dados["features"][0]
                        coords = [[c[1], c[0]] for c in feat["geometry"]["coordinates"]]
                        props = feat["properties"]["summary"]
                        dist_km = round(props["distance"] / 1000, 1)
                        dur_min = round(props["duration"] / 60)
                        h, m = divmod(dur_min, 60)
                        dur_str = f"{h}h {m}min" if h else f"{m} min"
                        return coords, dist_km, dur_str


                    rota_info_nova = {
                        "origem": st.session_state.cidade_saida_tecnico,
                        "destino": destino,
                        "rotas": []
                    }

                    # Rota 1: recomendada (ORS já prioriza asfalto por padrão)
                    coords_1, dist_1, dur_1 = None, None, None
                    try:
                        coords_1, dist_1, dur_1 = _buscar_rota_ors(pA[0], pA[1], pB[0], pB[1], avoid_unpaved=False)
                    except Exception as e_r1:
                        coords_1 = None

                    # Rota 2: explicitamente evitando estradas não asfaltadas e ferries
                    coords_2, dist_2, dur_2 = None, None, None
                    try:
                        coords_2, dist_2, dur_2 = _buscar_rota_ors(pA[0], pA[1], pB[0], pB[1], avoid_unpaved=True)
                    except Exception:
                        coords_2 = None

                    if coords_1:
                        folium.PolyLine(
                            coords_1, color="#007BFF", weight=6, opacity=0.9,
                            tooltip=f"🔵 Rota mais rápida: {dist_1} km · {dur_1}"
                        ).add_to(m_rota)
                        rota_info_nova["rotas"].append({
                            "label": "🔵 Rota mais rápida",
                            "distancia_km": dist_1,
                            "duracao_str": dur_1
                        })

                    # Só mostra rota asfaltada se for diferente da principal (>2 km)
                    if coords_2 and (coords_1 is None or abs((dist_2 or 0) - (dist_1 or 0)) > 2):
                        folium.PolyLine(
                            coords_2, color="#2E8B57", weight=5, opacity=0.85,
                            dash_array="6",
                            tooltip=f"🟢 Rota asfaltada: {dist_2} km · {dur_2}"
                        ).add_to(m_rota)
                        rota_info_nova["rotas"].append({
                            "label": "🟢 Rota asfaltada",
                            "distancia_km": dist_2,
                            "duracao_str": dur_2
                        })

                    if not coords_1 and not coords_2:
                        # Fallback: linha reta
                        folium.PolyLine(
                            [pA, pB], color="#007BFF", weight=4, opacity=0.7,
                            dash_array="8",
                            tooltip="Rota aproximada (linha reta)"
                        ).add_to(m_rota)
                        rota_info_nova["fallback"] = True
                        rota_info_nova["rotas"].append({
                            "label": "⚠️ Linha reta (ORS indisponível)",
                            "distancia_km": "—",
                            "duracao_str": "—"
                        })

                    st.session_state.rota_info = rota_info_nova

                    # Marcadores de início e fim
                    folium.Marker(
                        pA,
                        popup="🏠 Saída do Técnico",
                        tooltip="Saída do Técnico",
                        icon=folium.Icon(color="green", icon="home", prefix="fa")
                    ).add_to(m_rota)
                    folium.Marker(
                        pB,
                        popup="🏁 Destino",
                        tooltip="Destino",
                        icon=folium.Icon(color="red", icon="flag", prefix="fa")
                    ).add_to(m_rota)

                    m_rota.fit_bounds([pA, pB], padding=(40, 40))

                saída_mapa_rotas = st_folium(
                    m_rota, width=1800, height=700, use_container_width=True,
                    returned_objects=["last_object_clicked"],
                    key=f"mapa_rotas_lat_{st.session_state.map_center[0]}_zoom_{st.session_state.map_zoom}"
                )

                st.markdown(renderizar_legenda_dinamica_html(df_atual_filtrado), unsafe_allow_html=True)

                if saída_mapa_rotas and saída_mapa_rotas.get("last_object_clicked"):
                    lat_clicada = saída_mapa_rotas["last_object_clicked"]["lat"]
                    lng_clicada = saída_mapa_rotas["last_object_clicked"]["lng"]

                    dist_lat_r = abs(lat_clicada - st.session_state.map_center[0])
                    dist_lng_r = abs(lng_clicada - st.session_state.map_center[1])

                    if (dist_lat_r > 0.0001 or dist_lng_r > 0.0001) or st.session_state.map_zoom != 17:
                        st.session_state.map_center = [lat_clicada, lng_clicada]
                        st.session_state.map_zoom = 17
                        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.container().markdown("<br><br><center><h3>⬅️ Insira a planilha para renderizar os endereços</h3></center>",
                            unsafe_allow_html=True)