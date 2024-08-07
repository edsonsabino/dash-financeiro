import streamlit as st
import pandas as pd
import numpy as np
import os

# to do: definir os gráficos na seção adequada


# graph section
import matplotlib.pyplot as plt

def background_color(val):
    color = 'green' if val>=10000 else 'grey'
    return f'background-color: {color}'

def graph_donut(ativo):

    #   DONUT
    # Group by 'TIPO_RENDIMENTO' and sum 'APORTE'
    grouped_data = ativo.groupby("TIPO_RENDIMENTO")['APORTE'].sum()

    # Calculate the percentage for each group
    percentages = 100 * grouped_data / grouped_data.sum()

    # Prepare the labels with percentages
    labels = [f'{label} ({percentage:.1f}%)' for label, percentage in zip(grouped_data.index, percentages)]
    sizes = grouped_data.values

    # Create the donut plot
    fig_02, ax02 = plt.subplots(figsize=(8, 6), dpi=100)
    wedges, texts = ax02.pie(
        sizes, labels=labels, startangle=140, counterclock=False,
        wedgeprops=dict(width=0.5, edgecolor='w')  # width controls the thickness of the donut
    )

        # Customize the label font size
    plt.setp(texts, size=14)  # Increase font size here

        # Set the title
    plt.title('APORTE Distribution by TIPO_RENDIMENTO', fontsize=14, weight='bold')

        # Equal aspect ratio ensures that pie is drawn as a circle.
    ax02.axis('equal')

    return fig_02

def graph_bar(ativo):
    #   HORIZONTAL BAR PLOT

    # Group by 'EMISSOR' and sum 'APORTE'
    grouped_data = ativo.groupby("EMISSOR")['APORTE'].sum()

    # Sort the data in descending order
    sorted_data = grouped_data.sort_values(ascending=False)

    # Prepare the labels and sizes for the bar plot
    labels = sorted_data.index
    sizes = sorted_data.values

    # Create the horizontal bar plot
    fig_01, ax01 = plt.subplots(figsize=(10, 6), dpi=100)
    bars = ax01.barh(labels, sizes, color='skyblue')

    # Add value labels at the end of each bar
    for bar in bars:
        ax01.text(
            bar.get_width(),                        # X-coordinate for the text (end of the bar)
            bar.get_y() + bar.get_height() / 2,     # Y-coordinate for the text (center of the bar)
            f'{bar.get_width():.2f}',               # Text to display (value of the bar)
            va='center',                            # Vertical alignment
            ha='left',                              # Horizontal alignment
            fontsize=12,                            # Font size of the text
            color='black'                           # Color of the text
        )

        # Set the title and labels
    plt.title('Sum of APORTE by EMISSOR', fontsize=16, weight='bold')
    ax01.set_xlabel('Sum of APORTE', fontsize=14)
    ax01.set_ylabel('EMISSOR', fontsize=14)

    # Invert the y-ax01is to have the largest bar on top
    ax01.invert_yaxis()

    return fig_01

#   =======================================================================
#   =========================== SETTING config 
#   =======================================================================

st.set_page_config(page_title="Finanças da Ju",page_icon=":bar_chart:",layout="wide")

# Set precision for float values globally
pd.options.display.float_format = '{:.2f}'.format

bar=st.sidebar
bar.markdown("# Página principal")


path_main_folder=os.path.dirname(os.path.realpath(__file__))    #onde fica o .py na distribuição
path_folder_input=os.path.join(path_main_folder,'dados_entrada')    

#   =======================================================================
#   =========================== Read dataframe
#   =======================================================================

ativo = pd.read_csv(os.path.join(path_folder_input,"df_ativo.csv"),sep=';')

#   =======================================================================
#   =========================== SETTING SIDEBAR (filters)
#   =======================================================================

l_bancos=bar.multiselect("Bancos",ativo['EMISSOR'].unique(),ativo['EMISSOR'].unique())
l_produtos=bar.multiselect("Produtos",ativo['TIPO_PAPEL'].unique(),ativo['TIPO_PAPEL'].unique())




ativo_filtered = ativo[(ativo['EMISSOR'].isin(l_bancos)) & (ativo['TIPO_PAPEL'].isin(l_produtos))]
#   =======================================================================
#   =========================== SETTING dataframes
#   =======================================================================
#

wm = lambda x: np.average(x, weights=ativo.loc[x.index, "APORTE"])
df_taxa_media2=pd.DataFrame(ativo_filtered.groupby("TIPO_RENDIMENTO").agg(Media_A=("TAXA_AA",'mean'),
                                                                 Media_P=("TAXA_AA",wm),
                                                                 Mediana=("TAXA_AA",'median'),                       
                                                                 Min=("TAXA_AA",'min'),
                                                                 Max=("TAXA_AA",'max')
                                                                 ))

#

df_total=pd.read_csv(os.path.join(path_folder_input,"df_total.csv"),sep=';')

#
df_resgate_anomes=pd.read_csv(os.path.join(path_folder_input,"df_resgate_anomes.csv"),sep=';')

#
ativo_sorted = ativo.sort_values(by='DATA_RESGATE', ascending=True)
proximos_resgates=ativo_sorted[['DATA_RESGATE','EMISSOR','APORTE']].head(3)


#   =======================================================================
#   =========================== SETTING VAULES 
#   =======================================================================

# Aqui ficarão os dados para inserir nos cards de métricas

vb_patrimonio=df_total[(df_total['TIPO_ACUMULADO']=='VALOR_ATUAL_BRUTO')]['VALOR']
vl_patrimonio=df_total[(df_total['TIPO_ACUMULADO']=='VALOR_ATUAL_LIQUIDO')]['VALOR']
vb_patrimonio_aporte=df_total[(df_total['TIPO_ACUMULADO']=='APORTE')]['VALOR']

df_total2=(ativo_filtered[['APORTE','VALOR_ATUAL_BRUTO','VALOR_ATUAL_LIQUIDO']].sum())

vb_patrimonio=df_total2['VALOR_ATUAL_BRUTO']

vl_patrimonio=df_total2['VALOR_ATUAL_LIQUIDO']
vb_patrimonio_aporte=df_total2['APORTE']



vb_rentabilidade=vb_patrimonio-vb_patrimonio_aporte

df_dist_objetivo=pd.DataFrame(ativo_filtered.groupby("OBJETIVO")['VALOR_ATUAL_BRUTO'].sum())
df_dist_objetivo=df_dist_objetivo.reset_index()

vb_objetivo_rendimento=df_dist_objetivo[(df_dist_objetivo['OBJETIVO']=='Rend')]['VALOR_ATUAL_BRUTO']
vb_objetivo_reserva=df_dist_objetivo[(df_dist_objetivo['OBJETIVO']=='RE')]['VALOR_ATUAL_BRUTO']


#   =======================================================================
#   =========================== SETTING COLUMNS 
#   =======================================================================

col1,col2= st.columns([2,4])

with col1:

    col1.subheader("Titulo coluna 1")

    st.pyplot(graph_donut(ativo_filtered))   
    
    st.divider()
    st.dataframe(df_taxa_media2.T,use_container_width=True) 
with col2:
    col2.subheader("Estado atual")
    sub_col1, sub_col2 , sub_col3 = st.columns([1,1,2])
    with sub_col1:
        st.metric(label='Patrimônio líquido',value=round(vl_patrimonio/1000,2),delta=0)
    with sub_col2:
        st.metric(label='Reserva em milhares',value=round(vb_objetivo_reserva/1000,2),delta=0)                
    with sub_col3:
        st.dataframe(proximos_resgates, use_container_width=True, hide_index=True)
    st.divider()

    col2.subheader("Aportes a serem resgatados")
    st.dataframe(df_resgate_anomes.style.applymap(background_color, subset=['2024','2025','2026','2027','2029']), use_container_width=True, hide_index=True)
st.divider()

st.dataframe(ativo_filtered,use_container_width=True, hide_index=True)

""" 
[x]  Fazer cálculo diretaente no main2 em vez de fazer fora.
"""    


