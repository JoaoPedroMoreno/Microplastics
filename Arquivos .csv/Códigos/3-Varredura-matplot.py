import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

def plotar_grafico_csv(caminho_arquivo_agua, caminho_arquivos_microplasticos):
    dados_agua = processar_arquivo_csv(caminho_arquivo_agua)
    dados_microplasticos = [processar_arquivo_csv(caminho) for caminho in caminho_arquivos_microplasticos]
    return dados_agua, dados_microplasticos

def encontrar_frequencia_max_diff(df_agua, dfs_microplasticos):
    freq_diffs = {}

    for df_microplastico in dfs_microplasticos:
        for freq in df_agua['Freq']:
            if freq in df_microplastico['Freq'].values:
                s12_agua = df_agua[df_agua['Freq'] == freq]['S12'].values[0]
                s12_micro = df_microplastico[df_microplastico['Freq'] == freq]['S12'].values[0]
                diff = abs(s12_micro - s12_agua)
                if freq not in freq_diffs:
                    freq_diffs[freq] = diff
                else:
                    freq_diffs[freq] = max(freq_diffs[freq], diff)

    max_diff_freq = max(freq_diffs, key=freq_diffs.get)
    return max_diff_freq

def plotar_varredura(df_agua, dfs_microplasticos, caminho_arquivo_agua, caminho_arquivos_microplasticos):
    menor_freq = encontrar_frequencia_max_diff(df_agua, dfs_microplasticos)
    menor_freq = 2337500000
    menor_freq_ghz = menor_freq / 1e9
    menor_freq_ghz_str = '{:.2f}'.format(menor_freq_ghz)

    varreduras_por_posicao = {pos: [] for pos in range(1, 12)}

    for caminho_arquivo in caminho_arquivos_microplasticos:
        match = re.match(r'Cap\d+_pos(\d+)\(\d+\)\.csv', os.path.basename(caminho_arquivo))
        if match:
            pos = int(match.group(1))
            df_microplastico = processar_arquivo_csv(caminho_arquivo)
            valor_s12 = df_microplastico.loc[df_microplastico['Freq'] == menor_freq, 'S12'].iloc[0]
            varredura = df_agua.loc[df_agua['Freq'] == menor_freq, 'S12'].iloc[0] - valor_s12
            varreduras_por_posicao[pos].append(varredura)

    medias_varreduras = []
    erros_varreduras = []
    for pos in sorted(varreduras_por_posicao.keys()):
        if varreduras_por_posicao[pos]:
            medias_varreduras.append(np.mean(varreduras_por_posicao[pos]))
            erros_varreduras.append(np.std(varreduras_por_posicao[pos]))

    primeiro_valor_mm = -25
    passo_mm = 5
    valores_x_mm = [primeiro_valor_mm + i * passo_mm for i in range(len(medias_varreduras))]

    plt.errorbar(valores_x_mm, medias_varreduras, yerr=erros_varreduras, fmt='-o', ecolor='r', capsize=5, label='Média e desvio padrão')

    match = re.match(r'Cap(\d+)_agua', os.path.basename(caminho_arquivo_agua))
    if match:
        espessura = match.group(1)
        if espessura == '5':
            espessura = '0.5 mm'
        elif espessura == '10':
            espessura = '1 mm'

    plt.title(f'Varredura das posições do microplástico de {espessura} na frequência {menor_freq_ghz_str} GHz')
    plt.xlabel('Posição (mm)')
    plt.ylabel('S12 (dB)')
    plt.legend()
    plt.show()

diretorio_arquivos = os.path.join(os.getcwd(), 'Arquivos .csv', 'Medidas')
todos_arquivos = glob.glob(os.path.join(diretorio_arquivos, '*.csv'))

num_cap = input("Digite o número após 'Cap': ")

arquivos_filtrados = []
if num_cap == '5':
    arquivo_agua = os.path.join(diretorio_arquivos, 'Cap5_agua.csv')
elif num_cap == '10':
    arquivo_agua = os.path.join(diretorio_arquivos, 'Cap10_agua.csv')
else:
    arquivo_agua = None

if arquivo_agua and os.path.exists(arquivo_agua):
    arquivos_filtrados.append(arquivo_agua)

for medida in [1, 2, 3]:
    arquivos_filtrados.extend([arquivo for arquivo in todos_arquivos if re.match(rf'Cap{num_cap}_pos\d+\({medida}\)\.csv', os.path.basename(arquivo))])

arquivos_filtrados.sort(key=lambda x: int(re.search(r'_pos(\d+)\(', os.path.basename(x)).group(1)) if '_pos' in os.path.basename(x) else -1)

if not arquivos_filtrados:
    print("Nenhum arquivo encontrado com os critérios especificados.")
else:
    caminho_arquivo_agua = arquivo_agua
    caminho_arquivos_microplasticos = [arquivo for arquivo in arquivos_filtrados if arquivo != arquivo_agua]

    df_agua, dfs_microplasticos = plotar_grafico_csv(caminho_arquivo_agua, caminho_arquivos_microplasticos)
    plotar_varredura(df_agua, dfs_microplasticos, caminho_arquivo_agua, caminho_arquivos_microplasticos)
