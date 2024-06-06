import pandas as pd
import plotly.graph_objects as go
import re

def plotar_grafico_csv(fig, caminho_arquivo, legenda):
    # Inicializar variáveis para armazenar os dados
    dados = {'Freq': [], 'S12': []}

    # Flag para indicar quando começar a coletar dados
    coletar_dados = False

    # Ler o arquivo CSV linha por linha
    with open(caminho_arquivo, 'r') as file:
        for linha in file:
            # Verificar se a linha começa com '! CORRECTION2 ON U', indicando o início dos dados
            if linha.startswith('! CORRECTION2 ON U'):
                coletar_dados = True
            elif coletar_dados and not linha.startswith(('BEGIN', '!', 'END')) and linha.strip():
                # Ignorar linhas que começam com '!' e linhas em branco
                # Dividir a linha em valores e armazenar nas listas apropriadas
                valores = linha.strip().split(',')
                freq_ghz = float(valores[0]) / 1e9
                dados['Freq'].append(freq_ghz)
                dados['S12'].append(float(valores[1]))
            elif coletar_dados and linha.startswith('END'):
                # Se encontrar a linha 'END', parar a coleta de dados
                break

    # Criar um DataFrame pandas com os dados
    df = pd.DataFrame(dados)

    # Adicionar linha ao gráfico
    fig.add_trace(go.Scatter(x=df['Freq'], y=df['S12'], mode='lines', name=legenda, line=dict(width=1.5)))

    return df
# Criar figura Plotly
fig = go.Figure()

arquivos = ['RESS5(1)-AGUA.csv', 'RESS5(1)-GAP0.csv', 'RESS5(1)-GAP1.csv', 'RESS5(1)-GAP2.csv',
            'RESS5(1)-GAP3.csv', 'RESS5(1)-GAP4.csv', 'RESS5(1)-GAP5.csv', 'RESS5(1)-GAP6.csv', 'RESS5(1)-GAP7.csv']

# Extrair o número do ressoador e o número da medida do primeiro arquivo
match = re.match(r'RESS(\d+)\((\d+)\)-', arquivos[0])
if match:
    ressoador = match.group(1)
    medida = match.group(2)
    titulo = f'Ressoador {ressoador} Medida {medida}'

# Arquivos CSV para serem plotados
for arquivo in arquivos:
    plotar_grafico_csv(fig, arquivo, arquivo.split('-')[1].split('.')[0])

# Adicionar título e rótulos dos eixos
fig.update_layout(title={'text': titulo, 'x':0.5},
                  xaxis=dict(title='Frequência (GHz)', autorange=False, range=[0.9, 6.1]),  # Definindo a faixa manualmente
                  yaxis_title='S12 (dB)')

# Exibir o gráfico
fig.show()