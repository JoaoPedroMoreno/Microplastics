import os
import pandas as pd
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

def coletar_valores_s12_na_frequencia(df_agua, dfs_microplasticos, freq):
    valores_s12 = {'Agua': df_agua[df_agua['Freq'] == freq]['S12'].values[0]}
    for i, df_microplastico in enumerate(dfs_microplasticos):
        match = re.match(r'Cap\d+_pos(\d+)\(\d+\)\.csv', os.path.basename(caminho_arquivos_microplasticos[i]))
        if match:
            pos = int(match.group(1))
            valor_s12 = df_microplastico[df_microplastico['Freq'] == freq]['S12'].values[0]
            if f'Posicao {pos}' not in valores_s12:
                valores_s12[f'Posicao {pos}'] = [valor_s12]
            else:
                valores_s12[f'Posicao {pos}'].append(valor_s12)
    return valores_s12

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

    df_agua = processar_arquivo_csv(caminho_arquivo_agua)
    dfs_microplasticos = [processar_arquivo_csv(caminho) for caminho in caminho_arquivos_microplasticos]

    freq_max_diff = encontrar_frequencia_max_diff(df_agua, dfs_microplasticos)
    valores_s12 = coletar_valores_s12_na_frequencia(df_agua, dfs_microplasticos, freq_max_diff)

    # Criar DataFrame para salvar em CSV
    medidas = [f'Medida {i}' for i in range(1, 4)]
    colunas = [''] + ['Agua'] + [f'Posicao {i}' for i in range(1, 12)]
    dados_tabela = []

    for medida in medidas:
        linha = [medida, valores_s12['Agua']]
        for pos in range(1, 12):
            chave_pos = f'Posicao {pos}'
            if chave_pos in valores_s12 and len(valores_s12[chave_pos]) > medidas.index(medida):
                linha.append(valores_s12[chave_pos][medidas.index(medida)])
            else:
                linha.append(None)
        dados_tabela.append(linha)

    df_tabela = pd.DataFrame(dados_tabela, columns=colunas)
    df_tabela.to_csv('prova_real.csv', index=False)

    print("Arquivo 'prova_real.csv' criado com sucesso.")
