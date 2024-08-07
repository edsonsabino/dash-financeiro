import pandas as pd
import numpy as np
from datetime import datetime
import os 
from bcb import sgs



#   ========================    Functions    ========================

def parse_date(date_str):
    try:
        # Attempt to parse date using known formats. Iterative process
        date_formats = ['%d-%b-%y',
                        '%y-%b-%d',
                        '%d-%b-%Y',
                        '%Y-%b-%d',
                        '%m-%d-%Y %H:%M:%S',
                        '%d-%m-%Y %H:%M:%S',
                        '%d-%m-%Y %H:%M',
                        '%d-%m-%y %H:%M:%S',
                        '%d-%m-%y %H:%M',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d %H:%M',
                        '%d-%m-%Y',
                        '%m-%d-%Y %H:%M',
                        '%m/%d/%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M:%S',
                        '%m/%d/%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M',                        
                        '%d/%m/%Y',
                        '%m/%d/%Y %H:%M'
                  ]
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        # If none of the known formats match, return None
        return None
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None
def get_taxa_time_series_bcb(start_date:str,dict_nome_taxa:dict):
    """
    Retrieves a time series for the specified 'dict_nome_taxa' from SGS (Time Series Management System)
    of the Brazilian Central Bank, transforms it into a DataFrame.

    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        dict_nome_taxa (str): Name of the economic indicator

    Returns:
        pandas.DataFrame: A DataFrame containing data requestedd.

    Raises:
        ValueError: If the retrieved data is empty or there's an error during data retrieval.
    """

    try:
        # Fetch time series data using SGS
        data = sgs.get(dict_nome_taxa,
            start=start_date     
        )
        return data

    except Exception as e:
        raise ValueError(f"Error retrieving data: {e}")

def calc_cumulative_rate_cdi(data_inicio: str, data_fim: str, correcao_valor: float, df_historico: pd.DataFrame) -> float:
    """
    Processes a historical DataFrame containing economic indicators
    (SELIC and IPCA) to calculate the cumulative product for a specific period
    and taxa (column name).

    Args:
    data_inicio (str): Start date in YYYY-MM-DD format.
    data_fim (str): End date in YYYY-MM-DD format.
    correcao_valor (float): Correction value to be applied in the cumulative calculation.
    df_historico (pd.DataFrame): DataFrame with historical data indexed by dates.

    Returns:
    float: The penultimate value from the 'cumulativo' column.

    Raises:
    ValueError: If the selected data is empty or there's an error during processing.
    """
    
    # Select data within the specified date range
    df_taxa = df_historico.loc[data_inicio:data_fim].reset_index()
    
    # Check if any data is selected
    if df_taxa.empty:
        raise ValueError(f"No data found for between {data_inicio} and {data_fim}")

    # Add cumulative product column
    df_taxa['cumulativo'] = (1 + correcao_valor * df_taxa['CDI'] / 100).cumprod()

    # Check if the DataFrame has at least two rows to return the penultimate value
    if len(df_taxa['cumulativo']) < 2:
        return 1
    
        
    # Return the penultimate value from 'cumulativo'
    return df_taxa['cumulativo'].iloc[-2]

def calc_cumulative_rate_ipca(data_inicio:str,data_fim: str, correcao_valor:float,df_historico:pd.DataFrame) -> float:
  """
  Calculates the cumulative rate based on historical data and correction factors.

  Args:
      data_inicio (str): Start date in YYYY-MM-DD format.
      data_fim (str): End date in YYYY-MM-DD format.
      correcao_tipo (str): Type of correction (e.g., 'IPCA').
      correcao_valor (float): Correction value (e.g., annual inflation rate).
      df_historico (pd.DataFrame): Historical data DataFrame containing an 'ipca' column.

  Returns:
      float: The last value of the 'ipca_acumulado' column, representing the cumulative rate.
  """

  # Filter data within the specified date range
  # Select data within the specified date range
  #df = df_historico.loc[data_inicio:data_fim].reset_index()
  df = df_historico.loc[data_inicio::].reset_index()  

    # Check if any data is selected
  if df.empty:
    print(f"No data found for between {data_inicio} and {data_fim}")
    return 1
    raise ValueError(f"No data found for between {data_inicio} and {data_fim}")

    # Add cumulative product column
  df['cumulativo'] = (1 + correcao_valor * df['IPCA+taxa'] / 100).cumprod()

    # Check if the DataFrame has at least two rows to return the penultimate value
  if len(df['cumulativo']) < 2:
        return 1

  # Calculate month difference (assuming 'DATA' column stores dates)
  try:

    n_months = len(df)-2
  except Exception as e:
    raise ValueError("Dataframe 'df_historico' does not contain a 'DATA' column for date calculations.")

  # Calculate monthly adjustment factor (considering potential errors)
  try:
    taxa_fixa_periodo = (1 + correcao_valor) ** (n_months / 12) - 1
  except ZeroDivisionError:
    raise ValueError("Correction value cannot be zero.")

  # Add 'ipca_corrigido' column with error handling0
  try:
    df['ipca_corrigido'] = df['IPCA+taxa'] / 100 
  except Exception as e:
     print("Erro na criacao de ipca_corrigido",e)

  # Add 'ipca_acumulado' column for cumulative rate
  df['ipca_acumulado'] = (1 + df['ipca_corrigido']).cumprod()

  # Corrigir com taxa fixa
  df['ipca_acumulado']= (1+df['ipca_acumulado'])*(1+taxa_fixa_periodo)-1


  # Return the last value of 'ipca_acumulado' (cumulative rate)
  return df['ipca_acumulado'].iloc[-2]
def calc_cumulative_rate_pre(data_inicio:str, data_fim:str, taxa_ano:float, feriados:list):
  """
  This function calculates the accumulated interest rate for a bond with a fixed rate.

  Args:
      data_inicio (str): Date of the beginning of the period in format YYYY-MM-DD.
      data_fim (str): Date of the end of the period in format YYYY-MM-DD.
      feriados (list): List of holidays as dates in format YYYY-MM-DD.
      taxa_ano (float): Interest rate for the year.

  Returns:
      float: Accumulated interest rate for the period.
  """
  total_days1 = np.busday_count(data_inicio, data_fim,holidays=feriados)
  total_days = np.busday_count(data_inicio, data_fim)
  # Convert dates to datetime format
  data_inicio = pd.to_datetime(data_inicio)
  data_fim = pd.to_datetime(data_fim)


  # Convert holidays list to datetime format
  feriados_dt = pd.to_datetime(feriados)

  # Filter holidays within the period
  feriados_no_periodo = feriados_dt[(feriados_dt >= data_inicio) & (feriados_dt <= data_fim)]

  # Count number of holidays within the period
  num_feriados = feriados_no_periodo.shape[0]
  
  # Subtract holidays from total days
  dias_corridos = total_days-num_feriados+1 #- num_feriados-1

  dias_corridos=total_days1  
  #print("total de dias",total_days)
  #print("total de dias",total_days)

  #print('corridos',dias_corridos)
  #print('feriados',num_feriados)

  # Calculate daily interest rate
  juros_acumulados = (taxa_ano+1)**(dias_corridos/252)-1

  return 1+juros_acumulados
def calc_cumulative_rate_general(row,data_fim,df_hist_ipca,df_hist_selic,feriados)->float:
   
   taxa_tipo=row['TIPO_RENDIMENTO']
   taxa_ano=row['TAXA_AA']
   data_inicio=row['DATA_INICIO'] 

   print(taxa_tipo,taxa_ano,data_inicio)
   
   if taxa_tipo == 'CDI':
        return calc_cumulative_rate_cdi(data_inicio,data_fim,taxa_ano,df_hist_selic)
   elif taxa_tipo == 'IPCA+taxa':
        return calc_cumulative_rate_ipca(data_inicio,data_fim,taxa_ano,df_hist_ipca)
   elif taxa_tipo=='Pré':
        return calc_cumulative_rate_pre(data_inicio,data_fim,taxa_ano,feriados)
   else:
       return 0

def calcular_valor_liquido(row, data_atual):
    """
    Calcula o valor acumulado líquido considerando as regras de imposto regressivo da renda fixa do Brasil.
    
    Args:
    data_inicio (str): Data de início do investimento no formato 'YYYY-MM-DD'.
    data_atual (str): Data atual ou data de resgate no formato 'YYYY-MM-DD'.
    tipo_papel (str): Tipo do papel. Se for 'CDB', a regra de imposto será aplicada.
    valor_aporte (float): Valor inicial do aporte.
    valor_bruto (float): Valor bruto acumulado.
    
    Returns:
    float: Valor líquido acumulado após aplicação do imposto (se aplicável).
    """
    
    if row['TIPO_PAPEL'] != 'CDB':
        return row['VALOR_ATUAL_BRUTO']
    
   
    # Converter as datas para objetos datetime
    data_inicio = datetime.strptime(row['DATA_INICIO'], '%Y-%m-%d')
    data_atual = datetime.strptime(data_atual, '%Y-%m-%d')
    
    # Calcular o número de dias entre as duas datas
    dias = (data_atual - data_inicio).days
    
    # Determinar a alíquota de imposto com base no número de dias
    if dias <= 180:
        aliquota = 0.225
    elif dias <= 360:
        aliquota = 0.20
    elif dias <= 720:
        aliquota = 0.175
    else:
        aliquota = 0.15
    
    # Calcular o imposto devido
    rendimento_bruto = row['VALOR_ATUAL_BRUTO'] - row['APORTE']
    imposto = rendimento_bruto * aliquota
    
    # Calcular o valor líquido
    valor_liquido =  row['VALOR_ATUAL_BRUTO'] - imposto
    
    return valor_liquido

#   ========================    General settings    ========================

#   SET PRECISION
# Set precision for float values globally
pd.options.display.float_format = '{:.2f}'.format

#   PATHS

path_main_folder=os.path.dirname(os.path.realpath(__file__))    #onde fica o .py na distribuição

path_folder_input=os.path.join(path_main_folder,'dados_entrada')                             
path_folder_trusted=os.path.join(os.path.join(path_main_folder,'dados_trabalho'))      
path_folder_output=os.path.join(os.path.join(path_main_folder,'streamlit_apps','dados_entrada'))

#   SCHEMA and header

names_raw=['EMISSOR','TIPO_PAPEL','TIPO_RENDIMENTO','OBJETIVO','APORTE','TAXA_AA','DATA_INICIO','DATA_RESGATE']
feriados=[
    '2020-01-01',
    '2020-02-24',
    '2020-02-25',
    '2020-04-10',
    '2020-04-21',
    '2020-05-01',
    '2020-06-11',
    '2020-09-07',
    '2020-10-12',
    '2020-11-02',
    '2020-11-15',
    '2020-11-20',
    '2020-12-25',
    '2021-01-01',
    '2021-02-15',
    '2021-02-16',
    '2021-04-02',
    '2021-04-21',
    '2021-05-01',
    '2021-06-03',
    '2021-09-07',
    '2021-10-12',
    '2021-11-02',
    '2021-11-15',
    '2021-12-25',
    '2022-01-01',
    '2022-02-28',
    '2022-03-01',
    '2022-04-15',
    '2022-04-21',
    '2022-05-01',
    '2022-06-16',
    '2022-09-07',
    '2022-10-12',
    '2022-11-02',
    '2022-11-15',
    '2022-11-20',
    '2022-12-25',
    '2023-01-01',
    '2023-02-20',
    '2023-02-21',
    '2023-04-07',
    '2023-04-21',
    '2023-05-01',
    '2023-06-08',
    '2023-09-07',
    '2023-10-12',
    '2023-11-02',
    '2023-11-15',
    '2023-11-20',
    '2023-12-25',
    '2024-01-01',
    '2024-02-13',
    '2024-03-29',
    '2024-04-21',
    '2024-05-01',
    '2024-05-30',
    '2024-09-07',
    '2024-10-12',
    '2024-11-02',
    '2024-11-15',
    '2024-11-20',
    '2024-12-25'
]
#   NAMES

arq_investimentos="InvestNovo_06_daycoval_OK.csv"
# ================================================================================================
#   ========================    GET INDEX RATES    ========================
# ================================================================================================

start_date = "2017-01-01"
try:
    hist_selic = get_taxa_time_series_bcb(start_date, {"CDI": 11})
    hist_cdi = hist_selic.copy()  # Make a copy of the DataFrame
    hist_cdi.to_csv("hist_cdi.csv", sep=';')
    print("SELIC and CDI data successfully retrieved and saved.")

except Exception as e:
    print(f"Error retrieving SELIC data: {e}")
    print("Loading previously saved CDI data.")
    if os.path.exists("hist_cdi.csv"):
        hist_cdi = pd.read_csv("hist_cdi.csv", sep=';', index_col=0)
        print("Loaded CDI data from hist_cdi.csv.")
    else:
        print("No previous CDI data found. Exiting.")
        exit(1)

# Attempt to retrieve IPCA data
try:
    hist_ipca = get_taxa_time_series_bcb(start_date, {"IPCA+taxa": 433})
    hist_ipca.to_csv("hist_ipca.csv", sep=';')
    print("IPCA data successfully retrieved and saved.")

except Exception as e:
    print(f"Error retrieving IPCA data: {e}")
    print("Loading previously saved IPCA data.")
    if os.path.exists("hist_ipca.csv"):
        hist_ipca = pd.read_csv("hist_ipca.csv", sep=';', index_col=0)
        print("Loaded IPCA data from hist_ipca.csv.")
    else:
        print("No previous IPCA data found. Exiting.")
        exit(1)

# ================================================================================================
#   ========================    Read    ========================
# ================================================================================================

raw=pd.read_csv(os.path.join(path_folder_input,arq_investimentos),sep=';')

# ================================================================================================
#   ========================    Transform    ========================
# ================================================================================================

df=raw

#   CHANGE DATE_FORMAT

df['DATA_INICIO'] = df['DATA_INICIO'].apply(lambda x: parse_date(x).strftime('%Y-%m-%d') if parse_date(x) else x)
df['DATA_RESGATE'] = df['DATA_RESGATE'].apply(lambda x: parse_date(x).strftime('%Y-%m-%d') if parse_date(x) else x)


#   ADD ativo/inativo
try:
    dia_corrente= pd.Timestamp.now().strftime('%Y-%m-%d')
    df["SITUACAO"]=df.apply(lambda row: "Resgatado" if (row['DATA_RESGATE']<=dia_corrente or row['DATA_RESGATE']=="Resgatado") else "Ativo", axis=1) # usar apply aqui
except Exception as e:
    print('Erro situacao',e)

#   ADD ANO e MES RESGATE

try:
    df['ANO_RESGATE']= pd.to_datetime(df['DATA_RESGATE']).dt.year
    df['MES_RESGATE']= pd.to_datetime(df['DATA_RESGATE']).dt.month
except Exception as e:
    print("Erro adicionando mês e ano",e)

#   ============    Calculations    ============

#   FILTRAR ATIVOS
ativo=df[df['SITUACAO']=="Ativo"]

#   ADD VALOR ATUAL CDI
ativo['VALOR_ATUAL_BRUTO']=ativo.apply(lambda row: row['APORTE']*calc_cumulative_rate_general(row,"2024-07-09",hist_ipca,hist_cdi,feriados), axis=1)

#   ASS VALOR_ATUAL_LIQUIDO

ativo['VALOR_ATUAL_LIQUIDO']=ativo.apply(lambda row:calcular_valor_liquido(row,"2024-07-09",), axis=1)

ativo.to_csv('teste_02_add_bruto_daycoval.csv',sep =';', index=False)

#   Salvar df com investimentos ativos

ativo.to_csv(os.path.join(path_folder_output,'df_ativo.csv'),sep=';', index=False)

#   [sum] quanto dinheiro já foi investido e está ativo (volume aportado ativo)
df_total=pd.DataFrame(ativo[['APORTE','VALOR_ATUAL_BRUTO','VALOR_ATUAL_LIQUIDO']].sum())
df_total=df_total.reset_index().rename(columns={"index":'TIPO_ACUMULADO',0:'VALOR'})

print("Soma de aportes ativos\n",df_total)
print("colunas",df_total.columns)


df_total.to_csv(os.path.join(path_folder_output,'df_total.csv'),sep=';', index=False)
print('=============================================')

#   [sum] Quanto de dinheiro para cada banco, cada tipo de taxa, cada tipo de objetivo
print("Por emissor\n",ativo.groupby("EMISSOR")['APORTE'].sum())
print('=============================================')

df_dist_tipo_taxa=pd.DataFrame(ativo.groupby("TIPO_RENDIMENTO")['VALOR_ATUAL_LIQUIDO'].sum())
df_dist_tipo_taxa=df_dist_tipo_taxa.reset_index()
df_dist_tipo_taxa.to_csv(os.path.join(path_folder_output,'df_dist_tipo_taxa.csv'),sep=';', index=False)

print("Por tipo de taxa\n",df_dist_tipo_taxa)
print('=============================================')

df_dist_tipo_papel=pd.DataFrame(ativo.groupby("TIPO_PAPEL")['VALOR_ATUAL_LIQUIDO'].sum())
df_dist_tipo_papel=df_dist_tipo_papel.reset_index()
df_dist_tipo_papel.to_csv(os.path.join(path_folder_output,'df_dist_tipo_taxa.csv'),sep=';', index=False)

print("Por tipo de Papel \n",df_dist_tipo_papel)
print('=============================================')

print("Por tipo de Objetivo \n",ativo.groupby("OBJETIVO")['APORTE'].sum())
print('=============================================')

df_resgate_anomes=pd.DataFrame(ativo.groupby(["ANO_RESGATE",'MES_RESGATE'])['APORTE'].sum())
df_resgate_anomes=df_resgate_anomes.reset_index()

df_resgate_anomes_pvt= df_resgate_anomes.pivot_table(index=['MES_RESGATE'],
                        columns='ANO_RESGATE',
                        values='APORTE',
                        aggfunc='sum')
df_resgate_anomes_pvt.reset_index(inplace=True)

print("Soma dos aportes agrupado por ano \n",df_resgate_anomes_pvt)
df_resgate_anomes_pvt.to_csv(os.path.join(path_folder_output,'df_resgate_anomes.csv'),sep=';', index=False)

print('=============================================')

#[avg] Qual a média das taxas dos tipos de  taxas de investimentos ativos. Ao comparar com opções de mercado quero saber se já tenho algo melhor em carteira

df_taxa_media=pd.DataFrame(ativo.groupby("TIPO_RENDIMENTO")['TAXA_AA'].mean())
df_taxa_media=df_taxa_media.reset_index().rename(columns={"index":'TIPO_RENDIMENTO'})

print("Média das taxas por tipo de rendimento \n",df_taxa_media)
df_taxa_media.to_csv(os.path.join(path_folder_output,'df_taxa_media.csv'),sep=';', index=False)

print('=============================================')


wm = lambda x: np.average(x, weights=ativo.loc[x.index, "APORTE"])
df_taxa_media2=pd.DataFrame(ativo.groupby("TIPO_RENDIMENTO").agg(Media_A=("TAXA_AA",'mean'),
                                                                 Media_Ponderada=("TAXA_AA",wm),
                                                                 Mediana=("TAXA_AA",'median'),                       
                                                                 Min=("TAXA_AA",'min'),
                                                                 Max=("TAXA_AA",'max')
                                                                 ))
print("Média das taxas por tipo de rendimento 2 \n",df_taxa_media2)
df_taxa_media2.to_csv(os.path.join(path_folder_output,'df_taxa_media2.csv'),sep=';', index=True)

print('=============================================')



print('\n=========================    GRÁFICOS    =========================')
#teste=550*calc_cumulative_rate_ipca("2021-08-19","2024-05-15",'A',0.05,hist_ipca)
#                                        if (row['TIPO_RENDIMENTO']=='IPCA+taxa')) else 5
#                                 , axis=1)

# -- Agora seria interessante saber como tomar proveito desse agrupamento para conseguir as diversas agregações.
# -- Se isso tomar muito tempo, fazer diversos groupbys e "fé"
# https://clubedospoupadores.com/tesouro-direto/preco-do-tesouro-ipca.html