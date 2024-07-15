import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def gerar_df(caminho_arquivo):
    # Inicializar variáveis para armazenar os dados
    dados = {'Freq': [],'Agua':[], '0,1g/L': [], '0,5g/L': [], '1,0g/L': []}
    # Flag para indicar quando começar a coletar dados
    coletar_dados = False

    # Extrair a legenda do arquivo
    legenda = f'{caminho_arquivo.split("_")[2]}um'
    legenda = legenda.split('(')[0]

    # Ler o arquivo CSV linha por linha
    with open(caminho_arquivo, 'r') as file:
        for linha in file:
            # Verificar se a linha começa com '! CORRECTION2 ON U', indicando o início dos dados
            if linha.startswith('%freq[Hz]'):
                coletar_dados = True
            elif coletar_dados  and linha.strip(): # Ignorar linhas em branco
                # Dividir a linha em valores e armazenar nas listas apropriadas
                valores = linha.strip().split(',')
                valores = [float(valor) for valor in valores if valor]
                freq_ghz = valores[0]
                # S12 = mag2db(abs(re_Trc14_S21 + 1i * im_Trc14_S21))
                agua = 20 * np.log10(abs(valores[1] + 1j * valores[2]))
                gL_0_1 = 20 * np.log10(abs(valores[3] + 1j * valores[4]))
                gL_0_5 = 20 * np.log10(abs(valores[5] + 1j * valores[6]))
                gL_1_0 = 20 * np.log10(abs(valores[7] + 1j * valores[8]))
                dados['Freq'].append(freq_ghz); dados['Agua'].append(agua); dados['0,1g/L'].append(gL_0_1)
                dados['0,5g/L'].append(gL_0_5); dados['1,0g/L'].append(gL_1_0)
            elif coletar_dados and not linha.strip():
                # Se encontrar a linha 'END', parar a coleta de dados
                break

        return pd.DataFrame(dados), legenda


def plotar_varredura(df, legenda):
    # Calcular as subtrações entre as concentrações e os valores da água
    subtracoes = pd.DataFrame()
    subtracoes['0,1g/L'] = df['Agua'] - df['0,1g/L']
    subtracoes['0,5g/L'] = df['Agua'] - df['0,5g/L']
    subtracoes['1,0g/L'] = df['Agua'] - df['1,0g/L']
    
    # Encontrar o menor valor de subtração e a frequência correspondente
    menor_indice = subtracoes.stack().idxmin()[0]
    frequencia_correspondente = df.loc[menor_indice, 'Freq']
    frequencia_correspondente = '{:.2f}'.format(frequencia_correspondente)

    # Inicializar listas para armazenar os valores de S12 na frequência mínima para cada arquivo
    valores_s12 = []

    # Para cada arquivo, encontrar o valor de S12 correspondente à frequência mínima
    for i in ['0,1g/L', '0,5g/L', '1,0g/L']:
         valor_s12 = df[i][menor_indice]
         valores_s12.append(valor_s12)

    # Legenda para o gráfico
    legendas = f'{legenda} na frequência de {frequencia_correspondente} GHz'

    # Valores de concentração no eixo x
    eixo_x = ['0,1g/L', '0,5g/L', '1,0g/L']

    # Criar um gráfico de linha
    plt.plot(eixo_x, valores_s12, linestyle='-', label=legendas, linewidth=0.7)

    plt.legend()
    # Adicionar rótulos
    plt.title(f'Varredura das concentrações de microplásticos com cada espessura de plástico')
    plt.xlabel('Concentração (g/L)')
    plt.ylabel('S12 (dB)')


# Fazer dataframe e legenda para o primeiro arquivo
df,legenda = gerar_df('Cap_Copo_75um(2).dat')

# Plotar o gráfico de linhas
plotar_varredura(df,legenda)

# fazer dataframe e legenda para o segundo arquivo
df,legenda = gerar_df('Cap_Copo_150um(2).dat')

# Plotar o gráfico de linhas
plotar_varredura(df,legenda)

# Faer dataframe e legenda para o terceiro arquivo
df,legenda = gerar_df('Cap_Copo_300um(2)_sem_0_75.dat')

# Plotar o gráfico de linhas
plotar_varredura(df,legenda)

# Exibir o gráfico
plt.show()

