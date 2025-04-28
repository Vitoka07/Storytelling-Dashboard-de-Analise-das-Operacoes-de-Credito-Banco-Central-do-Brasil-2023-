# 1. IMPORTAR BIBLIOTECAS
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os
import glob

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard", layout="wide")

# CSS personalizado
st.markdown("""
    <style>
    /* Alterar a cor de fundo da barra lateral (filtros) */
    [data-testid="stSidebar"] {
        background-color: #1F537D;
    }
    /* Centralizar imagem na barra lateral */
    [data-testid="stSidebar"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    /* Alterar cor de fundo da área principal */
    .main {
        background-color: #D2D5D8;
    }
    /* Centralizar texto da barra lateral */
    [data-testid="stSidebar"] .sidebar-content {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 3. CARREGAMENTO E TRATAMENTO

# Definir o caminho da pasta onde os arquivos .csv estão armazenados
caminho_csvs = "C:/Users/VINICIUS-PC/Desktop/Faculdade/Projetos/Storytelling - Análise das Operações de Crédito do Banco Central do Brasil/dados"

# Obter a lista de todos os arquivos .csv na pasta
arquivos_csv = glob.glob(os.path.join(caminho_csvs, "planilha_2023*.csv"))

# Lista para armazenar cada DataFrame
lista_dfs = []

# Mapeamento de número do mês para nome do mês
meses_map = {
    '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
    '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
    '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
}

regioes = {
    'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

# Listar as colunas com valores monetários em formato de string
colunas_monetarias = [
    'carteira_inadimplida_arrastada', 'a_vencer_ate_90_dias', 'a_vencer_de_91_ate_360_dias', 
    'a_vencer_de_361_ate_1080_dias', 'a_vencer_de_1081_ate_1800_dias', 
    'a_vencer_de_1801_ate_5400_dias', 'a_vencer_acima_de_5400_dias', 
    'vencido_acima_de_15_dias', 'carteira_ativa', 'ativo_problematico'
]

# Ler todos os arquivos .csv e criar coluna 'Data' no formato Mês/Ano
for arquivo in arquivos_csv:
    try:
        # Ler o arquivo csv em um DataFrame com delimitador ";"
        df = pd.read_csv(arquivo, sep=';', on_bad_lines='skip')
        
       # Extrair o ano e mês do nome do arquivo (assumindo o formato "planilha_2023MM.csv")
        nome_arquivo = os.path.basename(arquivo)
        ano_mes = nome_arquivo.split('_')[1].split('.')[0]  # Extrai "202301" por exemplo
        ano, mes = ano_mes[:4], ano_mes[4:6]  # "2023", "01"
        
        # Criar colunas 'ano' e 'mes' com os valores extraídos, convertendo o mês para o nome
        df['ano'] = ano
        df['mes'] = meses_map[mes]  # Converte o número do mês para o nome do mês
        
        # Verificar se o DataFrame não está vazio antes de adicionar à lista
        if not df.empty:
            lista_dfs.append(df)
    except Exception as e:
        print(f"Erro ao ler o arquivo {arquivo}: {e}")

# Realiza a união de todos os DataFrames em um único DataFrame consolidado
df_consolidado = pd.concat(lista_dfs, ignore_index=True)

# Remover colunas duplicadas, se houver
df_consolidado = df_consolidado.loc[:, ~df_consolidado.columns.duplicated()]

# Excluir as colunas indesejadas, incluindo 'data_base' se necessário
colunas_a_excluir = ['data_base', 'sr', 'cnae_subclasse']
df_consolidado = df_consolidado.drop(columns=colunas_a_excluir, errors='ignore')

def obter_regiao(uf):
    for regiao, estados in regioes.items():
        if uf in estados:
            return regiao
    return 'Outros'  # Caso encontre alguma UF fora das regiões conhecidas

# Aplicando a função para criar a coluna 'região' no DataFrame consolidado
df_consolidado['regiao'] = df_consolidado['uf'].apply(obter_regiao)


# Loop para limpar e converter cada coluna para float
for coluna in colunas_monetarias:
    df_consolidado[coluna] = (
        df_consolidado[coluna]
        .replace(r'[R$\.,]', '', regex=True)  # Remove o símbolo de moeda e os separadores
        .str.replace(',', '.')               # Substitui a vírgula decimal por ponto
        .astype(float)                       # Converte para float
    )


# TRATAMENTO DA COLUNA 'numero_de_operacoes'
# Substituir o valor '<= 15' por 15 na coluna 'numero_de_operacoes'
df_consolidado['numero_de_operacoes'] = df_consolidado['numero_de_operacoes'].replace('<= 15', 15)

# Converter a coluna para o tipo numérico
df_consolidado['numero_de_operacoes'] = pd.to_numeric(df_consolidado['numero_de_operacoes'], errors='coerce')

# Criando a coluna Inadimplente (Sim / Não)
df_consolidado['inadimplente'] = df_consolidado['carteira_inadimplida_arrastada'].apply(lambda x: 'sim' if x > 0 else 'não')


# 4. TÍTULO DASHBOARD
with st.container():
    st.write("<h4 style='color:green; font-size:20px;'> MBA Ciência de Dados e Inteligência Artificial </h4>", unsafe_allow_html=True)
    st.write("<h4 style='color:green; font-size:20px;'> Projeto da Comunicação e Apresentação de Resultados (Prof. Alex Cordeiro) * Outubro - Novembro 2024 </h4>", unsafe_allow_html=True)
    st.write("<h1 style='color:white;'>Análise das Operações de Crédito do Banco Central do Brasil</h1>", unsafe_allow_html=True)
    st.write("<h5 style='color:white;'>Série histórica: 2023</h5>", unsafe_allow_html=True)
    st.write("<h5 style='color:white;'>Fonte: Gov.br - Banco Centro do Brasil</h5>", unsafe_allow_html=True)
    st.write("<h9 style='color:white; font-style: italic;'>Órgão responsável por garantir a estabilidade do poder de compra da moeda.</h9>", unsafe_allow_html=True)
    st.write("<h7 style='color:white;'>Quer acessar a fonte de dados? <a href='https://www.bcb.gov.br/pda/desig/planilha_2023.zip' target='_blank'>Clique aqui</a></h7>", unsafe_allow_html=True)
    st.write("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)
    st.write("<h5 style='color:white;'> Objetivo: </h5>", unsafe_allow_html=True)
    st.write("<h8 style='color:white;'> Funcionar por favor</h8>", unsafe_allow_html=True)
    st.write("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)

# 4. CRIANDO UM MENU LATERAL
st.sidebar.image("https://i.postimg.cc/pd2HC7Yy/logo-SENAC-bco.png", width=150)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Gov.br_logo.svg/2560px-Gov.br_logo.svg.png", width=150)
st.sidebar.image("https://logos-download.com/wp-content/uploads/2018/01/Banco_Central_do_Brasil_logo-700x176.png", width=280)
st.sidebar.header("Filtros")

# Visualizar uma amostra do DataFrame consolidado no terminal
print(df_consolidado.head(5))


# 5 FILTRANDO O DATAFRAME

filtro_ano = st.sidebar.multiselect("Ano", options=df_consolidado['ano'].unique(), default=df_consolidado['ano'].unique())
filtro_mes = st.sidebar.multiselect('Meses', options=df_consolidado['mes'].unique(), default=df_consolidado['mes'].unique())

df_filtrado = df_consolidado

# Aplicando o filtro de ano
if len(filtro_ano) > 0:
    df_filtrado = df_filtrado[df_filtrado['ano'].isin(filtro_ano)]

# Aplicando o filtro de mês
if len(filtro_mes) > 0:
    df_filtrado = df_filtrado[df_filtrado['mes'].isin(filtro_mes)]


# Função para formatar o número de forma compactada
def formatar_valor_compactado(valor):
    if valor >= 1_000_000_000_000:
        return f"R$ {valor/1_000_000_000_000:.2f}T"  # Tilhões
    elif valor >= 1_000_000:
        return f"R$ {valor/1_000_000:.2f}M"  # Tilhões
    elif valor >= 1_000:
        return f"R$ {valor/1_000:.2f}M"  # Bilhões
    else:
        return f"R$ {valor:.2f}"  # Para valores menores que mil
 
# Verificar se a coluna 'vlrtotalpago' existe no DataFrame
if 'carteira_inadimplida_arrastada' in df_filtrado.columns:
    # Somar todos os valores não nulos (ignorando NaN)
    total = df_filtrado['carteira_inadimplida_arrastada'].dropna().sum()
   
    # Formatar o valor de forma compactada
    total_formatado = formatar_valor_compactado(total)



# Contagem dos valores "sim" e "não" na coluna 'inadimplente'
contagem_inadimplencia =df_filtrado['inadimplente'].value_counts()

# Extrair os valores de inadimplentes e não inadimplentes
total_inadimplentes = contagem_inadimplencia.get("sim", 0)
total_nao_inadimplentes = contagem_inadimplencia.get("não", 0)

# Função para formatar o número de forma compactada
def formatar_valor_compactado_Inadimplentes(valor):
    if valor >= 1_000_000_000_000:
        return f"{valor/1_000_000_000_000:.2f}T"  # Trilhão
    elif valor >= 1_000_000:
        return f"{valor/1_000_000:.2f}B"  # Bilhão
    elif valor >= 1_000:
        return f"{valor/1_000:.2f}M"  # Milhão
    else:
        return f"{valor:.2f}K"  # Para valores menores que mil

total_inadimplentes_formatado = formatar_valor_compactado_Inadimplentes(total_inadimplentes)
total_nao_inadimplentes_formatado = formatar_valor_compactado_Inadimplentes(total_nao_inadimplentes)


# Criar colunas
col1, col2, col3= st.columns(3)
 
# Formatação dos números
col1.markdown(f"<h2 style='font-size: 24px; color: #0958D9;'>Pessoas Inadimplentes</h2>", unsafe_allow_html=True)
col1.markdown(f"<p style='font-size: 50px; color: green'>{(total_inadimplentes_formatado)}</p>", unsafe_allow_html=True)
 
col2.markdown(f"<h2 style='font-size: 24px; color: #0958D9;'>Pessoas Nadiplemtes</h2>", unsafe_allow_html=True)
col2.markdown(f"<p style='font-size: 50px; color: green'>{(total_nao_inadimplentes_formatado)}</p>", unsafe_allow_html=True)
 
col3.markdown(f"<h2 style='font-size: 24px; color: #0958D9;'>Valor de Inadimplencia </h2>", unsafe_allow_html=True)
col3.markdown(f"<p style='font-size: 50px; color: green'>{(total_formatado)}</p>", unsafe_allow_html=True)
 

st.write("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)

# Equipe
st.sidebar.header("Equipe")
st.sidebar.image("https://i.postimg.cc/C1YQkKL7/Equipe.png", width=200)



# TOP 8 MODALIDADE POR NÚMERO DE OPERAÇÃO
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:white;'> Top 5 Modalidades com Maior Número de Operações </h5>", unsafe_allow_html=True)

operacoes_por_modalidade = df_filtrado.groupby('modalidade')['numero_de_operacoes'].sum().reset_index()

# Ordenar e selecionar as 5 modalidades com maior número de operações
top_5_modalidades = operacoes_por_modalidade.nlargest(5, 'numero_de_operacoes')

# Criar o gráfico de barras para as 5 maiores modalidades
fig_modalidade_operacao = px.bar(
    top_5_modalidades, 
    x='modalidade', 
    y='numero_de_operacoes', 
    labels={'numero_de_operacoes': 'Número de Operações', 'modalidade': 'Modalidade'},
    color='numero_de_operacoes'
)

# Formatando os rótulos de dados com a função formatar_valor_compactado
fig_modalidade_operacao.update_traces(
    text=[formatar_valor_compactado(valor) for valor in top_5_modalidades['numero_de_operacoes']],
    texttemplate='%{text}',  # Exibir o valor formatado
    textposition='outside'   # Posicionar o texto fora das barras
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_modalidade_operacao)

st.write("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)

# DISTRIBUIÇÃO DA PF E PJ
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:white;'> Distribuição Percentual de Clientes PF e PJ </h5>", unsafe_allow_html=True)

# Contar a quantidade de ocorrências de 'PF' e 'PJ' na coluna 'cliente'
distribuicao_cliente = df_consolidado['cliente'].value_counts(normalize=True) * 100

# Criar o gráfico de pizza
fig_porcentagem_cliente = px.pie(values=distribuicao_cliente, names=distribuicao_cliente.index, 
             labels={'label': 'Tipo de Cliente', 'value': 'Percentual (%)'})

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_porcentagem_cliente)

st.write("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)



# TOP 8 MODALIDADE POR NÚMERO DE OPERAÇÃO
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:white;'> Regiões com maior valor de Inadimplência </h5>", unsafe_allow_html=True)

regiao_inadimplentes = df_filtrado.groupby('regiao')['carteira_inadimplida_arrastada'].sum().reset_index()


# Criar o gráfico de barras para as 8 maiores modalidades
fig_regiao_valor = px.bar(regiao_inadimplentes, 
             x='regiao', y='carteira_inadimplida_arrastada', 
             labels={'carteira_inadimplida_arrastada': 'Valor (R$)', 'regiao': 'Região'},
             color='carteira_inadimplida_arrastada',
             )

# Formatando os rótulos de dados diretamente com a função formatar_valor_compactado
fig_regiao_valor.update_traces(
    text=[formatar_valor_compactado(valor) for valor in regiao_inadimplentes['carteira_inadimplida_arrastada']],
    texttemplate='%{text}',  # Mostrar o valor formatado
    textposition='outside'   # Posicionar o texto fora das barras
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_regiao_valor)



# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:white;'> Regiões com Maior Número de Pessoas Inadimplentes </h5>", unsafe_allow_html=True)

# Filtrar apenas os inadimplentes
inadimplentes_por_regiao = df_filtrado[df_filtrado['inadimplente'] == 'sim'].groupby('regiao').size().reset_index(name='qtd_inadimplentes')

# Criar o gráfico de barras para mostrar inadimplentes por região
fig_inadimplentes_regiao = px.bar(
    inadimplentes_por_regiao,
    x='regiao', 
    y='qtd_inadimplentes',
    labels={'qtd_inadimplentes': 'Quantidade de Inadimplentes', 'regiao': 'Região'},
    color='qtd_inadimplentes',
)

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_inadimplentes_regiao)