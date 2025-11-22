import requests
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime

def gerar_grafico_cotacao(mes_ano):
    # 1. Transforma "MMYYYY" em uma data real
    inicio = datetime.strptime(mes_ano, "%m%Y")
    
    # Último dia do mês
    ultimo_dia = calendar.monthrange(inicio.year, inicio.month)[1]
    fim = inicio.replace(day=ultimo_dia)

    # A API NÃO aceita MMYYYY como data, então tem que criar datas completas
    data_inicial_api = inicio.strftime("%m-%d-%Y")   
    # formato aceito pela API
    data_final_api   = fim.strftime("%m-%d-%Y")

    # 2. Montar a URL da API PTAX
    url = (
        "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
        "CotacaoDolarPeriodo(dataInicial=@ini,dataFinalCotacao=@fim)?"
        f"@ini='{data_inicial_api}'&@fim='{data_final_api}'&"
        "$format=json&$select=cotacaoCompra,dataHoraCotacao"
    )

    # 3. Fazer requisição
    resposta = requests.get(url)
    dados = resposta.json().get("value", [])

    if not dados:
        print("Nenhuma cotação encontrada para esse mês.")
        return

    # 4. Organizar os dados
    df = pd.DataFrame(dados)
    df["dataHoraCotacao"] = pd.to_datetime(df["dataHoraCotacao"]).dt.date
    df = df.sort_values("dataHoraCotacao")

    # 5. Criar o gráfico
    fig = px.line(
        df,
        x="dataHoraCotacao",
        y="cotacaoCompra",
        title=f"Cotação do Dólar – {inicio.month:02d}/{inicio.year}",
        labels={"dataHoraCotacao": "Data", "cotacaoCompra": "Cotação (R$)"}
    )

    fig.show()

# Rodando com o meu mês (junho de 2011)
gerar_grafico_cotacao("062011")