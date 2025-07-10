"""
Funciones para cálculos matemáticos adicionales.
"""

import math
import numpy as np
from typing import Union, List, Dict, Any
import pandas as pd

def calcular_operacion(a: float, b: float, operacion: str = "suma_cuadrados") -> float:
    """
    Realiza operaciones matemáticas básicas.
    
    Args:
        a: Primer número
        b: Segundo número
        operacion: Tipo de operación
        
    Returns:
        float: Resultado de la operación
    """
    
    try:
        if operacion == "suma_cuadrados":
            return a**2 + b**2
        elif operacion == "suma":
            return a + b
        elif operacion == "resta":
            return a - b
        elif operacion == "multiplicacion":
            return a * b
        elif operacion == "division":
            return a / b if b != 0 else 0
        elif operacion == "promedio":
            return (a + b) / 2
        elif operacion == "distancia_euclidiana":
            return math.sqrt(a**2 + b**2)
        elif operacion == "maximo":
            return max(a, b)
        elif operacion == "minimo":
            return min(a, b)
        else:
            return a**2 + b**2  # Por defecto
            
    except Exception as e:
        print(f"❌ Error en cálculo: {str(e)}")
        return 0.0

def calcular_estadisticas_basicas(datos: List[float]) -> Dict[str, float]:
    """
    Calcula estadísticas básicas de una lista de números.
    
    Args:
        datos: Lista de números
        
    Returns:
        Dict: Estadísticas calculadas
    """
    
    if not datos:
        return {}
    
    try:
        datos_array = np.array(datos)
        
        return {
            "media": float(np.mean(datos_array)),
            "mediana": float(np.median(datos_array)),
            "desviacion_estandar": float(np.std(datos_array)),
            "varianza": float(np.var(datos_array)),
            "minimo": float(np.min(datos_array)),
            "maximo": float(np.max(datos_array)),
            "rango": float(np.max(datos_array) - np.min(datos_array)),
            "suma": float(np.sum(datos_array)),
            "cantidad": len(datos_array)
        }
        
    except Exception as e:
        print(f"❌ Error calculando estadísticas: {str(e)}")
        return {}

def calcular_correlacion(x: List[float], y: List[float]) -> float:
    """
    Calcula la correlación entre dos listas de números.
    
    Args:
        x: Primera lista
        y: Segunda lista
        
    Returns:
        float: Coeficiente de correlación
    """
    
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    
    try:
        return float(np.corrcoef(x, y)[0, 1])
    except Exception as e:
        print(f"❌ Error calculando correlación: {str(e)}")
        return 0.0

def calcular_percentiles(datos: List[float], percentiles: List[float] = [25, 50, 75]) -> Dict[str, float]:
    """
    Calcula percentiles de una lista de datos.
    
    Args:
        datos: Lista de números
        percentiles: Lista de percentiles a calcular
        
    Returns:
        Dict: Percentiles calculados
    """
    
    if not datos:
        return {}
    
    try:
        datos_array = np.array(datos)
        resultado = {}
        
        for p in percentiles:
            resultado[f"percentil_{p}"] = float(np.percentile(datos_array, p))
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error calculando percentiles: {str(e)}")
        return {}

def normalizar_datos(datos: List[float], metodo: str = "minmax") -> List[float]:
    """
    Normaliza una lista de datos.
    
    Args:
        datos: Lista de números
        metodo: Método de normalización ('minmax', 'zscore')
        
    Returns:
        List[float]: Datos normalizados
    """
    
    if not datos:
        return []
    
    try:
        datos_array = np.array(datos)
        
        if metodo == "minmax":
            # Normalización min-max (0-1)
            min_val = np.min(datos_array)
            max_val = np.max(datos_array)
            if max_val == min_val:
                return [0.5] * len(datos)
            return ((datos_array - min_val) / (max_val - min_val)).tolist()
        
        elif metodo == "zscore":
            # Normalización Z-score
            media = np.mean(datos_array)
            std = np.std(datos_array)
            if std == 0:
                return [0.0] * len(datos)
            return ((datos_array - media) / std).tolist()
        
        else:
            return datos
            
    except Exception as e:
        print(f"❌ Error normalizando datos: {str(e)}")
        return datos

def calcular_distancia_entre_puntos(punto1: List[float], punto2: List[float]) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos.
    
    Args:
        punto1: Coordenadas del primer punto
        punto2: Coordenadas del segundo punto
        
    Returns:
        float: Distancia euclidiana
    """
    
    if len(punto1) != len(punto2):
        return 0.0
    
    try:
        suma_cuadrados = sum((a - b)**2 for a, b in zip(punto1, punto2))
        return math.sqrt(suma_cuadrados)
    except Exception as e:
        print(f"❌ Error calculando distancia: {str(e)}")
        return 0.0

def calcular_indice_satisfaccion(respuestas: Dict[str, Any]) -> float:
    """
    Calcula un índice de satisfacción basado en respuestas.
    
    Args:
        respuestas: Diccionario con respuestas
        
    Returns:
        float: Índice de satisfacción (0-1)
    """
    
    try:
        # Buscar campos relacionados con satisfacción/calificación
        campos_satisfaccion = []
        
        for campo, valor in respuestas.items():
            if any(keyword in campo.lower() for keyword in ['satisfaccion', 'calificacion', 'rating', 'score']):
                try:
                    num_valor = float(valor)
                    campos_satisfaccion.append(num_valor)
                except:
                    pass
        
        if not campos_satisfaccion:
            return 0.5  # Valor neutral si no hay datos
        
        # Normalizar a escala 0-1 (asumiendo escala 1-10)
        indices_normalizados = [max(0, min(1, (x - 1) / 9)) for x in campos_satisfaccion]
        
        return sum(indices_normalizados) / len(indices_normalizados)
        
    except Exception as e:
        print(f"❌ Error calculando índice de satisfacción: {str(e)}")
        return 0.5

def calcular_coherencia_respuestas(respuestas: Dict[str, Any]) -> float:
    """
    Calcula un índice de coherencia de respuestas.
    
    Args:
        respuestas: Diccionario con respuestas
        
    Returns:
        float: Índice de coherencia (0-1)
    """
    
    try:
        # Buscar campos de confianza
        confianzas = []
        
        for campo, valor in respuestas.items():
            if 'confianza' in campo.lower():
                try:
                    confianza = float(valor)
                    confianzas.append(confianza)
                except:
                    pass
        
        if not confianzas:
            return 0.7  # Valor por defecto
        
        # Calcular coherencia basada en la varianza de confianzas
        varianza_confianza = np.var(confianzas)
        coherencia = max(0, 1 - varianza_confianza)
        
        return float(coherencia)
        
    except Exception as e:
        print(f"❌ Error calculando coherencia: {str(e)}")
        return 0.7

def generar_puntaje_calidad(respuestas: Dict[str, Any]) -> Dict[str, float]:
    """
    Genera un puntaje de calidad general de las respuestas.
    
    Args:
        respuestas: Diccionario con respuestas
        
    Returns:
        Dict: Puntajes de calidad
    """
    
    try:
        # Calcular diferentes métricas
        satisfaccion = calcular_indice_satisfaccion(respuestas)
        coherencia = calcular_coherencia_respuestas(respuestas)
        
        # Contar respuestas válidas
        respuestas_validas = sum(1 for v in respuestas.values() if v and str(v).strip())
        total_respuestas = len(respuestas)
        completitud = respuestas_validas / total_respuestas if total_respuestas > 0 else 0
        
        # Calcular puntaje general
        puntaje_general = (satisfaccion * 0.4 + coherencia * 0.3 + completitud * 0.3)
        
        return {
            "satisfaccion": satisfaccion,
            "coherencia": coherencia,
            "completitud": completitud,
            "puntaje_general": puntaje_general,
            "respuestas_validas": respuestas_validas,
            "total_respuestas": total_respuestas
        }
        
    except Exception as e:
        print(f"❌ Error generando puntaje de calidad: {str(e)}")
        return {
            "satisfaccion": 0.5,
            "coherencia": 0.5,
            "completitud": 0.5,
            "puntaje_general": 0.5,
            "respuestas_validas": 0,
            "total_respuestas": 0
        }

if __name__ == "__main__":
    # Ejemplos de uso
    print("🔢 Probando funciones matemáticas...")
    
    # Operaciones básicas
    resultado = calcular_operacion(3, 4, "suma_cuadrados")
    print(f"3² + 4² = {resultado}")
    
    # Estadísticas
    datos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    estadisticas = calcular_estadisticas_basicas(datos)
    print(f"Estadísticas: {estadisticas}")
    
    # Ejemplo con respuestas
    respuestas_ejemplo = {
        "satisfaccion": 8,
        "calificacion": 7,
        "confianza": 0.85,
        "respuesta_1": "Muy bueno",
        "respuesta_2": "Excelente"
    }
    
    calidad = generar_puntaje_calidad(respuestas_ejemplo)
    print(f"Puntaje de calidad: {calidad}")