import json
import os

RUTA_VIAJES = "viajes.json"
RUTA_VENDEDORAS = "vendedoras.json"
RUTA_USUARIOS = "usuarios.json"

def cargar_viajes():
    if not os.path.exists(RUTA_VIAJES):
        return []
    with open(RUTA_VIAJES, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_viajes(viajes):
    with open(RUTA_VIAJES, "w", encoding="utf-8") as f:
        json.dump(viajes, f, indent=4, ensure_ascii=False)

def cargar_vendedoras():
    if not os.path.exists(RUTA_VENDEDORAS):
        return []
    with open(RUTA_VENDEDORAS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_vendedoras(vendedoras):
    with open(RUTA_VENDEDORAS, "w", encoding="utf-8") as f:
        json.dump(vendedoras, f, indent=4, ensure_ascii=False)

def cargar_usuarios():
    if not os.path.exists(RUTA_USUARIOS):
        return []
    with open(RUTA_USUARIOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)
