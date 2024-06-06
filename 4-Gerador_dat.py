import pandas as pd

def gerar_df(arquivo_agua, arquivo0_1, arquivo0_5,arquivo0_75, arquivo1_0):
    # Inicializar variáveis para armazenar os dados
    dados = {
        'Freq': [], 'Agua_RE': [], 'Agua_IM': [], '0,1g/L_RE': [], '0,1g/L_IM': [],
        '0,5g/L_RE': [], '0,5g/L_IM': [], '0,75g/L_RE': [], '0,75g/L_IM': [],
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
                    re = valores[3]
                    im = valores[4]
                    dados[f'{prefixo}_RE'].append(re)
                    dados[f'{prefixo}_IM'].append(im)
                elif coletar_dados and not linha.strip():
                    break

    # Coletar dados de frequência
    coletar_freq(arquivo_agua)

    # Coletar dados das outras colunas
    coletar_dados(arquivo_agua, 'Agua')
    coletar_dados(arquivo0_1, '0,1g/L')
    coletar_dados(arquivo0_5, '0,5g/L')
    coletar_dados(arquivo0_75, '0,75g/L')
    coletar_dados(arquivo1_0, '1,0g/L')

    return pd.DataFrame(dados)

# Função para salvar o DataFrame no formato .dat
def salvar_arquivo_dat(df, nome):
    with open(nome, 'w') as file:
        # Escrever cabeçalho
        file.write('% Version 1.00\n')
        file.write('%\n')
        file.write('%freq[Hz],re:Agua,im:Agua,re:concentracao 0,1g/L,im:concentracao 0,1g/L,re:concentracao 0,5g/L,im:concentracao 0,5g/L,re:concentracao 0,75g/L,im:concentracao 0,75g/L,re:concentracao 1,0g/L,im:concentracao 1,0g/L\n')

        # Escrever dados
        for index, row in df.iterrows():
            file.write(','.join(f'{val:.16E}' for val in row) + ',\n')

# Caminhos dos arquivos
df = gerar_df('cap3_capi_p1_water.dat', 'cap3_capi_p1_0_01_plstc.dat', 'cap3_capi_p1_0_05_plstc.dat', 'cap3_capi_p1_0_75_plstc.dat', 'cap3_capi_p1_1_plstc.dat')

# Salvar o DataFrame no arquivo .dat
nome = 'Cap_Capilar_300um(3).dat'
salvar_arquivo_dat(df, nome)