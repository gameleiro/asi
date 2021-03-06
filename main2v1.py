import pandas as pd
import pdfminer
from pdfminer.high_level import extract_pages
import streamlit as st
import numpy as np
from PIL import Image
import streamlit as st
import graphviz as graphviz
import datetime
import scipy.special as sc
import math
import scipy
import seaborn as sns
from scipy.stats import t
from scipy.stats import chi2
from scipy.stats import shapiro
from scipy import stats
from scipy.stats import *
import matplotlib.pyplot as plt
from scipy.stats.mstats import mquantiles,mquantiles_cimj
import numpy.ma as ma
from numpy import float_, int_, ndarray
from scipy.stats import gaussian_kde

import base64
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', float_format="%.2f")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="ASI.xlsx"> Download do Resultado </a>' # decode b'abc' => abc


def boxplot(data_frame):


    tam = len(data_frame.columns)


    #fig, ax = plt.subplots(tam,2,figsize=(15,15 + 2*tam))

    #line = st.slider("Largura", min_value=4, max_value=40)
    #col = st.slider("Altura", min_value=5.6, max_value=40)
    fig, ax = plt.subplots(tam,2, figsize=(5.6*2,4.6*tam))

    descricao = pd.DataFrame()

    p=0
    for col in data_frame.columns:

        for i in range(len(data_frame.index)):
            data_frame.loc[i, col] = str(data_frame.loc[i, col]).replace(',', '.')

        x = (data_frame[col]).astype(np.float64).dropna()
        descricao[p] =x.describe()
        n = x.count()
        dt = x

        if(n<4):
            ax[p,0].hist(dt, density=True, histtype='step', color="#2466b6", alpha=.9, label='Histograma')
            ax[p,0].legend()
        else:
            KDEpdf = gaussian_kde(dt, bw_method='silverman')
            x = np.linspace((0.8*dt.min()), (dt.max()*1.2), 2000)
            #print(x)
            ax[p,0].plot(x, KDEpdf(x), 'r', color="black", linestyle='-', lw=3, label='Densidade aproximada')
            ax[p,0].hist(dt, density=True, histtype='step', color="#2466b6", alpha=.9, label='Histograma')

            ax[p,0].legend()

        green_diamond = dict(markerfacecolor='g', marker='D')
        ax[p,1].boxplot(dt,notch=False, showfliers=True, flierprops=green_diamond)



        p = p + 1
        #plt.show()
    descricao.columns = data_frame.columns
    descricao.index = ['quantidade','m??dia','desvio padr??o','valor m??nimo','25%','mediana','75%','valor m??ximo']
    st.table(descricao)
    st.pyplot(fig)
    plt.close()




    return

    #plt.close()


def dp_MJ(data, p):
    data = np.sort(data)  # conjunto ordenado
    n = data.size  # n

    betacdf = beta.cdf

    x = np.arange(1, n + 1, dtype=float_) / n
    y = x - 1. / n

    w = sc.betainc(p * (n + 1), (n + 1) * (1 - p), x) - sc.betainc(p * (n + 1), (n + 1) * (1 - p), y)
    # print(w)

    # W = betacdf(x,p*(n+1),(n+1)*(1-p)) - betacdf(y,p*(n+1),(n+1)*(1-p))
    # print(W)

    C1 = np.dot(w, data)  # valor esperado E[X]
    # print(C1)
    C2 = np.dot(w, data ** 2)  # valor esperado E[X^2]

    mj = np.sqrt(C2 - C1 ** 2)

    return mj


def medianaIgor(data, p):
    data = np.sort(data)  # conjunto ordenado
    n = data.size  # n

    betacdf = beta.cdf

    x = np.arange(1, n + 1, dtype=float_) / n
    y = x - 1. / n

    w = sc.betainc(p * (n + 1), (n + 1) * (1 - p), x) - sc.betainc(p * (n + 1), (n + 1) * (1 - p), y)
    # print(w)

    # W = betacdf(x,p*(n+1),(n+1)*(1-p)) - betacdf(y,p*(n+1),(n+1)*(1-p))
    # print(W)

    C1 = np.dot(w, data)  # valor esperado E[X]
    # print(C1)
    C2 = np.dot(w, data ** 2)  # valor esperado E[X^2]

    mj = np.sqrt(C2 - C1 ** 2)

    return C1



def abrirArquivo(arquivo):
    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8', low_memory=False)
    return df

def processaDf(df, mr=0, nc=0.95):
    obs = []
    n_out = []
    ls = []
    li = []
    mediana = []


    for col in df.columns:

        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(',', '.')
        df[col] = df[col].astype(float)
        df[col].dropna(inplace=True)

        n_0 = df[col].count()
        df[col] = remover_outliers(df[col], mr)
        n_1 = df[col].count()

        n_out.append(n_0-n_1)


        if (n_1 < 3):
            obs.append("Menos de 3 amostras v??lidas")
            mediana.append(0)
            ls.append(0)
            li.append(0)
        else:
            obs.append("Mais de 3 amostras v??lidas")

            t_coeficiente = t.ppf(0.5 + 0.5 * nc, n_1 - 1)


            dados = df[col].dropna()

            mediana_aux = medianaIgor(dados,0.5)
            dp_aux = dp_MJ(dados,0.5)

            mediana.append(mediana_aux)
            ls.append(mediana_aux + t_coeficiente*dp_aux)
            li.append(mediana_aux - t_coeficiente*dp_aux)



        x = pd.DataFrame()
        x['M??dia'] = df.mean().astype(float)
        x['Outliers Removidos'] = n_out
        x['Observa????o'] = obs
        x['Mediana'] = mediana
        x['Limite Inferior'] = li
        x['Limite Superior'] = ls

    return x



def remover_outliers(serie = pd.Series([],dtype="float64"), mr=0):

    iq = serie.quantile(0.75) - serie.quantile(.25)
    ls = serie.quantile(0.75) + 1.5*iq
    lin = serie.quantile(0.25) - 1.5*iq

    if(mr == 2):
        z = np.abs(stats.zscore(serie))
        for i,v in serie.items():
            if (z[i] > 3):
                serie[i] = np.nan

    if (mr == 1):
        serie[ (serie > ls ) | (serie < lin ) ] = np.nan

    return serie




def _max_width_():
    max_width_str = f"max-width: 1200px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )

st.write("""
# Acubens - ASI
  *Ferramenta para auxiliar na an??lise de indicativo estat??stico de sobrepre??o*
 """)

_max_width_()


#video_file = open('C:/Users/dpf.adm/Desktop/Streamlite-Teste/tutorial.mp4', 'rb')
#video_bytes = video_file.read()



with st.beta_expander("Executar An??lise Estat??stica"):
    st.write("""  **Etapa 1  - Leitura do arquivo** """)

    uploaded_file = st.file_uploader("Escolha um arquivo", ["csv"])


    if uploaded_file is not None:


        df = abrirArquivo(uploaded_file)

        st.write(df)

        st.write("""  **Etapa 2 - Investiga????o dos Dados: Distribui????o, Histograma e Boxplot** """)
        boxplot(df)


        left_column, right_column = st.beta_columns(2)
        # You can use a column just like st.sidebar:
        with left_column:
            st.write("""  **Etapa 3 - Remo????o de Outliers** """)
            mr = st.radio('M??todo',("Nenhum", "BoxPlot", "z-score"))

            if mr == "Nenhum":
                mr = 0

            if mr == "BoxPlot":
                mr = 1

            if mr == "z-score":
                mr = 2

        with right_column:
            st.write("""  **Etapa 4 - C??lculo do Intervalo de Confian??a** """)
            nc = st.radio('N??vel de Confian??a', ("95%", "99%", "90%"))

            if nc == "95%":
                nc = 0.95

            if nc == "99%":
                nc = 0.99

            if nc == "90%":
                nc = 0.90


        x = processaDf(df, mr, nc)


        y = pd.DataFrame()

        y['Outliers Removidos'] = x['Outliers Removidos']
        y['Estimador Mediana'] = x['Mediana']
        y['Limite Inferior'] = x['Limite Inferior']
        y['Limite Superior'] = x['Limite Superior']
        #y['Observa????o'] = x['Observa????o']

        st.table(y)

        df2 = y  # your dataframe

        st.write("Cique no bot??o para gerar um arquivo compat??vel com Excel")
        if st.button("Gerar arquivo"):
            st.markdown(get_table_download_link(df2), unsafe_allow_html=True)





with st.beta_expander("Tutorial"):
    st.write(""" 
    **Caso seja sua primeira vez utilizando o Acubens - ASI, confira o tutorial em v??deo abaixo**
    """)

    #st.video(video_bytes)


with st.beta_expander("M??todos Matem??ticos - Intervalo de Confian??a"):
    st.write(""" 
     **O m??todo aplicado pela ferramenta ?? composto por diversas t??cnicas de an??lise de dados, conforme explicado abaixo:**
    """)

    image = Image.open('C:/Users/dpf.adm/Desktop/Streamlite-Teste/Capturar.PNG')
    #st.image(image)

    image2 = Image.open('C:/Users/dpf.adm/Desktop/Streamlite-Teste/Capturar2.PNG')
    #st.image(image2)

    st.write(r"""
    Seja $X_{1}\text{,...,}X_{n}$, uma amostra aleat??ria de tamanho  $n$  retirada de uma distribui????o cont??nua com fun????o de distribui????o  $F(.)$. 
    Considere  $X_{(1)}\text{,...,} X_{(n)}$  a estat??stica ordenada da amostra e o vetor  $X =(X_{(1)}\text{,...,} X_{(n)})$.

    O valor esperado da k-??sima estat??stica ordenada ?? dado por:
    $$
    E(X_{(k)}) = { 1 \over \beta(k,n-k+1)} \displaystyle\int_{-\infty}^{+\infty}xF(x)^{k-1}  (1 - F(x))^{n-k}dF(x)
    $$
    
    $$
    = { 1 \over \beta(k,n-k+1)} \displaystyle\int_{0}^{1}F^{-1}(y)y^{k-1}(1-y)^{n-k}dy
    $$
    
    Dado que $E(X_{(n+1)p})$ converge para $F^{-1}(p)$ para $p\in(0,1)$, toma-se como estimador para $F^{-1}(p)$ o valor esperado para $E(X_{(n+1)p})$, sendo $(n+1)p$ inteiro ou n??o:
    
    $$
    Q_p = { 1 \over \beta((n+1)p,(n+1)(1-p))} \displaystyle\int_{0}^{1}F_n^{-1}(y)y^{(n+1)p-1}(1-y)^{(n+1)(1-p)}dy
    $$
    
    Onde $F_n(X)$ ?? a fun????o de distribui????o acumulada, $F_{n}(X) = n^{-1}\sum I(X_i \leq x)$ ,  $I(A)$ ?? a fun????o indicadora do conjunto $A$. O estimador pode ser reescrito como:
    
    $$
    Q_p = \displaystyle\sum_{i=1}^{n} W_{n,i} X_{(i)}
    $$
    
    Onde,
    
    $$
    W_{n,i} = { 1 \over \beta((n+1)p,(n+1)(1-p))} \displaystyle\int_{(i-1)/n}^{i/n}y^{(n+1)p-1}(1-y)^{(n+1)(1-p)}dy
    
    $$
    
    $$
    = I_{i/n}(p(n+1),(1-p)(n+1)) - I_{(i-1)/n}(p(n+1),(1-p)(n+1))
    $$
    
    e $I_{x}(a,b)$ denota a fun????o incompleta de beta
    
    Generalizando o procedimento descrito acima para o c??lculo do momento de ordem $l$, temos o estimador gen??rico : 
   
    $$
    C_d = \displaystyle\sum_{i=1}^{n} W_{n,i} X_{(i)}^d
    $$
    
    Conforme proposto em [1], utilizando os momentos de primeira e segunda ordem podemos expressar o desvio padr??o como:
    $$
    S_p = \sqrt{C_2 - C_1^2}
    $$
    
    Fazendo $p=0.5$, temos $Q_{0.5}$ como o estimador para a mediana e $S_{0.5}$ como desvio padr??o associado.


    Define-se o intervalo de confian??a com n??vel de confian??a $100(1-\alpha)\%$:
    
    $$
    IC_{\alpha} = Q_{0.5} \pm t_{\alpha,n-1} S_{0.5}
    $$
    
    onde $\alpha$ ?? o n??vel de signific??ncia.
    
    
    """)


with st.beta_expander("Sobre", expanded=True):
    st.write(""" 
    Idealizada pelos Peritos Criminais Federais: **Igor Gameleiro**, **Rafaela da Fonte** e **Vitor Gomes**, a ferramenta busca auxiliar na an??lise de sobrepre??o a partir de t??cnicas de visualiza????o de dados e de estima????o n??o param??trica. 
    """)


