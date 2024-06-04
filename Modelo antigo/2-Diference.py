import pandas as pd
import matplotlib.pyplot as plt
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


def plotar_varredura(df_agua, dfs_microplasticos):
    # Plotar a varredura para cada microplástico
    for i, df_microplastico in enumerate(dfs_microplasticos):
        varredura = df_agua.copy()
        varredura['S12'] = df_agua['S12'] - df_microplastico['S12']
        plt.plot(varredura['Freq'], varredura['S12'], label=f'Gap {i}', linewidth=0.8)

    # Encontrar a frequência com o menor valor de S12 em todos os dados
    menor_freq = varredura.loc[varredura['S12'].idxmin(), 'Freq']
    menor_s12 = varredura['S12'].min()
    print(f"A menor S12 (dB) é {menor_s12} Hz, ocorrendo em uma frequência de {menor_freq} Hz.")


# Valores do circuito apenas com água e valores do circuito com microplásticos
df_agua, dfs_microplasticos = plotar_grafico_csv('RESS5(1)-AGUA.csv', ['RESS5(1)-GAP0.csv','RESS5(1)-GAP1.csv','RESS5(1)-GAP2.csv','RESS5(1)-GAP3.csv','RESS5(1)-GAP4.csv','RESS5(1)-GAP5.csv','RESS5(1)-GAP6.csv','RESS5(1)-GAP7.csv'])

# Plotar a varredura
plotar_varredura(df_agua, dfs_microplasticos)

# Extrair o número do ressoador e o número da medida do primeiro arquivo
match = re.match(r'RESS(\d+)\((\d+)\)-', ['RESS5(1)-AGUA.csv'][0])
if match:
    ressoador = match.group(1)
    medida = match.group(2)

# Definir os limites do eixo y de -6 até 6
plt.ylim(-7, 7)

# Definir os ticks do eixo y de -6 até 6 com passo de 2
plt.gca().set_yticks(range(-6, 7, 2))

# Adicionar legenda ao gráfico
plt.legend()

# Adicionar título e rótulos dos eixos
plt.title(f'Gráfico da Diferença da Medida {medida} do Ressoador {ressoador}')
plt.xlabel('Frequência (Hz)')
plt.ylabel('S12 (dB)')

# Exibir o gráfico
plt.show()
