from database import conectar
from datetime import datetime


def registrar_vendedora():
    """Registra una nueva vendedora en la base de datos"""
    nombre = input("Nombre de la vendedora: ").strip()
    
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO vendedoras (nombre, activa, fecha_registro)
            VALUES (?, 1, ?)
        """, (nombre, fecha_actual))
        
        conexion.commit()
        print(f"✅ Vendedora '{nombre}' registrada correctamente.")
    except Exception as e:
        print(f"❌ Error al registrar vendedora: {e}")
    finally:
        conexion.close()


def ver_vendedoras():
    """Muestra todas las vendedoras registradas"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, activa
        FROM vendedoras
        ORDER BY id
    """)
    
    vendedoras = cursor.fetchall()
    conexion.close()
    
    print("\n👩‍💼 CATÁLOGO DE VENDEDORAS\n")
    
    if not vendedoras:
        print("No hay vendedoras registradas.")
        return
    
    for v in vendedoras:
        id_vendedora, nombre, activa = v
        estado = "ACTIVA" if activa == 1 else "INACTIVA"
        print(f"ID: {id_vendedora} | Nombre: {nombre} | Estado: {estado}")


def obtener_vendedora_por_id(id_vendedora):
    """Obtiene los datos de una vendedora por su ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, activa
        FROM vendedoras
        WHERE id = ?
    """, (id_vendedora,))
    
    vendedora = cursor.fetchone()
    conexion.close()
    
    if vendedora:
        return {
            "id": vendedora[0],
            "nombre": vendedora[1],
            "activa": vendedora[2] == 1
        }
    return None


def editar_vendedora():
    """Edita el nombre de una vendedora"""
    ver_vendedoras()
    
    try:
        id_vendedora = int(input("\nID de la vendedora a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    vendedora = obtener_vendedora_por_id(id_vendedora)
    
    if not vendedora:
        print("❌ Vendedora no encontrada.")
        return
    
    nuevo_nombre = input(f"Nombre actual: {vendedora['nombre']}\nNuevo nombre (ENTER para no cambiar): ").strip()
    
    if not nuevo_nombre:
        print("No se realizaron cambios.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE vendedoras
        SET nombre = ?
        WHERE id = ?
    """, (nuevo_nombre, id_vendedora))
    
    conexion.commit()
    conexion.close()
    
    print("✅ Vendedora editada correctamente.")


def cambiar_estado_vendedora():
    """Activa o desactiva una vendedora"""
    ver_vendedoras()
    
    try:
        id_vendedora = int(input("\nID de la vendedora: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    vendedora = obtener_vendedora_por_id(id_vendedora)
    
    if not vendedora:
        print("❌ Vendedora no encontrada.")
        return
    
    nuevo_estado = 0 if vendedora["activa"] else 1
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE vendedoras
        SET activa = ?
        WHERE id = ?
    """, (nuevo_estado, id_vendedora))
    
    conexion.commit()
    conexion.close()
    
    estado_texto = "ACTIVA" if nuevo_estado == 1 else "INACTIVA"
    print(f"✅ Vendedora ahora está {estado_texto}")


def obtener_vendedoras_activas():
    """Retorna lista de vendedoras activas para selección"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre
        FROM vendedoras
        WHERE activa = 1
        ORDER BY nombre
    """)
    
    vendedoras = cursor.fetchall()
    conexion.close()
    
    return vendedoras