from database import conectar
from datetime import datetime


def agregar_operador():
    """Agrega un nuevo operador mayorista"""
    print("\n" + "="*60)
    print("🏢 AGREGAR OPERADOR MAYORISTA")
    print("="*60)
    
    nombre = input("\nNombre del operador: ").strip()
    
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    contacto = input("Persona de contacto (opcional): ").strip()
    telefono = input("Teléfono (opcional): ").strip()
    email = input("Email (opcional): ").strip()
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO operadores (nombre, contacto, telefono, email, activo, veces_usado, fecha_registro)
            VALUES (?, ?, ?, ?, 1, 0, ?)
        """, (nombre, contacto, telefono, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conexion.commit()
        print(f"\n✅ Operador '{nombre}' agregado correctamente.")
        
    except sqlite3.IntegrityError:
        print(f"\n❌ El operador '{nombre}' ya existe.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        conexion.close()


def ver_operadores():
    """Muestra todos los operadores"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, contacto, telefono, email, veces_usado, activo
        FROM operadores
        ORDER BY nombre
    """)
    
    operadores = cursor.fetchall()
    conexion.close()
    
    print("\n" + "="*60)
    print("🏢 OPERADORES MAYORISTAS")
    print("="*60)
    
    if not operadores:
        print("\nNo hay operadores registrados.")
        return operadores
    
    for op in operadores:
        estado = "✅ Activo" if op[6] else "🔒 Inactivo"
        print(f"\nID: {op[0]} | {op[1]} {estado}")
        if op[2]:
            print(f"   Contacto: {op[2]}")
        if op[3]:
            print(f"   Teléfono: {op[3]}")
        if op[4]:
            print(f"   Email: {op[4]}")
        print(f"   Veces usado: {op[5]}")
        print("-" * 60)
    
    return operadores


def editar_operador():
    """Edita información de un operador"""
    ver_operadores()
    
    try:
        id_operador = int(input("\nID del operador a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM operadores WHERE id = ?", (id_operador,))
    operador = cursor.fetchone()
    
    if not operador:
        print("❌ Operador no encontrado.")
        conexion.close()
        return
    
    print(f"\n📝 Editando: {operador[1]}")
    print("(Presiona Enter para mantener el valor actual)\n")
    
    nombre = input(f"Nombre [{operador[1]}]: ").strip() or operador[1]
    contacto = input(f"Contacto [{operador[2] or ''}]: ").strip() or operador[2]
    telefono = input(f"Teléfono [{operador[3] or ''}]: ").strip() or operador[3]
    email = input(f"Email [{operador[4] or ''}]: ").strip() or operador[4]
    
    try:
        cursor.execute("""
            UPDATE operadores
            SET nombre = ?, contacto = ?, telefono = ?, email = ?
            WHERE id = ?
        """, (nombre, contacto, telefono, email, id_operador))
        
        conexion.commit()
        print(f"\n✅ Operador actualizado correctamente.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        conexion.close()


def cambiar_estado_operador():
    """Activa o desactiva un operador"""
    ver_operadores()
    
    try:
        id_operador = int(input("\nID del operador: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre, activo FROM operadores WHERE id = ?", (id_operador,))
    operador = cursor.fetchone()
    
    if not operador:
        print("❌ Operador no encontrado.")
        conexion.close()
        return
    
    nuevo_estado = 0 if operador[1] == 1 else 1
    accion = "activar" if nuevo_estado == 1 else "desactivar"
    
    confirmar = input(f"\n¿Seguro que deseas {accion} a '{operador[0]}'? (s/n): ").lower()
    
    if confirmar in ['s', 'si', 'sí', 'yes', 'y']:
        cursor.execute("UPDATE operadores SET activo = ? WHERE id = ?", (nuevo_estado, id_operador))
        conexion.commit()
        print(f"\n✅ Operador {'activado' if nuevo_estado == 1 else 'desactivado'}.")
    else:
        print("\n❌ Operación cancelada.")
    
    conexion.close()


def seleccionar_operador():
    """Permite seleccionar un operador y retorna su nombre"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre
        FROM operadores
        WHERE activo = 1
        ORDER BY nombre
    """)
    
    operadores = cursor.fetchall()
    
    if not operadores:
        print("\n⚠️  No hay operadores disponibles.")
        agregar = input("¿Deseas agregar uno ahora? (s/n): ").lower()
        if agregar in ['s', 'si', 'sí', 'yes', 'y']:
            conexion.close()
            agregar_operador()
            return seleccionar_operador()
        conexion.close()
        return None
    
    print("\n🏢 SELECCIONA OPERADOR:")
    for op in operadores:
        print(f"{op[0]}. {op[1]}")
    print(f"{len(operadores) + 1}. Agregar nuevo operador")
    print("0. Sin operador")
    
    try:
        seleccion = int(input("\nOpción: "))
    except ValueError:
        conexion.close()
        return None
    
    if seleccion == 0:
        conexion.close()
        return None
    
    if seleccion == len(operadores) + 1:
        conexion.close()
        agregar_operador()
        return seleccionar_operador()
    
    # Buscar el operador seleccionado
    for op in operadores:
        if op[0] == seleccion:
            # Incrementar contador de uso
            cursor.execute("""
                UPDATE operadores
                SET veces_usado = veces_usado + 1
                WHERE id = ?
            """, (op[0],))
            conexion.commit()
            conexion.close()
            return op[1]
    
    conexion.close()
    return None


def menu_operadores():
    """Menú de gestión de operadores"""
    while True:
        print("\n" + "="*60)
        print("🏢 GESTIÓN DE OPERADORES MAYORISTAS")
        print("="*60)
        print("\n1. Ver operadores")
        print("2. Agregar operador")
        print("3. Editar operador")
        print("4. Activar/Desactivar operador")
        print("5. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            ver_operadores()
        elif opcion == "2":
            agregar_operador()
        elif opcion == "3":
            editar_operador()
        elif opcion == "4":
            cambiar_estado_operador()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    import sqlite3
    menu_operadores()
