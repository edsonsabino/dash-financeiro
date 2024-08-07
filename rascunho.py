# Define a lambda function to compute the weighted mean:
wm = lambda x: np.average(x, weights=df.loc[x.index, "APORTE"])



# Groupby and aggregate with namedAgg [1]:
df.groupby(["TAXA_AA"]).agg(adjusted_lots=("TAXA_AA", "mean"),  
                            price_weighted_mean=("price", wm))

df_taxa_media2=pd.DataFrame(ativo.groupby("TIPO_RENDIMENTO").agg(Media_A=("TAXA_AA",'mean'),
                                                                 Media_Ponderada=("TAXA_AA",wm),
                                                                 Mediana=("TAXA_AA",'median'),                       
                                                                 Min=("TAXA_AA",'min'),
                                                                 Max=("TAXA_AA",'max')
                                                                 ))