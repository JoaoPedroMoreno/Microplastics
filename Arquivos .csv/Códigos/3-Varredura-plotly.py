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
                dados['Freq'].append(float(valores[0]))
                dados['S12'].append(float(valores[1]))
            elif coletar_dados and linha.startswith('END'):
                break
    return pd.DataFrame(dados)

def plotar_grafico_csv(fig, caminho_arquivo, legenda):
    df = processar_arquivo_csv(caminho_arquivo)
    fig.add_trace(go.Scatter(x=df['Freq'], y=df['S12'], mode='lines', name=legenda, line=dict(width=1.5)))
    return df

def encontrar_frequencia_max_diff(df_agua, df_microplastico):
    freq_diffs = {}
    
    for freq in df_agua['Freq']:
        if freq in df_microplastico['Freq'].values:
            s12_agua = df_agua[df_agua['Freq'] == freq]['S12'].values[0]
            s12_micro = df_microplastico[df_microplastico['Freq'] == freq]['S12'].values[0]
            diff = abs(s12_micro - s12_agua)
            freq_diffs[freq] = diff
    
    max_diff_freq = max(freq_diffs, key=freq_diffs.get)
    return max_diff_freq

def plotar_varredura(df_agua, df_microplasticos, freq_especifica):
    freq_especifica = 2337500000
    freq_especifica_ghz = freq_especifica / 1e9
    freq_especifica_ghz_str = '{:.2f}'.format(freq_especifica_ghz)
    
    # Cálculo da varredura para a frequência específica
    valor_s12_agua = df_agua.loc[df_agua['Freq'] == freq_especifica, 'S12'].iloc[0]
    varreduras = []

    for df_microplastico in df_microplasticos:
        if freq_especifica in df_microplastico['Freq'].values:
            valor_s12_micro = df_microplastico.loc[df_microplastico['Freq'] == freq_especifica, 'S12'].iloc[0]
            varredura = valor_s12_agua - valor_s12_micro
            varreduras.append(varredura)
    
    # Calculando valores do eixo X em milímetros
    primeiro_valor_mm = -7.8
    passo_mm = 1.3
    valores_x_mm = [primeiro_valor_mm + i * passo_mm for i in range(len(varreduras))]
    
    # Criando o gráfico Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=valores_x_mm, y=varreduras, mode='lines+markers', name='Varredura'))

    # Título e rótulos do gráfico
    match = re.match(r'Cap(\d+)_pos(\d+)\((\d+)\)', os.path.basename(caminho_arquivo_agua))
    if match:
        espessura = match.group(1)
        if espessura == '5':
            espessura = '5 mm'
        elif espessura == '10':
            espessura = '10 mm'
        medida = match.group(2)
        titulo = f'Microplástico de {espessura} mm Medida {medida}'
    
    fig.update_layout(title=f'Varredura das posições do ressoador na frequência {freq_especifica_ghz_str} GHz',
                      xaxis_title='Posição (mm)',
                      yaxis_title='Diferença de S12 (dB)')

    fig.show()

# Caminho para o diretório onde os arquivos CSV estão armazenados
diretorio_arquivos = os.path.join(os.getcwd(), 'Arquivos .csv', 'Medidas')
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
    caminho_arquivo_agua = arquivo_agua
    caminho_arquivos_microplasticos = [arquivo for arquivo in arquivos_filtrados if arquivo != arquivo_agua]

    # Processar dados
    df_agua = processar_arquivo_csv(caminho_arquivo_agua)
    df_microplasticos = [processar_arquivo_csv(arquivo) for arquivo in caminho_arquivos_microplasticos]
    
    # Encontrar a frequência com a maior diferença
    freq_max_diff = encontrar_frequencia_max_diff(df_agua, df_microplasticos[0])
    
    # Plotar o gráfico para a frequência com a maior diferença
    plotar_varredura(df_agua, df_microplasticos, freq_max_diff)
