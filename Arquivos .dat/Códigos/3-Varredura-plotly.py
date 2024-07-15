import pandas as pd
import plotly.graph_objects as go
import re


def plotar_grafico_csv(caminho_arquivo_agua, caminho_arquivos_microplasticos):
    # Inicializar variáveis para armazenar os dados
    dados_agua = {'Freq': [], 'S12': []}
    dados_microplasticos = []

    # Função para processar um arquivo CSV e criar o DataFrame correspondente
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

    # Processar o arquivo de água
    dados_agua = processar_arquivo_csv(caminho_arquivo_agua)

    # Processar os arquivos de microplástico
    for caminho_arquivo_microplastico in caminho_arquivos_microplasticos:
        dados_microplastico = processar_arquivo_csv(caminho_arquivo_microplastico)
        dados_microplasticos.append(dados_microplastico)

    return dados_agua, dados_microplasticos


def plotar_varredura(df_agua, dfs_microplasticos, caminho_arquivo_agua):
    # Encontrar a frequência com o menor valor de S12 em todos os dados
    menor_freq = df_agua.loc[df_agua['S12'].idxmin(), 'Freq']
    # Converter a frequência para GHz
    menor_freq_ghz = menor_freq / 1e9  # Divisão por 1 bilhão para converter para GHz

    # Formatando o valor para exibir 2 casas decimais
    menor_freq_ghz_str = '{:.2f}'.format(menor_freq_ghz)

    # Inicializar listas para armazenar os valores de S12 na frequência mínima para cada arquivo
    varreduras = []

    # Para cada arquivo, calcular a diferença de S12 em relação à água
    for df_microplastico in dfs_microplasticos:
        valor_s12_agua = df_agua.loc[df_agua['Freq'] == menor_freq, 'S12'].iloc[0]
        valor_s12_microplastico = df_microplastico.loc[df_microplastico['Freq'] == menor_freq, 'S12'].iloc[0]
        varredura = valor_s12_agua - valor_s12_microplastico
        varreduras.append(varredura)

    # Calcular os valores do eixo x em milímetros
    primeiro_valor_mm = -9.1
    passo_mm = 1.3
    valores_x_mm = [primeiro_valor_mm + i * passo_mm for i in range(len(varreduras))]
    # Extrair o número do ressoador e o número da medida do primeiro arquivo
    match = re.match(r'RESS(\d+)\((\d+)\)-', caminho_arquivo_agua[0])
    ressoador = match.group(1)
    # Criar um gráfico de linha
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=valores_x_mm, y=varreduras, mode='lines', name='Varredura de posição'))

    # Adicionar rótulos
    fig.update_layout(title={'text': f'Varredura das posições do ressoador {ressoador} na frequência {menor_freq_ghz_str} GHz', 'x':0.5},
                   xaxis=dict(autorange=False,  # Colando uma margem extra nas laterais
                             range=[-9.3, 9.3]),
                     xaxis_title='Posição (mm)',
                      yaxis_title='Diferença de S12 (dB)')

    # Exibir o gráfico
    fig.show()

# Valores do circuito apenas com água e valores do circuito com microplásticos
df_agua, dfs_microplasticos = plotar_grafico_csv('RESS5(1)-AGUA.csv', ['RESS5(1)-GAP0.csv','RESS5(1)-FNG1.csv','RESS5(1)-GAP1.csv','RESS5(1)-FNG2.csv','RESS5(1)-GAP2.csv','RESS5(1)-FNG3.csv','RESS5(1)-GAP3.csv','RESS5(1)-FNG4.csv','RESS5(1)-GAP4.csv','RESS5(1)-FNG5.csv','RESS5(1)-GAP5.csv','RESS5(1)-FNG6.csv','RESS5(1)-GAP6.csv','RESS5(1)-FNG7.csv','RESS5(1)-GAP7.csv'])

# Plotar o gráfico
plotar_varredura(df_agua, dfs_microplasticos, ['RESS5(1)-AGUA.csv'])