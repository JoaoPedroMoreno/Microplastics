import pandas as pd
import plotly.graph_objects as go
import numpy as np

def plotar_grafico_csv(fig, caminho_arquivo, legenda):
    # Inicializar variáveis para armazenar os dados
    dados = {'Freq': [],'Agua':[], '0,1g/L': [], '0,5g/L': [], '0,75g/L': [], '1,0g/L': []}
    legenda = ['Agua', '0,1g/L', '0,5g/L', '0,75g/L', '1,0g/L']
    # Flag para indicar quando começar a coletar dados
    coletar_dados = False

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
                freq_ghz = valores[0] / 1e9
                # S12 = mag2db(abs(re_Trc14_S21 + 1i * im_Trc14_S21))
                agua = 20 * np.log10(abs(valores[1] + 1j * valores[2]))
                gL_0_1 = 20 * np.log10(abs(valores[3] + 1j * valores[4]))
                gL_0_5 = 20 * np.log10(abs(valores[5] + 1j * valores[6]))
                gL_0_75 = 20 * np.log10(abs(valores[7] + 1j * valores[8]))
                gL_1_0 = 20 * np.log10(abs(valores[9] + 1j * valores[10]))
                dados['Freq'].append(freq_ghz); dados['Agua'].append(agua); dados['0,1g/L'].append(gL_0_1)
                dados['0,5g/L'].append(gL_0_5); dados['0,75g/L'].append(gL_0_75); dados['1,0g/L'].append(gL_1_0)
            elif coletar_dados and not linha.strip():
                # Se encontrar a linha 'END', parar a coleta de dados
                break

    # Criar um DataFrame pandas com os dados
    df = pd.DataFrame(dados)

    # Adicionar linha ao gráfico
    for i in range(0, 5):
        fig.add_trace(go.Scatter(x=df['Freq'], y=df[legenda[i]], mode='lines', name=legenda[i], line=dict(width=1.5)))

    return df
# Criar figura Plotly
fig = go.Figure()

arquivos = ['Cap1-Copo(2).dat']

titulo = 'Capacitor 1 - Copo 2'

# Arquivos CSV para serem plotados
for arquivo in arquivos:
    plotar_grafico_csv(fig, arquivo, arquivo.split('-')[1].split('.')[0])

# Adicionar título e rótulos dos eixos
fig.update_layout(title={'text': titulo, 'x':0.5},
                  xaxis=dict(title='Frequência (GHz)', autorange=False, range=[0.9, 6.1]),  # Definindo a faixa manualmente
                  yaxis_title='S12 (dB)')

# Exibir o gráfico
fig.show()