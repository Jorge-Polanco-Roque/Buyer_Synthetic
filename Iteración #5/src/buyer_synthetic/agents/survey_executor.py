"""
Agente Ejecutor de Encuestas - Aplica preguntas electorales a cada perfil
"""

import pandas as pd
import json
import openai
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import time

from buyer_synthetic.config.settings import settings
from buyer_synthetic.utils.logger import get_logger

logger = get_logger(__name__)

class SurveyExecutorAgent:
    """Agente que ejecuta encuestas a perfiles demográficos"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logger
        self.questions = settings.ELECTORAL_QUESTIONS
        
    def execute_survey(self, sample_df: pd.DataFrame, batch_size: int = 10) -> pd.DataFrame:
        """Ejecuta encuesta completa a todos los perfiles"""
        
        self.logger.info(f"Iniciando encuesta a {len(sample_df)} perfiles")
        
        results = []
        total_profiles = len(sample_df)
        
        for i in range(0, total_profiles, batch_size):
            batch = sample_df.iloc[i:i+batch_size]
            self.logger.info(f"Procesando lote {i//batch_size + 1} ({len(batch)} perfiles)")
            
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Rate limiting para OpenAI API
            time.sleep(1)
        
        # Crear DataFrame con resultados
        results_df = pd.DataFrame(results)
        
        self.logger.info(f"Encuesta completada: {len(results_df)} respuestas generadas")
        return results_df
    
    def _process_batch(self, batch_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Procesa un lote de perfiles"""
        batch_results = []
        
        for _, profile in batch_df.iterrows():
            try:
                profile_responses = self._survey_individual(profile.to_dict())
                batch_results.append(profile_responses)
                
            except Exception as e:
                self.logger.error(f"Error procesando perfil {profile['id']}: {str(e)}")
                # Crear respuesta de error
                error_response = self._create_error_response(profile.to_dict())
                batch_results.append(error_response)
        
        return batch_results
    
    def _survey_individual(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Encuesta individual a un perfil específico"""
        
        # Contexto cultural Peru 2024
        cultural_context = self._build_cultural_context(profile)
        
        # Generar todas las respuestas en una sola llamada para coherencia
        prompt = self._build_comprehensive_prompt(profile, cultural_context)
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE
        )
        
        # Parsear respuesta
        response_text = response.choices[0].message.content.strip()
        
        try:
            responses_json = json.loads(response_text)
            
            # Validar y procesar respuestas
            processed_responses = self._process_responses(profile, responses_json)
            return processed_responses
            
        except json.JSONDecodeError:
            self.logger.warning(f"Respuesta no JSON para perfil {profile['id']}, reintentando...")
            return self._retry_with_simple_format(profile)
    
    def _build_cultural_context(self, profile: Dict[str, Any]) -> str:
        """Construye contexto cultural específico para el perfil"""
        
        nse = profile['nse']
        region = profile['region']
        edad = profile['edad']
        
        context = f"""
        CONTEXTO POLÍTICO PERÚ 2024:
        - Gobierno actual: Dina Boluarte (crisis de gobernabilidad)
        - Próximas elecciones: 2026
        - Temas candentes: Corrupción, economía, seguridad
        - Desconfianza institucional generalizada
        
        CONTEXTO DEMOGRÁFICO ESPECÍFICO:
        - NSE {nse}: {self._get_nse_context(nse)}
        - Región {region}: {self._get_regional_context(region)}
        - Generación: {self._get_generational_context(edad)}
        """
        
        return context
    
    def _get_nse_context(self, nse: str) -> str:
        """Contexto específico por NSE"""
        contexts = {
            "A": "Preocupaciones por inversiones, estabilidad política, educación de calidad",
            "B": "Aspiraciones de movilidad social, estabilidad laboral, acceso a servicios",
            "C": "Preocupaciones por ingresos, seguridad, servicios básicos, empleo",
            "D": "Necesidades básicas, trabajo estable, programas sociales, supervivencia",
            "E": "Extrema vulnerabilidad, dependencia de programas sociales, subsistencia"
        }
        return contexts.get(nse, "Contexto general")
    
    def _get_regional_context(self, region: str) -> str:
        """Contexto específico por región"""
        contexts = {
            "Lima": "Perspectiva centralista, mayor acceso a información, problemática urbana",
            "Costa": "Economía pesquera/agrícola, conexión con Lima, desarrollo regional",
            "Sierra": "Tradición andina, actividad minera, descentralización, identidad cultural",
            "Selva": "Recursos naturales, conectividad, desarrollo sostenible, amazonía"
        }
        return contexts.get(region, "Contexto general")
    
    def _get_generational_context(self, edad: int) -> str:
        """Contexto generacional"""
        if edad < 25:
            return "Generación digital, redes sociales, nuevas perspectivas políticas"
        elif edad < 40:
            return "Millennials, estabilidad laboral, familia joven, optimismo moderado"
        elif edad < 55:
            return "Generación X, experiencia laboral, familia establecida, pragmatismo"
        else:
            return "Generación tradicional, experiencia política, estabilidad, conservadurismo"
    
    def _build_comprehensive_prompt(self, profile: Dict[str, Any], context: str) -> str:
        """Construye prompt comprehensivo para todas las preguntas"""
        
        prompt = f"""
        {context}
        
        Eres {profile['nombre']}, una persona de {profile['edad']} años que vive en {profile['ciudad']}, {profile['region']}.
        Tu perfil demográfico:
        - NSE: {profile['nse']}
        - Ocupación: {profile['ocupacion']}
        - Educación: {profile['educacion']}
        - Estado civil: {profile['estado_civil']}
        - Ingresos: {profile['ingresos']}
        
        Responde TODAS las siguientes preguntas como si fueras realmente esta persona, considerando:
        - Tu situación socioeconómica y perspectivas
        - El contexto político actual de Peru 2024
        - Tu edad y generación
        - Tu región y sus características
        
        PREGUNTAS:
        """
        
        for i, question in enumerate(self.questions, 1):
            prompt += f"\n{i}. {question['pregunta']}"
            if question['tipo'] == 'multiple':
                prompt += f"\n   Opciones: {', '.join(question['opciones'])}"
            elif question['tipo'] == 'escala':
                prompt += f"\n   Escala: {question['escala']}"
        
        prompt += f"""
        
        RESPONDE EN FORMATO JSON EXACTO:
        {{
            "respuestas": {{
                "{self.questions[0]['id']}": {{
                    "respuesta": "tu respuesta aquí",
                    "confianza": 0.8,
                    "razonamiento": "por qué respondiste así"
                }},
                [... para cada pregunta ...]
            }},
            "coherencia_general": 0.9,
            "comentarios_adicionales": "observaciones generales sobre tus respuestas"
        }}
        
        IMPORTANTE: 
        - Responde con tu personalidad y perspectiva específica
        - Sé coherente entre todas las respuestas
        - Incluye dudas y matices naturales
        - Usa lenguaje apropiado para tu NSE y educación
        """
        
        return prompt
    
    def _process_responses(self, profile: Dict[str, Any], responses_json: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida las respuestas JSON"""
        
        # Datos base del perfil
        result = {
            "id": profile["id"],
            "nombre": profile["nombre"],
            "edad": profile["edad"],
            "genero": profile["genero"],
            "ciudad": profile["ciudad"],
            "region": profile["region"],
            "nse": profile["nse"],
            "ocupacion": profile["ocupacion"],
            "ingresos": profile["ingresos"],
            "educacion": profile["educacion"],
            "survey_timestamp": datetime.now().isoformat()
        }
        
        # Agregar respuestas de cada pregunta
        respuestas = responses_json.get("respuestas", {})
        
        for question in self.questions:
            q_id = question["id"]
            if q_id in respuestas:
                response_data = respuestas[q_id]
                result[f"{q_id}_respuesta"] = response_data.get("respuesta", "")
                result[f"{q_id}_confianza"] = response_data.get("confianza", 0.5)
                result[f"{q_id}_razonamiento"] = response_data.get("razonamiento", "")
            else:
                # Respuesta por defecto si falta
                result[f"{q_id}_respuesta"] = "No respuesta"
                result[f"{q_id}_confianza"] = 0.1
                result[f"{q_id}_razonamiento"] = "Respuesta no generada"
        
        # Métricas adicionales
        result["coherencia_general"] = responses_json.get("coherencia_general", 0.5)
        result["comentarios_adicionales"] = responses_json.get("comentarios_adicionales", "")
        
        return result
    
    def _retry_with_simple_format(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Reintentar con formato más simple si falla el JSON"""
        
        self.logger.info(f"Reintentando con formato simple para perfil {profile['id']}")
        
        # Generar respuestas una por una
        result = {
            "id": profile["id"],
            "nombre": profile["nombre"],
            "edad": profile["edad"],
            "genero": profile["genero"],
            "ciudad": profile["ciudad"],
            "region": profile["region"],
            "nse": profile["nse"],
            "ocupacion": profile["ocupacion"],
            "survey_timestamp": datetime.now().isoformat()
        }
        
        for question in self.questions[:3]:  # Solo primeras 3 para reintento
            try:
                response = self._ask_single_question(profile, question)
                q_id = question["id"]
                result[f"{q_id}_respuesta"] = response.get("respuesta", "Error")
                result[f"{q_id}_confianza"] = response.get("confianza", 0.3)
                result[f"{q_id}_razonamiento"] = response.get("razonamiento", "Reintento")
                
            except Exception as e:
                self.logger.error(f"Error en pregunta {question['id']}: {str(e)}")
                continue
        
        return result
    
    def _ask_single_question(self, profile: Dict[str, Any], question: Dict[str, Any]) -> Dict[str, Any]:
        """Hace una pregunta individual simple"""
        
        prompt = f"""
        Eres {profile['nombre']}, {profile['edad']} años, NSE {profile['nse']}, vives en {profile['ciudad']}.
        
        Pregunta: {question['pregunta']}
        {f"Opciones: {', '.join(question['opciones'])}" if question['tipo'] == 'multiple' else ''}
        
        Responde en JSON:
        {{
            "respuesta": "tu respuesta",
            "confianza": 0.8,
            "razonamiento": "por qué"
        }}
        """
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _create_error_response(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Crear respuesta de error para perfil fallido"""
        
        result = {
            "id": profile["id"],
            "nombre": profile["nombre"],
            "edad": profile["edad"],
            "ciudad": profile["ciudad"],
            "nse": profile["nse"],
            "error": "Failed to generate responses",
            "survey_timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def save_results(self, results_df: pd.DataFrame, filename: str = None) -> str:
        """Guardar resultados de encuesta"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"encuesta_electoral_{timestamp}.csv"
        
        filepath = settings.DATA_DIR / "output" / filename
        results_df.to_csv(filepath, index=False, encoding='utf-8')
        
        self.logger.info(f"Resultados guardados en: {filepath}")
        return str(filepath)

def main():
    """Función principal para testing"""
    # Cargar muestra (asumiendo que existe)
    sample_path = settings.DATA_DIR / "input" / "muestra_representativa.csv"
    
    if not sample_path.exists():
        print("❌ No se encontró muestra. Ejecuta primero survey_creator.py")
        return
    
    sample_df = pd.read_csv(sample_path)
    
    executor = SurveyExecutorAgent()
    results_df = executor.execute_survey(sample_df.head(5))  # Solo 5 para testing
    filepath = executor.save_results(results_df)
    
    print(f"✅ Encuesta ejecutada: {filepath}")

if __name__ == "__main__":
    main()