import subprocess
import os

print("🚀 Ejecutando flujo principal...\n")
subprocess.run(["python", "-m", "agentes.flujo"], check=True)

print("\n📊 Generando visualización del flujo...\n")
subprocess.run(["python", "-m", "viz.viz_flujo"], check=True)

print("\n✅ Proceso completo.")
