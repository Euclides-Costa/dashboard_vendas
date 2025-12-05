import streamlit as st
import requests
import pandas as pd
import time

# Função para o download
@st.cache_data
def convert_csv(df):
    return df.to_csv(index = False).encode('utf-8') # index = False não armazena a informação do indece

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5) # Aparece a mensagem por 5 segundos
    sucesso.empty() # Remove a visualização

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
# Transfotmando de json para dataframe
dados = pd.DataFrame.from_dict(response.json())

# Formatando data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')


# Ocultar os filtros
with st.expander('Colunas'): # Deixa o nome das colunas ocultas
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns)) # O primeiro termo é o conjunto de dados e o segundo são os termos iniciais selecionados

# Filtros barra lateral
st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))

with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))




# Filtragem das colunas

## String de várias linhas
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv' # Manter o arquivo no formato correto

with coluna2:
    st.download_button('Fazer o download da tabela em csv', data=convert_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
