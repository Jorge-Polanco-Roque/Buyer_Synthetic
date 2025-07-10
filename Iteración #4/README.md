# 🗳️ Buyer Synthetic™ — Encuestas Electorales con IA

**Buyer Synthetic™** es una plataforma avanzada de análisis de encuestas electorales potenciada por inteligencia artificial. Genera perfiles demográficos representativos y respuestas sintéticas utilizando LangGraph y OpenAI para crear datos de investigación sin necesidad de trabajo de campo tradicional.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.5+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)

</div>

---

## 🚀 Características Principales

### 🎯 Doble Modo de Operación
- **🎮 Demo Mode**: Respuestas simuladas instantáneas para prototipado rápido
- **🤖 GenAI Mode**: Respuestas generadas con IA usando LangGraph + OpenAI

### 📊 Funcionalidades Completas
- **Generación de Muestras Representativas**: Perfiles demográficos del Perú 2024
- **Encuestas Electorales**: 10 preguntas pre-configuradas para elecciones 2026
- **Análisis Estadístico**: Visualizaciones automáticas y reportes detallados
- **Dashboard Interactivo**: Interfaz web completa con Streamlit

### 🧠 Tecnología Avanzada
- **LangGraph**: Orquestación de workflows de IA con validación
- **OpenAI GPT-4**: Generación inteligente de respuestas contextualizadas
- **Contexto Cultural**: Adaptado específicamente para el mercado peruano
- **Validación de Coherencia**: Sistema automático de control de calidad

---

## 🏗️ Arquitectura del Sistema

```
buyer-synthetic/
├── src/
│   ├── buyer_synthetic/           # Módulo principal
│   │   ├── agents/               # Agentes de IA
│   │   │   ├── survey_creator.py         # Creador de muestras
│   │   │   ├── survey_executor.py        # Ejecutor tradicional
│   │   │   ├── survey_executor_langgraph.py  # Ejecutor LangGraph
│   │   │   └── results_visualizer.py     # Visualizador de resultados
│   │   ├── config/               # Configuraciones
│   │   │   └── settings.py               # Settings centralizados
│   │   ├── models/               # Modelos de datos
│   │   ├── utils/                # Utilidades
│   │   └── ui/                   # Interfaz de usuario
│   └── ui/
│       └── dashboard.py          # Dashboard principal Streamlit
├── data/                         # Datos de entrada y salida
│   ├── input/                    # Muestras generadas
│   └── output/                   # Análisis y visualizaciones
├── agentes/                      # Implementación original
├── tests/                        # Suite de pruebas
└── venv/                         # Entorno virtual
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos
- **Python 3.8+**
- **Git**
- **OpenAI API Key** (opcional, para GenAI Mode)

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic.git
cd Buyer_Synthetic

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# 3. Instalar dependencias
pip install pandas langgraph langchain-core langchain-openai streamlit
pip install matplotlib scipy seaborn plotly python-dotenv

# 4. Configurar variables de entorno (opcional)
echo "OPENAI_API_KEY=tu_api_key_aquí" > .env
```

### Verificación de Instalación

```bash
# Ejecutar tests de integración
python test_langgraph_integration.py
```

**Resultado esperado:**
```
🎉 ALL TESTS PASSED! System is ready!
Overall: 3/3 tests passed
```

---

## 🚀 Uso del Sistema

### 1. Ejecutar Dashboard

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar dashboard
python -m streamlit run src/ui/dashboard.py --server.port 8505
```

**Acceder a:** http://localhost:8505

### 2. Uso del Dashboard

#### 📋 **Paso 1: Configurar Encuesta**
- Seleccionar **modo de operación**:
  - **Demo Mode**: Respuestas instantáneas simuladas
  - **GenAI Mode**: Respuestas generadas con IA
- Definir **tamaño de muestra** (100-1000 perfiles)
- Configurar **modelo de IA** (si usas GenAI Mode)

#### 👥 **Paso 2: Crear Muestra Representativa**
- Generar perfiles demográficos representativos del Perú
- Distribución automática por NSE, región, edad y género
- Descarga disponible en formato CSV

#### 🗳️ **Paso 3: Ejecutar Encuesta**
- 10 preguntas electorales pre-configuradas
- Procesamiento por lotes para optimizar rendimiento
- Respuestas contextualizadas culturalmente

#### 📊 **Paso 4: Analizar Resultados**
- Visualizaciones automáticas:
  - Intención de voto por candidato
  - Principales problemas del país
  - Distribución demográfica
  - Puntuaciones de aprobación
- Exportación de datos y gráficos

### 3. Uso por CLI

```python
# Crear muestra representativa
from src.buyer_synthetic.agents.survey_creator import SurveyCreatorAgent

creator = SurveyCreatorAgent(sample_size=300)
sample_df = creator.generate_representative_sample()

# Ejecutar encuesta con LangGraph
from src.buyer_synthetic.agents.survey_executor_langgraph import SurveyExecutorLangGraph

executor = SurveyExecutorLangGraph()
results = executor.execute_individual_survey(profile, questions)

# Generar análisis
from src.buyer_synthetic.agents.results_visualizer import ResultsVisualizerAgent

visualizer = ResultsVisualizerAgent()
analysis = visualizer.analyze_and_visualize(results_df)
```

---

## 🧪 Casos de Uso

### 🗳️ **Investigación Electoral**
- Sondeos de intención de voto
- Análisis de problemas prioritarios
- Evaluación de candidatos
- Estudios de opinión pública

### 🏢 **Investigación de Mercado**
- Validación de conceptos de producto
- Estudios de segmentación
- Análisis de preferencias del consumidor
- Pruebas de concepto rápidas

### 📊 **Análisis Demográfico**
- Distribución representativa por NSE
- Análisis regional y urbano/rural
- Segmentación por edad y género
- Perfiles socioeconómicos detallados

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

```bash
# API Configuration
OPENAI_API_KEY=tu_api_key_aquí
DEFAULT_MODEL=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=2000

# Survey Configuration
MIN_SAMPLE_SIZE=100
MAX_SAMPLE_SIZE=1000
DEFAULT_SAMPLE_SIZE=300

# LangGraph Configuration
LANGGRAPH_MAX_RETRIES=2
LANGGRAPH_VALIDATION_THRESHOLD=0.7
```

### Personalización de Preguntas

Las preguntas electorales están definidas en `src/buyer_synthetic/config/settings.py`:

```python
ELECTORAL_QUESTIONS = [
    {
        "id": "intent_voto",
        "pregunta": "Si las elecciones presidenciales fueran hoy, ¿por quién votarías?",
        "tipo": "multiple",
        "opciones": ["Candidato A", "Candidato B", "Candidato C", "Voto en blanco", "No votaría", "No sabe/No opina"]
    },
    # ... más preguntas
]
```

---

## 🧪 Testing

### Suite de Pruebas Incluida

```bash
# Test completo de integración
python test_langgraph_integration.py

# Test específico de crear muestras
python test_crear_muestras.py

# Test del sistema original
python test_system.py
```

### Cobertura de Tests
- ✅ **Demo Mode**: Generación de respuestas simuladas
- ✅ **GenAI Mode**: Integración LangGraph + OpenAI
- ✅ **Dashboard Integration**: Interfaz completa
- ✅ **Data Processing**: Creación de muestras y análisis

---

## 📊 Datos y Métricas

### Distribución Demográfica del Perú 2024

**NSE (Nivel Socioeconómico):**
- NSE A: 5%
- NSE B: 15%
- NSE C: 35%
- NSE D: 25%
- NSE E: 20%

**Distribución Regional:**
- Lima: 33%
- Costa: 11%
- Sierra: 30%
- Selva: 26%

**Rangos de Edad:**
- 18-24: 15%
- 25-34: 20%
- 35-44: 18%
- 45-54: 18%
- 55-64: 15%
- 65+: 14%

---

## 🔧 Tecnologías Utilizadas

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Backend** | Python | 3.8+ | Lógica principal |
| **IA/LLM** | OpenAI GPT-4 | 1.93+ | Generación de respuestas |
| **Orquestación** | LangGraph | 0.5+ | Workflows de IA |
| **Frontend** | Streamlit | 1.46+ | Interfaz web |
| **Análisis** | Pandas, NumPy | Latest | Procesamiento de datos |
| **Visualización** | Plotly, Matplotlib | Latest | Gráficos y reportes |
| **Validación** | Pydantic | 2.11+ | Modelos de datos |

---

## 📈 Roadmap y Próximas Funcionalidades

### 🔄 **Iteración #5 (Próxima)**
- [ ] **API REST**: Endpoints para integración externa
- [ ] **Carga de Preguntas Personalizadas**: Upload de archivos TXT/CSV
- [ ] **Exportación Avanzada**: PDF, Excel, JSON
- [ ] **Análisis Predictivo**: Modelos estadísticos avanzados

### 🚀 **Futuras Iteraciones**
- [ ] **Multi-idioma**: Soporte para español e inglés
- [ ] **Base de Datos**: PostgreSQL para persistencia
- [ ] **Autenticación**: Sistema de usuarios y roles
- [ ] **Cloud Deploy**: AWS/Azure deployment
- [ ] **Real-time Updates**: WebSockets para actualizaciones en vivo

---

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "ModuleNotFoundError: No module named 'buyer_synthetic'"**
```bash
# Solución: Ejecutar desde directorio raíz
cd /ruta/al/proyecto
source venv/bin/activate
python -m streamlit run src/ui/dashboard.py
```

**Error: "unsupported operand type(s) for +: 'int' and 'str'"**
```bash
# Ya resuelto en la versión actual
# Asegúrate de usar la última versión del código
```

**Dashboard no carga o errores de importación**
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

---

## 🤝 Contribuciones

### Cómo Contribuir

1. **Fork** el repositorio
2. **Crear** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abrir** un Pull Request

### Guías de Contribución

- Seguir PEP 8 para código Python
- Incluir tests para nuevas funcionalidades
- Documentar cambios importantes
- Mantener compatibilidad con versiones anteriores

---

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto y Soporte

### 👤 **Desarrollador Principal**
**Jorge Polanco Roque**
- 🐙 GitHub: [@Jorge-Polanco-Roque](https://github.com/Jorge-Polanco-Roque)
- 📧 Email: jorge.polanco.roque@gmail.com

### 🌐 **Repositorio Oficial**
- 📂 GitHub: [Buyer_Synthetic](https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic)
- 🐛 Issues: [Reportar Bugs](https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic/issues)
- 💡 Features: [Solicitar Funcionalidades](https://github.com/Jorge-Polanco-Roque/Buyer_Synthetic/discussions)

### 🆘 **Soporte Técnico**
- 📋 **Wiki**: Documentación completa disponible en GitHub Wiki
- 🔧 **Troubleshooting**: Guías de solución de problemas
- 💬 **Discussions**: Foro de la comunidad para preguntas

---

<div align="center">

**🚀 ¡Gracias por usar Buyer Synthetic™!**

*Investigación sin campo, con IA • Perú 2024-2026*

---

© 2024 Buyer Synthetic™. Desarrollado con ❤️ para la investigación electoral peruana.

</div>