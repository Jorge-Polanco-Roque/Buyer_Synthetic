# 🧠 Simulador de Panel de Encuesta con LLM

Este proyecto genera respuestas simuladas a un cuestionario estructurado en formato JSON, utilizando un modelo de lenguaje (`gpt-4o`) a través de la librería `langchain`. El resultado se guarda como un archivo `.csv` que simula encuestas contestadas por personas reales.

## 📁 Estructura del Proyecto

```
.
├── agentes/
│   └── test_panel.py               # Script principal
├── encuesta/
│   └── test_panel_1.csv            # Archivo generado con las respuestas simuladas
├── otros/
│   └── test_1.txt                  # Esquema de preguntas de la encuesta (formato JSON)
├── contexto/
│   ├── archivo1.txt                # Archivos de contexto extra para simular mejor
│   └── archivo2.txt                # (opcional, se agregan dinámicamente)
├── prompt/
│   └── prompt_perú2026.txt         # Instrucciones adicionales para guiar al modelo
└── .env                            # Contiene la variable OPENAI_API_KEY
```

## 🧪 Requisitos

- Python 3.8+
- Cuenta y API Key de OpenAI
- Archivo `.env` con:

```env
OPENAI_API_KEY=sk-...
```

## 📦 Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Requisitos mínimos (`requirements.txt`)

```
python-dotenv
pandas
langchain
langchain-openai
```

## 🚀 Ejecución

```bash
python agentes/test_panel.py
```

Esto generará el archivo `encuesta/test_panel_1.csv` con respuestas simuladas.

## ⚙️ ¿Cómo funciona?

1. **Carga el esquema** desde `otros/test_1.txt`, donde defines bloques y variables de la encuesta.
2. **Lee el contexto** desde los archivos `.txt` en la carpeta `contexto/` y el prompt base en `prompt/prompt_perú2026.txt`.
3. **Construye un prompt robusto** para el modelo, indicando claves, restricciones y formato JSON.
4. **Llama al modelo** `gpt-4o` para generar respuestas simuladas.
5. **Valida** que el JSON contenga todas las claves requeridas.
6. **Guarda el resultado** en un CSV listo para análisis.

## 📝 Ejemplo de entrada (`test_1.txt`)

```json
{
  "campos": [
    {
      "bloque": "Demografía",
      "variables": [
        {
          "nombre": "Edad",
          "nota": "Número entero entre 18 y 65"
        },
        {
          "nombre": "Región",
          "opciones": ["Lima", "Norte", "Sur", "Centro", "Oriente"]
        }
      ]
    }
  ]
}
```

## 📌 Notas

- Si alguna respuesta contiene claves faltantes o adicionales, se reintenta hasta 3 veces.
- Si falla, la fila se completa con `"ERROR"`.

# Notas importantes:

## Guardar versionamiento de librerías
pip freeze > requirements.txt

## Activar el flujo principal + visualización - Test Flujo
python run.py