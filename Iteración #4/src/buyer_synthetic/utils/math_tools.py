"""
Herramientas matemáticas y estadísticas para análisis de encuestas
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class StatisticalAnalyzer:
    """Analizador estadístico para datos de encuestas"""
    
    def __init__(self):
        self.confidence_level = 0.95
        self.alpha = 1 - self.confidence_level
    
    def descriptive_stats(self, data: pd.Series) -> Dict[str, float]:
        """Estadísticas descriptivas básicas"""
        
        data_clean = pd.to_numeric(data, errors='coerce').dropna()
        
        if len(data_clean) == 0:
            return {}
        
        return {
            "count": len(data_clean),
            "mean": float(data_clean.mean()),
            "median": float(data_clean.median()),
            "std": float(data_clean.std()),
            "min": float(data_clean.min()),
            "max": float(data_clean.max()),
            "q25": float(data_clean.quantile(0.25)),
            "q75": float(data_clean.quantile(0.75)),
            "skewness": float(stats.skew(data_clean)),
            "kurtosis": float(stats.kurtosis(data_clean))
        }
    
    def confidence_interval(self, data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
        """Intervalo de confianza para la media"""
        
        data_clean = pd.to_numeric(data, errors='coerce').dropna()
        
        if len(data_clean) < 2:
            return (0.0, 0.0)
        
        mean = data_clean.mean()
        sem = stats.sem(data_clean)  # Error estándar de la media
        
        # Usar t-distribution para muestras pequeñas
        if len(data_clean) < 30:
            t_value = stats.t.ppf((1 + confidence) / 2, len(data_clean) - 1)
            margin_error = t_value * sem
        else:
            z_value = stats.norm.ppf((1 + confidence) / 2)
            margin_error = z_value * sem
        
        return (float(mean - margin_error), float(mean + margin_error))
    
    def chi_square_test(self, var1: pd.Series, var2: pd.Series) -> Dict[str, Any]:
        """Test de independencia chi-cuadrado"""
        
        try:
            # Crear tabla de contingencia
            crosstab = pd.crosstab(var1, var2)
            
            # Realizar test
            chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
            
            # Calcular V de Cramer (tamaño del efecto)
            n = crosstab.sum().sum()
            cramers_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
            
            return {
                "chi2_statistic": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "cramers_v": float(cramers_v),
                "significant": p_value < self.alpha,
                "contingency_table": crosstab.to_dict()
            }
            
        except Exception as e:
            return {"error": str(e), "test": "chi_square"}
    
    def anova_test(self, values: pd.Series, groups: pd.Series) -> Dict[str, Any]:
        """Análisis de varianza (ANOVA)"""
        
        try:
            # Limpiar datos
            df_clean = pd.DataFrame({"values": values, "groups": groups}).dropna()
            
            if len(df_clean) < 3:
                return {"error": "Datos insuficientes", "test": "anova"}
            
            # Agrupar datos
            groups_data = [group_data['values'].values 
                          for name, group_data in df_clean.groupby('groups')
                          if len(group_data) > 0]
            
            if len(groups_data) < 2:
                return {"error": "Se necesitan al menos 2 grupos", "test": "anova"}
            
            # Realizar ANOVA
            f_stat, p_value = stats.f_oneway(*groups_data)
            
            # Estadísticas por grupo
            group_stats = df_clean.groupby('groups')['values'].agg([
                'count', 'mean', 'std'
            ]).to_dict()
            
            return {
                "f_statistic": float(f_stat),
                "p_value": float(p_value),
                "significant": p_value < self.alpha,
                "group_statistics": group_stats,
                "test": "anova"
            }
            
        except Exception as e:
            return {"error": str(e), "test": "anova"}
    
    def correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Matriz de correlación con tests de significancia"""
        
        try:
            # Solo columnas numéricas
            numeric_df = df.select_dtypes(include=[np.number])
            
            if numeric_df.empty:
                return {"error": "No hay columnas numéricas", "test": "correlation"}
            
            # Matriz de correlación de Pearson
            corr_matrix = numeric_df.corr()
            
            # Matriz de p-valores
            n = len(numeric_df)
            p_values = np.zeros((len(corr_matrix.columns), len(corr_matrix.columns)))
            
            for i, col1 in enumerate(corr_matrix.columns):
                for j, col2 in enumerate(corr_matrix.columns):
                    if i != j:
                        _, p_val = stats.pearsonr(
                            numeric_df[col1].dropna(), 
                            numeric_df[col2].dropna()
                        )
                        p_values[i, j] = p_val
            
            p_values_df = pd.DataFrame(
                p_values, 
                index=corr_matrix.index, 
                columns=corr_matrix.columns
            )
            
            return {
                "correlation_matrix": corr_matrix.to_dict(),
                "p_values": p_values_df.to_dict(),
                "significant_correlations": self._find_significant_correlations(
                    corr_matrix, p_values_df
                )
            }
            
        except Exception as e:
            return {"error": str(e), "test": "correlation"}
    
    def _find_significant_correlations(self, corr_matrix: pd.DataFrame, 
                                     p_values: pd.DataFrame) -> List[Dict[str, Any]]:
        """Encuentra correlaciones significativas"""
        
        significant = []
        
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:  # Evitar duplicados
                    corr_val = corr_matrix.iloc[i, j]
                    p_val = p_values.iloc[i, j]
                    
                    if p_val < self.alpha and not np.isnan(corr_val):
                        significant.append({
                            "variable1": col1,
                            "variable2": col2,
                            "correlation": float(corr_val),
                            "p_value": float(p_val),
                            "strength": self._interpret_correlation(abs(corr_val))
                        })
        
        return sorted(significant, key=lambda x: abs(x['correlation']), reverse=True)
    
    def _interpret_correlation(self, corr_abs: float) -> str:
        """Interpreta la fuerza de la correlación"""
        if corr_abs >= 0.7:
            return "Fuerte"
        elif corr_abs >= 0.5:
            return "Moderada"
        elif corr_abs >= 0.3:
            return "Débil"
        else:
            return "Muy débil"
    
    def t_test_independent(self, group1: pd.Series, group2: pd.Series) -> Dict[str, Any]:
        """Test t para muestras independientes"""
        
        try:
            # Limpiar datos
            g1_clean = pd.to_numeric(group1, errors='coerce').dropna()
            g2_clean = pd.to_numeric(group2, errors='coerce').dropna()
            
            if len(g1_clean) < 2 or len(g2_clean) < 2:
                return {"error": "Datos insuficientes", "test": "t_test"}
            
            # Test de normalidad (Shapiro-Wilk)
            _, p_norm1 = stats.shapiro(g1_clean[:5000])  # Máximo 5000 para Shapiro
            _, p_norm2 = stats.shapiro(g2_clean[:5000])
            
            # Test de homogeneidad de varianzas (Levene)
            _, p_levene = stats.levene(g1_clean, g2_clean)
            
            # Seleccionar test apropiado
            if p_levene > 0.05:  # Varianzas homogéneas
                t_stat, p_value = stats.ttest_ind(g1_clean, g2_clean, equal_var=True)
                test_type = "t-test (varianzas iguales)"
            else:  # Varianzas heterogéneas (Welch)
                t_stat, p_value = stats.ttest_ind(g1_clean, g2_clean, equal_var=False)
                test_type = "Welch t-test (varianzas desiguales)"
            
            # Tamaño del efecto (Cohen's d)
            pooled_std = np.sqrt(((len(g1_clean) - 1) * g1_clean.var() + 
                                 (len(g2_clean) - 1) * g2_clean.var()) / 
                                (len(g1_clean) + len(g2_clean) - 2))
            cohens_d = (g1_clean.mean() - g2_clean.mean()) / pooled_std
            
            return {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant": p_value < self.alpha,
                "test_type": test_type,
                "cohens_d": float(cohens_d),
                "effect_size": self._interpret_cohens_d(abs(cohens_d)),
                "group1_stats": {
                    "mean": float(g1_clean.mean()),
                    "std": float(g1_clean.std()),
                    "n": len(g1_clean)
                },
                "group2_stats": {
                    "mean": float(g2_clean.mean()),
                    "std": float(g2_clean.std()),
                    "n": len(g2_clean)
                },
                "normality_assumption": {
                    "group1_normal": p_norm1 > 0.05,
                    "group2_normal": p_norm2 > 0.05
                }
            }
            
        except Exception as e:
            return {"error": str(e), "test": "t_test"}
    
    def _interpret_cohens_d(self, d_abs: float) -> str:
        """Interpreta el tamaño del efecto Cohen's d"""
        if d_abs >= 0.8:
            return "Grande"
        elif d_abs >= 0.5:
            return "Mediano"
        elif d_abs >= 0.2:
            return "Pequeño"
        else:
            return "Muy pequeño"
    
    def proportions_test(self, success1: int, n1: int, success2: int, n2: int) -> Dict[str, Any]:
        """Test de diferencia de proporciones"""
        
        try:
            # Proporciones
            p1 = success1 / n1
            p2 = success2 / n2
            
            # Proporción combinada
            p_combined = (success1 + success2) / (n1 + n2)
            
            # Error estándar
            se = np.sqrt(p_combined * (1 - p_combined) * (1/n1 + 1/n2))
            
            # Estadístico z
            z_stat = (p1 - p2) / se
            
            # P-valor (test de dos colas)
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            
            # Intervalo de confianza para la diferencia
            se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
            z_critical = stats.norm.ppf((1 + self.confidence_level) / 2)
            diff = p1 - p2
            ci_lower = diff - z_critical * se_diff
            ci_upper = diff + z_critical * se_diff
            
            return {
                "z_statistic": float(z_stat),
                "p_value": float(p_value),
                "significant": p_value < self.alpha,
                "proportion1": float(p1),
                "proportion2": float(p2),
                "difference": float(diff),
                "confidence_interval": (float(ci_lower), float(ci_upper)),
                "sample_sizes": {"n1": n1, "n2": n2}
            }
            
        except Exception as e:
            return {"error": str(e), "test": "proportions"}
    
    def weighted_average(self, values: List[float], weights: List[float]) -> float:
        """Promedio ponderado"""
        
        if len(values) != len(weights):
            raise ValueError("Las listas deben tener la misma longitud")
        
        return float(np.average(values, weights=weights))
    
    def margin_of_error(self, sample_size: int, population_size: Optional[int] = None, 
                       confidence_level: float = 0.95) -> float:
        """Margen de error para una encuesta"""
        
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        if population_size is None:
            # Población infinita
            margin = z_score * np.sqrt(0.25 / sample_size)  # p=0.5 para máximo margen
        else:
            # Población finita
            fpc = np.sqrt((population_size - sample_size) / (population_size - 1))
            margin = z_score * np.sqrt(0.25 / sample_size) * fpc
        
        return float(margin)
    
    def sample_size_calculator(self, margin_of_error: float, confidence_level: float = 0.95,
                              population_size: Optional[int] = None) -> int:
        """Calcula tamaño de muestra necesario"""
        
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        if population_size is None:
            # Población infinita
            n = (z_score ** 2 * 0.25) / (margin_of_error ** 2)
        else:
            # Población finita
            numerator = population_size * (z_score ** 2) * 0.25
            denominator = (margin_of_error ** 2) * (population_size - 1) + (z_score ** 2) * 0.25
            n = numerator / denominator
        
        return int(np.ceil(n))

def main():
    """Función de prueba"""
    analyzer = StatisticalAnalyzer()
    
    # Datos de ejemplo
    data1 = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    data2 = pd.Series([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    
    print("Estadísticas descriptivas:")
    print(analyzer.descriptive_stats(data1))
    
    print("\nIntervalo de confianza:")
    print(analyzer.confidence_interval(data1))
    
    print("\nTest t independiente:")
    print(analyzer.t_test_independent(data1, data2))

if __name__ == "__main__":
    main()