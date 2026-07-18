import pandas as pd
import numpy as np

def limpiar_datos(df):
    df_clean = df.dropna(subset=['make', 'model', 'sellingprice', 'mmr', 'saledate', 'year']).copy()
    
    df_clean['sellingprice'] = pd.to_numeric(df_clean['sellingprice'], errors='coerce')
    df_clean['mmr'] = pd.to_numeric(df_clean['mmr'], errors='coerce')
    df_clean['year'] = pd.to_numeric(df_clean['year'], errors='coerce')
    
    df_clean = df_clean[(df_clean['sellingprice'] > 0) & (df_clean['mmr'] > 0)]
    
    df_clean['sale_year'] = df_clean['saledate'].str.extract(r'(\d{4})').astype(float)
    df_clean['edad'] = df_clean['sale_year'] - df_clean['year']
    
    df_clean['edad'] = np.where(df_clean['edad'] <= 0, 1, df_clean['edad'])
    
    df_clean = df_clean.dropna(subset=['edad', 'sale_year'])
    
    return df_clean