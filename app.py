import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

#Rodar o código com strealit > python -m streamlit run app.py

st.title("📊 Análise de Funcionários da empresa") #título da página
st.set_page_config(page_title='Análise de Funcionários', layout='wide', page_icon='📊') #título da página

st.sidebar.write("Upload do arquivo") #barra lateral
arquivo = st.sidebar.file_uploader('Selecione a planilha de funcionários',type=['xlsx'])#fazer o upload do arquivo em formato xlsx
st.page_link("https://www.linkedin.com/in/ogabrielpaivaa", label="LinkedIn", icon="📲")#botão linkedin

if arquivo:
    df = pd.read_excel(arquivo)

    df['Data de Contratacao'] = pd.to_datetime(df['Data de Contratacao'])
    df['Data de Demissao'] = pd.to_datetime(df['Data de Demissao'], errors='coerce')

    #Criar coluna de Status
    df['Status'] = df['Data de Demissao'].isna().map({True:'Ativo', False: 'Desligado'})

    #Criar cartões
    total_ativos = df[df['Status']== 'Ativo'].shape[0]
    total_desligados = df[df['Status']== 'Desligado'].shape[0]
    total_contratacoes = df['Data de Contratacao'].notna().sum()
    folha_salarial = (df['Salario'] + df['VR'] + df['VT']) [df['Status']=='Ativo'].sum()

    

    #filtros
    st.sidebar.markdown('### Filtros')
    status_opcoes = ['Ativo','Desligado']
    status_selecionado = st.sidebar.multiselect("Status", status_opcoes, default=status_opcoes)#cria os filtros laterais e o default deixa já selecionado por padrão os ativos e demitidos

    cargos = df['Cargo'].dropna().unique()
    cargos_selecionado = st.sidebar.multiselect('Cargos', sorted(cargos), default=cargos)

    

    df = df[
        (df['Status'].isin(status_selecionado)) &
        (df['Cargo'].isin(cargos_selecionado))
        ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ativos", total_ativos)
    col2.metric("Desligados", total_desligados)
    col3.metric("Contratações", total_contratacoes)
    col4.metric("Folha salarial", f"R$: {folha_salarial:,.2f}")

    #Criar abas dos gráficos
    aba1, aba2, aba3, aba4 = st.tabs(["Visão geral","Gráficos por área","Contratações vs Demissões","Tabela de dados"])
    with aba1:
        contar_cargos = df['Cargo'].value_counts()
        #fig = figura (o papel todo)
        #ax = Eixo (ou quadro) desenha os gráficos
        fig1, ax1 = plt.subplots()
        #Criar as barras
        barras = ax1.bar(contar_cargos.index, contar_cargos.values, color='#FF6701')
        ax1.set_title("Funcionários por cargo")
        #ax1.set_xlabel()
        ax1.bar_label(barras, padding=-15)
        st.pyplot(fig1)

    with aba2:
        col5, col6 = st.columns(2)
        with col5:
            salario_area = df.groupby("Área")['Salario'].median().sort_values()
            fig2, ax2 = plt.subplots()
            salario_area.plot(kind='barh', color='red', ax=ax2)
            ax2.bar_label(ax2.containers[0], padding=-70, fmt="R$ %.2F") #coloca os valores dentro da barra, "fmt=" equivale ao F de string

            ax2.set_ylabel("")
            ax2.set_title("Média Salarial por Área")
            st.pyplot(fig2)
            #grafico pizza teste
            df.columns = df.columns.str.strip()
            df["Área"] = df["Área"].astype(str)
            df["Avaliação do Funcionário"] = pd.to_numeric(df["Avaliação do Funcionário"], errors='coerce')

# Calcular média da avaliação por área
            media_por_area = df.groupby("Área")["Avaliação do Funcionário"].mean()

# Preparar valores e labels
            valores = media_por_area.values
            labels = media_por_area.index
            total = sum(valores)

# Função que mostra os valores reais dentro da fatia
            def mostrar_valor(pct):
                valor = pct * total / 100
                return f"{valor:.1f}"

# Criar gráfico
            fig, ax = plt.subplots(figsize=(8,8))#figsize muda o tamanho do gráfico
            ax.pie(valores, labels=labels, autopct=mostrar_valor, startangle=90)
            ax.axis("equal")

# Mostrar no Streamlit
            st.title("📊 Média da Avaliação por Área")
            st.pyplot(fig)

        with aba3:

        
            df["Ano Contratacao"] = df["Data de Contratacao"].dt.year
            df["Ano Demissao"] = df["Data de Demissao"].dt.year
            contratacoes_ano = df["Ano Contratacao"].value_counts().sort_index()
            demissoes_ano = df["Ano Demissao"].value_counts().sort_index()

            fig6, ax6 = plt.subplots()
            contratacoes_ano.plot(kind="line", marker="o",color='blue' , label="Contratações", ax=ax6)
            demissoes_ano.plot(kind="line", marker="s",color='red' ,label="Demissões", ax=ax6)
            ax6.set_ylabel("Quantidade")    
            ax6.set_xlabel("")  # Remove o nome do eixo X  
            ax6.legend()
            st.pyplot(fig6)

        with col6:
            horas_area = df.groupby("Área")['Horas Extras'].sum().sort_values()
            fig3, ax3 = plt.subplots()
            horas_area.plot(kind='barh', color='grey', ax=ax3)#caso mude o gráfico para deitado, usar o comando rot=0
            ax3.bar_label(ax3.containers[0], padding=-70) #coloca os valores dentro da barra
            ax3.set_title("Total de horas extras por área")
            ax3.set_xlabel("")
            st.pyplot(fig3)

    with aba4:
        st.markdown("### Visualização da Tabela de dados")
        # df["Nome Completo"] = df["Nome"].str.cat(df["Sobrenome"], sep=" ", na_rep="")
        df["Nome Completo"] = df["Nome"] + " " + df["Sobrenome"]
        # Apagando a coluna "Sobrenome"
        df.drop(columns=["Nome","Sobrenome"], inplace=True)
        # Barra de pesquisa
        busca = st.text_input("Pesquisar por nome completo")

        if busca:
            # Filtra linhas que contêm o texto digitado (case insensitive)
            # filtra as linhas que contêm o texto digitado, ignorando maiúsculas/minúsculas.
            # trata valores ausentes (NaN) como False, ou seja, se o campo
            # estiver vazio, não vai causar erro e nem retornar True.
            df_filtrado = df[df["Nome Completo"].str.contains(busca, case=False, na=False)]
        else:
            df_filtrado = df
            # st.dataframe(df)
        st.dataframe(df_filtrado[['Nome Completo', 'Cargo', 'Área', 'Horas Extras', 'Salario']])
        
else:
    st.warning("Por favor, carregue um arquivo Excel para iniciara a análise")