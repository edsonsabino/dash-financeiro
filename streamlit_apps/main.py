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

#   =======================================================================
#   =========================== SETTING config 
#   =======================================================================

st.set_page_config(page_title="Finanças da Ju",page_icon=":bar_chart:",layout="wide")

st.sidebar.markdown("# Página principal")

path_main_folder=os.path.dirname(os.path.realpath(__file__))    #onde fica o .py na distribuição
path_folder_input=os.path.join(path_main_folder,'dados_entrada')    

#   =======================================================================
#   =========================== Read dataframes
#   =======================================================================

# defining random values in a dataframe using pandas and numpy for tests
df = pd.DataFrame(
 np.random.randn(30, 10),
 columns=('col_no %d' % i for i in range(10)))

# Sample DataFrame for demonstration (replace with your actual data)
data = {
    'EMISSOR': ['Banco A', 'Banco B', 'Banco A', 'Banco C', 'Banco B', 'Banco A'],
    'APORTE': [100, 150, 200, 50, 100, 99 ]
}
    #   AVERAGE
data = {
    'TIPO_RENDIMENTO': ['cdi', 'ipca+', 'cdi', 'outro', 'ipca+', 'cdi'],
    'APORTE': [100, 150, 200, 50, 100, 250]
}


ativo = pd.read_csv(os.path.join(path_folder_input,"df_ativo.csv"),sep=';')
#
df_taxa_media =pd.read_csv(os.path.join(path_folder_input,"df_taxa_media.csv"),sep=';')
df_taxa_media['TAXA_AA']=df_taxa_media['TAXA_AA']*100

#
df_total=pd.read_csv(os.path.join(path_folder_input,"df_total.csv"),sep=';')

#
df_resgate_anomes=pd.read_csv(os.path.join(path_folder_input,"df_resgate_anomes.csv"),sep=';')

#
ativo_sorted = ativo.sort_values(by='DATA_RESGATE', ascending=True)
proximos_resgates=ativo_sorted[['DATA_RESGATE','EMISSOR','APORTE']].head(5)

#   =======================================================================
#   =========================== SETTING VAULES 
#   =======================================================================

# Aqui ficarão os dados para inserir nos cards de métricas

vb_patrimonio=df_total[(df_total['TIPO_ACUMULADO']=='VALOR_ATUAL_BRUTO')]['VALOR']
vb_patrimonio_aporte=df_total[(df_total['TIPO_ACUMULADO']=='APORTE')]['VALOR']

vb_rentabilidade=(vb_patrimonio.iloc[0]-vb_patrimonio_aporte.iloc[0])

#   =======================================================================
#   =========================== SETTING GRAPHS
#   =======================================================================

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


#   =======================================================================
#   =========================== SETTING COLUMNS 
#   =======================================================================

col1,col2, col3 = st.columns(3)

with col1:
    st.metric(label='Patrimônio em milhares',value=round(vb_patrimonio/1000,2),delta=round(vb_rentabilidade/1000,2))
    st.dataframe(proximos_resgates)
    
with col2:
    st.metric(label='a colocar',value=8,delta=1)


    st.pyplot(fig_02)
with col3:
    st.metric(label='Teste',value=8,delta=1)
    st.dataframe(df_taxa_media)
    

st.dataframe(df_resgate_anomes.style.applymap(background_color, subset=['2024','2025','2026','2027','2029']))
st.pyplot(fig_01)