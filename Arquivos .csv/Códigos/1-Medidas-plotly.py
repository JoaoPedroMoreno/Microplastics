import os
import pandas as pd
import plotly.graph_objects as go
import re
import glob

def processar_arquivo_csv(caminho_arquivo):
    dados = {'Freq': [], 'S12': []}
    coletar_dados = False
    with open(caminho_arquivo, 'r') as file:
        for linha in file:
            if linha.startswith('! CORRECTION2 ON U'):
                coletar_dados = True
            elif coletar_dados and not linha.startswith(('BEGIN', '!', 'END')) and linha.strip():
                valores = linha.strip().split(',')
                freq_ghz = float(valores[0]) / 1e9
                dados['Freq'].append(freq_ghz)
                dados['S12'].append(float(valores[1]))
            elif coletar_dados and linha.startswith('END'):
                break
    return pd.DataFrame(dados)

def plotar_grafico_csv(fig, caminho_arquivo, legenda):
    df = processar_arquivo_csv(caminho_arquivo)
    fig.add_trace(go.Scatter(x=df['Freq'], y=df['S12'], mode='lines', name=legenda, line=dict(width=1.5)))
    return df

# Definir o caminho para o diretório onde os arquivos CSV estão armazenados
diretorio_arquivos = os.path.join(os.getcwd(), 'Arquivos .csv', 'Medidas')

# Usar glob para listar todos os arquivos CSV no diretório especificado
todos_arquivos = glob.glob(os.path.join(diretorio_arquivos, '*.csv'))

# Pegar o número do Cap e o número dentro dos parênteses desejado através de um input
num_cap = input("Digite a espessura do microplástico: ")
num_parenteses = input("Digite o número da medida: ")

# Filtrar arquivos que atendem aos critérios
arquivos_filtrados = [arquivo for arquivo in todos_arquivos if re.match(rf'Cap{num_cap}_pos\d+\({num_parenteses}\)\.csv', os.path.basename(arquivo))]

# Adicionar o arquivo Cap5_agua.csv se ele existir
if num_cap == '5':
    arquivo_agua = os.path.join(diretorio_arquivos, 'Cap5_agua.csv')
elif num_cap == '10':
    arquivo_agua = os.path.join(diretorio_arquivos, 'Cap10_agua.csv')

if os.path.exists(arquivo_agua):
    arquivos_filtrados.append(arquivo_agua)

# Ordenar os arquivos filtrados pela posição
arquivos_filtrados.sort(key=lambda x: int(re.search(r'_pos(\d+)\(', os.path.basename(x)).group(1)) if '_pos' in os.path.basename(x) else -1)

# Verificar se algum arquivo foi encontrado
if not arquivos_filtrados:
    print("Nenhum arquivo encontrado com os critérios especificados.")
else:
    # Criar figura Plotly
    fig = go.Figure()

    # Extrair o número do ressoador e o número da medida do primeiro arquivo
    arquivo_referencia = os.path.basename(arquivos_filtrados[1])
    match = re.match(r'Cap(\d+)_pos(\d+)\((\d+)\)', arquivo_referencia)

    if match:
        espessura = match.group(1)
        if espessura == '5':
            espessura = '0.5 mm'
        elif espessura == '10':
            espessura = '1 mm'
        medida = match.group(3)
        titulo = f'Microplástico de {espessura} Medida {medida}'

    # Arquivos CSV para serem plotados
    for arquivo in arquivos_filtrados:
        base_name = os.path.basename(arquivo)
        if base_name == 'Cap5_agua.csv' or base_name == 'Cap10_agua.csv':
            legenda = 'Água'
        else:
            pos_num = re.search(r'_pos(\d+)\(', base_name).group(1)
            legenda = f'Posição {pos_num}'
        plotar_grafico_csv(fig, arquivo, legenda)

    # Adicionar título e rótulos dos eixos
    fig.update_layout(
        title={'text': titulo, 'x': 0.5},
        xaxis=dict(title='Frequência (GHz)', autorange=False, range=[1.9, 3.6]),  # Definindo a faixa manualmente
        yaxis_title='S12 (dB)'
    )

    # Exibir o gráfico
    fig.show()
