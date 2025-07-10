"""
Analizador de resultados de encuestas.
Genera reportes PDF y visualizaciones de los datos.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import Dict, Any, List
from fpdf import FPDF
import numpy as np
from datetime import datetime
import sys

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalizadorResultados:
    """Analizador de resultados de encuestas sintéticas"""
    
    def __init__(self, ruta_datos: str = None):
        self.ruta_datos = ruta_datos or "output/resultado_final.csv"
        self.datos = None
        self.figuras = []
        
    def cargar_datos(self) -> pd.DataFrame:
        """Carga los datos de resultados"""
        try:
            if Path(self.ruta_datos).exists():
                self.datos = pd.read_csv(self.ruta_datos)
                print(f"✅ Datos cargados: {self.datos.shape}")
                return self.datos
            else:
                print(f"❌ No se encontró el archivo: {self.ruta_datos}")
                return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error cargando datos: {str(e)}")
            return pd.DataFrame()
    
    def analizar_distribuciones(self) -> Dict[str, Any]:
        """Analiza las distribuciones de respuestas"""
        if self.datos is None or self.datos.empty:
            return {}
        
        analisis = {
            "resumen_general": {
                "total_respuestas": len(self.datos),
                "total_columnas": len(self.datos.columns),
                "fecha_analisis": datetime.now().isoformat()
            },
            "distribuciones": {}
        }
        
        # Analizar columnas numéricas
        columnas_numericas = self.datos.select_dtypes(include=[np.number]).columns
        for col in columnas_numericas:
            analisis["distribuciones"][col] = {
                "tipo": "numerica",
                "media": float(self.datos[col].mean()),
                "mediana": float(self.datos[col].median()),
                "desviacion_estandar": float(self.datos[col].std()),
                "min": float(self.datos[col].min()),
                "max": float(self.datos[col].max()),
                "valores_nulos": int(self.datos[col].isnull().sum())
            }
        
        # Analizar columnas categóricas
        columnas_categoricas = self.datos.select_dtypes(include=['object']).columns
        for col in columnas_categoricas:
            valores_unicos = self.datos[col].value_counts().head(10)
            analisis["distribuciones"][col] = {
                "tipo": "categorica",
                "valores_unicos": int(self.datos[col].nunique()),
                "top_valores": valores_unicos.to_dict(),
                "valores_nulos": int(self.datos[col].isnull().sum())
            }
        
        return analisis
    
    def generar_graficas(self) -> List[str]:
        """Genera gráficas de análisis"""
        if self.datos is None or self.datos.empty:
            return []
        
        rutas_graficas = []
        output_dir = Path("output/graficas")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Gráfica 1: Distribución de edades (si existe)
        if 'edad' in self.datos.columns:
            plt.figure(figsize=(10, 6))
            plt.hist(self.datos['edad'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Distribución de Edades', fontsize=16, fontweight='bold')
            plt.xlabel('Edad')
            plt.ylabel('Frecuencia')
            plt.grid(True, alpha=0.3)
            
            ruta = output_dir / "distribucion_edades.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            plt.close()
            rutas_graficas.append(str(ruta))
        
        # Gráfica 2: Distribución por ciudades (si existe)
        if 'ciudad' in self.datos.columns:
            plt.figure(figsize=(12, 8))
            ciudades = self.datos['ciudad'].value_counts().head(10)
            plt.bar(ciudades.index, ciudades.values, color='lightcoral', alpha=0.8)
            plt.title('Distribución por Ciudades', fontsize=16, fontweight='bold')
            plt.xlabel('Ciudad')
            plt.ylabel('Cantidad')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            ruta = output_dir / "distribucion_ciudades.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            plt.close()
            rutas_graficas.append(str(ruta))
        
        # Gráfica 3: Matriz de correlación para variables numéricas
        columnas_numericas = self.datos.select_dtypes(include=[np.number]).columns
        if len(columnas_numericas) > 1:
            plt.figure(figsize=(10, 8))
            matriz_corr = self.datos[columnas_numericas].corr()
            sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', center=0, 
                       square=True, fmt='.2f')
            plt.title('Matriz de Correlación', fontsize=16, fontweight='bold')
            
            ruta = output_dir / "matriz_correlacion.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            plt.close()
            rutas_graficas.append(str(ruta))
        
        # Gráfica 4: Distribución de confianza (si existe)
        columnas_confianza = [col for col in self.datos.columns if 'confianza' in col.lower()]
        if columnas_confianza:
            plt.figure(figsize=(12, 6))
            for i, col in enumerate(columnas_confianza[:5]):  # Máximo 5 columnas
                plt.subplot(1, min(5, len(columnas_confianza)), i+1)
                self.datos[col].hist(bins=20, alpha=0.7, color=f'C{i}')
                plt.title(f'Confianza\n{col}', fontsize=10)
                plt.xlabel('Confianza')
                plt.ylabel('Frecuencia')
            
            plt.tight_layout()
            ruta = output_dir / "distribucion_confianza.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            plt.close()
            rutas_graficas.append(str(ruta))
        
        print(f"✅ Generadas {len(rutas_graficas)} gráficas")
        return rutas_graficas
    
    def generar_reporte_pdf(self, analisis: Dict[str, Any], rutas_graficas: List[str]) -> str:
        """Genera un reporte PDF con el análisis"""
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Buyer Synthetic - Reporte de Análisis', 0, 1, 'C')
                self.ln(5)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        
        # Resumen general
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Resumen General', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        resumen = analisis.get("resumen_general", {})
        pdf.cell(0, 6, f'Total de respuestas: {resumen.get("total_respuestas", 0)}', 0, 1)
        pdf.cell(0, 6, f'Total de columnas: {resumen.get("total_columnas", 0)}', 0, 1)
        pdf.cell(0, 6, f'Fecha de análisis: {resumen.get("fecha_analisis", "N/A")}', 0, 1)
        pdf.ln(5)
        
        # Distribuciones
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Análisis de Distribuciones', 0, 1)
        
        distribuciones = analisis.get("distribuciones", {})
        for variable, datos in distribuciones.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'{variable}:', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            if datos.get("tipo") == "numerica":
                pdf.cell(0, 5, f'  Media: {datos.get("media", 0):.2f}', 0, 1)
                pdf.cell(0, 5, f'  Mediana: {datos.get("mediana", 0):.2f}', 0, 1)
                pdf.cell(0, 5, f'  Desviación estándar: {datos.get("desviacion_estandar", 0):.2f}', 0, 1)
                pdf.cell(0, 5, f'  Rango: {datos.get("min", 0):.2f} - {datos.get("max", 0):.2f}', 0, 1)
            
            elif datos.get("tipo") == "categorica":
                pdf.cell(0, 5, f'  Valores únicos: {datos.get("valores_unicos", 0)}', 0, 1)
                top_valores = datos.get("top_valores", {})
                for valor, frecuencia in list(top_valores.items())[:3]:
                    pdf.cell(0, 5, f'    {valor}: {frecuencia}', 0, 1)
            
            pdf.ln(3)
        
        # Agregar gráficas
        if rutas_graficas:
            for ruta in rutas_graficas:
                if Path(ruta).exists():
                    pdf.add_page()
                    pdf.set_font('Arial', 'B', 14)
                    nombre_grafica = Path(ruta).stem.replace('_', ' ').title()
                    pdf.cell(0, 10, nombre_grafica, 0, 1)
                    
                    # Agregar imagen
                    try:
                        pdf.image(ruta, x=10, y=30, w=190)
                    except Exception as e:
                        pdf.set_font('Arial', '', 10)
                        pdf.cell(0, 10, f'Error cargando imagen: {str(e)}', 0, 1)
        
        # Guardar PDF
        output_path = Path("output/reporte_analisis.pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))
        
        print(f"✅ Reporte PDF generado: {output_path}")
        return str(output_path)
    
    def ejecutar_analisis_completo(self) -> Dict[str, Any]:
        """Ejecuta el análisis completo"""
        print("📊 Iniciando análisis completo...")
        
        # Cargar datos
        self.cargar_datos()
        
        if self.datos is None or self.datos.empty:
            print("❌ No hay datos para analizar")
            return {}
        
        # Generar análisis
        analisis = self.analizar_distribuciones()
        
        # Generar gráficas
        rutas_graficas = self.generar_graficas()
        
        # Generar reporte PDF
        ruta_pdf = self.generar_reporte_pdf(analisis, rutas_graficas)
        
        resultado = {
            "analisis": analisis,
            "rutas_graficas": rutas_graficas,
            "ruta_pdf": ruta_pdf
        }
        
        print("✅ Análisis completo terminado")
        return resultado

def ejemplo_uso():
    """Ejemplo de uso del analizador"""
    analizador = AnalizadorResultados()
    resultado = analizador.ejecutar_analisis_completo()
    return resultado

if __name__ == "__main__":
    ejemplo_uso()