"""
Script de migración: Crea vendedoras en la BD basándose en usuarios.json
"""
from database import conectar, crear_tablas
from datetime import datetime
import json
import os

def migrar_vendedoras():
    """Migra vendedoras desde usuarios.json a la base de datos"""
    
    # Crear tablas si no existen
    crear_tablas()
    
    # Cargar usuarios.json
    if not os.path.exists("usuarios.json"):
        print("❌ No se encontró usuarios.json")
        return
    
    with open("usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)
    
    # Conectar a la BD
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener vendedoras únicas del JSON
    vendedoras_dict = {}
    
    for u in usuarios:
        if u["rol"] == "VENDEDORA":
            id_vendedora = u["id_vendedora"]
            nombre = u["nombre"]
            
            if id_vendedora not in vendedoras_dict:
                vendedoras_dict[id_vendedora] = nombre
    
    if not vendedoras_dict:
        print("❌ No hay vendedoras en usuarios.json")
        conexion.close()
        return
    
    print(f"\n🔄 Encontradas {len(vendedoras_dict)} vendedoras en usuarios.json\n")
    
    # Insertar vendedoras en la BD
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for id_vendedora, nombre in vendedoras_dict.items():
        # Verificar si ya existe
        cursor.execute("SELECT id FROM vendedoras WHERE id = ?", (id_vendedora,))
        existe = cursor.fetchone()
        
        if existe:
            print(f"⚠️  Vendedora ID {id_vendedora} '{nombre}' ya existe en BD")
        else:
            # Insertar con el ID específico
            cursor.execute("""
                INSERT INTO vendedoras (id, nombre, activa, fecha_registro)
                VALUES (?, ?, 1, ?)
            """, (id_vendedora, nombre, fecha_actual))
            print(f"✅ Vendedora ID {id_vendedora} '{nombre}' migrada a BD")
    
    conexion.commit()
    conexion.close()
    
    print("\n✅ Migración completada.\n")


if __name__ == "__main__":
    print("="*60)
    print("MIGRACIÓN DE VENDEDORAS: usuarios.json → Base de Datos")
    print("="*60)
    migrar_vendedoras()
