"""
Funciones para manipular y llenar archivos CSV.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

def guardar_resultado(resultados: List[Dict[str, Any]], archivo_salida: str = None) -> str:
    """
    Guarda una lista de resultados en archivo CSV.
    
    Args:
        resultados: Lista de diccionarios con resultados
        archivo_salida: Ruta del archivo de salida
        
    Returns:
        str: Ruta del archivo guardado
    """
    
    if not resultados:
        print("⚠️  No hay resultados para guardar")
        return ""
    
    # Crear directorio de salida si no existe
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Definir archivo de salida
    if not archivo_salida:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = output_dir / f"resultado_final_{timestamp}.csv"
    else:
        archivo_salida = Path(archivo_salida)
    
    try:
        # Convertir resultados a DataFrame
        df = normalizar_resultados_para_csv(resultados)
        
        # Guardar CSV
        df.to_csv(archivo_salida, index=False, encoding='utf-8')
        
        print(f"✅ Resultados guardados en: {archivo_salida}")
        print(f"📊 Dimensiones: {df.shape}")
        
        return str(archivo_salida)
        
    except Exception as e:
        print(f"❌ Error guardando resultados: {str(e)}")
        return ""

def normalizar_resultados_para_csv(resultados: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Normaliza una lista de resultados para convertir a CSV.
    
    Args:
        resultados: Lista de diccionarios con resultados
        
    Returns:
        pd.DataFrame: DataFrame normalizado
    """
    
    filas_normalizadas = []
    
    for i, resultado in enumerate(resultados):
        fila_normalizada = {"id": i + 1}
        
        # Agregar datos originales
        if "fila_original" in resultado:
            fila_original = resultado["fila_original"]
            for key, value in fila_original.items():
                fila_normalizada[f"original_{key}"] = value
        
        # Agregar respuesta LLM
        if "respuesta_llm" in resultado:
            respuesta_llm = resultado["respuesta_llm"]
            if isinstance(respuesta_llm, dict):
                for key, value in respuesta_llm.items():
                    fila_normalizada[f"llm_{key}"] = value
            else:
                fila_normalizada["llm_respuesta"] = str(respuesta_llm)
        
        # Agregar cálculo matemático
        if "calculo_matematico" in resultado:
            fila_normalizada["calculo_matematico"] = resultado["calculo_matematico"]
        
        # Agregar timestamp
        if "timestamp" in resultado:
            fila_normalizada["timestamp"] = resultado["timestamp"]
        
        filas_normalizadas.append(fila_normalizada)
    
    return pd.DataFrame(filas_normalizadas)

def cargar_datos_csv(archivo: str) -> pd.DataFrame:
    """
    Carga datos desde un archivo CSV.
    
    Args:
        archivo: Ruta del archivo CSV
        
    Returns:
        pd.DataFrame: DataFrame con los datos
    """
    
    try:
        if not Path(archivo).exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return pd.DataFrame()
        
        df = pd.read_csv(archivo, encoding='utf-8')
        print(f"✅ Datos cargados desde {archivo}: {df.shape}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error cargando CSV: {str(e)}")
        return pd.DataFrame()

def validar_estructura_csv(df: pd.DataFrame, columnas_requeridas: List[str]) -> bool:
    """
    Valida que un DataFrame tenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Lista de columnas que deben existir
        
    Returns:
        bool: True si es válido
    """
    
    if df.empty:
        print("❌ DataFrame está vacío")
        return False
    
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        print(f"❌ Columnas faltantes: {columnas_faltantes}")
        return False
    
    print("✅ Estructura CSV válida")
    return True

def limpiar_datos_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara datos CSV para procesamiento.
    
    Args:
        df: DataFrame a limpiar
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    
    df_limpio = df.copy()
    
    # Remover filas completamente vacías
    df_limpio = df_limpio.dropna(how='all')
    
    # Remover espacios en blanco en columnas de texto
    for col in df_limpio.select_dtypes(include=['object']).columns:
        df_limpio[col] = df_limpio[col].astype(str).str.strip()
    
    # Reemplazar valores vacíos con valores por defecto
    df_limpio = df_limpio.fillna({
        'nombre': 'Sin nombre',
        'edad': 0,
        'ciudad': 'Sin especificar'
    })
    
    print(f"✅ Datos limpiados: {df_limpio.shape}")
    return df_limpio

def agregar_columnas_calculadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columnas calculadas al DataFrame.
    
    Args:
        df: DataFrame base
        
    Returns:
        pd.DataFrame: DataFrame con columnas adicionales
    """
    
    df_calculado = df.copy()
    
    # Agregar ID secuencial si no existe
    if 'id' not in df_calculado.columns:
        df_calculado['id'] = range(1, len(df_calculado) + 1)
    
    # Agregar timestamp de procesamiento
    df_calculado['timestamp_procesamiento'] = datetime.now().isoformat()
    
    # Calcular edad en rangos si existe edad
    if 'edad' in df_calculado.columns:
        df_calculado['rango_edad'] = df_calculado['edad'].apply(clasificar_edad)
    
    # Agregar columnas de análisis
    df_calculado['procesado'] = True
    df_calculado['fuente'] = 'buyer_synthetic'
    
    return df_calculado

def clasificar_edad(edad: int) -> str:
    """
    Clasifica edad en rangos.
    
    Args:
        edad: Edad numérica
        
    Returns:
        str: Rango de edad
    """
    
    try:
        edad = int(edad)
        if edad < 18:
            return "Menor de edad"
        elif edad < 25:
            return "18-24"
        elif edad < 35:
            return "25-34"
        elif edad < 45:
            return "35-44"
        elif edad < 55:
            return "45-54"
        elif edad < 65:
            return "55-64"
        else:
            return "65+"
    except:
        return "No especificado"

def exportar_multiples_formatos(df: pd.DataFrame, nombre_base: str = "datos_procesados") -> List[str]:
    """
    Exporta DataFrame a múltiples formatos.
    
    Args:
        df: DataFrame a exportar
        nombre_base: Nombre base para los archivos
        
    Returns:
        List[str]: Lista de archivos creados
    """
    
    if df.empty:
        print("❌ No hay datos para exportar")
        return []
    
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    archivos_creados = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # CSV
        archivo_csv = output_dir / f"{nombre_base}_{timestamp}.csv"
        df.to_csv(archivo_csv, index=False, encoding='utf-8')
        archivos_creados.append(str(archivo_csv))
        
        # Excel
        archivo_excel = output_dir / f"{nombre_base}_{timestamp}.xlsx"
        df.to_excel(archivo_excel, index=False, engine='openpyxl')
        archivos_creados.append(str(archivo_excel))
        
        # JSON
        archivo_json = output_dir / f"{nombre_base}_{timestamp}.json"
        df.to_json(archivo_json, orient='records', indent=2, force_ascii=False)
        archivos_creados.append(str(archivo_json))
        
        print(f"✅ Datos exportados a {len(archivos_creados)} formatos")
        
    except Exception as e:
        print(f"❌ Error exportando: {str(e)}")
    
    return archivos_creados

def crear_resumen_datos(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Crea un resumen estadístico de los datos.
    
    Args:
        df: DataFrame a resumir
        
    Returns:
        Dict: Resumen estadístico
    """
    
    if df.empty:
        return {}
    
    resumen = {
        "total_filas": len(df),
        "total_columnas": len(df.columns),
        "columnas": list(df.columns),
        "tipos_datos": df.dtypes.to_dict(),
        "valores_nulos": df.isnull().sum().to_dict(),
        "estadisticas_numericas": {},
        "fecha_resumen": datetime.now().isoformat()
    }
    
    # Estadísticas para columnas numéricas
    columnas_numericas = df.select_dtypes(include=['number']).columns
    for col in columnas_numericas:
        resumen["estadisticas_numericas"][col] = {
            "media": float(df[col].mean()),
            "mediana": float(df[col].median()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "desviacion_std": float(df[col].std())
        }
    
    return resumen

def guardar_resumen_datos(df: pd.DataFrame, archivo: str = None) -> str:
    """
    Guarda resumen de datos en archivo JSON.
    
    Args:
        df: DataFrame a resumir
        archivo: Ruta del archivo de salida
        
    Returns:
        str: Ruta del archivo guardado
    """
    
    resumen = crear_resumen_datos(df)
    
    if not archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"output/resumen_datos_{timestamp}.json"
    
    try:
        Path(archivo).parent.mkdir(parents=True, exist_ok=True)
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Resumen guardado en: {archivo}")
        return archivo
        
    except Exception as e:
        print(f"❌ Error guardando resumen: {str(e)}")
        return ""

if __name__ == "__main__":
    # Ejemplo de uso
    print("📊 Probando funciones CSV...")
    
    # Crear datos de ejemplo
    datos_ejemplo = [
        {
            "fila_original": {"nombre": "Juan", "edad": 25, "ciudad": "Lima"},
            "respuesta_llm": {"satisfaccion": 8, "confianza": 0.85},
            "calculo_matematico": 25.5,
            "timestamp": datetime.now().isoformat()
        },
        {
            "fila_original": {"nombre": "María", "edad": 30, "ciudad": "Arequipa"},
            "respuesta_llm": {"satisfaccion": 9, "confianza": 0.92},
            "calculo_matematico": 30.2,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Guardar resultados
    archivo_guardado = guardar_resultado(datos_ejemplo)
    
    # Cargar y resumir
    if archivo_guardado:
        df = cargar_datos_csv(archivo_guardado)
        resumen = crear_resumen_datos(df)
        print(f"Resumen: {resumen}")