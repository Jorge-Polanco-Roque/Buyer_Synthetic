"""
Agente Visualizador de Resultados - Análisis y gráficas de encuestas electorales
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json
from pathlib import Path

from buyer_synthetic.config.settings import settings
from buyer_synthetic.utils.logger import get_logger
from buyer_synthetic.utils.math_tools import StatisticalAnalyzer

logger = get_logger(__name__)

class ResultsVisualizerAgent:
    """Agente para visualización y análisis de resultados electorales"""
    
    def __init__(self):
        self.logger = logger
        self.analyzer = StatisticalAnalyzer()
        
        # Configurar estilo de gráficas
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("Set2")
        
    def analyze_and_visualize(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis completo y visualización de resultados"""
        
        self.logger.info(f"Analizando resultados de {len(results_df)} respuestas")
        
        # Análisis estadístico
        analysis_results = {
            "summary": self._generate_summary(results_df),
            "demographic_analysis": self._analyze_demographics(results_df),
            "electoral_analysis": self._analyze_electoral_responses(results_df),
            "statistical_tests": self._perform_statistical_tests(results_df),
            "insights": self._generate_insights(results_df)
        }
        
        # Generar visualizaciones
        viz_paths = self._create_visualizations(results_df, analysis_results)
        analysis_results["visualizations"] = viz_paths
        
        # Guardar análisis
        analysis_path = self._save_analysis(analysis_results)
        analysis_results["analysis_file"] = analysis_path
        
        self.logger.info("Análisis completado exitosamente")
        return analysis_results
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen ejecutivo"""
        
        return {
            "total_responses": len(df),
            "response_date": datetime.now().isoformat(),
            "sample_composition": {
                "nse_distribution": df['nse'].value_counts().to_dict() if 'nse' in df.columns else {},
                "region_distribution": df['region'].value_counts().to_dict() if 'region' in df.columns else {},
                "gender_distribution": df['genero'].value_counts().to_dict() if 'genero' in df.columns else {},
                "age_stats": {
                    "mean": float(df['edad'].mean()) if 'edad' in df.columns else 0,
                    "median": float(df['edad'].median()) if 'edad' in df.columns else 0,
                    "std": float(df['edad'].std()) if 'edad' in df.columns else 0
                }
            },
            "data_quality": {
                "completion_rate": self._calculate_completion_rate(df),
                "average_confidence": self._calculate_average_confidence(df)
            }
        }
    
    def _analyze_demographics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis demográfico detallado"""
        
        demographic_analysis = {}
        
        # Análisis por NSE
        demographic_analysis["by_nse"] = self._analyze_by_dimension(df, "nse")
        
        # Análisis por región  
        demographic_analysis["by_region"] = self._analyze_by_dimension(df, "region")
        
        # Análisis por edad
        df['grupo_edad'] = pd.cut(df['edad'], bins=[18, 30, 45, 60, 100], 
                                 labels=['18-29', '30-44', '45-59', '60+'])
        demographic_analysis["by_age_group"] = self._analyze_by_dimension(df, "grupo_edad")
        
        # Cross-tabulations
        demographic_analysis["cross_tabs"] = self._generate_cross_tabs(df)
        
        return demographic_analysis
    
    def _analyze_electoral_responses(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico de respuestas electorales"""
        
        electoral_analysis = {}
        
        # Intención de voto
        if 'intent_voto_respuesta' in df.columns:
            electoral_analysis["intencion_voto"] = self._analyze_voting_intention(df)
        
        # Aprobación gubernamental
        if 'aprobacion_gobierno_respuesta' in df.columns:
            electoral_analysis["aprobacion_gobierno"] = self._analyze_government_approval(df)
        
        # Principales problemas
        if 'principal_problema_respuesta' in df.columns:
            electoral_analysis["principales_problemas"] = self._analyze_main_problems(df)
        
        # Confianza institucional
        if 'confianza_instituciones_respuesta' in df.columns:
            electoral_analysis["confianza_institucional"] = self._analyze_institutional_trust(df)
        
        return electoral_analysis
    
    def _perform_statistical_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Realiza tests estadísticos usando math_tools"""
        
        tests_results = {}
        
        # Test de independencia chi-cuadrado
        if 'intent_voto_respuesta' in df.columns and 'nse' in df.columns:
            chi2_result = self.analyzer.chi_square_test(
                df['intent_voto_respuesta'], df['nse']
            )
            tests_results["voto_por_nse"] = chi2_result
        
        # Correlaciones
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            correlation_matrix = self.analyzer.correlation_matrix(df[numeric_cols])
            tests_results["correlations"] = correlation_matrix
        
        # ANOVA para diferencias por grupos
        if 'aprobacion_gobierno_respuesta' in df.columns:
            try:
                approval_scores = pd.to_numeric(df['aprobacion_gobierno_respuesta'], errors='coerce')
                anova_result = self.analyzer.anova_test(approval_scores, df['nse'])
                tests_results["approval_by_nse"] = anova_result
            except:
                self.logger.warning("No se pudo realizar ANOVA para aprobación")
        
        return tests_results
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Genera insights clave basados en el análisis"""
        
        insights = []
        
        # Insight sobre participación
        total_responses = len(df)
        insights.append(f"Se generaron {total_responses} respuestas sintéticas representativas")
        
        # Insight sobre distribución demográfica
        nse_dist = df['nse'].value_counts(normalize=True)
        dominant_nse = nse_dist.idxmax()
        insights.append(f"NSE {dominant_nse} representa el {nse_dist[dominant_nse]:.1%} de la muestra")
        
        # Insights electorales
        if 'intent_voto_respuesta' in df.columns:
            voto_dist = df['intent_voto_respuesta'].value_counts()
            if len(voto_dist) > 0:
                leading_candidate = voto_dist.idxmax()
                insights.append(f"'{leading_candidate}' lidera intención de voto con {voto_dist[leading_candidate]} menciones")
        
        # Insight sobre problemas principales
        if 'principal_problema_respuesta' in df.columns:
            problem_dist = df['principal_problema_respuesta'].value_counts()
            if len(problem_dist) > 0:
                main_problem = problem_dist.idxmax()
                insights.append(f"'{main_problem}' es el principal problema identificado")
        
        # Insight sobre confianza
        if 'confianza_instituciones_respuesta' in df.columns:
            try:
                conf_scores = pd.to_numeric(df['confianza_instituciones_respuesta'], errors='coerce')
                avg_confidence = conf_scores.mean()
                insights.append(f"Confianza institucional promedio: {avg_confidence:.1f}/10")
            except:
                pass
        
        return insights
    
    def _create_visualizations(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Crea todas las visualizaciones"""
        
        viz_paths = []
        viz_dir = settings.OUTPUT_DIR / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Distribución demográfica
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # NSE
        if 'nse' in df.columns:
            df['nse'].value_counts().plot(kind='bar', ax=axes[0,0], color='skyblue')
            axes[0,0].set_title('Distribución por NSE')
            axes[0,0].set_ylabel('Cantidad')
        else:
            axes[0,0].text(0.5, 0.5, 'No hay datos NSE', ha='center', va='center', transform=axes[0,0].transAxes)
        
        # Región
        if 'region' in df.columns:
            df['region'].value_counts().plot(kind='bar', ax=axes[0,1], color='lightcoral')
            axes[0,1].set_title('Distribución por Región')
            axes[0,1].set_ylabel('Cantidad')
        else:
            axes[0,1].text(0.5, 0.5, 'No hay datos Región', ha='center', va='center', transform=axes[0,1].transAxes)
        
        # Edad
        if 'edad' in df.columns:
            df['edad'].hist(bins=20, ax=axes[1,0], color='lightgreen', alpha=0.7)
            axes[1,0].set_title('Distribución de Edades')
            axes[1,0].set_xlabel('Edad')
            axes[1,0].set_ylabel('Frecuencia')
        else:
            axes[1,0].text(0.5, 0.5, 'No hay datos Edad', ha='center', va='center', transform=axes[1,0].transAxes)
        
        # Género
        if 'genero' in df.columns:
            df['genero'].value_counts().plot(kind='pie', ax=axes[1,1], autopct='%1.1f%%')
            axes[1,1].set_title('Distribución por Género')
        else:
            axes[1,1].text(0.5, 0.5, 'No hay datos Género', ha='center', va='center', transform=axes[1,1].transAxes)
        
        plt.tight_layout()
        demo_path = viz_dir / f"demografia_{timestamp}.png"
        plt.savefig(demo_path, dpi=300, bbox_inches='tight')
        plt.close()
        viz_paths.append(str(demo_path))
        
        # 2. Intención de voto
        if 'intent_voto_respuesta' in df.columns:
            plt.figure(figsize=(12, 8))
            voto_counts = df['intent_voto_respuesta'].value_counts()
            
            plt.subplot(2, 1, 1)
            voto_counts.plot(kind='bar', color='steelblue')
            plt.title('Intención de Voto - Total')
            plt.ylabel('Cantidad')
            plt.xticks(rotation=45)
            
            # Por NSE
            plt.subplot(2, 1, 2)
            cross_tab = pd.crosstab(df['nse'], df['intent_voto_respuesta'])
            cross_tab.plot(kind='bar', stacked=True, ax=plt.gca())
            plt.title('Intención de Voto por NSE')
            plt.ylabel('Cantidad')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            voto_path = viz_dir / f"intencion_voto_{timestamp}.png"
            plt.savefig(voto_path, dpi=300, bbox_inches='tight')
            plt.close()
            viz_paths.append(str(voto_path))
        
        # 3. Principales problemas
        if 'principal_problema_respuesta' in df.columns:
            plt.figure(figsize=(12, 8))
            
            problem_counts = df['principal_problema_respuesta'].value_counts()
            
            plt.subplot(2, 1, 1)
            problem_counts.plot(kind='barh', color='orange')
            plt.title('Principales Problemas del País')
            plt.xlabel('Cantidad de Menciones')
            
            # Heatmap por región
            plt.subplot(2, 1, 2)
            cross_tab = pd.crosstab(df['region'], df['principal_problema_respuesta'])
            sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd')
            plt.title('Principales Problemas por Región')
            
            plt.tight_layout()
            problems_path = viz_dir / f"principales_problemas_{timestamp}.png"
            plt.savefig(problems_path, dpi=300, bbox_inches='tight')
            plt.close()
            viz_paths.append(str(problems_path))
        
        # 4. Análisis de confianza y aprobación
        numeric_responses = []
        labels = []
        
        if 'aprobacion_gobierno_respuesta' in df.columns:
            try:
                approval = pd.to_numeric(df['aprobacion_gobierno_respuesta'], errors='coerce')
                numeric_responses.append(approval.dropna())
                labels.append('Aprobación Gobierno')
            except:
                pass
        
        if 'confianza_instituciones_respuesta' in df.columns:
            try:
                trust = pd.to_numeric(df['confianza_instituciones_respuesta'], errors='coerce')
                numeric_responses.append(trust.dropna())
                labels.append('Confianza Institucional')
            except:
                pass
        
        if numeric_responses:
            plt.figure(figsize=(12, 6))
            
            for i, (data, label) in enumerate(zip(numeric_responses, labels)):
                plt.subplot(1, len(numeric_responses), i+1)
                data.hist(bins=10, alpha=0.7, color=f'C{i}')
                plt.title(f'{label}\n(Promedio: {data.mean():.1f})')
                plt.xlabel('Puntuación (1-10)')
                plt.ylabel('Frecuencia')
            
            plt.tight_layout()
            scores_path = viz_dir / f"puntuaciones_{timestamp}.png"
            plt.savefig(scores_path, dpi=300, bbox_inches='tight')
            plt.close()
            viz_paths.append(str(scores_path))
        
        self.logger.info(f"Generadas {len(viz_paths)} visualizaciones")
        return viz_paths
    
    def _calculate_completion_rate(self, df: pd.DataFrame) -> float:
        """Calcula tasa de completitud de respuestas"""
        response_cols = [col for col in df.columns if col.endswith('_respuesta')]
        if not response_cols:
            return 0.0
        
        total_possible = len(df) * len(response_cols)
        total_completed = df[response_cols].notna().sum().sum()
        
        return float(total_completed / total_possible)
    
    def _calculate_average_confidence(self, df: pd.DataFrame) -> float:
        """Calcula confianza promedio de respuestas"""
        confidence_cols = [col for col in df.columns if col.endswith('_confianza')]
        if not confidence_cols:
            return 0.0
        
        all_confidences = []
        for col in confidence_cols:
            confidences = pd.to_numeric(df[col], errors='coerce').dropna()
            all_confidences.extend(confidences.tolist())
        
        return float(np.mean(all_confidences)) if all_confidences else 0.0
    
    def _analyze_by_dimension(self, df: pd.DataFrame, dimension: str) -> Dict[str, Any]:
        """Análisis por dimensión específica"""
        
        analysis = {
            "distribution": df[dimension].value_counts().to_dict(),
            "percentage": df[dimension].value_counts(normalize=True).to_dict()
        }
        
        # Análisis de respuestas por dimensión
        response_cols = [col for col in df.columns if col.endswith('_respuesta')]
        
        for col in response_cols[:3]:  # Primeras 3 preguntas
            cross_tab = pd.crosstab(df[dimension], df[col])
            analysis[f"{col}_by_{dimension}"] = cross_tab.to_dict()
        
        return analysis
    
    def _generate_cross_tabs(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera tablas cruzadas importantes"""
        
        cross_tabs = {}
        
        # NSE x Región
        cross_tabs["nse_region"] = pd.crosstab(df['nse'], df['region']).to_dict()
        
        # NSE x Grupo de edad
        if 'grupo_edad' in df.columns:
            cross_tabs["nse_edad"] = pd.crosstab(df['nse'], df['grupo_edad']).to_dict()
        
        return cross_tabs
    
    def _analyze_voting_intention(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico de intención de voto"""
        
        voting_analysis = {
            "total_distribution": df['intent_voto_respuesta'].value_counts().to_dict(),
            "by_nse": pd.crosstab(df['nse'], df['intent_voto_respuesta']).to_dict(),
            "by_region": pd.crosstab(df['region'], df['intent_voto_respuesta']).to_dict()
        }
        
        return voting_analysis
    
    def _analyze_government_approval(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de aprobación gubernamental"""
        
        try:
            approval_scores = pd.to_numeric(df['aprobacion_gobierno_respuesta'], errors='coerce').dropna()
            
            analysis = {
                "average_score": float(approval_scores.mean()),
                "median_score": float(approval_scores.median()),
                "std_deviation": float(approval_scores.std()),
                "distribution": approval_scores.value_counts().to_dict()
            }
            
            # Por NSE
            nse_approval = df.groupby('nse')['aprobacion_gobierno_respuesta'].apply(
                lambda x: pd.to_numeric(x, errors='coerce').mean()
            ).to_dict()
            analysis["by_nse"] = nse_approval
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analizando aprobación: {str(e)}")
            return {}
    
    def _analyze_main_problems(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de principales problemas"""
        
        return {
            "ranking": df['principal_problema_respuesta'].value_counts().to_dict(),
            "by_nse": pd.crosstab(df['nse'], df['principal_problema_respuesta']).to_dict(),
            "by_region": pd.crosstab(df['region'], df['principal_problema_respuesta']).to_dict()
        }
    
    def _analyze_institutional_trust(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de confianza institucional"""
        
        try:
            trust_scores = pd.to_numeric(df['confianza_instituciones_respuesta'], errors='coerce').dropna()
            
            return {
                "average_trust": float(trust_scores.mean()),
                "median_trust": float(trust_scores.median()),
                "low_trust_percentage": float((trust_scores <= 3).mean()),
                "high_trust_percentage": float((trust_scores >= 7).mean())
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando confianza: {str(e)}")
            return {}
    
    def _save_analysis(self, analysis: Dict[str, Any]) -> str:
        """Guarda análisis completo en JSON"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analisis_electoral_{timestamp}.json"
        filepath = settings.OUTPUT_DIR / filename
        
        # Convertir numpy types a tipos serializables
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
                return str(obj)
            return obj
        
        def clean_for_json(data):
            if isinstance(data, dict):
                return {k: clean_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_for_json(v) for v in data]
            elif isinstance(data, bool):
                return bool(data)
            else:
                return convert_numpy(data)
        
        clean_analysis = clean_for_json(analysis)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_analysis, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Análisis guardado en: {filepath}")
        return str(filepath)

def main():
    """Función principal para testing"""
    # Cargar resultados (asumiendo que existen)
    results_path = settings.OUTPUT_DIR / "encuesta_electoral.csv"
    
    if not results_path.exists():
        print("❌ No se encontraron resultados. Ejecuta primero survey_executor.py")
        return
    
    results_df = pd.read_csv(results_path)
    
    visualizer = ResultsVisualizerAgent()
    analysis = visualizer.analyze_and_visualize(results_df)
    
    print(f"✅ Análisis completado")
    print(f"📊 Insights: {analysis['insights']}")
    print(f"📈 Visualizaciones: {len(analysis['visualizations'])} gráficas generadas")

if __name__ == "__main__":
    main()