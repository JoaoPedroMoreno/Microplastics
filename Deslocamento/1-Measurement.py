import pandas as pd
import matplotlib.pyplot as plt
import re

def plotar_grafico_csv(caminho_arquivo, legenda):
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

    # Exemplo de criação de um gráfico de linha com legenda
    plt.plot(df['Freq'], df['S12'], label=legenda, linewidth=0.5)

arquivos = ['Cap5_agua.csv', 'Cap5_pos1(1).csv', 'Cap5_pos2(1).csv', 'Cap5_pos3(1).csv', 'Cap5_pos4(1).csv' , 'Cap5_pos5(1).csv', 'Cap5_pos7(1).csv',
            'Cap5_pos8(1).csv', 'Cap5_pos9(1).csv', 'Cap5_pos10(1).csv', 'Cap5_pos11(1).csv']

# Extrair o número do ressoador e o número da medida do primeiro arquivo
match = re.match(r'Cap(\d+)_pos1\((\d+)\)\.csv', arquivos[1])
if match:
    espessura = match.group(1)
    medida = match.group(2)
    if espessura == '5':
        titulo = f'Microplástico de 0.5 mm de espessura Medida {medida}'
    elif espessura == '10':
        titulo = f'Microplástico de 1 mm de espessura Medida {medida}'


# Arquivos CSV para serem plotados
for arquivo in arquivos:
    plotar_grafico_csv(arquivo, arquivo.split('_')[1].split('.')[0].split('(')[0])

# Adicionar legenda ao gráfico
plt.legend()

# Adicionar título e rótulos dos eixos
plt.title(f'{titulo}')
plt.xlabel('Frequência (GHz)')
plt.ylabel('S12 (dB)')

# Exibir o gráfico
plt.show()
