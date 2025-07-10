"""
Agente Creador de Encuestas con Representatividad Demográfica
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import json

from buyer_synthetic.config.settings import settings
from buyer_synthetic.utils.logger import get_logger

logger = get_logger(__name__)

class SurveyCreatorAgent:
    """Agente para crear muestras representativas de encuestas"""
    
    def __init__(self, sample_size: int = None):
        self.sample_size = sample_size or settings.DEFAULT_SAMPLE_SIZE
        self.logger = logger
        
    def generate_representative_sample(self) -> pd.DataFrame:
        """Genera muestra representativa basada en demografía Peru 2024"""
        
        self.logger.info(f"Generando muestra representativa de {self.sample_size} personas")
        
        # Calcular cantidad por segmento
        segments = self._calculate_segments()
        
        # Generar perfiles
        profiles = []
        profile_id = 1
        
        for segment, count in segments.items():
            nse, region, age_range = segment.split("_")
            
            for _ in range(count):
                profile = self._generate_profile(profile_id, nse, region, age_range)
                profiles.append(profile)
                profile_id += 1
        
        # Crear DataFrame
        df = pd.DataFrame(profiles)
        
        # Shuffle para randomizar
        df = df.sample(frac=1).reset_index(drop=True)
        
        self.logger.info(f"Muestra generada: {len(df)} perfiles")
        self._log_sample_distribution(df)
        
        return df
    
    def _calculate_segments(self) -> Dict[str, int]:
        """Calcula distribución de segmentos"""
        segments = {}
        
        # Para muestras pequeñas, usar método simplificado
        if self.sample_size < 50:
            return self._calculate_simple_segments()
        
        for nse, nse_pct in settings.NSE_DISTRIBUTION.items():
            for region, region_pct in settings.REGION_DISTRIBUTION.items():
                for age_range, age_pct in settings.AGE_RANGES.items():
                    segment_key = f"{nse}_{region}_{age_range}"
                    segment_size = int(self.sample_size * nse_pct * region_pct * age_pct)
                    
                    if segment_size > 0:
                        segments[segment_key] = segment_size
        
        # Ajustar para llegar al tamaño exacto
        total = sum(segments.values())
        if total < self.sample_size and segments:
            # Agregar diferencia al segmento más grande
            largest_segment = max(segments, key=segments.get)
            segments[largest_segment] += (self.sample_size - total)
        
        return segments
    
    def _calculate_simple_segments(self) -> Dict[str, int]:
        """Método simplificado para muestras pequeñas"""
        segments = {}
        
        # Distribuir principalmente por NSE
        for nse, nse_pct in settings.NSE_DISTRIBUTION.items():
            count = max(1, int(self.sample_size * nse_pct))
            
            # Seleccionar región más común
            main_region = max(settings.REGION_DISTRIBUTION, key=settings.REGION_DISTRIBUTION.get)
            
            # Seleccionar rango de edad más común
            main_age = max(settings.AGE_RANGES, key=settings.AGE_RANGES.get)
            
            segment_key = f"{nse}_{main_region}_{main_age}"
            segments[segment_key] = count
        
        # Ajustar total
        total = sum(segments.values())
        if total != self.sample_size:
            largest_segment = max(segments, key=segments.get)
            segments[largest_segment] += (self.sample_size - total)
        
        return segments
    
    def _generate_profile(self, profile_id: int, nse: str, region: str, age_range: str) -> Dict[str, Any]:
        """Genera perfil individual"""
        
        # Edad específica dentro del rango
        age_min, age_max = self._parse_age_range(age_range)
        edad = np.random.randint(age_min, age_max + 1)
        
        # Nombre según género
        gender = np.random.choice(["M", "F"])
        nombre = self._generate_name(gender)
        
        # Ciudad específica según región
        ciudad = self._select_city(region)
        
        # Ocupación según NSE
        ocupacion = self._select_occupation(nse, edad)
        
        # Ingresos según NSE
        ingresos = self._select_income(nse)
        
        # Educación según NSE
        educacion = self._select_education(nse, edad)
        
        return {
            "id": profile_id,
            "nombre": nombre,
            "edad": edad,
            "genero": gender,
            "ciudad": ciudad,
            "region": region,
            "nse": nse,
            "ocupacion": ocupacion,
            "ingresos": ingresos,
            "educacion": educacion,
            "estado_civil": self._select_marital_status(edad),
            "hijos": self._select_children(edad, gender),
            "created_at": datetime.now().isoformat()
        }
    
    def _parse_age_range(self, age_range: str) -> tuple:
        """Parsear rango de edad"""
        if age_range == "65+":
            return 65, 80
        else:
            min_age, max_age = map(int, age_range.split("-"))
            return min_age, max_age
    
    def _generate_name(self, gender: str) -> str:
        """Generar nombre según género"""
        nombres_m = ["Carlos", "José", "Luis", "Miguel", "Roberto", "Fernando", "Jorge", "Manuel", "Pedro", "Ricardo"]
        nombres_f = ["María", "Ana", "Carmen", "Rosa", "Elena", "Patricia", "Sandra", "Lucía", "Teresa", "Mónica"]
        apellidos = ["García", "González", "López", "Martínez", "Rodríguez", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"]
        
        if gender == "M":
            nombre = np.random.choice(nombres_m)
        else:
            nombre = np.random.choice(nombres_f)
        
        apellido = np.random.choice(apellidos)
        return f"{nombre} {apellido}"
    
    def _select_city(self, region: str) -> str:
        """Seleccionar ciudad según región"""
        cities = {
            "Lima": ["Lima", "Callao"],
            "Costa": ["Trujillo", "Chiclayo", "Piura", "Ica", "Tacna"],
            "Sierra": ["Arequipa", "Cusco", "Huancayo", "Cajamarca", "Ayacucho"],
            "Selva": ["Iquitos", "Pucallpa", "Tarapoto", "Puerto Maldonado"]
        }
        return np.random.choice(cities[region])
    
    def _select_occupation(self, nse: str, edad: int) -> str:
        """Seleccionar ocupación según NSE y edad"""
        occupations = {
            "A": ["Ejecutivo", "Empresario", "Profesional Senior", "Director"],
            "B": ["Profesional", "Técnico Especializado", "Empleado Calificado", "Comerciante"],
            "C": ["Empleado", "Técnico", "Comerciante", "Obrero Calificado"],
            "D": ["Obrero", "Empleado Básico", "Comerciante Menor", "Trabajador Independiente"],
            "E": ["Trabajador Eventual", "Subempleado", "Desempleado", "Trabajo Doméstico"]
        }
        
        if edad < 25:
            return "Estudiante/Trabajador Joven"
        elif edad > 65:
            return "Jubilado"
        else:
            return np.random.choice(occupations[nse])
    
    def _select_income(self, nse: str) -> str:
        """Seleccionar ingresos según NSE"""
        income_ranges = {
            "A": "S/ 10,000+",
            "B": "S/ 4,000 - S/ 10,000",
            "C": "S/ 2,000 - S/ 4,000", 
            "D": "S/ 1,000 - S/ 2,000",
            "E": "Menos de S/ 1,000"
        }
        return income_ranges[nse]
    
    def _select_education(self, nse: str, edad: int) -> str:
        """Seleccionar educación según NSE y edad"""
        education_levels = {
            "A": ["Superior completa", "Postgrado"],
            "B": ["Superior completa", "Superior incompleta", "Técnica completa"],
            "C": ["Secundaria completa", "Técnica completa", "Superior incompleta"],
            "D": ["Secundaria completa", "Secundaria incompleta", "Técnica incompleta"],
            "E": ["Primaria completa", "Secundaria incompleta", "Sin educación formal"]
        }
        
        if edad < 25:
            return "Estudiando"
        else:
            return np.random.choice(education_levels[nse])
    
    def _select_marital_status(self, edad: int) -> str:
        """Seleccionar estado civil según edad"""
        if edad < 25:
            return np.random.choice(["Soltero", "Conviviente"], p=[0.8, 0.2])
        elif edad < 35:
            return np.random.choice(["Soltero", "Casado", "Conviviente"], p=[0.4, 0.4, 0.2])
        else:
            return np.random.choice(["Casado", "Soltero", "Divorciado", "Viudo"], p=[0.6, 0.2, 0.15, 0.05])
    
    def _select_children(self, edad: int, gender: str) -> int:
        """Seleccionar número de hijos"""
        if edad < 25:
            return np.random.choice([0, 1], p=[0.8, 0.2])
        elif edad < 35:
            return np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        else:
            return np.random.choice([0, 1, 2, 3, 4], p=[0.2, 0.3, 0.3, 0.15, 0.05])
    
    def _log_sample_distribution(self, df: pd.DataFrame):
        """Log distribución de la muestra"""
        self.logger.info("Distribución de la muestra:")
        
        # NSE
        nse_dist = df['nse'].value_counts(normalize=True).sort_index()
        for nse, pct in nse_dist.items():
            self.logger.info(f"  NSE {nse}: {pct:.1%}")
        
        # Región  
        region_dist = df['region'].value_counts(normalize=True)
        for region, pct in region_dist.items():
            self.logger.info(f"  {region}: {pct:.1%}")
    
    def save_sample(self, df: pd.DataFrame, filename: str = None) -> str:
        """Guardar muestra generada"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"muestra_representativa_{timestamp}.csv"
        
        filepath = settings.DATA_DIR / "input" / filename
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        self.logger.info(f"Muestra guardada en: {filepath}")
        return str(filepath)
    
    def create_survey_metadata(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Crear metadata de la encuesta"""
        return {
            "sample_size": len(df),
            "creation_date": datetime.now().isoformat(),
            "nse_distribution": df['nse'].value_counts().to_dict(),
            "region_distribution": df['region'].value_counts().to_dict(),
            "age_distribution": df.groupby('edad').size().to_dict(),
            "gender_distribution": df['genero'].value_counts().to_dict(),
            "questions": settings.ELECTORAL_QUESTIONS
        }

def main():
    """Función principal para testing"""
    creator = SurveyCreatorAgent(sample_size=300)
    sample_df = creator.generate_representative_sample()
    filepath = creator.save_sample(sample_df)
    metadata = creator.create_survey_metadata(sample_df)
    
    print(f"✅ Muestra creada: {filepath}")
    print(f"📊 Metadata: {json.dumps(metadata, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()