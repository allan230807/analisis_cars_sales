import pandas as pd
import src.limpieza as limpieza
import src.analisis as analisis
import numpy as np 
def main():
    # 1. Cargar el dataset original
    print("🚀 Cargando datos originales...")
    df_raw = pd.read_csv('data/raw/car_prices.csv')
    
    # 2. Limpieza de datos
    print("🧹 Ejecutando pipeline de limpieza...")
    df_clean = limpieza.limpiar_datos(df_raw)
    
    # Adición de variables base necesarias para el análisis antes de evaluar riesgo
    df_clean['margen_usd'] = df_clean['sellingprice'] - df_clean['mmr']
    df_clean['depreciacion_anual'] = (df_clean['mmr'] - df_clean['sellingprice']) / df_clean['edad']
    df_clean['depreciacion_anual'] = df_clean['depreciacion_anual'].clip(lower=0)
    
    # 3. Enriquecer con el modelo de riesgo segmentado
    print("🧠 Evaluando riesgo y segmentación de mercado...")
    df_final = analisis.evaluar_riesgo_segmentado(df_clean)
    
    # 4. Verificar calidad e imprimir reporte rápido en consola
    print("\n📊 --- REPORTE COMPROBACIÓN DE CALIDAD ---")
    reporte = analisis.verificar_calidad(df_final)
    for clave, valor in reporte.items():
        print(f"{clave}: {valor}")
    
    # 5. Exportar el dataset procesado para el Dashboard de Streamlit
    print("\n💾 Guardando dataset enriquecido...")
    df_final.to_csv('car_prices_clean.csv', index=False)
    print("✅ ¡Proceso completado con éxito! Archivo 'car_prices_clean.csv' listo.")

if __name__ == "__main__":
    main()