<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Maps BR</title>

  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      display: flex;
      height: 100vh;
      width: 100vw;
      background-color: #0e1117;
      color: #fafafa;
      overflow: hidden;
    }

    /* --- SIDEBAR --- */
    aside {
      position: relative;
      width: 320px;
      height: 100%;
      background-color: #262730;
      padding: 1.25rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      border-right: 1px solid rgba(250, 250, 250, 0.05);
      flex-shrink: 0;
      transition: width 0.3s ease, padding 0.3s ease;
      overflow-y: auto;
      overflow-x: hidden;
      z-index: 1000;
    }

    aside.collapsed {
      width: 0;
      padding: 1.25rem 0;
      border-right: none;
    }

    .toggle-btn {
      position: fixed;
      top: 1rem;
      left: 305px;
      width: 28px;
      height: 28px;
      background-color: #262730;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 50%;
      color: #fafafa;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 2000;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
      transition: left 0.3s ease, background-color 0.2s;
    }

    aside.collapsed + .toggle-btn {
      left: 10px;
    }

    .toggle-btn:hover { background-color: #3b3d4a; }

    .badge-version {
      align-self: flex-start;
      font-size: 0.7rem;
      background: rgba(255, 255, 255, 0.08);
      color: #9a9ca1;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .app-title {
      font-size: 1.2rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding-bottom: 0.8rem;
      border-bottom: 1px solid rgba(250, 250, 250, 0.1);
    }

    .upload-card {
      background-color: #1a1c23;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
      cursor: pointer;
    }

    .upload-card:hover { border-color: rgba(255, 255, 255, 0.3); }

    .upload-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.85rem;
      color: #fafafa;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 0.35rem 0.65rem;
      border-radius: 4px;
    }

    .upload-info {
      font-size: 0.7rem;
      color: #7b7e87;
      word-break: break-all;
    }

    /* --- EXPANDER MENUS --- */
    .expander-container {
      background: #1e1e24;
      border-radius: 8px;
      border: 1px solid #3e404f;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .expander-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem;
      cursor: pointer;
      user-select: none;
      background-color: #1e1e24;
      transition: background-color 0.2s;
    }

    .expander-header:hover {
      background-color: #262730;
    }

    .expander-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: #fafafa;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .expander-icon {
      width: 14px;
      height: 14px;
      color: #9a9ca1;
      transition: transform 0.25s ease;
      flex-shrink: 0;
    }

    .expander-container.open .expander-icon {
      transform: rotate(180deg);
    }

    .expander-body {
      display: none;
      flex-direction: column;
      gap: 0.75rem;
      padding: 0 0.75rem 0.75rem 0.75rem;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      background: #1e1e24;
    }

    .expander-container.open .expander-body {
      display: flex;
    }

    .expander-body label {
      font-size: 0.75rem;
      color: #9a9ca1;
      margin-bottom: 2px;
      display: block;
    }

    select, input[type="text"] {
      width: 100%;
      background-color: #262730;
      border: 1px solid #464855;
      color: #fafafa;
      padding: 6px 8px;
      border-radius: 4px;
      font-size: 0.8rem;
      outline: none;
    }

    .btn-group {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.25rem;
    }

    .btn-primary {
      flex: 1;
      background-color: #007BFF;
      color: white;
      border: none;
      padding: 8px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: bold;
      cursor: pointer;
    }
    .btn-primary:hover { background-color: #0056b3; }

    .btn-secondary {
      flex: 1;
      background-color: #3b3d4a;
      color: white;
      border: none;
      padding: 8px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: bold;
      cursor: pointer;
    }
    .btn-secondary:hover { background-color: #4a4d57; }

    /* Lista Interna dos Chamados */
    .lista-chamados-container {
      max-height: 260px;
      overflow-y: auto;
      background-color: #1a1c23;
      padding: 6px;
      border-radius: 6px;
      border: 1px solid #3e404f;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .chamado-item-btn {
      background: #262730;
      color: #e0e0e0;
      border: 1px solid #464855;
      border-left: 6px solid #464855;
      padding: 8px 10px;
      text-align: left;
      font-size: 11px;
      font-family: monospace;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.2s, border-color 0.2s;
    }
    .chamado-item-btn:hover { background-color: #31333f; }
    .chamado-item-btn.selected {
      border-color: #007BFF;
      background-color: #2b3040;
    }

    /* Cards de Rota Selecionáveis */
    .rota-card-option {
      background: #1a1c23;
      border: 2px solid #3e404f;
      padding: 8px 10px;
      border-radius: 6px;
      margin-top: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .rota-card-option:hover {
      border-color: #007BFF;
      background: #22252e;
    }
    .rota-card-option.active {
      border-color: #007BFF;
      background: #007BFF1a;
    }

    /* --- PIN DE LOCALIZAÇÃO SVG/CSS (PONTOS DE ROTA) --- */
    .map-pin {
      position: relative;
      width: 30px;
      height: 40px;
      cursor: pointer;
    }
    .map-pin svg {
      width: 100%;
      height: 100%;
      filter: drop-shadow(0px 3px 5px rgba(0,0,0,0.6));
    }

    /* --- CONTEÚDO PRINCIPAL --- */
    main {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      height: 100vh;
      overflow: hidden;
    }

    .tabs-bar {
      display: flex;
      background-color: #1E1E24;
      padding: 6px 12px;
      margin: 10px 15px 0 15px;
      border-radius: 8px;
      border: 1px solid #3e404f;
      gap: 8px;
      align-items: center;
      z-index: 500;
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: #E0E0E0;
      font-size: 13px;
      font-weight: bold;
      padding: 6px 16px;
      border-radius: 6px;
      cursor: pointer;
    }

    .tab-btn.active {
      background-color: #007BFF;
      color: #FFFFFF;
    }

    /* --- TOOLBAR DE ROTAS --- */
    .rota-toolbar {
      display: none;
      gap: 10px;
      align-items: center;
      padding: 8px 15px;
      background: #1a1c23;
      margin: 8px 15px 0 15px;
      border-radius: 6px;
      border: 1px solid #3e404f;
      z-index: 500;
      position: relative;
    }

    .multiselect-dropdown {
      position: relative;
      flex: 2;
      min-width: 220px;
    }

    .multiselect-btn {
      width: 100%;
      background-color: #262730;
      border: 1px solid #464855;
      color: #fafafa;
      padding: 7px 10px;
      border-radius: 4px;
      font-size: 0.8rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .multiselect-list {
      display: none;
      position: absolute;
      top: 105%;
      left: 0;
      right: 0;
      max-height: 250px;
      overflow-y: auto;
      background-color: #1e1e24;
      border: 1px solid #3e404f;
      border-radius: 6px;
      padding: 6px;
      z-index: 2000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }

    .multiselect-list.open {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .multiselect-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 8px;
      border-radius: 4px;
      font-size: 0.8rem;
      color: #e0e0e0;
      cursor: pointer;
    }

    .multiselect-item:hover {
      background-color: #262730;
    }

    .multiselect-item input[type="checkbox"] {
      width: auto;
      cursor: pointer;
    }

    #map-container {
      flex: 1;
      width: calc(100% - 30px);
      margin: 10px 15px 15px 15px;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid #3e404f;
      position: relative;
    }

    #map {
      width: 100%;
      height: 100%;
      background-color: #0e1117;
    }

    .legenda-container {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      background-color: #1E1E24;
      padding: 10px 15px;
      border-radius: 8px;
      border: 1px solid #3e404f;
      margin: 0 15px 10px 15px;
      max-height: 90px;
      overflow-y: auto;
    }

    .legenda-item {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 500;
      color: #E0E0E0;
    }

    .legenda-cor {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      border: 1px solid #1E1E1E;
      flex-shrink: 0;
    }

    /* Ícone customizado Leaflet DivIcon para chamados */
    .custom-cluster-icon {
      border: 1px solid #1E1E1E;
      border-radius: 50%;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      cursor: pointer;
    }

    .empty-state {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 1.15rem;
      font-weight: 500;
      color: #fafafa;
      text-align: center;
      z-index: 400;
    }
  </style>
</head>
<body>

  <input type="file" id="file-input" accept=".xlsx, .xls" style="display: none;" />

  <!-- Sidebar -->
  <aside id="sidebar">
    <div class="badge-version">v0.5.0</div>
    <div class="app-title">
      <span>📍</span>
      <span>My Maps BR</span>
    </div>

    <!-- Upload -->
    <div class="upload-card" id="upload-card">
      <div class="upload-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        Upload
      </div>
      <div class="upload-info" id="upload-label">200MB per file • XLSX</div>
    </div>

    <!-- Filtros Recolhíveis (Expander) -->
    <div class="expander-container" id="filtros-container" style="display: none;">
      <div class="expander-header" id="expander-filtros-toggle">
        <div class="expander-title">⏳ Filtros</div>
        <svg class="expander-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>

      <div class="expander-body">
        <div>
          <label>Intervenção:</label>
          <select id="filtro-intervencao"><option value="Todos">Todos</option></select>
        </div>

        <div>
          <label>Cliente:</label>
          <select id="filtro-cliente"><option value="Todos">Todos</option></select>
        </div>

        <div>
          <label>Região:</label>
          <select id="filtro-regiao"><option value="Todos">Todos</option></select>
        </div>

        <div class="btn-group">
          <button class="btn-primary" id="btn-aplicar-filtros">⚡ Aplicar</button>
          <button class="btn-secondary" id="btn-limpar-filtros">🧹 Limpar</button>
        </div>
      </div>
    </div>

    <!-- Lista de Chamados Recolhível (Expander) -->
    <div class="expander-container" id="container-lista" style="display: none;">
      <div class="expander-header" id="expander-chamados-toggle">
        <div class="expander-title" id="label-chamados">📋 Lista de Chamados (0)</div>
        <svg class="expander-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>

      <div class="expander-body">
        <input type="text" id="busca-chamado" placeholder="🔍 Ex: PR ou Curitiba..." />
        <div class="lista-chamados-container" id="lista-chamados"></div>
      </div>
    </div>

    <!-- Info Rota Sidebar -->
    <div id="sidebar-rota-info" style="display: none; background:#1e1e24; padding:10px; border-radius:6px; font-size:12px; border:1px solid #3e404f;"></div>
  </aside>

  <!-- Botão Toggle Sidebar -->
  <button class="toggle-btn" id="toggle-btn">
    <svg id="toggle-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="15 18 9 12 15 6"></polyline>
    </svg>
  </button>

  <!-- Painel Principal -->
  <main>
    <div class="tabs-bar" id="tabs-bar" style="display: none;">
      <button class="tab-btn active" id="tab-geral">🗺️ Visão Geral</button>
      <button class="tab-btn" id="tab-rotas">🚗 Traçar Rotas</button>
    </div>

    <!-- Toolbar de Rotas -->
    <div class="rota-toolbar" id="rota-toolbar">
      <input type="text" id="rota-saida" placeholder="🏠 Saída (ex: Videira - SC)" style="flex: 1.5;" />
      
      <!-- Multi-Select Dropdown -->
      <div class="multiselect-dropdown" id="multiselect-dropdown">
        <div class="multiselect-btn" id="multiselect-btn">
          <span id="multiselect-btn-text">🏁 Selecionar Destinos (0)</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
        <div class="multiselect-list" id="multiselect-list"></div>
      </div>

      <button class="btn-primary" id="btn-calc-rota" style="flex: 1;">🚀 Calcular Rota</button>
    </div>

    <!-- Mapa -->
    <div id="map-container">
      <div class="empty-state" id="empty-state">⬅️ Insira a planilha para renderizar os endereços</div>
      <div id="map"></div>
    </div>

    <!-- Legenda Dinâmica -->
    <div class="legenda-container" id="legenda-dinamica" style="display: none;"></div>
  </main>

  <!-- Dependências JS (Leaflet + SheetJS) -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>

  <script>
    /* =========================================================================
       1. CONSTANTES, CORES E CONFIGURAÇÕES
       ========================================================================= */
    const CORES_INTERVENCAO = {
      "Alteração de engenharia": "#4B0082",
      "Autorização de deslocamento": "#4682B4",
      "Cofre": "#708090",
      "Corretiva": "#FF4B4B",
      "Corretiva POS reincidentes": "#B22222",
      "Desinstalação": "#FF8C00",
      "Helpdesk": "#008B8B",
      "Inspeção técnica": "#9ACD32",
      "Instalação": "#2E8B57",
      "Laudo técnico": "#8B008B",
      "Manutenção gerencial": "#5F9EA0",
      "Orçamento": "#FFD700",
      "Orçamento aprovado": "#32CD32",
      "Orçamento pendente da filial detalhar motivo": "#FFA500",
      "Orçamento pendente de aprovação do cliente": "#DAA520",
      "Orçamento reprovado": "#8B0000",
      "Preventiva": "#007BFF",
      "Preventiva gerencial": "#1E90FF",
      "Reinstalação": "#20B2AA",
      "Treinamento": "#9370DB",
      "Troca de Veloh C": "#8B4513",
      "Não Informado": "#464855"
    };

    const EXCECOES_CIDADES = {
      "ZORTEA-SC": [-27.4514, -51.5542],
      "CHAPECO-SC": [-27.1004, -52.6152],
      "CHAPECÓ-SC": [-27.1004, -52.6152],
      "NAVEGANTES-SC": [-26.8914, -48.6548],
      "SAO JOSE-SC": [-27.6146, -48.6353],
      "SÃO JOSÉ-SC": [-27.6146, -48.6353],
      "CAMPO GRANDE-MS": [-20.4697, -54.6201],
      "CAMPO GRANDO-MS": [-20.4697, -54.6201],
      "PARANAIBA-MS": [-19.7942, -51.1809],
      "PARANAÍBA-MS": [-19.7942, -51.1809],
      "SAO CRISTOVAO DO SUL-SC": [-27.2666, -50.4388],
      "LUZERNA-SC": [-27.1304, -51.4682]
    };

    /* =========================================================================
       2. ESTADO GLOBAL DA APLICAÇÃO
       ========================================================================= */
    let dfRaw = [];
    let dfFinal = [];
    let markersLayer = L.layerGroup();
    let routesLayer = L.layerGroup();
    let map = null;
    let abaAtiva = "geral";
    let coordsSessao = {};
    let chamadoSelecionado = null;
    let marcadoresPorOS = {};
    let destinosSelecionados = new Set();
    let marcadorAbertoPorClique = null;
    let rotasCalculadas = [];
    let rotaPolylines = [];

    /* =========================================================================
       3. CACHE LOCAL (localStorage)
       ========================================================================= */
    function carregarCacheLocal() {
      try {
        return JSON.parse(localStorage.getItem("geocodificacao_cache") || "{}");
      } catch {
        return {};
      }
    }

    function salvarCacheLocal(chave, dados) {
      const cache = carregarCacheLocal();
      cache[chave] = dados;
      localStorage.setItem("geocodificacao_cache", JSON.stringify(cache));
    }

    /* =========================================================================
       4. INICIALIZAÇÃO DO MAPA (Leaflet)
       ========================================================================= */
    function initMap() {
      if (!map) {
        map = L.map('map', { zoomControl: true }).setView([-14.2350, -51.9253], 4);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; OpenStreetMap'
        }).addTo(map);

        markersLayer.addTo(map);
        routesLayer.addTo(map);

        map.on('click', () => {
          marcadorAbertoPorClique = null;
        });
      }
    }

    /* =========================================================================
       5. GEOCODIFICAÇÃO (Rua, Cidade / Estado)
       ========================================================================= */
    function normalizar(str) {
      return (str || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().trim();
    }

    async function buscarCoordenadas(rua, cid, uf) {
      const ruaLimpa = (rua || "").trim();
      const cidLimpa = (cid || "").trim();
      const ufLimpa = (uf || "").trim();

      const chaveBusca = `${ruaLimpa}, ${cidLimpa} / ${ufLimpa}`.toUpperCase().trim();
      const chaveExcecao = `${normalizar(cidLimpa)}-${normalizar(ufLimpa)}`;

      if (EXCECOES_CIDADES[chaveExcecao]) {
        return EXCECOES_CIDADES[chaveExcecao];
      }

      if (coordsSessao[chaveBusca]) return coordsSessao[chaveBusca];
      const cacheLocal = carregarCacheLocal();
      if (cacheLocal[chaveBusca]) {
        coordsSessao[chaveBusca] = [cacheLocal[chaveBusca].lat, cacheLocal[chaveBusca].lng];
        return coordsSessao[chaveBusca];
      }

      const queries = [
        `${ruaLimpa}, ${cidLimpa} / ${ufLimpa}`,
        `${ruaLimpa}, ${cidLimpa} - ${ufLimpa}, Brasil`,
        `${ruaLimpa.split(',')[0]}, ${cidLimpa} / ${ufLimpa}`,
        `${cidLimpa} / ${ufLimpa}`,
        `${cidLimpa}, ${ufLimpa}, Brasil`
      ];

      for (const q of queries) {
        try {
          const resp = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=1`);
          const json = await resp.json();
          if (json.features && json.features.length > 0) {
            const [lng, lat] = json.features[0].geometry.coordinates;
            coordsSessao[chaveBusca] = [lat, lng];
            salvarCacheLocal(chaveBusca, { lat, lng, cidade: cidLimpa, estado: ufLimpa });
            return [lat, lng];
          }
        } catch (e) {
          console.warn("[GEOCODE WARN]", e);
        }
      }
      return null;
    }

    /* =========================================================================
       6. PRIORIDADE DE COR & AGRUPAMENTO DE MARCADORES (CHAMADOS)
       ========================================================================= */
    function obterCorPrioritaria(intervencoes) {
      const set = new Set(intervencoes.map(i => String(i).trim()));
      if (set.has("Corretiva")) return CORES_INTERVENCAO["Corretiva"];
      if (set.has("Corretiva POS reincidentes")) return CORES_INTERVENCAO["Corretiva POS reincidentes"];
      if (set.has("Preventiva")) return CORES_INTERVENCAO["Preventiva"];
      if (set.has("Preventiva gerencial")) return CORES_INTERVENCAO["Preventiva gerencial"];

      const PRIORITY_ORC = [
        "Orçamento aprovado", "Orçamento pendente de aprovação do cliente",
        "Orçamento pendente da filial detalhar motivo", "Orçamento reprovado", "Orçamento"
      ];
      for (const key of PRIORITY_ORC) {
        if (set.has(key)) return CORES_INTERVENCAO[key] || "#FFD700";
      }

      if (set.has("Instalação")) return CORES_INTERVENCAO["Instalação"];
      if (set.has("Reinstalação")) return CORES_INTERVENCAO["Reinstalação"];

      const first = Array.from(set)[0];
      return CORES_INTERVENCAO[first] || "#FF4B4B";
    }

    function renderizarMarcadores(dados) {
      markersLayer.clearLayers();
      marcadoresPorOS = {};
      marcadorAbertoPorClique = null;
      if (!dados || dados.length === 0) return;

      const grupos = {};
      dados.forEach(item => {
        if (!item.pos) return;
        const key = `${item.pos[0].toFixed(5)},${item.pos[1].toFixed(5)}`;
        if (!grupos[key]) grupos[key] = [];
        grupos[key].push(item);
      });

      const bounds = [];

      Object.values(grupos).forEach(grupo => {
        const primeiro = grupo[0];
        const [lat, lng] = primeiro.pos;
        bounds.push([lat, lng]);

        const total = grupo.length;
        const intervencoes = grupo.map(g => g.Intervencao);
        const cor = obterCorPrioritaria(intervencoes);

        const raio = Math.min(9 + (total * 0.2), 28);
        const diam = Math.round(raio * 2);
        const fonte = Math.max(8, Math.min(12, Math.round(raio * 0.65)));

        const customIcon = L.divIcon({
          className: 'custom-cluster-icon',
          html: `<div style="background-color:${cor}; width:${diam}px; height:${diam}px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:${fonte}px; box-shadow:0 0 8px ${cor};">${total}</div>`,
          iconSize: [diam, diam],
          iconAnchor: [raio, raio]
        });

        let htmlPopup = `<div style="font-family: Arial, sans-serif; min-width: 200px;">
          <b style="color:#FF4B4B;">📍 ${primeiro.Cidade} / ${primeiro.SiglaUF}</b><br>
          <small style="color:#666;">${primeiro.Endereco}</small><hr style="margin:6px 0; border:0; border-top:1px solid #ddd;">`;

        grupo.forEach((ch, idx) => {
          htmlPopup += `<b>Intervenção:</b> ${ch.Intervencao}<br><b>Cliente:</b> ${ch.Cliente}<br><b>Nº Chamado:</b> ${ch.CodOS}<br>`;
          if (ch.SLA && !["S/N", "NAN"].includes(String(ch.SLA).toUpperCase())) {
            htmlPopup += `<b>SLA:</b> ${ch.SLA}<br>`;
          }
          if (idx < grupo.length - 1) htmlPopup += `<hr style="margin:4px 0; border:0; border-top:1px dashed #eee;">`;
        });

        htmlPopup += `<div style="margin-top:6px; font-size:11px; font-weight:bold; color:#333;">Total de chamados: ${total}</div></div>`;

        const marker = L.marker([lat, lng], { icon: customIcon });
        marker.bindPopup(htmlPopup, { autoClose: false, closeOnClick: false });

        grupo.forEach(ch => {
          marcadoresPorOS[ch.CodOS] = marker;
        });

        marker.on('mouseover', () => {
          marker.openPopup();
        });

        marker.on('mouseout', () => {
          if (marcadorAbertoPorClique !== marker) {
            marker.closePopup();
          }
        });

        marker.on('click', () => {
          marcadorAbertoPorClique = marker;
          map.flyTo([lat, lng], 17, { duration: 1.2 });
          marker.openPopup();

          chamadoSelecionado = primeiro.CodOS;
          const container = document.getElementById('container-lista');
          if (!container.classList.contains('open')) {
            container.classList.add('open');
          }
          renderizarListaChamados(dfFinal);

          setTimeout(() => {
            const btnSel = document.querySelector(`.chamado-item-btn[data-os="${primeiro.CodOS}"]`);
            if (btnSel) {
              btnSel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
          }, 200);
        });

        markersLayer.addLayer(marker);
      });

      if (bounds.length > 0 && routesLayer.getLayers().length === 0) {
        map.fitBounds(bounds, { padding: [40, 40] });
      }
    }

    /* =========================================================================
       7. PROCESSAMENTO DO ARQUIVO EXCEL
       ========================================================================= */
    function mapearColuna(colunas, alvos) {
      for (const col of colunas) {
        if (alvos.map(a => a.toUpperCase()).includes(String(col).trim().toUpperCase())) return col;
      }
      for (const col of colunas) {
        for (const alvo of alvos) {
          if (String(col).trim().toLowerCase().includes(alvo.toLowerCase())) return col;
        }
      }
      return null;
    }

    async function processarPlanilha(file) {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: 'array' });

      let targetSheet = null;
      for (const prioridade of ["unificado", "rat's", "rats", "chamados"]) {
        const found = workbook.SheetNames.find(s => s.trim().toLowerCase() === prioridade);
        if (found) { targetSheet = found; break; }
      }
      if (!targetSheet) targetSheet = workbook.SheetNames[0];

      const sheet = workbook.Sheets[targetSheet];
      const jsonRows = XLSX.utils.sheet_to_json(sheet, { defval: "" });

      if (jsonRows.length === 0) {
        alert("Aba vazia ou formato inválido.");
        return;
      }

      const colunas = Object.keys(jsonRows[0]);
      const cOS = mapearColuna(colunas, ["CodOS", "Chamado", "ID", "Ticket"]);
      const cCid = mapearColuna(colunas, ["Cidade", "Municipio", "Cid"]);
      const cUF = mapearColuna(colunas, ["SiglaUF", "UF", "Estado"]);
      const cRua = mapearColuna(colunas, ["Endereco", "Endereço", "Logradouro", "Rua"]);
      const cInterv = mapearColuna(colunas, ["Intervencao", "Intervenção", "Tipo"]);
      const cClie = mapearColuna(colunas, ["Cliente", "NomeCliente", "RazaoSocial", "Aba Cliente", "Empresa"]);
      const cReg = mapearColuna(colunas, ["Regiao", "Região", "Distrito", "Area", "Zona"]);
      const cSla = mapearColuna(colunas, ["LimiteAtendimento", "LimiteAtend", "Limite Atendimento", "SLA", "Prazo"]);

      if (!cOS || !cCid || !cUF || !cRua) {
        alert("❌ Não foi possível encontrar todas as colunas obrigatórias na planilha.");
        return;
      }

      const vistos = new Set();
      dfRaw = [];

      for (const row of jsonRows) {
        const codOS = String(row[cOS]).split('.')[0].trim();
        if (!codOS || vistos.has(codOS)) continue;
        vistos.add(codOS);

        dfRaw.push({
          CodOS: codOS,
          Cidade: String(row[cCid]).trim(),
          SiglaUF: String(row[cUF]).trim(),
          Endereco: String(row[cRua]).trim(),
          Intervencao: cInterv && row[cInterv] ? String(row[cInterv]).trim() : "Não Informado",
          Cliente: cClie && row[cClie] ? String(row[cClie]).trim() : "Não Informado",
          Regiao: cReg && row[cReg] ? String(row[cReg]).trim() : "Não Informado",
          SLA: cSla && row[cSla] ? String(row[cSla]).trim() : ""
        });
      }

      document.getElementById('empty-state').style.display = 'none';
      initMap();

      for (const item of dfRaw) {
        item.pos = await buscarCoordenadas(item.Endereco, item.Cidade, item.SiglaUF);
      }

      dfFinal = [...dfRaw];
      popularFiltros(dfFinal);
      aplicarFiltros();

      document.getElementById('filtros-container').style.display = 'flex';
      document.getElementById('container-lista').style.display = 'flex';
      document.getElementById('tabs-bar').style.display = 'flex';
      document.getElementById('legenda-dinamica').style.display = 'flex';
    }

    /* =========================================================================
       8. FILTROS E LISTA LATERAL
       ========================================================================= */
    function popularFiltros(dados) {
      const preencherSelect = (id, valores) => {
        const select = document.getElementById(id);
        const atual = select.value;
        select.innerHTML = '<option value="Todos">Todos</option>';
        valores.forEach(v => {
          const opt = document.createElement('option');
          opt.value = v;
          opt.textContent = v;
          select.appendChild(opt);
        });
        if (valores.includes(atual)) {
          select.value = atual;
        }
      };

      const intervencoes = [...new Set(dados.map(d => d.Intervencao))].sort();
      const clientes = [...new Set(dados.map(d => d.Cliente))].sort();
      const regioes = [...new Set(dados.map(d => d.Regiao))].sort();

      preencherSelect('filtro-intervencao', intervencoes);
      preencherSelect('filtro-cliente', clientes);
      preencherSelect('filtro-regiao', regioes);
    }

    function renderizarLegendaDinamica(dadosFiltrados) {
      const legContainer = document.getElementById('legenda-dinamica');
      const ativas = new Set(dadosFiltrados.map(d => d.Intervencao));
      legContainer.innerHTML = '';

      for (const [tipo, cor] of Object.entries(CORES_INTERVENCAO)) {
        if (ativas.has(tipo) && tipo !== "Não Informado") {
          const div = document.createElement('div');
          div.className = 'legenda-item';
          div.innerHTML = `<div class="legenda-cor" style="background-color:${cor}; box-shadow:0 0 4px ${cor};"></div><span>${tipo}</span>`;
          legContainer.appendChild(div);
        }
      }
    }

    function renderizarListaChamados(dados) {
      const lista = document.getElementById('lista-chamados');
      const label = document.getElementById('label-chamados');
      lista.innerHTML = '';
      label.textContent = `📋 Lista de Chamados (${dados.length})`;

      const busca = document.getElementById('busca-chamado').value.toLowerCase().trim();
      const filtrados = dados.filter(d => 
        !busca || 
        d.CodOS.toLowerCase().includes(busca) || 
        d.Cidade.toLowerCase().includes(busca) || 
        d.SiglaUF.toLowerCase().includes(busca)
      );

      filtrados.sort((a, b) => (a.Cidade + a.CodOS).localeCompare(b.Cidade + b.CodOS));

      filtrados.forEach(ch => {
        const btn = document.createElement('button');
        btn.className = 'chamado-item-btn';
        btn.setAttribute('data-os', ch.CodOS);
        if (chamadoSelecionado === ch.CodOS) {
          btn.classList.add('selected');
        }
        const cor = CORES_INTERVENCAO[ch.Intervencao] || '#464855';
        btn.style.borderLeftColor = cor;
        const prefixo = chamadoSelecionado === ch.CodOS ? "🔷" : "🔵";
        btn.textContent = `${prefixo} [${ch.Cidade}/${ch.SiglaUF}] OS: ${ch.CodOS}`;

        btn.addEventListener('click', () => {
          chamadoSelecionado = ch.CodOS;
          renderizarListaChamados(dfFinal);
          if (ch.pos) {
            map.flyTo(ch.pos, 17, { duration: 1.2 });
            const marker = marcadoresPorOS[ch.CodOS];
            if (marker) {
              marcadorAbertoPorClique = marker;
              marker.openPopup();
            }
          }
        });
        lista.appendChild(btn);
      });
    }

    function aplicarFiltros() {
      const fInterv = document.getElementById('filtro-intervencao').value;
      const fClie = document.getElementById('filtro-cliente').value;
      const fReg = document.getElementById('filtro-regiao').value;

      const filtrados = dfRaw.filter(d => {
        if (fInterv !== "Todos" && d.Intervencao !== fInterv) return false;
        if (fClie !== "Todos" && d.Cliente !== fClie) return false;
        if (fReg !== "Todos" && d.Regiao !== fReg) return false;
        return true;
      });

      dfFinal = filtrados;
      renderizarMarcadores(filtrados);
      renderizarLegendaDinamica(filtrados);
      renderizarListaChamados(filtrados);
      popularMultiSelectDestinos(filtrados);
    }

    /* =========================================================================
       9. TRAÇADO DE ROTAS PELAS VIAS (OSRM) + PINS DE LOCALIZAÇÃO GEOGRÁFICA
       ========================================================================= */
    function popularMultiSelectDestinos(dados) {
      const container = document.getElementById('multiselect-list');
      container.innerHTML = '';
      
      const destinosValidos = new Set();

      if (dados.length === 0) {
        container.innerHTML = '<div style="font-size:11px; color:#888; padding:6px;">Nenhum chamado disponível nesta região/filtro.</div>';
      } else {
        dados.forEach(d => {
          const id = d.CodOS;
          const label = `[${d.Cidade}/${d.SiglaUF}] OS: ${d.CodOS} - ${d.Cliente} (${d.Regiao})`;
          destinosValidos.add(id);

          const item = document.createElement('div');
          item.className = 'multiselect-item';

          const cb = document.createElement('input');
          cb.type = 'checkbox';
          cb.value = id;
          cb.checked = destinosSelecionados.has(id);

          cb.addEventListener('change', (e) => {
            if (e.target.checked) {
              destinosSelecionados.add(id);
            } else {
              destinosSelecionados.delete(id);
            }
            atualizarTextoBotaoMultiSelect();
          });

          const span = document.createElement('span');
          span.textContent = label;

          item.appendChild(cb);
          item.appendChild(span);
          item.addEventListener('click', (e) => {
            if (e.target !== cb) {
              cb.checked = !cb.checked;
              cb.dispatchEvent(new Event('change'));
            }
          });

          container.appendChild(item);
        });
      }

      for (const sel of destinosSelecionados) {
        if (!destinosValidos.has(sel)) {
          destinosSelecionados.delete(sel);
        }
      }
      atualizarTextoBotaoMultiSelect();
    }

    function atualizarTextoBotaoMultiSelect() {
      const btnText = document.getElementById('multiselect-btn-text');
      const count = destinosSelecionados.size;
      btnText.textContent = count === 0 
        ? "🏁 Selecionar Destinos (0)" 
        : `🏁 ${count} chamado(s) selecionado(s)`;
    }

    async function buscarRotasOSRM(coordsLngLat) {
      const coordsString = coordsLngLat.map(c => `${c[0]},${c[1]}`).join(';');
      const url = `https://router.project-osrm.org/route/v1/driving/${coordsString}?overview=full&geometries=geojson&alternatives=true&steps=false`;

      try {
        const resp = await fetch(url);
        if (!resp.ok) return null;
        const data = await resp.json();
        if (!data.routes || data.routes.length === 0) return null;

        return data.routes.map((r, index) => {
          const latLngs = r.geometry.coordinates.map(c => [c[1], c[0]]);
          const distKm = (r.distance / 1000).toFixed(1);
          const durMin = Math.round(r.duration / 60);
          const h = Math.floor(durMin / 60);
          const m = durMin % 60;
          const durStr = h > 0 ? `${h}h ${m}min` : `${m} min`;

          return {
            id: index,
            nome: index === 0 ? "🔵 Rota Principal (Mais rápida)" : `🟢 Rota Alternativa ${index}`,
            cor: index === 0 ? "#007BFF" : "#2E8B57",
            coords: latLngs,
            distKm,
            durStr
          };
        });
      } catch (err) {
        console.error("Erro ao buscar rota OSRM:", err);
        return null;
      }
    }

    function selecionarRota(idRota) {
      rotaPolylines.forEach(item => {
        if (item.id === idRota) {
          item.line.setStyle({
            color: item.corOriginal,
            weight: 7,
            opacity: 1.0
          });
          item.line.bringToFront();
        } else {
          item.line.setStyle({
            color: "#6b7280",
            weight: 4,
            opacity: 0.5
          });
        }
      });

      document.querySelectorAll('.rota-card-option').forEach(card => {
        if (parseInt(card.getAttribute('data-id')) === idRota) {
          card.classList.add('active');
        } else {
          card.classList.remove('active');
        }
      });
    }

    async function calcularRota() {
      const saidaStr = document.getElementById('rota-saida').value.trim();

      if (!saidaStr) {
        alert("❌ Informe a cidade de saída do técnico.");
        return;
      }
      if (destinosSelecionados.size === 0) {
        alert("❌ Selecione ao menos um chamado de destino.");
        return;
      }

      const [cidS, ufS] = saidaStr.split(/[\/-]/).map(s => s.trim());
      const pA = await buscarCoordenadas("", cidS || saidaStr, ufS || "Brasil");
      if (!pA) {
        alert("❌ Não foi possível obter coordenadas para a saída do técnico.");
        return;
      }

      const pontosLngLat = [[pA[1], pA[0]]];
      const chamadosRota = [];

      for (const codOS of destinosSelecionados) {
        const item = dfRaw.find(d => d.CodOS === codOS);
        if (item && item.pos) {
          pontosLngLat.push([item.pos[1], item.pos[0]]);
          chamadosRota.push(item);
        }
      }

      if (chamadosRota.length === 0) {
        alert("❌ Nenhum dos chamados selecionados possui coordenadas válidas.");
        return;
      }

      routesLayer.clearLayers();
      rotaPolylines = [];
      rotasCalculadas = [];

      // 1. PIN de Saída do Técnico (Ícone de Casa em formato de gota)
      const iconePinSaida = L.divIcon({
        className: '',
        html: `
          <div class="map-pin">
            <svg viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 32 12 32C12 32 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="#2E8B57" stroke="#1E1E1E" stroke-width="1.2"/>
              <circle cx="12" cy="12" r="8" fill="#ffffff"/>
              <text x="12" y="15" text-anchor="middle" font-size="10" font-family="Arial" font-weight="bold" fill="#2E8B57">🏠</text>
            </svg>
          </div>
        `,
        iconSize: [30, 40],
        iconAnchor: [15, 40],
        popupAnchor: [0, -36]
      });

      const markerSaida = L.marker(pA, { icon: iconePinSaida }).bindPopup(`<b>🏠 Saída do Técnico:</b><br>${saidaStr}`);
      markerSaida.on('mouseover', () => markerSaida.openPopup());
      markerSaida.on('mouseout', () => markerSaida.closePopup());
      markerSaida.addTo(routesLayer);

      // 2. PINs de Localização das Paradas (Ponto de localização vermelho/gota)
      chamadosRota.forEach((item, index) => {
        const iconePinDestino = L.divIcon({
          className: '',
          html: `
            <div class="map-pin">
              <svg viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 32 12 32C12 32 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="#FF4B4B" stroke="#1E1E1E" stroke-width="1.2"/>
                <circle cx="12" cy="12" r="5" fill="#ffffff"/>
                <circle cx="12" cy="12" r="2.5" fill="#FF4B4B"/>
              </svg>
            </div>
          `,
          iconSize: [28, 38],
          iconAnchor: [14, 38],
          popupAnchor: [0, -34]
        });

        const markerDest = L.marker(item.pos, { icon: iconePinDestino })
          .bindPopup(`<b>📍 Parada:</b> [${item.Cidade}/${item.SiglaUF}]<br><b>OS:</b> ${item.CodOS}<br><b>Cliente:</b> ${item.Cliente}`);
        
        markerDest.on('mouseover', () => markerDest.openPopup());
        markerDest.on('mouseout', () => markerDest.closePopup());
        markerDest.addTo(routesLayer);
      });

      // Cálculo das rotas pelas vias
      const rotas = await buscarRotasOSRM(pontosLngLat);
      const sidebarInfo = document.getElementById('sidebar-rota-info');
      sidebarInfo.style.display = 'block';

      let htmlSidebar = `<b>🗺️ Rota (${chamadosRota.length} Paradas)</b><br>🏠 <b>Saída:</b> ${saidaStr}<br>`;
      chamadosRota.forEach((c, idx) => {
        htmlSidebar += `📍 <b>${idx + 1}.</b> [${c.Cidade}/${c.SiglaUF}] OS: ${c.CodOS}<br>`;
      });
      htmlSidebar += `<hr style="margin:8px 0; border:0; border-top:1px solid #3e404f;"><div style="margin-bottom:6px; font-weight:600; color:#fafafa;">Selecione a rota desejada:</div>`;

      if (rotas && rotas.length > 0) {
        rotasCalculadas = rotas;

        rotas.slice().reverse().forEach(r => {
          const line = L.polyline(r.coords, {
            color: r.cor,
            weight: r.id === 0 ? 7 : 4,
            opacity: r.id === 0 ? 1.0 : 0.6,
            lineJoin: 'round'
          }).bindTooltip(`${r.nome}: ${r.distKm} km · ${r.durStr}`).addTo(routesLayer);

          line.on('click', () => selecionarRota(r.id));
          rotaPolylines.push({ id: r.id, line, corOriginal: r.cor });
        });

        rotas.forEach(r => {
          htmlSidebar += `
            <div class="rota-card-option ${r.id === 0 ? 'active' : ''}" data-id="${r.id}" onclick="selecionarRota(${r.id})">
              <div style="font-weight:bold; color:#fafafa; margin-bottom:2px;">${r.nome}</div>
              <div style="font-size:11px; color:#cbd5e1;">📍 <b>${r.distKm} km</b> &nbsp; ⏱️ <b>${r.durStr}</b></div>
            </div>
          `;
        });
      } else {
        const coordsLinha = [pA, ...chamadosRota.map(c => c.pos)];
        L.polyline(coordsLinha, { color: '#007BFF', weight: 4, dashArray: '8' }).addTo(routesLayer);
        htmlSidebar += `<div style="color:#FFA500; margin-top:4px;">⚠️ Rota aproximada (conexão com vias indisponível).</div>`;
      }

      sidebarInfo.innerHTML = htmlSidebar;

      const todasCoords = [pA, ...chamadosRota.map(c => c.pos)];
      map.fitBounds(todasCoords, { padding: [50, 50] });
    }

    /* =========================================================================
       10. EVENT LISTENERS
       ========================================================================= */
    document.getElementById('upload-card').addEventListener('click', () => {
      document.getElementById('file-input').click();
    });

    document.getElementById('file-input').addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        document.getElementById('upload-label').textContent = `Carregado: ${file.name}`;
        processarPlanilha(file);
      }
    });

    document.getElementById('toggle-btn').addEventListener('click', () => {
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.toggle('collapsed');
      const isCollapsed = sidebar.classList.contains('collapsed');
      document.getElementById('toggle-icon').innerHTML = isCollapsed
        ? '<polyline points="9 18 15 12 9 6"></polyline>'
        : '<polyline points="15 18 9 12 15 6"></polyline>';
      setTimeout(() => { map && map.invalidateSize(); }, 350);
    });

    // Expander Filtros
    document.getElementById('expander-filtros-toggle').addEventListener('click', () => {
      document.getElementById('filtros-container').classList.toggle('open');
    });

    // Expander Chamados
    document.getElementById('expander-chamados-toggle').addEventListener('click', () => {
      document.getElementById('container-lista').classList.toggle('open');
    });

    document.getElementById('btn-aplicar-filtros').addEventListener('click', aplicarFiltros);
    document.getElementById('filtro-regiao').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-intervencao').addEventListener('change', aplicarFiltros);
    document.getElementById('filtro-cliente').addEventListener('change', aplicarFiltros);

    document.getElementById('btn-limpar-filtros').addEventListener('click', () => {
      document.getElementById('filtro-intervencao').value = 'Todos';
      document.getElementById('filtro-cliente').value = 'Todos';
      document.getElementById('filtro-regiao').value = 'Todos';
      aplicarFiltros();
    });

    document.getElementById('busca-chamado').addEventListener('input', () => {
      const container = document.getElementById('container-lista');
      if (!container.classList.contains('open')) {
        container.classList.add('open');
      }
      renderizarListaChamados(dfFinal);
    });

    // Multi-Select Toggle
    const multiBtn = document.getElementById('multiselect-btn');
    const multiList = document.getElementById('multiselect-list');

    multiBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      multiList.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!document.getElementById('multiselect-dropdown').contains(e.target)) {
        multiList.classList.remove('open');
      }
    });

    // Controle de Abas
    document.getElementById('tab-geral').addEventListener('click', () => {
      abaAtiva = "geral";
      document.getElementById('tab-geral').classList.add('active');
      document.getElementById('tab-rotas').classList.remove('active');
      document.getElementById('rota-toolbar').style.display = 'none';
      routesLayer.clearLayers();
      document.getElementById('sidebar-rota-info').style.display = 'none';
      aplicarFiltros();
    });

    document.getElementById('tab-rotas').addEventListener('click', () => {
      abaAtiva = "rotas";
      document.getElementById('tab-rotas').classList.add('active');
      document.getElementById('tab-geral').classList.remove('active');
      document.getElementById('rota-toolbar').style.display = 'flex';
      setTimeout(() => { map && map.invalidateSize(); }, 200);
      aplicarFiltros();
    });

    document.getElementById('btn-calc-rota').addEventListener('click', calcularRota);
  </script>
</body>
</html>