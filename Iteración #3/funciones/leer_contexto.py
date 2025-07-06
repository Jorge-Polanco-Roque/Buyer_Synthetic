import os

def leer_contexto(carpeta_contexto: str) -> str:
    textos = []
    for fname in os.listdir(carpeta_contexto):
        if fname.endswith(".txt"):
            with open(os.path.join(carpeta_contexto, fname), encoding="utf-8") as f:
                textos.append(f.read())
    return "\n".join(textos)
