import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Carregar os dados
leads_data = pd.read_csv('TabelaPesquisaUTMsn.csv')
sales_data = pd.read_csv('TabelaVendas.csv')
persona_data = pd.read_csv('TabelaPesquisa.csv')
ads_data = pd.read_csv('TabelaAdsLinks.csv')

# Renomear colunas "Unnamed" e remover "id2"
for df in [leads_data, sales_data, persona_data, ads_data]:
    df.rename(columns=lambda x: 'id' if x.startswith('Unnamed: 0.1') else ('id2' if x.startswith('Unnamed: 0') else x), inplace=True)
    if 'id2' in df.columns:
        df.drop(columns='id2', inplace=True)
        
# Estudo de Análise de Dados de Lançamento de Produto
st.title('Estudo de Análise de Dados de Lançamento de Produto')

# Introdução
st.markdown("""
Este estudo tem como objetivo analisar dados fictícios de um lançamento de produto, utilizando técnicas de Business Intelligence (BI) para extrair insights úteis que podem auxiliar em futuras campanhas de marketing e estratégias de vendas. Ressaltamos que os dados utilizados são fictícios, o que implica que a precisão das análises e conclusões não reflete a realidade, mas serve como um exemplo prático de como essas análises podem ser realizadas.

Os dados fornecidos estão distribuídos em quatro tabelas principais:
- **Dados de Leads Inscritos:** Contém informações sobre os leads que se inscreveram para participar do lançamento, incluindo o e-mail e os parâmetros UTM que indicam a origem do lead.
- **Dados de Compradores:** Composta apenas pelo e-mail dos leads que efetivamente compraram a oferta realizada no lançamento.
- **Dados da Pesquisa de Persona:** Coletados durante a captação de leads, fornecem informações adicionais como idade, renda e há quanto tempo o lead conhece o expert.
- **Dados dos Anúncios:** Contém links para anúncios que foram utilizados como origem dos leads e informações adicionais sobre os anúncios.

### Análises Realizadas

1. **Taxa de Conversão por Canal de Origem**
   A taxa de conversão é uma métrica essencial que indica a eficácia de cada canal de marketing em converter leads em compradores. Para calcular essa taxa, juntamos os dados de leads inscritos com os dados de compradores e calculamos a proporção de leads que se converteram em compradores para cada canal de origem.

2. **Taxa de Conversão por Parâmetro UTM**
   Os parâmetros UTM (Source, Medium e Term) fornecem informações detalhadas sobre a origem dos leads. A análise da taxa de conversão para cada combinação de parâmetros UTM ajuda a identificar quais campanhas, anúncios e palavras-chave são mais eficazes na conversão de leads.

3. **Taxa de Conversão por Perfil de Persona**
   Ao analisar os perfis dos leads (idade, renda e quanto tempo conhecem o expert), podemos identificar quais grupos demográficos têm maior probabilidade de se converterem em compradores. Isso é útil para direcionar futuras campanhas de marketing para os segmentos mais promissores.

4. **Objetivo da Pesquisa de Persona**
   A pesquisa de persona fornece uma visão mais profunda sobre os leads, permitindo identificar características que diferenciam compradores de não compradores. Esta análise ajuda a entender melhor o público-alvo e ajustar as estratégias de marketing de acordo.
""")

# Exibir os dados com filtros e navegação
st.write("## Dados de Leads Inscritos")
st.dataframe(leads_data)

st.write("## Dados de Compradores")
st.dataframe(sales_data)

st.write("## Dados da Pesquisa de Persona")
st.dataframe(persona_data)

st.write("## Dados dos Anúncios")
st.dataframe(ads_data)


# Análise dos Anúncios mais Repetidos na UTM Term
utm_term_count = leads_data['utmterm'].value_counts().reset_index()
utm_term_count.columns = ['UTM Term', 'Frequency']
utm_term_count = utm_term_count.merge(ads_data[['utmterm', 'instagram_permalink_url']], left_on='UTM Term', right_on='utmterm', how='left')
utm_term_count.drop(columns='utmterm', inplace=True)
utm_term_count.columns = ['UTM Term', 'Frequency', 'Instagram Link']
top_utm_terms = utm_term_count.head(10)

st.write("## Anúncios mais Repetidos na UTM Term")
st.dataframe(top_utm_terms)

# Gráfico dos Anúncios mais Repetidos na UTM Term
fig = px.bar(top_utm_terms, x='UTM Term', y='Frequency', title='Anúncios mais Repetidos na UTM Term', text='Frequency')
st.plotly_chart(fig)

# Explicação
st.write("""
### Análise dos Anúncios mais Repetidos na UTM Term
Nesta análise, identificamos os anúncios mais frequentes na coluna `utmterm` e associamos cada um deles aos links correspondentes do Instagram. Esses dados são fundamentais para entender quais criativos estão gerando maior engajamento e tráfego para a campanha.
Os termos sem links (`barriga-negativa`, `[BIO]`, e `[STORIES]`) indicam fontes de tráfego específicas e são autoexplicativos. `barriga-negativa` provavelmente se refere a um conceito ou tema específico, enquanto `[BIO]` e `[STORIES]` indicam tráfego vindo diretamente da bio de um perfil e dos stories do Instagram, respectivamente.
""")

# Análise da Taxa de Conversão por Canal de Origem
conversion_by_source = leads_data.merge(sales_data, on='email', how='left', indicator=True)
conversion_by_source['is_buyer'] = (conversion_by_source['_merge'] == 'both').astype(int)
conversion_rate_by_source = conversion_by_source.groupby('utmsource')['is_buyer'].mean().reset_index()
conversion_rate_by_source.columns = ['Source', 'Conversion Rate']

st.write("## Taxa de Conversão por Canal de Origem")
st.dataframe(conversion_rate_by_source)

# Gráfico da Taxa de Conversão por Canal de Origem
fig = px.bar(conversion_rate_by_source, x='Source', y='Conversion Rate', title='Taxa de Conversão por Canal de Origem', text='Conversion Rate')
st.plotly_chart(fig)
st.write("### Explicação")
st.write("O gráfico acima mostra a taxa de conversão para cada canal de origem. Podemos observar quais canais de marketing são mais eficazes na conversão de leads em compradores.")

# Análise da Taxa de Conversão por Parâmetro UTM
conversion_by_utm = leads_data.merge(sales_data, on='email', how='left', indicator=True)
conversion_by_utm['is_buyer'] = (conversion_by_utm['_merge'] == 'both').astype(int)
conversion_rate_by_utm = conversion_by_utm.groupby(['utmsource', 'utmmedium', 'utmterm'])['is_buyer'].mean().reset_index()
conversion_rate_by_utm.columns = ['Source', 'Medium', 'Term', 'Conversion Rate']

# Destacar os parâmetros UTM mais relevantes
top_utm = conversion_rate_by_utm.sort_values(by='Conversion Rate', ascending=False).head(10)

st.write("## Taxa de Conversão por Parâmetro UTM")
st.dataframe(top_utm)

# Gráfico da Taxa de Conversão por Parâmetro UTM
fig = px.bar(top_utm, x='Source', y='Conversion Rate', color='Medium', barmode='group', title='Taxa de Conversão por Parâmetro UTM', text='Conversion Rate')
st.plotly_chart(fig)
st.write("### Explicação")
st.write("O gráfico acima mostra a taxa de conversão para os principais parâmetros UTM. Analisamos as combinações de Source, Medium e Term para identificar quais campanhas e anúncios são mais eficazes na conversão de leads em compradores.")

# Análise da Taxa de Conversão por Perfil de Persona
persona_conversion = persona_data.merge(sales_data, on='email', how='left', indicator=True)
persona_conversion['is_buyer'] = (persona_conversion['_merge'] == 'both').astype(int)
conversion_rate_by_persona = persona_conversion.groupby(['idade', 'renda', 'tempo_me_conhece'])['is_buyer'].mean().reset_index()
conversion_rate_by_persona.columns = ['Age', 'Income', 'Time Knowing Expert', 'Conversion Rate']

# Destacar os perfis de persona mais relevantes
top_persona = conversion_rate_by_persona.sort_values(by='Conversion Rate', ascending=False).head(10)

st.write("## Taxa de Conversão por Perfil de Persona")
st.dataframe(top_persona)

# Gráfico da Taxa de Conversão por Perfil de Persona
fig = px.bar(top_persona, x='Age', y='Conversion Rate', color='Income', barmode='group', title='Taxa de Conversão por Perfil de Persona', text='Conversion Rate')
st.plotly_chart(fig)
st.write("### Explicação")
st.write("O gráfico acima mostra a taxa de conversão para diferentes perfis de persona. Analisamos a idade, renda e quanto tempo o lead conhece o expert para identificar quais grupos têm maior probabilidade de se converter em compradores.")

# Análise de Criativos (UTM Term) e Públicos (UTM Medium)
utm_analysis = leads_data.merge(sales_data, on='email', how='left', indicator=True)
utm_analysis['is_buyer'] = (utm_analysis['_merge'] == 'both').astype(int)

utm_term_analysis = utm_analysis.groupby('utmterm')['is_buyer'].mean().reset_index().sort_values(by='is_buyer', ascending=False).head(10)
utm_medium_analysis = utm_analysis.groupby('utmmedium')['is_buyer'].mean().reset_index().sort_values(by='is_buyer', ascending=False).head(10)

utm_term_analysis.columns = ['Creative (UTM Term)', 'Conversion Rate']
utm_medium_analysis.columns = ['Public (UTM Medium)', 'Conversion Rate']

st.write("## Análise de Criativos (UTM Term)")
st.dataframe(utm_term_analysis)

fig = px.bar(utm_term_analysis, x='Creative (UTM Term)', y='Conversion Rate', title='Taxa de Conversão por Criativo (UTM Term)', text='Conversion Rate')
st.plotly_chart(fig)
st.write("### Explicação")
st.write("O gráfico acima mostra a taxa de conversão para cada criativo (UTM Term). Isso nos permite identificar quais criativos estão gerando mais conversões e são mais eficazes nas campanhas de marketing.")

st.write("## Análise de Públicos (UTM Medium)")
st.dataframe(utm_medium_analysis)

fig = px.bar(utm_medium_analysis, x='Public (UTM Medium)', y='Conversion Rate', title='Taxa de Conversão por Público (UTM Medium)', text='Conversion Rate')
st.plotly_chart(fig)

st.write("### Explicação")
st.write("O gráfico acima mostra a taxa de conversão para cada público (UTM Medium). Isso ajuda a entender quais públicos-alvo têm maior probabilidade de conversão e como otimizar campanhas futuras para esses segmentos.")


    
# Salvar resultados para análise no Power BI
conversion_rate_by_source.to_csv('conversion_rate_by_source.csv', index=False)
conversion_rate_by_utm.to_csv('conversion_rate_by_utm.csv', index=False)
conversion_rate_by_persona.to_csv('conversion_rate_by_persona.csv', index=False)
utm_term_analysis.to_csv('utm_term_analysis.csv', index=False)
utm_medium_analysis.to_csv('utm_medium_analysis.csv', index=False)
if 'data' in leads_data.columns and pd.api.types.is_datetime64_any_dtype(leads_data['data']):
    conversion_over_time.to_csv('conversion_over_time.csv', index=False)

# Explicação do Código
st.header('Explicação do Código')

st.subheader('Carregamento e Pré-processamento dos Dados:')
st.markdown("""
Utilizamos a biblioteca pandas para carregar os dados de quatro tabelas principais: leads_data, sales_data, persona_data e ads_data (Essas respectivas tabelas são os CSV's: TabelaPesquisaUTMsn, TabelaVendas, TabelaPesquisa e TabelaAdsLinks) que contêm informações sobre leads inscritos, compradores, pesquisa de persona e anúncios, respectivamente.
Renomeamos as colunas 'Unnamed' para 'id' e 'id2' para melhorar a clareza dos dados e, em seguida, removemos a coluna 'id2' se existir.
""")

st.write("""
## Análise da Taxa de Conversão

A taxa de conversão em todos os casos foi calculada através de uma abordagem similar, mas aplicada a diferentes grupos ou parâmetros. A seguir, detalho cada passo que foi utilizado no código para calcular a taxa de conversão:

### 1. Taxa de Conversão por Canal de Origem

Para calcular a taxa de conversão por canal de origem, seguimos os seguintes passos:
- Juntamos os dados de leads (leads_data) com os dados de compradores (sales_data) com base no campo email.
- Criamos uma nova coluna `is_buyer` para indicar se o lead se converteu em comprador (1 para sim, 0 para não).
- Agrupamos os dados pelo campo `utmsource` (canal de origem) e calculamos a média de `is_buyer` para obter a taxa de conversão por canal de origem.

### 2. Taxa de Conversão por Parâmetro UTM

Para calcular a taxa de conversão por parâmetro UTM, seguimos os seguintes passos:
- Juntamos os dados de leads (leads_data) com os dados de compradores (sales_data) com base no campo email.
- Criamos uma nova coluna `is_buyer` para indicar se o lead se converteu em comprador (1 para sim, 0 para não).
- Agrupamos os dados pelos campos `utmsource`, `utmmedium` e `utmterm` e calculamos a média de `is_buyer` para obter a taxa de conversão por parâmetro UTM.

### 3. Taxa de Conversão por Perfil de Persona

Para calcular a taxa de conversão por perfil de persona, seguimos os seguintes passos:
- Juntamos os dados de persona (persona_data) com os dados de compradores (sales_data) com base no campo email.
- Criamos uma nova coluna `is_buyer` para indicar se o lead se converteu em comprador (1 para sim, 0 para não).
- Agrupamos os dados pelos campos `idade`, `renda` e `tempo_me_conhece` e calculamos a média de `is_buyer` para obter a taxa de conversão por perfil de persona.

### 5. Análise de Criativos (UTM Term) e Públicos (UTM Medium)

Para analisar a taxa de conversão por criativos (UTM Term) e públicos (UTM Medium), seguimos os seguintes passos:
- Juntamos os dados de leads (leads_data) com os dados de compradores (sales_data) com base no campo email.
- Criamos uma nova coluna `is_buyer` para indicar se o lead se converteu em comprador (1 para sim, 0 para não).
- Agrupamos os dados pelos campos `utmterm` e `utmmedium` e calculamos a média de `is_buyer` para cada um deles.

Em resumo, a taxa de conversão foi calculada como a média da coluna `is_buyer` após agrupar os dados pelos diferentes parâmetros de interesse (como `utmsource`, `utmmedium`, `utmterm`, `idade`, `renda`, e `tempo_me_conhece`). Essa abordagem permitiu determinar a eficácia de diferentes canais, campanhas, e perfis de persona em converter leads em compradores.
""")



st.subheader('Análise de Criativos (UTM Term) e Públicos (UTM Medium):')
st.markdown("""
Realizamos a análise dos criativos (utm term) e dos públicos (utm medium) para identificar quais criativos e públicos estão gerando mais conversões.
Agrupamos os dados pelos campos 'utmterm' e 'utmmedium' e calculamos a média de is_buyer para cada um deles.
""")

st.subheader('Visualização dos Dados:')
st.markdown("""
Utilizamos a biblioteca plotly.express para criar gráficos interativos (barras, scatter plot) que mostram as taxas de conversão e insights das análises realizadas.
Cada gráfico é acompanhado por uma explicação que destaca os principais pontos observados e como essas informações podem ser úteis para ajustar estratégias futuras.
""")





