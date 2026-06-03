"""
buscar_cidades_estado.py
------------------------
Busca todas as cidades de um estado brasileiro com suas coordenadas
usando o Photon (mesmo geocodificador do my_maps.py) e adiciona ao
arquivo cidades.json.

Uso:
    python buscar_cidades_estado.py SC
    python buscar_cidades_estado.py PR
    python buscar_cidades_estado.py RS
"""

import json
import sys
import ssl
import time
import unicodedata
import urllib.request
import urllib.parse
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl._create_unverified_context()

# ── Mapeamento sigla → (código IBGE, nome do estado) ─────────────────────────
ESTADOS = {
    "AC": (12, "Acre"),               "AL": (27, "Alagoas"),
    "AM": (13, "Amazonas"),           "AP": (16, "Amapá"),
    "BA": (29, "Bahia"),              "CE": (23, "Ceará"),
    "DF": (53, "Distrito Federal"),   "ES": (32, "Espírito Santo"),
    "GO": (52, "Goiás"),              "MA": (21, "Maranhão"),
    "MG": (31, "Minas Gerais"),       "MS": (50, "Mato Grosso do Sul"),
    "MT": (51, "Mato Grosso"),        "PA": (15, "Pará"),
    "PB": (25, "Paraíba"),            "PE": (26, "Pernambuco"),
    "PI": (22, "Piauí"),              "PR": (41, "Paraná"),
    "RJ": (33, "Rio de Janeiro"),     "RN": (24, "Rio Grande do Norte"),
    "RO": (11, "Rondônia"),           "RR": (14, "Roraima"),
    "RS": (43, "Rio Grande do Sul"),  "SC": (42, "Santa Catarina"),
    "SE": (28, "Sergipe"),            "SP": (35, "São Paulo"),
    "TO": (17, "Tocantins"),
}

OUTPUT_JSON = Path(__file__).parent / "cidades.json"


def normalizar(texto: str) -> str:
    return (
        unicodedata.normalize("NFKD", texto)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .upper()
        .strip()
    )


def carregar_json() -> dict:
    if OUTPUT_JSON.exists():
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def salvar_json(dados: dict):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def buscar_municipios_ibge(codigo_uf: int) -> list:
    """Lista municípios do estado via API IBGE."""
    import gzip
    url = (
        f"https://servicodados.ibge.gov.br/api/v1/localidades"
        f"/estados/{codigo_uf}/municipios"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "mymaps_br/1.0",
        "Accept-Encoding": "gzip, deflate",
    })
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as r:
        raw = r.read()
        encoding = r.headers.get("Content-Encoding", "")
        if encoding == "gzip":
            raw = gzip.decompress(raw)
        return json.loads(raw.decode("utf-8"))


def buscar_coords_photon(cidade: str, uf: str) -> tuple | None:
    """Busca coordenadas via Photon (mesmo usado no my_maps.py)."""
    # Tenta do mais específico ao mais simples
    queries = [
        f"{cidade}, {uf}, Brasil",
        cidade,
    ]
    for q in queries:
        try:
            params = urllib.parse.urlencode({
                "q": q,
                "limit": 1,
                "lang": "pt",
                "bbox": "-73.99,-33.75,-28.84,5.27",  # bounding box do Brasil
            })
            url = f"https://photon.komoot.io/api?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "mymaps_br/1.0"})
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=10) as r:
                data = json.loads(r.read())
            features = data.get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"]
                # Photon retorna [lng, lat]
                return float(coords[1]), float(coords[0])
        except Exception:
            pass
        time.sleep(0.3)
    return None


def barra_progresso(atual: int, total: int, cidade: str):
    pct = atual / total
    blocos = int(pct * 30)
    barra = "█" * blocos + "░" * (30 - blocos)
    print(f"\r  [{barra}] {atual}/{total} — {cidade[:35]:<35}", end="", flush=True)


def main():
    if len(sys.argv) < 2:
        print("Uso: python buscar_cidades_estado.py <SIGLA_UF>")
        print("Ex:  python buscar_cidades_estado.py PR")
        print(f"\nEstados disponíveis: {', '.join(sorted(ESTADOS))}")
        sys.exit(1)

    uf = sys.argv[1].upper().strip()
    if uf not in ESTADOS:
        print(f"Estado '{uf}' não reconhecido.")
        print(f"Disponíveis: {', '.join(sorted(ESTADOS))}")
        sys.exit(1)

    codigo_uf, nome_estado = ESTADOS[uf]
    print(f"\n🗺️  Buscando cidades de {nome_estado} ({uf})...\n")

    # 1. Lista municípios via IBGE
    print("  📡 Consultando IBGE...")
    try:
        municipios = buscar_municipios_ibge(codigo_uf)
    except Exception as e:
        print(f"  ❌ Erro ao consultar IBGE: {e}")
        sys.exit(1)
    print(f"  ✅ {len(municipios)} municípios encontrados.\n")

    # 2. Carrega JSON existente
    dados = carregar_json()
    ja_existem = sum(1 for m in municipios if normalizar(m["nome"]) in dados)
    print(f"  📂 JSON atual: {len(dados)} entradas ({ja_existem} de {uf} já presentes).\n")

    # 3. Busca coordenadas via Photon
    print("  🔍 Buscando coordenadas (Photon)...\n")
    novos = 0
    ignorados = 0
    erros = []

    for idx, municipio in enumerate(municipios, 1):
        nome = municipio["nome"]
        chave = normalizar(nome)
        barra_progresso(idx, len(municipios), nome)

        if chave in dados:
            ignorados += 1
            continue

        coords = buscar_coords_photon(nome, uf)
        if coords:
            dados[chave] = {"nome": nome, "uf": uf, "lat": coords[0], "lng": coords[1]}
            novos += 1
        else:
            erros.append(nome)

        # Salva a cada 10 novas cidades para não perder progresso
        if novos > 0 and novos % 10 == 0:
            salvar_json(dados)

    salvar_json(dados)

    print(f"\n\n  ✅ Concluído!")
    print(f"     Novas entradas:  {novos}")
    print(f"     Já existiam:     {ignorados}")
    print(f"     Não encontradas: {len(erros)}")
    print(f"     Total no JSON:   {len(dados)}")
    print(f"     Arquivo:         {OUTPUT_JSON}\n")

    if erros:
        print(f"  ⚠️  Cidades sem coordenadas encontradas:")
        for e in erros:
            print(f"     - {e}")
        print()


if __name__ == "__main__":
    main()