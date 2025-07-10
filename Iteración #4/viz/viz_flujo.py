"""
Visualización del flujo de trabajo con LangGraph.
"""

import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
from typing import Dict, List, Tuple
import json

def generar_diagrama_flujo():
    """Genera un diagrama visual del flujo de trabajo"""
    
    # Crear grafo dirigido
    G = nx.DiGraph()
    
    # Definir nodos del flujo
    nodos = [
        ("inicio", "Inicio"),
        ("cargar_datos", "Cargar Datos\nCSV"),
        ("cargar_contexto", "Cargar Contexto\nPolitico/Cultural"),
        ("procesar_fila", "Procesar Fila\ncon LLM"),
        ("calculo_matematico", "Cálculos\nMatemáticos"),
        ("validar_respuesta", "Validar\nRespuesta JSON"),
        ("decision", "¿Todas las filas\nprocesadas?"),
        ("guardar_resultados", "Guardar\nResultados"),
        ("generar_reporte", "Generar\nReporte PDF"),
        ("fin", "Fin")
    ]
    
    # Agregar nodos
    for nodo_id, etiqueta in nodos:
        G.add_node(nodo_id, label=etiqueta)
    
    # Definir aristas (conexiones)
    aristas = [
        ("inicio", "cargar_datos"),
        ("cargar_datos", "cargar_contexto"),
        ("cargar_contexto", "procesar_fila"),
        ("procesar_fila", "calculo_matematico"),
        ("calculo_matematico", "validar_respuesta"),
        ("validar_respuesta", "decision"),
        ("decision", "procesar_fila"),  # Loop
        ("decision", "guardar_resultados"),
        ("guardar_resultados", "generar_reporte"),
        ("generar_reporte", "fin")
    ]
    
    # Agregar aristas
    G.add_edges_from(aristas)
    
    # Crear figura
    plt.figure(figsize=(14, 10))
    
    # Definir posiciones de nodos
    pos = {
        "inicio": (0, 5),
        "cargar_datos": (2, 5),
        "cargar_contexto": (4, 5),
        "procesar_fila": (6, 5),
        "calculo_matematico": (8, 5),
        "validar_respuesta": (10, 5),
        "decision": (12, 5),
        "guardar_resultados": (12, 3),
        "generar_reporte": (12, 1),
        "fin": (12, -1)
    }
    
    # Colores para diferentes tipos de nodos
    colores_nodos = {
        "inicio": "#90EE90",
        "cargar_datos": "#FFE4B5",
        "cargar_contexto": "#FFE4B5",
        "procesar_fila": "#87CEEB",
        "calculo_matematico": "#DDA0DD",
        "validar_respuesta": "#F0E68C",
        "decision": "#FF6347",
        "guardar_resultados": "#98FB98",
        "generar_reporte": "#98FB98",
        "fin": "#FF69B4"
    }
    
    # Dibujar nodos
    for nodo in G.nodes():
        color = colores_nodos.get(nodo, "#CCCCCC")
        nx.draw_networkx_nodes(G, pos, nodelist=[nodo], 
                             node_color=color, node_size=2000, alpha=0.8)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                          arrows=True, arrowsize=20, arrowstyle='->')
    
    # Agregar etiquetas
    etiquetas = {nodo: G.nodes[nodo]['label'] for nodo in G.nodes()}
    nx.draw_networkx_labels(G, pos, etiquetas, font_size=8, font_weight='bold')
    
    # Configurar gráfica
    plt.title("Flujo de Trabajo - Buyer Synthetic", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # Guardar diagrama
    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)
    
    plt.savefig(output_dir / "diagrama_flujo.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "diagrama_flujo.pdf", dpi=300, bbox_inches='tight')
    
    print("✅ Diagrama de flujo generado: viz/diagrama_flujo.png")
    
    plt.show()
    plt.close()

def generar_diagrama_arquitectura():
    """Genera un diagrama de arquitectura del sistema"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Definir componentes
    componentes = [
        {"nombre": "Usuario", "x": 1, "y": 9, "width": 2, "height": 1, "color": "#FFE4B5"},
        {"nombre": "run.py\n(Entrada)", "x": 1, "y": 7, "width": 2, "height": 1, "color": "#90EE90"},
        {"nombre": "LangGraph\n(Orquestador)", "x": 5, "y": 7, "width": 3, "height": 1, "color": "#87CEEB"},
        {"nombre": "Contexto\n(Archivos .txt)", "x": 1, "y": 5, "width": 2, "height": 1, "color": "#DDA0DD"},
        {"nombre": "OpenAI GPT-4\n(LLM)", "x": 9, "y": 7, "width": 3, "height": 1, "color": "#FF6347"},
        {"nombre": "Datos CSV\n(Entrada)", "x": 1, "y": 3, "width": 2, "height": 1, "color": "#F0E68C"},
        {"nombre": "Procesamiento\n(Funciones)", "x": 5, "y": 5, "width": 3, "height": 1, "color": "#98FB98"},
        {"nombre": "Resultados CSV\n(Salida)", "x": 9, "y": 3, "width": 3, "height": 1, "color": "#FFB6C1"},
        {"nombre": "Reportes PDF\n(Análisis)", "x": 9, "y": 1, "width": 3, "height": 1, "color": "#FFA07A"},
        {"nombre": "Gráficas\n(Visualización)", "x": 5, "y": 1, "width": 3, "height": 1, "color": "#20B2AA"}
    ]
    
    # Dibujar componentes
    for comp in componentes:
        rect = plt.Rectangle((comp["x"], comp["y"]), comp["width"], comp["height"], 
                           facecolor=comp["color"], edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(comp["x"] + comp["width"]/2, comp["y"] + comp["height"]/2, 
                comp["nombre"], ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Dibujar conexiones
    conexiones = [
        # (x1, y1, x2, y2)
        (2, 9, 2, 8),      # Usuario -> run.py
        (2, 7, 5, 7.5),    # run.py -> LangGraph
        (2, 5, 5, 5.5),    # Contexto -> Procesamiento
        (2, 3, 5, 4.5),    # Datos CSV -> Procesamiento
        (6.5, 7, 9, 7.5),  # LangGraph -> OpenAI
        (8, 5.5, 9, 3.5),  # Procesamiento -> Resultados
        (8, 4.5, 9, 1.5),  # Procesamiento -> Reportes
        (6.5, 5, 6.5, 2)   # Procesamiento -> Gráficas
    ]
    
    for x1, y1, x2, y2 in conexiones:
        ax.arrow(x1, y1, x2-x1, y2-y1, head_width=0.1, head_length=0.1, 
                fc='gray', ec='gray', linewidth=2)
    
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title("Arquitectura del Sistema - Buyer Synthetic", fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Guardar diagrama
    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)
    
    plt.savefig(output_dir / "arquitectura_sistema.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "arquitectura_sistema.pdf", dpi=300, bbox_inches='tight')
    
    print("✅ Diagrama de arquitectura generado: viz/arquitectura_sistema.png")
    
    plt.show()
    plt.close()

def generar_metricas_visuales():
    """Genera visualizaciones de métricas del sistema"""
    
    # Datos de ejemplo para métricas
    metricas = {
        "procesamiento": {
            "tiempo_promedio": 2.5,
            "filas_por_minuto": 24,
            "tasa_exito": 0.95,
            "precision_json": 0.92
        },
        "calidad": {
            "coherencia": 0.87,
            "confianza": 0.85,
            "completitud": 0.93,
            "satisfaccion": 0.78
        }
    }
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Gráfico 1: Métricas de procesamiento
    proc_metricas = metricas["procesamiento"]
    ax1.bar(proc_metricas.keys(), proc_metricas.values(), 
            color=['#87CEEB', '#98FB98', '#FFB6C1', '#DDA0DD'])
    ax1.set_title("Métricas de Procesamiento")
    ax1.set_ylabel("Valor")
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Gráfico 2: Métricas de calidad
    cal_metricas = metricas["calidad"]
    ax2.bar(cal_metricas.keys(), cal_metricas.values(), 
            color=['#FF6347', '#F0E68C', '#20B2AA', '#FFA07A'])
    ax2.set_title("Métricas de Calidad")
    ax2.set_ylabel("Valor (0-1)")
    ax2.set_ylim(0, 1)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Gráfico 3: Distribución de tiempos
    tiempos = [1.2, 2.1, 1.8, 3.2, 2.5, 1.9, 2.8, 2.3, 1.7, 2.6]
    ax3.hist(tiempos, bins=5, color='#90EE90', alpha=0.7, edgecolor='black')
    ax3.set_title("Distribución de Tiempos de Procesamiento")
    ax3.set_xlabel("Tiempo (segundos)")
    ax3.set_ylabel("Frecuencia")
    
    # Gráfico 4: Tendencia de calidad
    dias = list(range(1, 11))
    calidad_tendencia = [0.82, 0.84, 0.86, 0.83, 0.87, 0.89, 0.85, 0.88, 0.90, 0.87]
    ax4.plot(dias, calidad_tendencia, marker='o', color='#FF6347', linewidth=2)
    ax4.set_title("Tendencia de Calidad (10 días)")
    ax4.set_xlabel("Día")
    ax4.set_ylabel("Calidad Promedio")
    ax4.set_ylim(0.8, 0.95)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Guardar métricas
    output_dir = Path("viz")
    output_dir.mkdir(exist_ok=True)
    
    plt.savefig(output_dir / "metricas_sistema.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "metricas_sistema.pdf", dpi=300, bbox_inches='tight')
    
    print("✅ Métricas visuales generadas: viz/metricas_sistema.png")
    
    plt.show()
    plt.close()

def generar_todas_visualizaciones():
    """Genera todas las visualizaciones del sistema"""
    
    print("📊 Generando visualizaciones del sistema...")
    
    try:
        generar_diagrama_flujo()
        generar_diagrama_arquitectura()
        generar_metricas_visuales()
        
        print("✅ Todas las visualizaciones generadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error generando visualizaciones: {str(e)}")

if __name__ == "__main__":
    generar_todas_visualizaciones()