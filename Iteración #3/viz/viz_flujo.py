import os
import networkx as nx
import matplotlib.pyplot as plt
from agentes.flujo import graph

# Crear grafo dirigido
G = nx.DiGraph()
for node in graph.nodes:
    G.add_node(node)
for u, v in graph.edges:
    G.add_edge(u, v)

# Layout y figura
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=2000, font_size=10)
plt.title("Flujo LangGraph completo")
plt.axis('off')

# Guardar imagen en carpeta output
output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "graph_flujo.png")
plt.savefig(output_path, bbox_inches="tight")
print(f"✅ Diagrama guardado en: {output_path}")

# Mostrar en pantalla
plt.show()
