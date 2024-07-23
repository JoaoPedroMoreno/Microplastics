import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import glob

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
        titulo = f'Microplastico de {espessura} Medida {medida}'

    # Arquivos CSV para serem plotados
    for arquivo in arquivos_filtrados:
        base_name = os.path.basename(arquivo)
        if base_name == 'Cap5_agua.csv' or base_name == 'Cap10_agua.csv':
            legenda = 'Agua'
        else:
            pos_num = re.search(r'_pos(\d+)\(', base_name).group(1)
            legenda = f'Posição {pos_num}'
        plotar_grafico_csv(arquivo, legenda)

    # Adicionar legenda ao gráfico
    plt.legend()

    # Adicionar título e rótulos dos eixos
    plt.title(titulo)
    plt.xlabel('Frequência (GHz)')
    plt.ylabel('S12 (dB)')

    # Exibir o gráfico
    plt.show()
