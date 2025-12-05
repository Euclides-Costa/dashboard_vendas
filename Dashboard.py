import streamlit as st
import requests # Fazer a leitura dos dados da api
import pandas as pd
import plotly.express as px 

# Deixar centralizado 
st.set_page_config(layout = 'wide')

# Funções
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS 🛒')

# Caminho dos dados
url = 'https://labdados.com/produtos' 

# Filtrando por região 
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

## Criando barra lateral
st.sidebar.title('Filtros')

regiao = st.sidebar.selectbox('Região', regioes)

# Seleciona todas as regiões
if regiao == 'Brasil':
    regiao = ''

# Filtragem por ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)

if todos_anos:
    ano = ''
else:
    # Cria um slider para selcionar o ano entre 2020 e 2023
    ano = st.sidebar.slider('Ano', 2020, 2023)

# Passando as modificações para a URL
query_string = {'regiao':regiao.lower(), 'ano':ano}

# Armazena o resultado da requisição, é um json
response = requests.get(url, params=query_string)

# Transfotmando de json para dataframe
dados = pd.DataFrame.from_dict(response.json()) 

# Formatando data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format= '%d/%m/%Y')

# Filtro dos vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# Tabelas
## Tabelas de receitas (aba 1)
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

receita_mesal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))[['Preço']].sum().reset_index()
receita_mesal['Ano'] = receita_mesal['Data da Compra'].dt.year
receita_mesal['Mes'] = receita_mesal['Data da Compra'].dt.month

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Tabelas de quantidade de vendas (aba 2)
qtd_vendas_estado = dados.groupby('Local da compra').size().reset_index(name='Quantidade de vendas')

qtd_vendas_estado = (
    dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']]
    .merge(qtd_vendas_estado, on='Local da compra')
    .sort_values('Quantidade de vendas', ascending=False)
)

qtd_vendas_mesal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M')).size().reset_index(name='Quantidade de vendas')
qtd_vendas_mesal['Ano'] = qtd_vendas_mesal['Data da Compra'].dt.year
qtd_vendas_mesal['Mes'] = qtd_vendas_mesal['Data da Compra'].dt.month

top_5_qtd_vendas_estado = qtd_vendas_estado.nlargest(5, 'Quantidade de vendas') # nlargest seleciona apenas as 5 maiores quantidades de vendas

qtd_vendas_categorias = dados.groupby('Categoria do Produto').size().reset_index(name='Quantidade de produtos')

## Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])) # Cria as colunas de suma e contagem

# Gráficos
## Mapa receita por estado
fig_mapa_receita = px.scatter_geo(receita_estados,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Preço',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Receita por Estado')

## Mapa qtd_vendas por estado
fig_mapa_qtd_vendas = px.scatter_geo(qtd_vendas_estado,
                                   lat = 'lat',
                                   lon = 'lon',
                                   scope = 'south america',
                                   size = 'Quantidade de vendas',
                                   template = 'seaborn',
                                   hover_name = 'Local da compra',
                                   hover_data = {'lat':False,'lon':False},
                                   title = 'Quantidade de vendas por Estado')

## Gráfico de linhas
fig_receita_mensal = px.line(receita_mesal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True, # Coloca um ponto em cada mês
                             range_y = (0, receita_mesal.max()), # Começar o gráfico em zero
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal') 

## Gráfico de linhas quantidade de vendas
fig_qtd_vendas_mensal = px.line(qtd_vendas_mesal,
                             x = 'Mes',
                             y = 'Quantidade de vendas',
                             markers = True, # Coloca um ponto em cada mês
                             range_y = (0, receita_mesal.max()), # Começar o gráfico em zero
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Quantidade de Vendas Mensal')

## Altera o eixo y
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

## Gráfico de barras
fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True, # Vai indicar que o valor de cada receita vai ficar em cima de cada coluna
                             title = 'Top estados (receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

## Gráfico de barras
fig_receita_categorias = px.bar(receita_categorias,
                               text_auto=True,
                               title='Receita por categoria')

## Altera o eixo y
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


fig_top_5_qtd_vendas = px.bar(
            top_5_qtd_vendas_estado, 
            x='Local da compra', 
            y='Quantidade de vendas',
            text_auto=True,
            title=f'Top {5} vendas por estados'
            )

fig_qtd_vendas_categoria = px.bar(
            qtd_vendas_categorias, 
            x='Categoria do Produto', 
            y='Quantidade de produtos',
            text_auto=True,
            title=f'Quantidade de vendas por categoria'
            )


# Visualização no streamlit
## Criando abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    # Melhorando a visualização das métricas
    coluna1, coluna2 = st.columns(2)
    with coluna1: # Acessa as colunas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True) # O gráfico não pode ultrapassar o tamanho da coluna: use_container_width = True
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    # Melhorando a visualização das métricas
    coluna1, coluna2 = st.columns(2)
    with coluna1: # Acessa as colunas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_qtd_vendas, use_container_width=True)
        st.plotly_chart(fig_top_5_qtd_vendas, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtd_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_qtd_vendas_categoria, use_container_width = True)

with aba3:
    # Construindos interações
    qtd_vendedores = st.number_input('Quantidade de vendedores: ', 2, 10,5) # No mínimo 2 números, máximo 10  e começa no 5

    coluna1, coluna2 = st.columns(2)
    with coluna1: # Acessa as colunas
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        # Receita total X Vendedor
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores), 
            x='sum', 
            y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (receita)'
            )
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(
            vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), 
            x='count', 
            y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (quantiade de vendas)'
            )
        st.plotly_chart(fig_vendas_vendedores)

# Representando dados
# st.dataframe(dados)
# st.dataframe(qtd_vendas_categorias)