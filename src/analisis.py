import numpy as np
import pandas as pd

def calcular_depreciacion(df):
    df['depreciacion_anual'] = (df['mmr'] - df['sellingprice']) / df['edad']
    df['depreciacion_anual'] = df['depreciacion_anual'].clip(lower=0)
    resultado = df.groupby('make')['depreciacion_anual'].mean().sort_values(ascending=False).head(10)
    return resultado

def rentabilidad_por_marca(df):
    rentabilidad = df.groupby('make')['margen_usd'].agg(['sum', 'mean']).rename(columns={'sum': 'ganancia_total', 'mean': 'margen_promedio'}).reset_index()
    top_rentables = rentabilidad.sort_values(by='margen_promedio', ascending=False)
    
    return top_rentables.head(5)

def verificar_calidad(df):
    len_total = len(df)
    registros_sin_precio = df[df['sellingprice'] == 0].shape[0]
    estados_unicos = df['state'].nunique()
    report = {
        'total_registros': len_total,
        'registros_sin_precio': registros_sin_precio,
        'estados_unicos': estados_unicos
    }
    return report

def analizar_impacto_odometro(df):
    df_filtered = df[df['odometer'] > 0].copy()
    df_grouped = df_filtered.groupby('make').agg({
        'odometer': 'mean',
        'sellingprice': 'mean'
    }).reset_index()
    df_grouped['valor_por_milla'] = df_grouped['sellingprice'] / df_grouped['odometer']
    return df_grouped.sort_values(by='valor_por_milla', ascending=False)

def analizar_modelo_especifico(df, marca, modelo):
    df_filtrado = df[
        (df['make'].str.upper() == marca.upper()) & 
        (df['model'].str.upper() == modelo.upper())
    ].copy()
    
    if df_filtrado.empty:
        return {"error": f"No se encontraron registros para {marca} {modelo}"}
        
    resumen = {
        'marca': marca.upper(),
        'modelo': modelo.upper(),
        'unidades_vendidas': int(len(df_filtrado)),
        'precio_promedio': float(df_filtrado['sellingprice'].mean()),
        'kilometraje_promedio': float(df_filtrado['odometer'].mean()),
        'margen_promedio': float(df_filtrado['margen_usd'].mean()),
        'depreciacion_promedio': float(df_filtrado['depreciacion_anual'].mean())
    }
    return resumen

def evaluar_viabilidad_inventario(df):
    resumen = df.groupby(['make', 'model']).agg({
        'edad': 'mean',
        'margen_usd': 'mean',
        'sellingprice': 'count' 
    }).reset_index()
    resumen = resumen.rename(columns={'sellingprice': 'volumen_ventas'})
    modelos_viables = resumen[
        (resumen['edad'] <= 10) & 
        (resumen['margen_usd'] > 0) & 
        (resumen['volumen_ventas'] > 5)
    ].copy()
    return modelos_viables.sort_values(by='margen_usd', ascending=False)

def analizar_oportunidades_mercado(df):
    df['mes_venta'] = pd.to_datetime(df['saledate'], errors='coerce').dt.month
    tendencias_mes = df.groupby('mes_venta')['sellingprice'].mean().reset_index().sort_values(by='mes_venta')
    df_estados_validos = df[df.groupby('state')['state'].transform('size') > 100]
    top_estados = df_estados_validos.groupby('state')['sellingprice'].mean().reset_index().sort_values(by='sellingprice', ascending=False).head(5)
    return {
        'mejores_estados': top_estados,
        'estacionalidad_mes': tendencias_mes
    }

def evaluar_riesgo_segmentado(df):
    df_riesgo = df.copy()
    condiciones_categoria = [
        (df_riesgo['mmr'] < 15000),
        (df_riesgo['mmr'] >= 15000) & (df_riesgo['mmr'] <= 45000),
        (df_riesgo['mmr'] > 45000)
    ]
    valores_categoria = ['Masivo', 'Gama Media', 'Lujo']
    df_riesgo['categoria_mercado'] = np.select(condiciones_categoria, valores_categoria, default='Masivo')
    if 'odometer' not in df_riesgo.columns:
        df_riesgo['odometer'] = np.nan
    if 'edad' not in df_riesgo.columns:
        df_riesgo['edad'] = np.nan 
    condiciones_riesgo = [
        (df_riesgo['categoria_mercado'] == 'Masivo') & ((df_riesgo['odometer'] > 350000) | (df_riesgo['edad'] > 20)),
        (df_riesgo['categoria_mercado'] == 'Gama Media') & ((df_riesgo['odometer'] > 200000) | (df_riesgo['edad'] > 15)),
        (df_riesgo['categoria_mercado'] == 'Lujo') & ((df_riesgo['odometer'] > 100000) & (df_riesgo['edad'] < 5))
    ]
    df_riesgo['riesgo'] = np.select(condiciones_riesgo, ['Alto Riesgo', 'Alto Riesgo', 'Alto Riesgo'], default='Bajo Riesgo')
    return df_riesgo


