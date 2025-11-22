import requests
import folium
from folium import Map, CircleMarker, Popup
import statistics

# 1. Meu token
SPTRANS_TOKEN = "deca79917d3e50d27a89803c19b203e9ec1f634558ee08f5d0c17c006c39c5c5"

# 2. Linha que escolhi - Terminal Pirituba a Vila Mirante (Linha Noturna)
CODIGO_LINHA = "N140-11"

# 3. Funções auxiliares
def autenticar(session, token):
    # Autentica no Olho Vivo com o token e retorna True se ok
    url_login = f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}"
    resp = session.post(url_login)
    print("Resposta do login:", resp.text.strip(), "| status:", resp.status_code)
    return resp.status_code == 200 and resp.text.strip().lower() == "true"

def buscar_linhas_por_termo(session, termo):
    # Procura linhas que contenham o termo (retorna lista de dicts)
    url = "http://api.olhovivo.sptrans.com.br/v2.1/Linha/Buscar"

    # Conforme a documentação oficial da SPtrans, /linha/buscar deve ser acessada via GET
    r = session.get(url, params={"termosBusca": termo})

    r.raise_for_status()
    return r.json()

def resolver_cl(session, termo):

    # Recebe um termo/letreiro (ex: "N140-11") e tenta retornar o código interno 'cl'
    # Retorna None se não encontrar.

    linhas = buscar_linhas_por_termo(session, termo)
    if not linhas:
        return None

    # tenta correspondência exata no letreiro
    for l in linhas:
        if str(l.get("lt", "")).upper() == str(termo).upper():
            return l.get("cl")

    # senão devolve o primeiro disponível
    return linhas[0].get("cl")

def buscar_paradas(session, codigo_linha):
    # Retorna lista de paradas (cada item com px, py, np, cp etc.)
    url = "http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha"
    r = session.get(url, params={"codigoLinha": codigo_linha})
    r.raise_for_status()
    return r.json()

def buscar_posicoes(session, codigo_linha):
    # Retorna posições atuais da linha
    url = "http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha"
    r = session.get(url, params={"codigoLinha": codigo_linha})
    r.raise_for_status()
    return r.json()

# 4. Rotina principal
def construir_mapa_linha(token, codigo_linha_input, salvar_html="mapa_frota.html"):
    s = requests.Session()

    print("Autenticando no Olho Vivo...")
    ok = autenticar(s, token)
    if not ok:
        print("Erro na autenticação. Verifique o token.")
        return

    # Se for letreiro, converte para CL
    codigo_cl = codigo_linha_input
    if isinstance(codigo_linha_input, str) and not codigo_linha_input.isdigit():
        print(f"'{codigo_linha_input}' parece ser um letreiro — vou buscar o código interno (cl)...")
        codigo_cl = resolver_cl(s, codigo_linha_input)
        if codigo_cl is None:
            print("Não encontrei um código interno para esse letreiro.")
            return
        print(f"Código interno (cl) encontrado: {codigo_cl}")

    print(f"Buscando paradas da linha {codigo_cl}...")
    paradas = buscar_paradas(s, codigo_cl)
    if not paradas:
        print("Nenhuma parada encontrada para essa linha.")
        return

    lats = [p["py"] for p in paradas if p.get("py") is not None]
    lons = [p["px"] for p in paradas if p.get("px") is not None]
    if not lats or not lons:
        print("Paradas não possuem coordenadas válidas.")
        return

    center = [statistics.mean(lats), statistics.mean(lons)]
    m = Map(location=center, zoom_start=14)

    # Paradas — azul
    for p in paradas:
        lat = p.get("py")
        lon = p.get("px")
        nome = p.get("np") or "Parada"
        endereco = p.get("ed") or ""
        popup_text = f"{nome} <br>{endereco} <br>CP: {p.get('cp')}"
        CircleMarker(
            location=[lat, lon],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=Popup(popup_text, max_width=300)
        ).add_to(m)

    print("Buscando posições em tempo real...")
    pos = buscar_posicoes(s, codigo_cl)
    vehicles = pos.get("vs", []) if isinstance(pos, dict) else []

    # Veículos — vermelho
    for v in vehicles:
        lat = v.get("py")
        lon = v.get("px")
        placa = v.get("p")
        ativo = v.get("a")
        ta = v.get("ta")
        popup = f"Veículo: {placa}<br>Ativo: {ativo}<br>Horário: {ta}"
        CircleMarker(
            location=[lat, lon],
            radius=6,
            color="red",
            fill=True,
            fill_opacity=0.9,
            popup=Popup(popup, max_width=250)
        ).add_to(m)

    # Legenda
    folium.map.Marker(
        location=[center[0] + 0.01, center[1] - 0.02],
        icon=folium.DivIcon(html="<div style='font-size:12px'><span style='color:blue'>&#9679;</span> Paradas &nbsp;&nbsp; <span style='color:red'>&#9679;</span> Ônibus</div>")
    ).add_to(m)

    m.save(salvar_html)
    print(f"Mapa salvo em: {salvar_html}")

# 5. Execução
if __name__ == "__main__":
    construir_mapa_linha(SPTRANS_TOKEN, CODIGO_LINHA, salvar_html="mapa_linha_N140-11.html")