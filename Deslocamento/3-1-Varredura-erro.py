import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np

def plotar_grafico_csv(caminho_arquivo_agua, caminho_arquivos_microplasticos):
    # Inicializar variáveis para armazenar os dados
    dados_agua = {'Freq': [], 'S12': []}
    dados_microplasticos = {}

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
        match = re.match(r'Cap(\d+)_pos(\d+)\((\d+)\)\.csv', caminho_arquivo_microplastico)
        if match:
            espessura = match.group(1)
            posicao = int(match.group(2))
            medida = int(match.group(3))
            df_microplastico = processar_arquivo_csv(caminho_arquivo_microplastico)
            if posicao not in dados_microplasticos:
                dados_microplasticos[posicao] = []
            dados_microplasticos[posicao].append(df_microplastico)

    return dados_agua, dados_microplasticos


def plotar_varredura(df_agua, dados_microplasticos):
    # Encontrar a frequência com o menor valor de S12 na primeira medição de microplástico
    menor_freq = df_agua.loc[df_agua['S12'].idxmin(), 'Freq']
    menor_freq_ghz = menor_freq / 1e9  # Divisão por 1 bilhão para converter para GHz
    menor_freq_ghz_str = '{:.2f}'.format(menor_freq_ghz)

    # Inicializar listas para armazenar os valores de S12 na frequência mínima para cada posição
    varreduras = []
    varreduras_std = []
    posicoes = []

    # Para cada posição, encontrar o valor de S12 correspondente à frequência mínima
    for posicao, dfs_microplastico in sorted(dados_microplasticos.items()):
        valores_s12 = []
        for df_microplastico in dfs_microplastico:
            valor_s12 = df_microplastico.loc[df_microplastico['Freq'] == menor_freq, 'S12'].iloc[0]
            valores_s12.append(valor_s12)
        valor_s12_agua = df_agua.loc[df_agua['Freq'] == menor_freq, 'S12'].iloc[0]
        varredura = [valor_s12_agua - valor for valor in valores_s12]
        varreduras.append(np.mean(varredura))
        varreduras_std.append(np.std(varredura))
        posicoes.append(posicao)

    # Calcular os valores do eixo x em milímetros
    primeiro_valor_mm = -25
    passo_mm = 5
    valores_x_mm = [primeiro_valor_mm + i * passo_mm for i in range(len(posicoes))]

    # Criar um gráfico de linha com barras de erro
    plt.errorbar(valores_x_mm, varreduras, yerr=varreduras_std, fmt='-o', label='Média e Desvio Padrão', linewidth=0.5)

    # Adicionar rótulos
    plt.title(f'Varredura das posições com plástico na frequência {menor_freq_ghz_str} GHz')
    plt.xlabel('Posição (mm)')
    plt.ylabel('S12 (dB)')

    # Adicionar legenda
    plt.legend()

    # Exibir o gráfico
    plt.show()

# Valores do circuito apenas com água e valores do circuito com microplásticos
df_agua, dados_microplasticos = plotar_grafico_csv('Cap5_agua.csv', [
    'Cap5_pos1(1).csv', 'Cap5_pos1(2).csv', 'Cap5_pos1(3).csv', 
    'Cap5_pos2(1).csv', 'Cap5_pos2(2).csv', 'Cap5_pos2(3).csv', 
    'Cap5_pos3(1).csv', 'Cap5_pos3(2).csv', 'Cap5_pos3(3).csv', 
    'Cap5_pos4(1).csv', 'Cap5_pos4(2).csv', 'Cap5_pos4(3).csv',
    'Cap5_pos5(1).csv', 'Cap5_pos5(2).csv', 'Cap5_pos5(3).csv',
    'Cap5_pos6(1).csv', 'Cap5_pos6(2).csv', 'Cap5_pos6(3).csv',
    'Cap5_pos7(1).csv', 'Cap5_pos7(2).csv', 'Cap5_pos7(3).csv',
    'Cap5_pos8(1).csv', 'Cap5_pos8(2).csv', 'Cap5_pos8(3).csv', 
    'Cap5_pos9(1).csv', 'Cap5_pos9(2).csv', 'Cap5_pos9(3).csv',
    'Cap5_pos10(1).csv', 'Cap5_pos10(2).csv', 'Cap5_pos10(3).csv', 
    'Cap5_pos11(1).csv', 'Cap5_pos11(2).csv', 'Cap5_pos11(3).csv'])

# Plotar o gráfico de varredura
plotar_varredura(df_agua, dados_microplasticos)