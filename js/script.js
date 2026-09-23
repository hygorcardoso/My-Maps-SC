/* =========================================================================
   MY MAPS BR - SCRIPT PRINCIPAL OTIMIZADO (v0.9.3)
   ========================================================================= */

let TEMPO_MEDIO_ATENDIMENTO_MIN = 45; 
let LIMITE_DIARIO_MINUTOS = 300; 
let temaAppAtual = "escuro";          
let sincronizarComMapa = true;         
let modoPesquisa = "rapida";          

const CENTROIDES_ESTADOS_BR = {
  "AC": [-8.77, -70.55], "AL": [-9.71, -35.73], "AM": [-3.07, -61.66],
  "AP": [1.41, -51.77],  "BA": [-12.96, -38.51], "CE": [-3.71, -38.54],
  "DF": [-15.78, -47.93], "ES": [-19.19, -40.34], "GO": [-16.64, -49.31],
  "MA": [-2.55, -44.30], "MG": [-18.10, -44.38], "MS": [-20.51, -54.54],
  "MT": [-12.64, -55.42], "PA": [-5.53, -52.29], "PB": [-7.06, -35.55],
  "PE": [-8.28, -35.07], "PI": [-8.28, -43.68], "PR": [-24.89, -51.55],
  "RJ": [-22.84, -43.15], "RN": [-5.22, -36.52], "RO": [-11.22, -62.80],
  "RR": [1.89, -61.22],  "RS": [-30.01, -51.22], "SC": [-27.33, -49.44],
  "SE": [-10.90, -37.07], "SP": [-23.55, -46.64], "TO": [-10.25, -48.25]
};

const BASE_CIDADES_BRASIL = {
  "PIRATUBA-SC": [-27.4209, -51.7725], "SAO JOSE-SC": [-27.6146, -48.6353],
  "CONCORDIA-SC": [-27.2342, -52.0286], "CHAPECO-SC": [-27.1004, -52.6152],
  "VIDEIRA-SC": [-27.0084, -51.1528], "JOACABA-SC": [-27.1751, -51.5042],
  "HERVAL D OESTE-SC": [-27.1828, -51.4967], "CACADOR-SC": [-26.7753, -51.0125],
  "ZORTEA-SC": [-27.4514, -51.5542], "CAMPOS NOVOS-SC": [-27.4019, -51.2253],
  "CAPINZAL-SC": [-27.3481, -51.6119], "LUZERNA-SC": [-27.1304, -51.4682],
  "SEARA-SC": [-27.1481, -52.3117], "XANXERE-SC": [-26.8747, -52.4036],
  "FLORIANOPOLIS-SC": [-27.5954, -48.5480], "JOINVILLE-SC": [-26.3045, -48.8487],
  "BLUMENAU-SC": [-26.9194, -49.0661], "ITAJAI-SC": [-26.9078, -48.6619],
  "CRICIUMA-SC": [-28.6775, -49.3704], "LAGES-SC": [-27.8161, -50.3260],
  "NAVEGANTES-SC": [-26.8914, -48.6548], "BALNEARIO CAMBORIU-SC": [-26.9928, -48.6350],
  "TUBARAO-SC": [-28.4735, -49.0074], "ARARANGUA-SC": [-28.9356, -49.4850],
  "SAO CRISTOVAO DO SUL-SC": [-27.2666, -50.4388], "PORTO BELO-SC": [-27.1578, -48.5528],
  "CAMBORIU-SC": [-27.0250, -48.6539], "POMERODE-SC": [-26.7408, -49.1769],
  "XAXIM-SC": [-26.9617, -52.5347], "GARUVA-SC": [-26.0269, -48.8550],
  "SAO JOAO BATISTA-SC": [-27.2758, -48.8489], "TAIO-SC": [-27.1164, -49.9981],
  "AGRONOMICA-SC": [-27.2650, -49.7108], "BENEDITO NOVO-SC": [-26.8000, -49.4170],
  "SAO JOAO DO SUL-SC": [-29.2238, -49.8110], "SAO PAULO-SP": [-23.5505, -46.6333],
  "SAO JOSE DOS CAMPOS-SP": [-23.1791, -45.8872], "CAMPINAS-SP": [-22.9099, -47.0626],
  "RIO DE JANEIRO-RJ": [-22.9068, -43.1729], "BELO HORIZONTE-MG": [-19.9167, -43.9345],
  "CURITIBA-PR": [-25.4284, -49.2733], "PORTO ALEGRE-RS": [-30.0346, -51.2177]
};

const CORES_INTERVENCAO = {
  "Alteração de engenharia": "#4B0082", "Autorização de deslocamento": "#4682B4",
  "Cofre": "#708090", "Corretiva": "#FF4B4B", "Corretiva POS reincidentes": "#B22222",
  "Desinstalação": "#FF8C00", "Helpdesk": "#008B8B", "Inspeção técnica": "#9ACD32",
  "Instalação": "#2E8B57", "Laudo técnico": "#8B008B", "Manutenção gerencial": "#5F9EA0",
  "Orçamento": "#FFD700", "Orçamento aprovado": "#32CD32", "Orçamento pendente da filial detalhar motivo": "#FFA500",
  "Orçamento pendente de aprovação do cliente": "#DAA520", "Orçamento reprovado": "#8B0000",
  "Preventiva": "#007BFF", "Preventiva gerencial": "#1E90FF", "Reinstalação": "#20B2AA",
  "Treinamento": "#9370DB", "Troca de Veloh C": "#8B4513", "Não Informado": "#464855"
};

const CORES_DIAS = ["#007BFF", "#10B981", "#8B5CF6", "#F59E0B", "#06B6D4", "#EC4899", "#6366F1"];

let dfRaw = [];
let dfFinal = [];
let chamadosMap = new Map();
let markersLayer = L.layerGroup();
let routesLayer = L.layerGroup();
let map = null;
let osmTileLayer = null;
let chamadoSelecionado = null;
let marcadoresPorOS = {};
let destinosSelecionados = new Set();
let marcadorAbertoPorClique = null;
let rotasPorDia = [];
let rotaPolylinesPorDia = [];
let buscaDebounceTimer = null;

/* =========================================================================
   INICIALIZAÇÃO DO MAPA COM ZOOM SUAVE E ANTI-TRAVADAS
   ========================================================================= */
function initMap() {
  if (!map) {
    map = L.map('map', {
      zoomControl: true,
      preferCanvas: true,
      fadeAnimation: true,
      zoomAnimation: true,
      inertia: true,
      worldCopyJump: false,
      scrollWheelZoom: false, // Controle manual anti-sensibilidade excessiva
      zoomSnap: 1,
      zoomDelta: 1
    }).setView([-14.2350, -51.9253], 4);

    let ultimaRolleada = 0;
    map.getContainer().addEventListener('wheel', (e) => {
      e.preventDefault();
      const agora = Date.now();
      if (agora - ultimaRolleada < 180) return; // Trava anti-disparo rápido
      ultimaRolleada = agora;

      if (e.deltaY < 0) {
        map.setZoom(map.getZoom() + 1, { animate: true });
      } else {
        map.setZoom(map.getZoom() - 1, { animate: true });
      }
    }, { passive: false });

    osmTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      minZoom: 3,
      noWrap: true,
      keepBuffer: 12,
      updateWhenZooming: false,
      updateWhenIdle: true,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    markersLayer.addTo(map);
    routesLayer.addTo(map);
    atualizarVisualTema();

    map.on('click', () => { marcadorAbertoPorClique = null; });
  }
}

function atualizarVisualTema() {
  const body = document.body;
  const btnClaro = document.getElementById('btn-tema-claro');
  const btnEscuro = document.getElementById('btn-tema-escuro');
  const tilePane = document.querySelector('.leaflet-tile-pane');

  if (temaAppAtual === 'claro') {
    body.classList.add('theme-light');
    if(btnClaro) btnClaro.classList.add('active');
    if(btnEscuro) btnEscuro.classList.remove('active');
  } else {
    body.classList.remove('theme-light');
    if(btnEscuro) btnEscuro.classList.add('active');
    if(btnClaro) btnClaro.classList.remove('active');
  }

  if (tilePane) {
    if (sincronizarComMapa && temaAppAtual === 'escuro') {
      tilePane.classList.add('map-dark-mode');
    } else {
      tilePane.classList.remove('map-dark-mode');
    }
  }
}

/* =========================================================================
   PROCESSAMENTO DE DADOS & GEOCODIFICAÇÃO
   ========================================================================= */
function normalizar(str) {
  return (str || "").toString()
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]/g, " ").toUpperCase().trim();
}

function coordenadaValidaBrasil(lat, lng) {
  if (lat == null || lng == null) return false;
  const nLat = parseFloat(lat), nLng = parseFloat(lng);
  return !isNaN(nLat) && !isNaN(nLng) && nLat <= 6.0 && nLat >= -34.5 && nLng >= -74.5 && nLng <= -32.0;
}

function extrairSiglaUFValida(textoUF, textoCidade = "") {
  const ufsValidas = Object.keys(CENTROIDES_ESTADOS_BR);
  const ufNorm = normalizar(textoUF).replace(/\s+/g, '');
  if (ufsValidas.includes(ufNorm)) return ufNorm;

  const cidNorm = normalizar(textoCidade);
  for (const uf of ufsValidas) {
    if (cidNorm.endsWith(` ${uf}`) || cidNorm.endsWith(`/${uf}`) || cidNorm.endsWith(`-${uf}`)) return uf;
  }
  return "SC";
}

function resolverCoordenadaCidadeEstrita(cidade, uf) {
  const cidNorm = normalizar(cidade).replace(/\s+/g, ' ');
  const siglaUF = extrairSiglaUFValida(uf, cidade);
  const chaveCompleta = `${cidNorm}-${siglaUF}`;

  if (BASE_CIDADES_BRASIL[chaveCompleta]) return BASE_CIDADES_BRASIL[chaveCompleta];

  for (const [k, v] of Object.entries(BASE_CIDADES_BRASIL)) {
    if (k.endsWith(`-${siglaUF}`) && k.replace(`-${siglaUF}`, '') === cidNorm) return v;
  }
  return CENTROIDES_ESTADOS_BR[siglaUF] || [-27.33, -49.44];
}

function resolverCoordenadaRapida(cidade, uf, index = 0) {
  const baseCoord = resolverCoordenadaCidadeEstrita(cidade, uf);
  const angulo = index * 2.3999;
  const raioOffset = (index % 8) * 0.0035;
  return [baseCoord[0] + Math.sin(angulo) * raioOffset, baseCoord[1] + Math.cos(angulo) * raioOffset];
}

const esperar = ms => new Promise(resolve => setTimeout(resolve, ms));

function mapearColuna(colunas, alvos) {
  const alvosNorm = alvos.map(normalizar);
  for (const alvo of alvosNorm) {
    for (const col of colunas) { if (normalizar(col) === alvo) return col; }
  }
  for (const alvo of alvosNorm) {
    const alvoSemEspaco = alvo.replace(/\s+/g, '');
    for (const col of colunas) {
      if (normalizar(col).replace(/\s+/g, '') === alvoSemEspaco) return col;
    }
  }
  return null;
}

function formatarValorSLA(val) {
  if (!val) return "";
  if (typeof val === "number") {
    const dataJs = new Date(Math.round((val - 25569) * 86400 * 1000));
    if (!isNaN(dataJs.getTime())) {
      return dataJs.toLocaleDateString("pt-BR") + " " + dataJs.toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit' });
    }
  }
  return String(val).trim();
}

async function processarPlanilha(file) {
  const data = await file.arrayBuffer();
  const workbook = XLSX.read(data, { type: 'array', cellDates: true });

  const mapaSlaChamados = new Map();
  const sheetChamadosName = workbook.SheetNames.find(s => normalizar(s).includes("CHAMADOS"));
  if (sheetChamadosName) {
    const sheetCh = workbook.Sheets[sheetChamadosName];
    const rawRowsCh = XLSX.utils.sheet_to_json(sheetCh, { header: 1, defval: "" });
    if (rawRowsCh.length > 0) {
      let headerIdxCh = 0, cChamadoCh = null, cLimiteCh = null;
      for (let r = 0; r < Math.min(rawRowsCh.length, 15); r++) {
        const linha = (rawRowsCh[r] || []).map(cell => String(cell || "").trim());
        cChamadoCh = mapearColuna(linha, ["Chamado", "CodOS", "NumOS", "OS"]);
        cLimiteCh = mapearColuna(linha, ["LimiteAtendimento", "SLA", "Prazo"]);
        if (cChamadoCh && cLimiteCh) { headerIdxCh = r; break; }
      }
      if (cChamadoCh && cLimiteCh) {
        const jsonRowsCh = XLSX.utils.sheet_to_json(sheetCh, { range: headerIdxCh, defval: "", raw: false });
        jsonRowsCh.forEach(row => {
          const osId = String(row[cChamadoCh] || "").split('.')[0].trim();
          if (osId && row[cLimiteCh]) mapaSlaChamados.set(osId, formatarValorSLA(row[cLimiteCh]));
        });
      }
    }
  }

  let targetSheet = workbook.SheetNames[0];
  for (const prioridade of ["unificado", "ordem_servico", "chamados", "atendimentos"]) {
    const found = workbook.SheetNames.find(s => normalizar(s).includes(normalizar(prioridade)));
    if (found) { targetSheet = found; break; }
  }

  const sheet = workbook.Sheets[targetSheet];
  const rawRows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });
  if (rawRows.length === 0) { alert("Aba vazia ou inválida."); return; }

  let headerRowIndex = 0, colunas = [], cOS = null, cRegiao = null, cCliente = null, cLocal = null, cEndereco = null, cBairro = null, cCidade = null, cUF = null;

  for (let r = 0; r < Math.min(rawRows.length, 15); r++) {
    const linha = (rawRows[r] || []).map(cell => String(cell || "").trim());
    cOS = mapearColuna(linha, ["CodOS", "NumOS", "Chamado", "OS"]);
    cCidade = mapearColuna(linha, ["Cidade", "Municipio"]);
    cEndereco = mapearColuna(linha, ["Endereco", "Logradouro", "Rua"]);
    if (cOS && (cCidade || cEndereco)) {
      headerRowIndex = r;
      colunas = linha;
      cRegiao = mapearColuna(linha, ["Regiao", "Regional"]);
      cCliente = mapearColuna(linha, ["Cliente", "RazaoSocial"]);
      cLocal = mapearColuna(linha, ["LocalAtendimento", "Local"]);
      cBairro = mapearColuna(linha, ["Bairro"]);
      cUF = mapearColuna(linha, ["SiglaUF", "UF"]);
      break;
    }
  }

  const jsonRows = XLSX.utils.sheet_to_json(sheet, { range: headerRowIndex, defval: "", raw: false });
  const cInterv = mapearColuna(colunas, ["Intervencao", "Tipo", "Servico"]);

  const vistos = new Set();
  dfRaw = [];
  chamadosMap.clear();

  for (let i = 0; i < jsonRows.length; i++) {
    const row = jsonRows[i];
    const codOS = String(row[cOS] || "").split('.')[0].trim();
    if (!codOS || vistos.has(codOS)) continue;
    vistos.add(codOS);

    const ruaPura = cEndereco && row[cEndereco] ? String(row[cEndereco]).trim() : "";
    const bairroPuro = cBairro && row[cBairro] ? String(row[cBairro]).trim() : "";
    const cidVal = cCidade && row[cCidade] ? String(row[cCidade]).trim() : "";
    const rawUF = cUF && row[cUF] ? String(row[cUF]).trim() : "";
    const ufVal = extrairSiglaUFValida(rawUF, cidVal);
    const localNome = cLocal && row[cLocal] ? String(row[cLocal]).trim() : `${cidVal} (OS ${codOS})`;
    const regiaoVal = cRegiao && row[cRegiao] ? String(row[cRegiao]).trim() : "Não Informado";
    const clienteVal = cCliente && row[cCliente] ? String(row[cCliente]).trim() : "Não Informado";

    let slaFinal = mapaSlaChamados.get(codOS) || (cSlaUnificado && row[cSlaUnificado] ? formatarValorSLA(row[cSlaUnificado]) : "");

    const partesEndereco = [];
    if (ruaPura && !['nan', 'null', 'undefined'].includes(ruaPura.toLowerCase())) partesEndereco.push(ruaPura);
    if (bairroPuro && !['nan', 'null', 'undefined', 'centro'].includes(bairroPuro.toLowerCase())) partesEndereco.push(bairroPuro);
    if (cidVal) partesEndereco.push(ufVal ? `${cidVal} - ${ufVal}` : cidVal);
    const enderecoCompleto = partesEndereco.join(", ") || `${cidVal} - ${ufVal}`;

    const item = {
      CodOS: codOS, Cidade: cidVal, SiglaUF: ufVal, Rua: ruaPura, Bairro: bairroPuro,
      Endereco: ruaPura || enderecoCompleto, EnderecoCompleto: enderecoCompleto,
      LocalAtendimento: localNome, Intervencao: cInterv && row[cInterv] ? String(row[cInterv]).trim() : "Não Informado",
      Cliente: clienteVal, Regiao: regiaoVal, SLA: slaFinal, pos: resolverCoordenadaRapida(cidVal, ufVal, i), precisao: 'cidade'
    };

    dfRaw.push(item);
    chamadosMap.set(codOS, item);
  }

  initMap();
  concluirRenderizacaoPosGeocodificacao();
}

function concluirRenderizacaoPosGeocodificacao() {
  document.getElementById('btn-remover-arquivo').style.display = 'inline-flex';
  document.getElementById('filtros-container').style.display = 'flex';
  document.getElementById('container-lista').style.display = 'flex';
  document.getElementById('tabs-bar').style.display = 'flex';
  document.getElementById('legenda-dinamica').style.display = 'flex';

  dfFinal = [...dfRaw];
  popularFiltros(dfFinal);
  if (map) map.invalidateSize();

  renderizarMarcadores(dfFinal, true);
  renderizarLegendaDinamica(dfFinal);
  renderizarListaChamados(dfFinal);
  popularMultiSelectDestinos(dfFinal);
}

function removerPlanilhaAtual() {
  dfRaw = []; dfFinal = []; chamadosMap.clear(); destinosSelecionados.clear();
  rotasPorDia = []; rotaPolylinesPorDia = []; chamadoSelecionado = null; marcadorAbertoPorClique = null;

  if (markersLayer) markersLayer.clearLayers();
  if (routesLayer) routesLayer.clearLayers();
  if (map) map.setView([-14.2350, -51.9253], 4);

  document.getElementById('file-input').value = '';
  document.getElementById('upload-label').textContent = '200MB per file • XLSX';
  document.getElementById('upload-label').style.color = 'var(--text-muted)';
  document.getElementById('btn-remover-arquivo').style.display = 'none';
  document.getElementById('progress-box').style.display = 'none';
  document.getElementById('map-loading-overlay').style.display = 'none';
  document.getElementById('filtros-container').style.display = 'none';
  document.getElementById('container-lista').style.display = 'none';
  document.getElementById('tabs-bar').style.display = 'none';
  document.getElementById('legenda-dinamica').style.display = 'none';
  document.getElementById('rota-toolbar').style.display = 'none';
  document.getElementById('sidebar-rota-info').style.display = 'none';

  document.getElementById('tab-geral').classList.add('active');
  document.getElementById('tab-rotas').classList.remove('active');
}

/* =========================================================================
   RENDERIZAÇÃO DE MAPA E LISTAS COM DOCUMENT FRAGMENT (ALTA PERFORMANCE)
   ========================================================================= */
function obterCorPrioritaria(listaIntervencoes) {
  const contagem = {};
  for (const interv of listaIntervencoes) { contagem[interv] = (contagem[interv] || 0) + 1; }
  let tipoPrioritario = "Não Informado", maiorContagem = -1;
  for (const [interv, qtd] of Object.entries(contagem)) {
    if (qtd > maiorContagem) { maiorContagem = qtd; tipoPrioritario = interv; }
  }
  return CORES_INTERVENCAO[tipoPrioritario] || CORES_INTERVENCAO["Não Informado"];
}

function renderizarMarcadores(dados, ajustarZoom = false) {
  if (!map) initMap();
  markersLayer.clearLayers();
  marcadoresPorOS = {};
  if (!dados || dados.length === 0) return;

  const grupos = {};
  for (let i = 0; i < dados.length; i++) {
    const item = dados[i];
    if (!item.pos) continue;
    const key = `${item.pos[0].toFixed(4)},${item.pos[1].toFixed(4)}`;
    if (!grupos[key]) grupos[key] = [];
    grupos[key].push(item);
  }

  const bounds = [];
  Object.values(grupos).forEach(grupo => {
    const primeiro = grupo[0];
    bounds.push(primeiro.pos);

    const total = grupo.length;
    const cor = obterCorPrioritaria(grupo.map(g => g.Intervencao));
    const raio = Math.min(9 + (total * 0.2), 28);
    const diam = Math.round(raio * 2);

    const customIcon = L.divIcon({
      className: 'custom-cluster-icon',
      html: `<div style="background-color:${cor}; width:${diam}px; height:${diam}px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:11px;">${total}</div>`,
      iconSize: [diam, diam], iconAnchor: [raio, raio]
    });

    let htmlPopup = `<div style="font-family: Arial, sans-serif; min-width: 230px;">
      <b style="color:#FF4B4B; font-size:13px;">🏢 ${primeiro.LocalAtendimento}</b><br>
      <small>📍 ${primeiro.EnderecoCompleto}</small><hr style="margin:6px 0;">`;

    grupo.forEach((ch, j) => {
      htmlPopup += `<b>OS:</b> ${ch.CodOS} | <b>Cliente:</b> ${ch.Cliente}<br><b>Intervenção:</b> ${ch.Intervencao}<br>`;
      if (ch.SLA && !["S/N", "NAN"].includes(ch.SLA.toUpperCase())) htmlPopup += `<b>SLA:</b> ${ch.SLA}<br>`;
      if (j < grupo.length - 1) htmlPopup += `<hr style="margin:4px 0; border-top:1px dashed var(--border-light);">`;
    });
    htmlPopup += `</div>`;

    const marker = L.marker(primeiro.pos, { icon: customIcon });
    marker.bindPopup(htmlPopup, { autoClose: false, closeOnClick: false });
    grupo.forEach(ch => { marcadoresPorOS[ch.CodOS] = marker; });

    marker.on('mouseover', () => marker.openPopup());
    marker.on('mouseout', () => { if (marcadorAbertoPorClique !== marker) marker.closePopup(); });
    marker.on('click', () => {
      marcadorAbertoPorClique = marker;
      map.setView(primeiro.pos, 16, { animate: true, duration: 0.35 });
      marker.openPopup();
      chamadoSelecionado = primeiro.CodOS;
      document.getElementById('container-lista').classList.add('open');
      renderizarListaChamados(dfFinal);
    });

    markersLayer.addLayer(marker);
  });

  if (bounds.length > 0 && ajustarZoom) {
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 8 });
  }
}

function popularFiltros(dados) {
  const preencherSelect = (id, valores) => {
    const select = document.getElementById(id);
    const atual = select.value;
    select.innerHTML = '<option value="Todos">Todos</option>';
    valores.forEach(v => {
      if (!v) return;
      const opt = document.createElement('option');
      opt.value = v; opt.textContent = v; select.appendChild(opt);
    });
    if (valores.includes(atual)) select.value = atual;
  };

  preencherSelect('filtro-intervencao', [...new Set(dados.map(d => d.Intervencao))].sort());
  preencherSelect('filtro-cliente', [...new Set(dados.map(d => d.Cliente))].sort());
  preencherSelect('filtro-regiao', [...new Set(dados.map(d => d.Regiao))].sort());

  const estados = [...new Set(dados.map(d => d.SiglaUF))].sort();
  const boxEstado = document.getElementById('box-filtro-estado');
  if (estados.length > 1) {
    preencherSelect('filtro-estado', estados);
    boxEstado.style.display = 'block';
  } else {
    boxEstado.style.display = 'none';
    document.getElementById('filtro-estado').value = 'Todos';
  }
}

function renderizarLegendaDinamica(dadosFiltrados) {
  const legContainer = document.getElementById('legenda-dinamica');
  const ativas = new Set(dadosFiltrados.map(d => d.Intervencao));
  legContainer.innerHTML = '';
  for (const [tipo, cor] of Object.entries(CORES_INTERVENCAO)) {
    if (ativas.has(tipo) && tipo !== "Não Informado") {
      const div = document.createElement('div');
      div.className = 'legenda-item';
      div.innerHTML = `<div class="legenda-cor" style="background-color:${cor};"></div><span>${tipo}</span>`;
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
  const filtrados = busca ? dados.filter(d => d.CodOS.toLowerCase().includes(busca) || d.Cidade.toLowerCase().includes(busca) || d.LocalAtendimento.toLowerCase().includes(busca)) : dados;
  filtrados.sort((a, b) => (a.Cidade + a.CodOS).localeCompare(b.Cidade + b.CodOS));

  const fragment = document.createDocumentFragment();
  for (let i = 0; i < filtrados.length; i++) {
    const ch = filtrados[i];
    const btn = document.createElement('button');
    btn.className = `chamado-item-btn ${chamadoSelecionado === ch.CodOS ? 'selected' : ''}`;
    btn.style.borderLeftColor = CORES_INTERVENCAO[ch.Intervencao] || '#464855';
    btn.textContent = `${chamadoSelecionado === ch.CodOS ? '🔷' : '🔵'} [${ch.Cidade}/${ch.SiglaUF}] OS: ${ch.CodOS} - ${ch.LocalAtendimento}`;
    btn.addEventListener('click', () => {
      chamadoSelecionado = ch.CodOS;
      renderizarListaChamados(dfFinal);
      if (ch.pos) {
        map.setView(ch.pos, 16, { animate: true, duration: 0.35 });
        const marker = marcadoresPorOS[ch.CodOS];
        if (marker) { marcadorAbertoPorClique = marker; marker.openPopup(); }
      }
    });
    fragment.appendChild(btn);
  }
  lista.appendChild(fragment);
}

function aplicarFiltros(ajustarZoom = false) {
  const fInterv = document.getElementById('filtro-intervencao').value;
  const fClie = document.getElementById('filtro-cliente').value;
  const fReg = document.getElementById('filtro-regiao').value;
  const fEst = document.getElementById('filtro-estado').value;

  dfFinal = dfRaw.filter(d => {
    if (fInterv !== "Todos" && d.Intervencao !== fInterv) return false;
    if (fClie !== "Todos" && d.Cliente !== fClie) return false;
    if (fReg !== "Todos" && d.Regiao !== fReg) return false;
    if (fEst !== "Todos" && d.SiglaUF !== fEst) return false;
    return true;
  });

  renderizarMarcadores(dfFinal, ajustarZoom);
  renderizarLegendaDinamica(dfFinal);
  renderizarListaChamados(dfFinal);
  popularMultiSelectDestinos(dfFinal);
}

function popularMultiSelectDestinos(dados) {
  const container = document.getElementById('multiselect-list');
  container.innerHTML = '';
  const fragment = document.createDocumentFragment();
  const destinosValidos = new Set();

  if (dados.length === 0) {
    container.innerHTML = '<div style="font-size:11px; color:var(--text-muted); padding:6px;">Nenhum chamado disponível.</div>';
  } else {
    dados.forEach(d => {
      destinosValidos.add(d.CodOS);
      const item = document.createElement('div');
      item.className = 'multiselect-item';
      const cb = document.createElement('input');
      cb.type = 'checkbox'; cb.value = d.CodOS; cb.checked = destinosSelecionados.has(d.CodOS);
      cb.addEventListener('change', (e) => {
        if (e.target.checked) destinosSelecionados.add(d.CodOS);
        else destinosSelecionados.delete(d.CodOS);
        atualizarTextoBotaoMultiSelect();
      });
      const span = document.createElement('span');
      span.textContent = `[${d.Cidade}/${d.SiglaUF}] OS: ${d.CodOS} - ${d.LocalAtendimento}`;
      item.appendChild(cb); item.appendChild(span);
      item.addEventListener('click', (e) => { if (e.target !== cb) { cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); } });
      fragment.appendChild(item);
    });
    container.appendChild(fragment);
  }

  destinosSelecionados.forEach(sel => { if (!destinosValidos.has(sel)) destinosSelecionados.delete(sel); });
  atualizarTextoBotaoMultiSelect();
}

function atualizarTextoBotaoMultiSelect() {
  const btnText = document.getElementById('multiselect-btn-text');
  const count = destinosSelecionados.size;
  btnText.textContent = count === 0 ? "🏁 Selecionar Destinos (0)" : `🏁 ${count} chamado(s) selecionado(s)`;
}

/* =========================================================================
   ROTEAMENTO E CONFIGURAÇÕES
   ========================================================================= */
async function calcularRotasDiariasHoras() {
  const saidaStr = document.getElementById('rota-saida').value.trim();
  if (!saidaStr) { alert("❌ Informe a cidade de saída do técnico."); return; }

  if (destinosSelecionados.size === 0) {
    dfFinal.forEach(d => destinosSelecionados.add(d.CodOS));
    popularMultiSelectDestinos(dfFinal);
  }

  const [cidS, ufS] = saidaStr.split(/[\/-]/).map(s => s.trim());
  const pA = resolverCoordenadaRapida(cidS || saidaStr, ufS || "SC", 0);
  let chamadosParaAtender = [];
  destinosSelecionados.forEach(codOS => { const item = chamadosMap.get(codOS); if (item?.pos) chamadosParaAtender.push(item); });

  if (chamadosParaAtender.length === 0) { alert("❌ Nenhum destino válido."); return; }
  
  const diasCalculados = [{ diaNum: 1, cor: CORES_DIAS[0], paradas: chamadosParaAtender, duracaoTransitoMin: 60, distanciaTotalKm: 45 }];
  await desenharRotasPorDias(pA, diasCalculados);
}

async function desenharRotasPorDias(pontoSaida, diasCalculados) {
  routesLayer.clearLayers();
  const boundsTodasRotas = [pontoSaida];

  for (const dia of diasCalculados) {
    dia.paradas.forEach((item, pIdx) => {
      boundsTodasRotas.push(item.pos);
      const iconePin = L.divIcon({
        className: '',
        html: `<div class="map-pin"><svg viewBox="0 0 24 32" fill="none"><path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 32 12 32C12 32 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="${dia.cor}" stroke="#1E1E1E" stroke-width="1.2"/><circle cx="12" cy="12" r="7.5" fill="#ffffff"/><text x="12" y="15" text-anchor="middle" font-size="8.5" font-family="Arial" font-weight="bold" fill="${dia.cor}">D${dia.diaNum}-${pIdx + 1}</text></svg></div>`,
        iconSize: [34, 42], iconAnchor: [17, 42], popupAnchor: [0, -38]
      });
      L.marker(item.pos, { icon: iconePin }).bindPopup(`<b>Parada ${pIdx + 1}</b><br>${item.LocalAtendimento}`).addTo(routesLayer);
    });
  }
  map.fitBounds(boundsTodasRotas, { padding: [50, 50] });
}

/* =========================================================================
   EVENT LISTENERS GERAIS
   ========================================================================= */
const modalSettings = document.getElementById('modal-settings');
document.getElementById('btn-abrir-settings').addEventListener('click', () => modalSettings.classList.add('open'));
document.getElementById('btn-fechar-settings').addEventListener('click', () => modalSettings.classList.remove('open'));

document.getElementById('upload-card').addEventListener('click', (e) => {
  if (!document.getElementById('btn-remover-arquivo').contains(e.target)) document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    document.getElementById('upload-label').textContent = `Carregado: ${file.name}`;
    document.getElementById('upload-label').style.color = '#00c853';
    processarPlanilha(file);
  }
});

document.getElementById('btn-remover-arquivo').addEventListener('click', (e) => { e.stopPropagation(); removerPlanilhaAtual(); });
document.getElementById('app-title-container').addEventListener('click', () => document.getElementById('sidebar').classList.toggle('collapsed'));
document.getElementById('expander-filtros-toggle').addEventListener('click', () => document.getElementById('filtros-container').classList.toggle('open'));
document.getElementById('expander-chamados-toggle').addEventListener('click', () => document.getElementById('container-lista').classList.toggle('open'));

document.getElementById('btn-aplicar-filtros').addEventListener('click', () => aplicarFiltros(true));
['filtro-regiao', 'filtro-estado', 'filtro-intervencao', 'filtro-cliente'].forEach(id => {
  document.getElementById(id).addEventListener('change', () => aplicarFiltros(true));
});

document.getElementById('btn-limpar-filtros').addEventListener('click', () => {
  ['filtro-intervencao', 'filtro-cliente', 'filtro-regiao', 'filtro-estado'].forEach(id => document.getElementById(id).value = 'Todos');
  aplicarFiltros(true);
});

document.getElementById('busca-chamado').addEventListener('input', () => {
  clearTimeout(buscaDebounceTimer);
  buscaDebounceTimer = setTimeout(() => {
    document.getElementById('container-lista').classList.add('open');
    renderizarListaChamados(dfFinal);
  }, 150);
});

const multiBtn = document.getElementById('multiselect-btn');
const multiList = document.getElementById('multiselect-list');
multiBtn.addEventListener('click', (e) => { e.stopPropagation(); multiList.classList.toggle('open'); });
document.addEventListener('click', (e) => { if (!document.getElementById('multiselect-dropdown').contains(e.target)) multiList.classList.remove('open'); });

document.getElementById('tab-geral').addEventListener('click', () => {
  abaAtiva = "geral";
  document.getElementById('tab-geral').classList.add('active');
  document.getElementById('tab-rotas').classList.remove('active');
  document.getElementById('rota-toolbar').style.display = 'none';
  document.getElementById('btn-sugerir-rotas-sidebar').style.display = 'none';
  routesLayer.clearLayers();
  document.getElementById('sidebar-rota-info').style.display = 'none';
  renderizarMarcadores(dfFinal, false);
});

document.getElementById('tab-rotas').addEventListener('click', () => {
  abaAtiva = "rotas";
  document.getElementById('tab-rotas').classList.add('active');
  document.getElementById('tab-geral').classList.remove('active');
  document.getElementById('rota-toolbar').style.display = 'flex';
  if (dfRaw.length > 0) document.getElementById('btn-sugerir-rotas-sidebar').style.display = 'flex';
  setTimeout(() => { if (map) map.invalidateSize(); }, 100);
});

document.getElementById('btn-calc-rota').addEventListener('click', calcularRotasDiariasHoras);
document.getElementById('btn-sugerir-rotas-sidebar').addEventListener('click', calcularRotasDiariasHoras);

// Inicialização do Mapa
initMap();