"""
Dashboard principal de Buyer_Synthetic
Interfaz de usuario paso a paso para el flujo completo
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import json
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.core import get_logger
from src.agents.survey_creator import SurveyCreatorAgent
from src.agents.survey_executor import SurveyExecutorAgent
from src.agents.results_visualizer import ResultsVisualizerAgent

logger = get_logger(__name__)

class BuyerSyntheticDashboard:
    """Dashboard principal del sistema"""
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configuración de la página Streamlit"""
        st.set_page_config(
            page_title="Buyer Synthetic™ - Encuestas con IA",
            page_icon="🗳️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Inicializar estado de la sesión"""
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        
        if 'sample_df' not in st.session_state:
            st.session_state.sample_df = None
        
        if 'results_df' not in st.session_state:
            st.session_state.results_df = None
        
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        
        if 'uploaded_sample' not in st.session_state:
            st.session_state.uploaded_sample = None
        
        if 'uploaded_questions' not in st.session_state:
            st.session_state.uploaded_questions = None
        
        if 'custom_questions' not in st.session_state:
            st.session_state.custom_questions = []
    
    def render_header(self):
        """Renderizar cabecera"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1>🗳️ Buyer Synthetic™</h1>
                <h3>Encuestas Electorales con Inteligencia Artificial</h3>
                <p><em>Investigación sin campo, con IA • Peru 2024-2026</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_progress_bar(self):
        """Renderizar barra de progreso"""
        steps = [
            "0️⃣ Cargar Datos",
            "1️⃣ Crear Muestra",
            "2️⃣ Ejecutar Encuesta", 
            "3️⃣ Analizar Resultados"
        ]
        
        cols = st.columns(len(steps))
        
        for i, (col, step) in enumerate(zip(cols, steps)):
            with col:
                if i + 1 < st.session_state.current_step:
                    st.success(f"✅ {step}")
                elif i + 1 == st.session_state.current_step:
                    st.info(f"⚠️ {step}")
                else:
                    st.write(f"⭕ {step}")
        
        progress_pct = max(0.0, min(1.0, st.session_state.current_step / (len(steps) - 1)))
        st.progress(progress_pct)
    
    def render_sidebar(self):
        """Renderizar sidebar con configuración"""
        st.sidebar.header("⚙️ Configuración")
        
        # Configuración de muestra
        st.sidebar.subheader("📊 Muestra")
        sample_size = st.sidebar.slider(
            "Tamaño de muestra",
            min_value=50,
            max_value=1000,
            value=settings.DEFAULT_SAMPLE_SIZE,
            step=50
        )
        
        # Configuración de modelo
        st.sidebar.subheader("🤖 Modelo IA")
        model = st.sidebar.selectbox(
            "Modelo OpenAI",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
        
        temperature = st.sidebar.slider(
            "Creatividad (Temperature)",
            min_value=0.0,
            max_value=1.0,
            value=settings.TEMPERATURE,
            step=0.1
        )
        
        # Info del sistema
        st.sidebar.subheader("ℹ️ Sistema")
        st.sidebar.info(f"""
        **Estado**: {'🟢 Operativo' if settings.OPENAI_API_KEY else '🔴 Sin API Key'}
        
        **Configuración**:
        - Muestra: {sample_size} personas
        - Modelo: {model}
        - Temp: {temperature}
        
        **Preguntas**: {len(settings.ELECTORAL_QUESTIONS)}
        """)
        
        return {
            "sample_size": sample_size,
            "model": model,
            "temperature": temperature
        }
    
    def render_step_0_upload(self, config):
        """Paso 0: Cargar archivos CSV y TXT"""
        st.header("0️⃣ Cargar Datos Personalizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Cargar Muestra CSV")
            st.write("Sube un archivo CSV con perfiles demográficos para usar como base.")
            
            st.write("**Formato esperado del CSV:**")
            st.code("""
id,nombre,edad,genero,ciudad,region,nse,ocupacion,educacion,estado_civil,ingresos
1,Juan Pérez,35,M,Lima,Lima,C,Ingeniero,Universitaria,Casado,3500
2,María García,28,F,Arequipa,Sierra,B,Doctora,Universitaria,Soltera,4500
...
            """)
            
            uploaded_csv = st.file_uploader(
                "Selecciona archivo CSV",
                type=['csv'],
                key="csv_uploader"
            )
            
            if uploaded_csv is not None:
                try:
                    # Leer CSV
                    df = pd.read_csv(uploaded_csv)
                    
                    # Validar columnas requeridas
                    required_cols = ['id', 'nombre', 'edad', 'genero', 'region', 'nse']
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Faltan columnas requeridas: {', '.join(missing_cols)}")
                        st.write("**Columnas encontradas:**", list(df.columns))
                    else:
                        # Guardar en session state
                        st.session_state.uploaded_sample = df
                        st.success(f"✅ CSV cargado: {len(df)} perfiles")
                        
                        # Mostrar vista previa
                        st.write("**Vista previa:**")
                        st.dataframe(df.head(10))
                        
                        # Estadísticas básicas
                        col_stats1, col_stats2, col_stats3 = st.columns(3)
                        with col_stats1:
                            st.metric("Total Perfiles", len(df))
                        with col_stats2:
                            st.metric("Edad Promedio", f"{df['edad'].mean():.1f}")
                        with col_stats3:
                            st.metric("% Mujeres", f"{(df['genero'] == 'F').mean():.1%}")
                        
                except Exception as e:
                    st.error(f"❌ Error al leer CSV: {str(e)}")
        
        with col2:
            st.subheader("❓ Cargar Preguntas TXT")
            st.write("Sube un archivo TXT con preguntas personalizadas para la encuesta.")
            
            st.write("**Formato esperado del TXT:**")
            st.code("""
1. ¿Cuál es tu opinión sobre el gobierno actual?
   Tipo: escala
   Escala: 1-10

2. ¿Por quién votarías en las próximas elecciones?
   Tipo: multiple
   Opciones: Candidato A, Candidato B, Candidato C, Voto en blanco

3. ¿Cuál es el principal problema del país?
   Tipo: multiple
   Opciones: Economía, Seguridad, Corrupción, Educación
            """)
            
            uploaded_txt = st.file_uploader(
                "Selecciona archivo TXT",
                type=['txt'],
                key="txt_uploader"
            )
            
            if uploaded_txt is not None:
                try:
                    # Leer TXT
                    content = uploaded_txt.read().decode('utf-8')
                    
                    # Parsear preguntas
                    questions = self._parse_questions_from_txt(content)
                    
                    if questions:
                        st.session_state.custom_questions = questions
                        st.success(f"✅ TXT cargado: {len(questions)} preguntas")
                        
                        # Mostrar vista previa
                        st.write("**Preguntas detectadas:**")
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"Pregunta {i}: {q['pregunta'][:50]}..."):
                                st.write(f"**Pregunta:** {q['pregunta']}")
                                st.write(f"**Tipo:** {q['tipo']}")
                                if q['tipo'] == 'multiple':
                                    st.write(f"**Opciones:** {', '.join(q['opciones'])}")
                                elif q['tipo'] == 'escala':
                                    st.write(f"**Escala:** {q['escala']}")
                    else:
                        st.warning("⚠️ No se pudieron parsear preguntas del archivo")
                        
                except Exception as e:
                    st.error(f"❌ Error al leer TXT: {str(e)}")
        
        # Opciones de continuar
        st.markdown("---")
        st.subheader("🚀 Continuar con el Proceso")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Usar Datos Predeterminados", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        
        with col2:
            if st.session_state.uploaded_sample is not None:
                if st.button("📋 Usar CSV Cargado", type="primary", use_container_width=True):
                    st.session_state.sample_df = st.session_state.uploaded_sample
                    st.session_state.current_step = 2  # Saltar creación, ir directo a encuesta
                    st.rerun()
        
        with col3:
            if st.session_state.uploaded_sample is not None or st.session_state.custom_questions:
                if st.button("🔧 Configurar y Continuar", use_container_width=True):
                    st.session_state.current_step = 1
                    st.rerun()
    
    def _parse_questions_from_txt(self, content):
        """Parsear preguntas desde contenido TXT"""
        questions = []
        lines = content.strip().split('\n')
        
        current_question = {}
        question_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar nueva pregunta (empieza con número)
            if line.startswith(f"{question_counter}."):
                if current_question:
                    # Finalizar pregunta anterior
                    questions.append(current_question)
                
                # Iniciar nueva pregunta
                current_question = {
                    "id": f"custom_q{question_counter}",
                    "pregunta": line[len(f"{question_counter}."):].strip(),
                    "tipo": "abierta",  # Default
                    "opciones": [],
                    "escala": ""
                }
                question_counter += 1
                
            elif line.lower().startswith("tipo:"):
                tipo = line.split(":", 1)[1].strip().lower()
                if tipo in ["multiple", "escala", "abierta"]:
                    current_question["tipo"] = tipo
                    
            elif line.lower().startswith("opciones:"):
                opciones = line.split(":", 1)[1].strip()
                current_question["opciones"] = [opt.strip() for opt in opciones.split(",")]
                
            elif line.lower().startswith("escala:"):
                escala = line.split(":", 1)[1].strip()
                current_question["escala"] = escala
        
        # Agregar última pregunta
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def render_step_1_creator(self, config):
        """Paso 1: Creador de encuestas"""
        st.header("1️⃣ Creador de Muestra Representativa")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Configuración Demográfica")
            
            # Mostrar distribución objetivo
            st.write("**Distribución objetivo basada en Peru 2024:**")
            
            nse_df = pd.DataFrame([
                {"NSE": k, "Porcentaje": f"{v:.1%}", "Descripción": self._get_nse_description(k)}
                for k, v in settings.NSE_DISTRIBUTION.items()
            ])
            
            st.dataframe(nse_df, use_container_width=True)
            
            region_df = pd.DataFrame([
                {"Región": k, "Porcentaje": f"{v:.1%}"}
                for k, v in settings.REGION_DISTRIBUTION.items()
            ])
            
            col_nse, col_region = st.columns(2)
            with col_nse:
                st.write("**Por NSE:**")
                fig_nse = px.pie(
                    values=list(settings.NSE_DISTRIBUTION.values()),
                    names=list(settings.NSE_DISTRIBUTION.keys()),
                    title="Distribución NSE"
                )
                st.plotly_chart(fig_nse, use_container_width=True)
            
            with col_region:
                st.write("**Por Región:**")
                fig_region = px.pie(
                    values=list(settings.REGION_DISTRIBUTION.values()),
                    names=list(settings.REGION_DISTRIBUTION.keys()),
                    title="Distribución Regional"
                )
                st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            st.subheader("🚀 Generar Muestra")
            
            if st.button("🎯 Crear Muestra Representativa", type="primary", use_container_width=True):
                with st.spinner(f"Generando {config['sample_size']} perfiles..."):
                    try:
                        creator = SurveyCreatorAgent(sample_size=config['sample_size'])
                        sample_df = creator.generate_representative_sample()
                        
                        # Guardar en sesión
                        st.session_state.sample_df = sample_df
                        
                        # Guardar archivo
                        filepath = creator.save_sample(sample_df)
                        
                        st.success(f"✅ Muestra creada: {len(sample_df)} perfiles")
                        st.session_state.current_step = 2
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        # Mostrar muestra si existe
        if st.session_state.sample_df is not None:
            st.subheader("👥 Muestra Generada")
            
            df = st.session_state.sample_df
            
            # Estadísticas de la muestra
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Perfiles", len(df))
            with col2:
                st.metric("Edad Promedio", f"{df['edad'].mean():.1f} años")
            with col3:
                st.metric("% Mujeres", f"{(df['genero'] == 'F').mean():.1%}")
            with col4:
                st.metric("NSE Dominante", df['nse'].mode()[0])
            
            # Mostrar muestra
            st.dataframe(df.head(10), use_container_width=True)
            
            if st.button("➡️ Continuar a Encuesta"):
                st.session_state.current_step = 2
                st.rerun()
    
    def render_step_2_executor(self, config):
        """Paso 2: Ejecutor de encuestas"""
        st.header("2️⃣ Ejecutor de Encuesta Electoral")
        
        if st.session_state.sample_df is None:
            st.warning("⚠️ Primero debes crear una muestra representativa")
            if st.button("⬅️ Volver al Paso 1"):
                st.session_state.current_step = 1
                st.rerun()
            return
        
        df = st.session_state.sample_df
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("❓ Preguntas de la Encuesta")
            
            # Usar preguntas personalizadas si están disponibles
            questions_to_use = st.session_state.custom_questions if st.session_state.custom_questions else settings.ELECTORAL_QUESTIONS
            
            if st.session_state.custom_questions:
                st.info(f"📋 Usando {len(questions_to_use)} preguntas personalizadas cargadas")
            else:
                st.info(f"📋 Usando {len(questions_to_use)} preguntas predeterminadas")
            
            # Mostrar preguntas
            for i, q in enumerate(questions_to_use, 1):
                with st.expander(f"Pregunta {i}: {q['pregunta'][:50]}..."):
                    st.write(f"**Pregunta completa**: {q['pregunta']}")
                    st.write(f"**Tipo**: {q['tipo']}")
                    if q['tipo'] == 'multiple':
                        st.write(f"**Opciones**: {', '.join(q['opciones'])}")
                    elif q['tipo'] == 'escala':
                        st.write(f"**Escala**: {q['escala']}")
        
        with col2:
            st.subheader("🎯 Ejecutar Encuesta")
            
            questions_to_use = st.session_state.custom_questions if st.session_state.custom_questions else settings.ELECTORAL_QUESTIONS
            
            st.info(f"""
            **Muestra**: {len(df)} perfiles
            **Preguntas**: {len(questions_to_use)}
            **Estimado**: ~{len(df) * 2} minutos
            """)
            
            # Configuración de ejecución
            batch_size = st.selectbox("Tamaño de lote", [5, 10, 20], index=1)
            
            if st.button("🚀 Ejecutar Encuesta Completa", type="primary", use_container_width=True):
                self._execute_survey_with_progress(df, batch_size, config, questions_to_use)
        
        # Mostrar resultados si existen
        if st.session_state.results_df is not None:
            st.subheader("📊 Resultados Preliminares")
            
            results_df = st.session_state.results_df
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Respuestas", len(results_df))
            with col2:
                completion_rate = self._calculate_completion_rate(results_df)
                st.metric("Completitud", f"{completion_rate:.1%}")
            with col3:
                avg_confidence = self._calculate_avg_confidence(results_df)
                st.metric("Confianza Prom.", f"{avg_confidence:.2f}")
            with col4:
                error_count = len(results_df[results_df['error'].notna()]) if 'error' in results_df.columns else 0
                st.metric("Errores", error_count)
            
            # Vista previa
            st.dataframe(results_df.head(), use_container_width=True)
            
            if st.button("➡️ Continuar a Análisis"):
                st.session_state.current_step = 3
                st.rerun()
    
    def render_step_3_visualizer(self, config):
        """Paso 3: Visualizador de resultados"""
        st.header("3️⃣ Análisis y Visualización de Resultados")
        
        if st.session_state.results_df is None:
            st.warning("⚠️ Primero debes ejecutar la encuesta")
            if st.button("⬅️ Volver al Paso 2"):
                st.session_state.current_step = 2
                st.rerun()
            return
        
        results_df = st.session_state.results_df
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Análisis Disponibles")
            
            analysis_options = st.multiselect(
                "Selecciona análisis a realizar:",
                [
                    "Distribución demográfica",
                    "Intención de voto", 
                    "Principales problemas",
                    "Confianza institucional",
                    "Cross-tabulations por NSE",
                    "Tests estadísticos"
                ],
                default=["Distribución demográfica", "Intención de voto"]
            )
        
        with col2:
            st.subheader("🎯 Generar Análisis")
            
            if st.button("📊 Analizar Resultados", type="primary", use_container_width=True):
                self._analyze_results_with_progress(results_df, analysis_options)
        
        # Mostrar análisis si existe
        if st.session_state.analysis_results is not None:
            self._render_analysis_results()
    
    def _execute_survey_with_progress(self, df, batch_size, config, questions):
        """Ejecutar encuesta con barra de progreso"""
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Configurar executor
            executor = SurveyExecutorAgent()
            
            # Simular procesamiento por lotes
            total_batches = len(df) // batch_size + (1 if len(df) % batch_size else 0)
            
            results = []
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min((batch_num + 1) * batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                status_text.text(f"Procesando lote {batch_num + 1}/{total_batches} ({len(batch_df)} perfiles)")
                
                # Procesar lote (simplificado para demo)
                batch_results = self._process_batch_demo(batch_df, questions)
                results.extend(batch_results)
                
                # Actualizar progreso
                progress = (batch_num + 1) / total_batches
                progress_bar.progress(progress)
                
                # Simular tiempo de procesamiento
                time.sleep(1)
            
            # Crear DataFrame de resultados
            results_df = pd.DataFrame(results)
            
            # Guardar en sesión
            st.session_state.results_df = results_df
            
            # Limpiar elementos de progreso
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ Encuesta completada: {len(results_df)} respuestas generadas")
            
        except Exception as e:
            st.error(f"❌ Error ejecutando encuesta: {str(e)}")
    
    def _process_batch_demo(self, batch_df, questions):
        """Procesar lote - versión demo simplificada"""
        results = []
        
        for _, profile in batch_df.iterrows():
            # Simular respuestas (para demo rápida)
            result = {
                "id": profile["id"],
                "nombre": profile["nombre"],
                "edad": profile["edad"],
                "genero": profile["genero"],  # Agregar campo genero
                "ciudad": profile.get("ciudad", ""),  # Agregar campo ciudad
                "nse": profile["nse"],
                "region": profile["region"],
                "ocupacion": profile.get("ocupacion", ""),  # Campos opcionales
                "educacion": profile.get("educacion", ""),
                "estado_civil": profile.get("estado_civil", ""),
                "ingresos": profile.get("ingresos", ""),
                "survey_timestamp": datetime.now().isoformat()
            }
            
            # Generar respuestas para cada pregunta
            for question in questions:
                q_id = question["id"]
                
                if question["tipo"] == "multiple":
                    # Simular respuesta multiple choice
                    options = question.get("opciones", ["Opción A", "Opción B", "Opción C"])
                    response = options[hash(profile["nombre"] + q_id) % len(options)]
                    result[f"{q_id}_respuesta"] = response
                    
                elif question["tipo"] == "escala":
                    # Simular respuesta escala
                    scale_parts = question.get("escala", "1-10").split("-")
                    min_val = int(scale_parts[0]) if scale_parts[0].isdigit() else 1
                    max_val = int(scale_parts[1]) if len(scale_parts) > 1 and scale_parts[1].isdigit() else 10
                    response = min_val + (hash(profile["edad"] + q_id) % (max_val - min_val + 1))
                    result[f"{q_id}_respuesta"] = response
                    
                else:  # abierta
                    # Simular respuesta abierta
                    responses = ["Muy bueno", "Bueno", "Regular", "Malo", "Muy malo"]
                    response = responses[hash(profile["nse"] + q_id) % len(responses)]
                    result[f"{q_id}_respuesta"] = response
                
                # Agregar confianza simulada
                result[f"{q_id}_confianza"] = 0.6 + (hash(profile["nombre"] + q_id) % 40) / 100
            
            results.append(result)
        
        return results
    
    def _simulate_vote_intention(self, profile):
        """Simular intención de voto basada en perfil"""
        candidates = ["Candidato A", "Candidato B", "Candidato C", "Voto en blanco", "No votaría"]
        
        # Sesgo basado en NSE
        if profile["nse"] in ["A", "B"]:
            weights = [0.3, 0.25, 0.2, 0.15, 0.1]
        else:
            weights = [0.2, 0.3, 0.25, 0.15, 0.1]
        
        return candidates[hash(profile["nombre"]) % len(candidates)]
    
    def _simulate_main_problem(self, profile):
        """Simular problema principal"""
        problems = ["Corrupción", "Economía", "Seguridad ciudadana", "Desempleo", "Salud", "Educación"]
        return problems[hash(profile["ciudad"]) % len(problems)]
    
    def _analyze_results_with_progress(self, results_df, analysis_options):
        """Analizar resultados con progreso"""
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            visualizer = ResultsVisualizerAgent()
            
            status_text.text("Iniciando análisis estadístico...")
            progress_bar.progress(0.2)
            
            # Analizar resultados
            analysis_results = visualizer.analyze_and_visualize(results_df)
            
            progress_bar.progress(0.8)
            status_text.text("Generando visualizaciones...")
            
            # Guardar en sesión
            st.session_state.analysis_results = analysis_results
            
            progress_bar.progress(1.0)
            status_text.text("Análisis completado")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Análisis completado exitosamente")
            
        except Exception as e:
            st.error(f"❌ Error en análisis: {str(e)}")
    
    def _render_analysis_results(self):
        """Renderizar resultados de análisis"""
        
        analysis = st.session_state.analysis_results
        
        # Insights principales
        st.subheader("🔍 Insights Principales")
        
        for insight in analysis.get("insights", []):
            st.info(f"💡 {insight}")
        
        # Tabs para diferentes análisis
        tabs = st.tabs(["📊 Resumen", "🗳️ Electoral", "👥 Demográfico", "📈 Estadístico"])
        
        with tabs[0]:
            self._render_summary_tab(analysis)
        
        with tabs[1]:
            self._render_electoral_tab(analysis)
        
        with tabs[2]:
            self._render_demographic_tab(analysis)
        
        with tabs[3]:
            self._render_statistical_tab(analysis)
    
    def _render_summary_tab(self, analysis):
        """Tab de resumen"""
        summary = analysis.get("summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Respuestas", summary.get("total_responses", 0))
        
        with col2:
            completion = summary.get("data_quality", {}).get("completion_rate", 0)
            st.metric("Completitud", f"{completion:.1%}")
        
        with col3:
            confidence = summary.get("data_quality", {}).get("average_confidence", 0)
            st.metric("Confianza Promedio", f"{confidence:.2f}")
        
        with col4:
            age_mean = summary.get("sample_composition", {}).get("age_stats", {}).get("mean", 0)
            st.metric("Edad Promedio", f"{age_mean:.1f} años")
    
    def _render_electoral_tab(self, analysis):
        """Tab electoral"""
        electoral = analysis.get("electoral_analysis", {})
        
        # Intención de voto
        if "intencion_voto" in electoral:
            st.subheader("🗳️ Intención de Voto")
            
            voto_data = electoral["intencion_voto"].get("total_distribution", {})
            if voto_data:
                fig = px.bar(
                    x=list(voto_data.keys()),
                    y=list(voto_data.values()),
                    title="Intención de Voto - Total"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Principales problemas
        if "principales_problemas" in electoral:
            st.subheader("⚠️ Principales Problemas")
            
            problems_data = electoral["principales_problemas"].get("ranking", {})
            if problems_data:
                fig = px.bar(
                    x=list(problems_data.values()),
                    y=list(problems_data.keys()),
                    orientation='h',
                    title="Principales Problemas del País"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_demographic_tab(self, analysis):
        """Tab demográfico"""
        demographic = analysis.get("demographic_analysis", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución NSE
            nse_data = demographic.get("by_nse", {}).get("distribution", {})
            if nse_data:
                fig = px.pie(
                    values=list(nse_data.values()),
                    names=list(nse_data.keys()),
                    title="Distribución por NSE"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribución regional
            region_data = demographic.get("by_region", {}).get("distribution", {})
            if region_data:
                fig = px.pie(
                    values=list(region_data.values()),
                    names=list(region_data.keys()),
                    title="Distribución por Región"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_statistical_tab(self, analysis):
        """Tab estadístico"""
        stats = analysis.get("statistical_tests", {})
        
        if stats:
            st.subheader("📐 Tests Estadísticos")
            
            for test_name, test_result in stats.items():
                with st.expander(f"Test: {test_name}"):
                    st.json(test_result)
        else:
            st.info("No se realizaron tests estadísticos")
    
    def _get_nse_description(self, nse):
        """Descripción del NSE"""
        descriptions = {
            "A": "Ejecutivos, empresarios",
            "B": "Profesionales, técnicos",
            "C": "Empleados, comerciantes",
            "D": "Obreros, trabajadores",
            "E": "Trabajadores eventuales"
        }
        return descriptions.get(nse, "")
    
    def _calculate_completion_rate(self, df):
        """Calcular tasa de completitud"""
        response_cols = [col for col in df.columns if col.endswith('_respuesta')]
        if not response_cols:
            return 0.0
        
        total_possible = len(df) * len(response_cols)
        total_completed = df[response_cols].notna().sum().sum()
        
        return total_completed / total_possible if total_possible > 0 else 0.0
    
    def _calculate_avg_confidence(self, df):
        """Calcular confianza promedio"""
        confidence_cols = [col for col in df.columns if col.endswith('_confianza')]
        if not confidence_cols:
            return 0.0
        
        all_confidences = []
        for col in confidence_cols:
            confidences = pd.to_numeric(df[col], errors='coerce').dropna()
            all_confidences.extend(confidences.tolist())
        
        return sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
    
    def run(self):
        """Ejecutar dashboard"""
        self.render_header()
        
        # Sidebar
        config = self.render_sidebar()
        
        # Barra de progreso
        self.render_progress_bar()
        
        st.markdown("---")
        
        # Renderizar paso actual
        if st.session_state.current_step == 0:
            self.render_step_0_upload(config)
        elif st.session_state.current_step == 1:
            self.render_step_1_creator(config)
        elif st.session_state.current_step == 2:
            self.render_step_2_executor(config)
        elif st.session_state.current_step == 3:
            self.render_step_3_visualizer(config)

def main():
    """Función principal"""
    dashboard = BuyerSyntheticDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()