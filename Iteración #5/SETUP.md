# 🚀 Setup Guide - Buyer Synthetic™

Esta guía te ayudará a configurar y ejecutar **Buyer Synthetic™** paso a paso.

## ✅ **Estado del Proyecto**

- 🧹 **Ambientes virtuales**: Limpiados (eliminados `venv/` y `simple_venv/`)
- 📦 **Ambiente principal**: `.venv/` con todas las dependencias
- 🔧 **Makefile**: Actualizado para usar `.venv/` directamente
- ✅ **Tests**: Todos los tests de integración pasan
- 📝 **Documentación**: README.md actualizado y mejorado

## 🛠️ **Configuración Inicial**

### **Opción 1: Ambiente ya configurado (Recomendado)**

Si ya tienes el proyecto descargado con `.venv/` presente:

```bash
# 1. Verificar que el ambiente funcione
make test-integration

# 2. Ejecutar dashboard
make dev
```

### **Opción 2: Setup desde cero**

Si necesitas configurar desde cero:

```bash
# 1. Crear ambiente virtual
python3 -m venv .venv

# 2. Activar ambiente
source .venv/bin/activate

# 3. Instalar dependencias
pip install -e .

# 4. Verificar instalación
make test-integration

# 5. Ejecutar proyecto
make dev
```

## 🎯 **Comandos Principales**

### **Desarrollo**
```bash
make dev                    # Dashboard principal (puerto 8505)
make dev-simple            # Dashboard básico (puerto 8505)
make audit-dashboard       # Dashboard de auditoría (puerto 8506)
make audit-chat            # Chatbot CLI de auditoría
```

### **Testing**
```bash
make test-integration      # Tests de integración completos
make test                  # Tests unitarios (Poetry)
make test-cov             # Tests con cobertura (Poetry)
```

### **Calidad de Código**
```bash
make lint                 # Linters (ruff, black, isort)
make format              # Formatear código
make type-check          # Verificación de tipos
make security-check      # Análisis de seguridad
```

### **Docker**
```bash
make docker-build        # Construir imagen
make docker-run          # Ejecutar contenedor
make docker-compose-up   # Servicios completos
```

## 🌐 **Acceso a la Aplicación**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Dashboard Principal** | http://localhost:8505 | Interfaz completa para encuestas |
| **Dashboard de Auditoría** | http://localhost:8506 | Sistema de trazabilidad |

## 🔧 **Configuración Opcional**

### **API Key de OpenAI (Para GenAI Mode)**

```bash
# Crear archivo .env
echo "OPENAI_API_KEY=tu_api_key_aquí" > .env
```

### **Variables de Entorno Adicionales**

```bash
# .env
DEFAULT_MODEL=gpt-4
TEMPERATURE=0.7
DEFAULT_SAMPLE_SIZE=300
LANGGRAPH_MAX_RETRIES=2
```

## 📊 **Uso del Sistema**

### **Flujo de Trabajo**

1. **Ejecutar Dashboard**: `make dev`
2. **Configurar Modo**: Demo (instantáneo) o GenAI (IA)
3. **Crear Muestra**: Perfiles demográficos representativos
4. **Ejecutar Encuesta**: 10 preguntas electorales especializadas
5. **Analizar Resultados**: Visualizaciones y estadísticas
6. **Auditoría**: Consultar trazabilidad con chatbot IA

### **Ejemplo de Uso**

```bash
# 1. Iniciar sistema
make dev

# 2. En otra terminal - ver trazabilidad
make audit-dashboard

# 3. Consultar chatbot de auditoría
make audit-chat
```

## 🐛 **Troubleshooting**

### **Error: ModuleNotFoundError**
```bash
# Verificar ambiente
ls -la .venv/

# Reinstalar si es necesario
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### **Error: Dashboard no carga**
```bash
# Verificar puerto
lsof -i :8505

# Usar puerto alternativo
.venv/bin/streamlit run src/buyer_synthetic/ui/dashboard.py --server.port 8506
```

### **Error: Dependencias faltantes**
```bash
# Reinstalar dependencias
pip install -e . --force-reinstall
```

## 📁 **Estructura del Proyecto**

```
buyer-synthetic/
├── .venv/                     # ✅ Ambiente virtual principal
├── src/buyer_synthetic/       # ✅ Código fuente
│   ├── agents/               # Agentes de IA
│   ├── config/               # Configuraciones
│   ├── core/                 # Componentes centrales
│   ├── ui/                   # Interfaces de usuario
│   └── utils/                # Utilidades
├── tests/                    # ✅ Suite de pruebas
├── data/                     # Datos y trazas
├── Makefile                  # ✅ Comandos de desarrollo
├── pyproject.toml           # ✅ Configuración Poetry
└── README.md                # ✅ Documentación principal
```

## 🎉 **¡Listo para usar!**

El proyecto está completamente configurado y listo. Simplemente ejecuta:

```bash
make dev
```

Y abre http://localhost:8505 en tu navegador.