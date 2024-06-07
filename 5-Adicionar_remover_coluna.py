import pandas as pd

def ler_arquivo_dat(caminho):
    # Ler o arquivo .dat e retornar um DataFrame
    with open(caminho, 'r') as file:
        linhas = file.readlines()
    
    # Encontrar a linha do cabeçalho
    cabecalho = []
    for linha in linhas:
        if linha.startswith('%') and 'freq[Hz]' in linha:
            cabecalho = linha.strip('%').strip().split(',')
            break
    
    # Carregar os dados em um DataFrame, ignorando as linhas de comentário
    dados = [linha.strip().split(',') for linha in linhas if not linha.startswith('%')]
    df = pd.DataFrame(dados, columns=cabecalho)
    
    return df.apply(pd.to_numeric)

def salvar_arquivo_dat(df, nome):
    with open(nome, 'w') as file:
        # Escrever cabeçalho
        file.write('% Version 1.00\n')
        file.write('%\n')
        file.write('%freq[Hz],re:Agua,im:Agua,re:concentracao 0,1g/L,im:concentracao 0,1g/L,re:concentracao 0,5g/L,im:concentracao 0,5g/L,re:concentracao 1,0g/L,im:concentracao 1,0g/L\n')

        
        # Escrever dados
        for index, row in df.iterrows():
            file.write(','.join(f'{val:.16E}' for val in row) + ',\n')

def gerar_df(arquivo_principal, arquivo_secundario):
    # Inicializar variáveis para armazenar os dados
    dados = {
        'Freq': [], 'Agua_RE': [], 'Agua_IM': [], '0,1g/L_RE': [], '0,1g/L_IM': [],
        '0,5g/L_RE': [], '0,5g/L_IM': [],
        '1,0g/L_RE': [], '1,0g/L_IM': []
    }

    # Função para coletar dados de frequência
    def coletar_freq(arquivo):
        coletar_freq = False
        with open(arquivo, 'r') as file:
            for linha in file:
                if linha.startswith('%freq[Hz]'):
                    coletar_freq = True
                elif coletar_freq and linha.strip():
                    valores_freq = linha.strip().split(',')
                    freq_ghz = float(valores_freq[0]) / 1e9
                    dados['Freq'].append(freq_ghz)
                elif coletar_freq and not linha.strip():
                    break

    # Função para coletar dados de um arquivo específico
    def coletar_dados(arquivo, prefixo):
        coletar_dados = False
        with open(arquivo, 'r') as file:
            for linha in file:
                if linha.startswith('%freq[Hz]'):
                    coletar_dados = True
                elif coletar_dados and linha.strip():
                    valores = linha.strip().split(',')
                    valores = [float(valor) for valor in valores if valor]
                    if prefixo == 'Agua':
                        re = valores[1]
                        im = valores[2]
                        dados[f'{prefixo}_RE'].append(re)
                        dados[f'{prefixo}_IM'].append(im)
                    elif prefixo == '0,1g/L':
                        re = valores[3]
                        im = valores[4]
                        dados[f'{prefixo}_RE'].append(re)
                        dados[f'{prefixo}_IM'].append(im)
                    elif prefixo == '0,5g/L':
                        re = valores[7]
                        im = valores[8]
                        dados[f'{prefixo}_RE'].append(re)
                        dados[f'{prefixo}_IM'].append(im)
                    elif prefixo == '0,75g/L':
                        re = valores[5]
                        im = valores[6]
                        dados[f'{prefixo}_RE'].append(re)
                        dados[f'{prefixo}_IM'].append(im)
                    elif prefixo == '1,0g/L':
                        re = valores[9]
                        im = valores[10]
                        dados[f'{prefixo}_RE'].append(re)
                        dados[f'{prefixo}_IM'].append(im)

                elif coletar_dados and not linha.strip():
                    break

    # Coletar dados de frequência
    coletar_freq(arquivo_principal)

    # Coletar dados das outras colunas
    coletar_dados(arquivo_principal, 'Agua')
    coletar_dados(arquivo_principal, '0,1g/L')
    coletar_dados(arquivo_principal, '0,5g/L')
    coletar_dados(arquivo_principal, '1,0g/L')

    return pd.DataFrame(dados)

# Caminhos dos arquivos
arquivo_principal = 'Cap_Copo_300um(2).dat'
arquivo_secundario = 'Cap2_Duto1_plstc_all.dat'

# Adicionar dados
df = gerar_df(arquivo_principal, arquivo_secundario)

# Salvar o DataFrame no arquivo .dat
nome = 'Cap_Duto_300um(2)1.dat'
salvar_arquivo_dat(df, nome)