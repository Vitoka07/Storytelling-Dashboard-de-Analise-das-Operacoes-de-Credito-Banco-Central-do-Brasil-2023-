# 1. IMPORTAR BIBLIOTECAS
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os
import glob
from pathlib import Path
import dask.dataframe as dd 
import time


start_time = time.time()


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

# 3. CARREGAMENTO E TRATAMENTO (Baixe o arquvivo CSv disponibilizado no Readme ou aqui "https://www.bcb.gov.br/pda/desig/planilha_2023.zip")

# 3.1. CARREGAMENTO DOS DADOS (mude o caminho para o local onde estão os arquivos CSV do seu computador)
caminho_csvs = Path("")
csv_files = str(caminho_csvs / '*.csv')
df_consolidado = dd.read_csv(csv_files, encoding='utf-8', delimiter=';', dtype='object', on_bad_lines='skip')
# Exibir os dados brutos
print(df_consolidado.head(50))
print(df_consolidado.dtypes)


# 3.2. TRATAMENTO DOS DADOS 
# Converter as colunas de string em float
colunas_para_converter = [
    'carteira_inadimplida_arrastada', 'a_vencer_ate_90_dias', 
    'a_vencer_de_91_ate_360_dias', 'a_vencer_de_361_ate_1080_dias', 
    'a_vencer_de_1081_ate_1800_dias', 'a_vencer_de_1801_ate_5400_dias', 
    'a_vencer_acima_de_5400_dias', 'vencido_acima_de_15_dias', 
    'carteira_ativa', 'ativo_problematico', 'numero_de_operacoes'
]
def converter_para_float(valor):
    if isinstance(valor, str):
        valor = valor.replace('.', '').replace(',', '.')
    try:
        return float(valor)
    except ValueError:
        return 0.0  
for coluna in colunas_para_converter:
    df_consolidado[coluna] = df_consolidado[coluna].map(converter_para_float, meta=('coluna', 'float64'))

# Converter a coluna data_base para data
df_consolidado['data_base'] = dd.to_datetime(df_consolidado['data_base'], format='%Y-%m-%d', errors='coerce')

# Adicionando as regiões
regioes = {
    'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}
estado_para_regiao = {estado: regiao for regiao, estados in regioes.items() for estado in estados}

def mapear_regiao(uf):
    return estado_para_regiao.get(uf, 'Desconhecido')

df_consolidado['regiao'] = df_consolidado['uf'].map(mapear_regiao, meta=('x', 'object'))

# Adicionando a coluna do nome do mês e ano
df_consolidado['mes'] = df_consolidado['data_base'].dt.month
df_consolidado['ano'] = df_consolidado['data_base'].dt.year

# Adicionando a coluna Inadimplente (Sim/Não)
df_consolidado['inadimplente'] = df_consolidado['carteira_inadimplida_arrastada'].apply(lambda x: 'sim' if x > 0 else 'não')



# 4. TÍTULO DASHBOARD
with st.container():
    st.write("<h4 style='color:green; font-size:20px;'> MBA Ciência de Dados e Inteligência Artificial </h4>", unsafe_allow_html=True)
    st.write("<h4 style='color:green; font-size:20px;'> Projeto da Comunicação e Apresentação de Resultados (Prof. Alex Cordeiro) * Outubro - Novembro 2024 </h4>", unsafe_allow_html=True)
    st.write("<h1 style='color:black;'>Análise das Operações de Crédito do Banco Central do Brasil</h1>", unsafe_allow_html=True)
    st.write("<h5 style='color:black;'>Série histórica: 2023</h5>", unsafe_allow_html=True)
    st.write("<h5 style='color:black;'>Fonte: Gov.br - Banco Centro do Brasil</h5>", unsafe_allow_html=True)
    st.write("<h9 style='color:black; font-style: italic;'>Órgão responsável por garantir a estabilidade do poder de compra da moeda.</h9>", unsafe_allow_html=True)
    st.write("<h7 style='color:black;'>Quer acessar a fonte de dados? <a href='https://www.bcb.gov.br/pda/desig/planilha_2023.zip' target='_blank'>Clique aqui</a></h7>", unsafe_allow_html=True)
    st.write("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
    st.write("<h5 style='color:black;'> Objetivo: </h5>", unsafe_allow_html=True)
    st.write("<h8 style='color:black;'> Funcionar por favor</h8>", unsafe_allow_html=True)
    st.write("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

# 4. CRIANDO UM MENU LATERAL
st.sidebar.image("https://i.postimg.cc/pd2HC7Yy/logo-SENAC-bco.png", width=150)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Gov.br_logo.svg/2560px-Gov.br_logo.svg.png", width=150)
st.sidebar.image("https://logos-download.com/wp-content/uploads/2018/01/Banco_Central_do_Brasil_logo-700x176.png", width=280)
st.sidebar.header("Filtros")

# Visualizar uma amostra do DataFrame consolidado no terminal
print(df_consolidado.head(5))


# 5 FILTRANDO O DATAFRAME

filtro_ano = st.sidebar.multiselect("Ano", options=df_consolidado['ano'].unique().compute(), default=df_consolidado['ano'].unique().compute())
filtro_mes = st.sidebar.multiselect('Meses', options=df_consolidado['mes'].unique().compute(), default=df_consolidado['mes'].unique().compute())

df_filtrado = df_consolidado

# Aplicando o filtro de ano
if len(filtro_ano) > 0:
    df_filtrado = df_filtrado[df_filtrado['ano'].isin(filtro_ano)]

# Aplicando o filtro de mês
if len(filtro_mes) > 0:
    df_filtrado = df_filtrado[df_filtrado['mes'].isin(filtro_mes)]


df_filtrado = df_filtrado.persist()

# Função para formatar o número de forma compactada
def formatar_valor_compactado(valor):
    # Verificar se o valor é maior ou igual a 1 trilhão
    if valor >= 1_000_000_000_000:
        return f"R$ {valor / 1_000_000_000_000:.2f}T"  # Trilhão
    # Verificar se o valor é maior ou igual a 1 milhão
    elif valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f}M"  # Milhão
    # Verificar se o valor é maior ou igual a 1 mil
    elif valor >= 1_000:
        return f"R$ {valor / 1_000:.2f}K"  # Mil
    else:
        return f"R$ {valor:.2f}"  # Menor que 1 mil
 
# Verificar se a coluna 'vlrtotalpago' existe no DataFrame
if 'carteira_inadimplida_arrastada' in df_filtrado.columns:
    # Somar todos os valores não nulos (ignorando NaN)
    total = df_filtrado['carteira_inadimplida_arrastada'].dropna().sum()
   
    # Formatar o valor de forma compactada
    total_formatado = formatar_valor_compactado(total.compute())



# Contagem dos valores "sim" e "não" na coluna 'inadimplente'
contagem_inadimplencia = df_filtrado['inadimplente'].value_counts()
contagem_inadimplencia = contagem_inadimplencia.compute()

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
col1.markdown(f"<p style='font-size: 50px; color: #1e1e1e'>{(total_inadimplentes_formatado)}</p>", unsafe_allow_html=True)
 
col2.markdown(f"<h2 style='font-size: 24px; color: #0958D9;'>Pessoas Nadiplemtes</h2>", unsafe_allow_html=True)
col2.markdown(f"<p style='font-size: 50px; color: #1e1e1e'>{(total_nao_inadimplentes_formatado)}</p>", unsafe_allow_html=True)
 
col3.markdown(f"<h2 style='font-size: 24px; color: #0958D9;'>Valor de Inadimplencia </h2>", unsafe_allow_html=True)
col3.markdown(f"<p style='font-size: 50px; color: #1e1e1e'>{(total_formatado)}</p>", unsafe_allow_html=True)
 

st.write("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

# Equipe
st.sidebar.header("Equipe")
st.sidebar.image("https://i.postimg.cc/C1YQkKL7/Equipe.png", width=200)



# TOP 8 MODALIDADE POR NÚMERO DE OPERAÇÃO
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:black;'> Top 5 Modalidades com Maior Número de Operações </h5>", unsafe_allow_html=True)

operacoes_por_modalidade = df_filtrado.groupby('modalidade')['numero_de_operacoes'].sum().reset_index()

# Ordenar e selecionar as 5 modalidades com maior número de operações
top_5_modalidades = operacoes_por_modalidade.nlargest(5, 'numero_de_operacoes')
top_5_modalidades = top_5_modalidades.compute()

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

st.write("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

# DISTRIBUIÇÃO DA PF E PJ
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:black;'> Distribuição Percentual de Clientes PF e PJ </h5>", unsafe_allow_html=True)

# Contar a quantidade de ocorrências de 'PF' e 'PJ' na coluna 'cliente'
distribuicao_cliente = df_consolidado['cliente'].value_counts(normalize=True) * 100
distribuicao_cliente = distribuicao_cliente.compute()
# Criar o gráfico de pizza
fig_porcentagem_cliente = px.pie(values=distribuicao_cliente, names=distribuicao_cliente.index, 
             labels={'label': 'Tipo de Cliente', 'value': 'Percentual (%)'})

# Exibir o gráfico no Streamlit
st.plotly_chart(fig_porcentagem_cliente)

st.write("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)



# TOP 8 MODALIDADE POR NÚMERO DE OPERAÇÃO
# Exibe um título para a seção no Streamlit com formatação HTML
st.write("<h5 style='color:black;'> Regiões com maior valor de Inadimplência </h5>", unsafe_allow_html=True)

regiao_inadimplentes = df_filtrado.groupby('regiao')['carteira_inadimplida_arrastada'].sum().reset_index()
regiao_inadimplentes = regiao_inadimplentes.compute()

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
st.write("<h5 style='color:black;'> Regiões com Maior Número de Pessoas Inadimplentes </h5>", unsafe_allow_html=True)

# Filtrar apenas os inadimplentes
inadimplentes_por_regiao = df_filtrado[df_filtrado['inadimplente'] == 'sim'].groupby('regiao').size()

# Resetar o índice e renomear a coluna de contagem
inadimplentes_por_regiao = inadimplentes_por_regiao.reset_index()
inadimplentes_por_regiao.columns = ['regiao', 'qtd_inadimplentes']  # Renomear as colunas

# Realizar o cálculo com Dask (caso o DataFrame seja do Dask)
inadimplentes_por_regiao = inadimplentes_por_regiao.compute()

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

total_time = time.time() - start_time
st.write(f"Tempo levado para o processamento complento: {total_time:.2f} segundos")