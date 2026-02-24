from database import conectar
from datetime import datetime
from operadores import seleccionar_operador


def registrar_grupo():
    """Registra un nuevo grupo"""
    print("\n" + "="*60)
    print("📦 REGISTRAR NUEVO GRUPO")
    print("="*60)
    
    nombre_grupo = input("\nNombre del grupo: ").strip()
    
    # Seleccionar operador
    operador = seleccionar_operador()
    
    hotel = input("Hotel: ").strip()
    fecha_inicio = input("Fecha de inicio (DD-MM-YYYY): ").strip().replace("/", "-")
    fecha_fin = input("Fecha de fin (DD-MM-YYYY): ").strip().replace("/", "-")
    
    try:
        inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fin = datetime.strptime(fecha_fin, "%d-%m-%Y")
        noches = (fin - inicio).days
    except:
        print("❌ Fechas inválidas.")
        return
    
    if noches <= 0:
        print("❌ La fecha de fin debe ser posterior a la de inicio.")
        return
    
    print(f"\n✅ {noches} noches")
    
    try:
        habitaciones_totales = int(input("Habitaciones totales: "))
        
        print("\n💵 PRECIOS POR NOCHE:")
        precio_doble = float(input("Precio por noche (Doble): $"))
        precio_triple = float(input("Precio por noche (Triple): $"))
        precio_cuadruple = float(input("Precio por noche (Cuádruple): $"))
        
        print("\n👶 PRECIOS MENORES POR NOCHE:")
        precio_menor_doble = float(input("Precio menor (Doble): $"))
        precio_menor_triple = float(input("Precio menor (Triple): $"))
        precio_menor_cuadruple = float(input("Precio menor (Cuádruple): $"))
        
        costo_real = float(input("\nCosto real del grupo: $"))
        
    except ValueError:
        print("❌ Valores numéricos inválidos.")
        return
    
    # Datos del responsable
    print("\n👤 DATOS DEL RESPONSABLE:")
    responsable = input("Nombre del responsable [Mamá]: ").strip() or "Mamá"
    celular_responsable = input("Celular del responsable: ").strip()
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO grupos (
            nombre_grupo, operador, hotel, fecha_inicio, fecha_fin, noches,
            habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
            precio_noche_doble, precio_noche_triple, precio_noche_cuadruple,
            precio_menor_doble, precio_menor_triple, precio_menor_cuadruple,
            costo_real, responsable, celular_responsable, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVO', ?)
    """, (
        nombre_grupo, operador, hotel, fecha_inicio, fecha_fin, noches,
        habitaciones_totales, habitaciones_totales,
        precio_doble, precio_triple, precio_cuadruple,
        precio_menor_doble, precio_menor_triple, precio_menor_cuadruple,
        costo_real, responsable, celular_responsable, fecha_registro
    ))
    
    grupo_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Grupo '{nombre_grupo}' registrado con ID: {grupo_id}")


def ver_grupos(solo_activos=False):
    """Muestra todos los grupos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    if solo_activos:
        cursor.execute("""
            SELECT id, nombre_grupo, hotel, fecha_inicio, fecha_fin, noches,
                   habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
                   responsable, estado
            FROM grupos
            WHERE estado = 'ACTIVO'
            ORDER BY fecha_inicio
        """)
    else:
        cursor.execute("""
            SELECT id, nombre_grupo, hotel, fecha_inicio, fecha_fin, noches,
                   habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
                   responsable, estado
            FROM grupos
            ORDER BY fecha_inicio DESC
        """)
    
    grupos = cursor.fetchall()
    conexion.close()
    
    print("\n" + "="*60)
    print("📦 GRUPOS" + (" ACTIVOS" if solo_activos else ""))
    print("="*60)
    
    if not grupos:
        print("\nNo hay grupos registrados.")
        return []
    
    for g in grupos:
        estado_icon = "✅" if g[10] == "ACTIVO" else "🔒"
        ocupacion = (g[7] / g[6] * 100) if g[6] > 0 else 0
        
        print(f"\n{estado_icon} ID: {g[0]} | {g[1]}")
        print(f"   Hotel: {g[2]}")
        print(f"   Fechas: {g[3]} al {g[4]} ({g[5]} noches)")
        print(f"   Habitaciones: {g[7]}/{g[6]} vendidas ({ocupacion:.0f}%) | {g[8]} disponibles")
        print(f"   Responsable: {g[9]}")
        print(f"   Estado: {g[10]}")
        print("-" * 60)
    
    return grupos


def obtener_grupo_por_id(grupo_id):
    """Obtiene un grupo por su ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre_grupo, operador, hotel, fecha_inicio, fecha_fin, noches,
               habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
               precio_noche_doble, precio_noche_triple, precio_noche_cuadruple,
               precio_menor_doble, precio_menor_triple, precio_menor_cuadruple,
               costo_real, responsable, celular_responsable, estado
        FROM grupos
        WHERE id = ?
    """, (grupo_id,))
    
    grupo = cursor.fetchone()
    conexion.close()
    
    if not grupo:
        return None
    
    return {
        'id': grupo[0],
        'nombre_grupo': grupo[1],
        'operador': grupo[2],
        'hotel': grupo[3],
        'fecha_inicio': grupo[4],
        'fecha_fin': grupo[5],
        'noches': grupo[6],
        'habitaciones_totales': grupo[7],
        'habitaciones_vendidas': grupo[8],
        'habitaciones_disponibles': grupo[9],
        'precio_noche_doble': grupo[10],
        'precio_noche_triple': grupo[11],
        'precio_noche_cuadruple': grupo[12],
        'precio_menor_doble': grupo[13],
        'precio_menor_triple': grupo[14],
        'precio_menor_cuadruple': grupo[15],
        'costo_real': grupo[16],
        'responsable': grupo[17],
        'celular_responsable': grupo[18],
        'estado': grupo[19]
    }


def editar_grupo():
    """Edita información de un grupo"""
    ver_grupos()
    
    try:
        grupo_id = int(input("\nID del grupo a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    grupo = obtener_grupo_por_id(grupo_id)
    
    if not grupo:
        print("❌ Grupo no encontrado.")
        return
    
    if grupo['estado'] != 'ACTIVO':
        print("❌ No se puede editar un grupo cerrado.")
        return
    
    print(f"\n📝 Editando: {grupo['nombre_grupo']}")
    print("(Presiona Enter para mantener el valor actual)\n")
    
    # Editar campos
    nombre = input(f"Nombre [{grupo['nombre_grupo']}]: ").strip() or grupo['nombre_grupo']
    hotel = input(f"Hotel [{grupo['hotel']}]: ").strip() or grupo['hotel']
    
    print("\n💵 PRECIOS POR NOCHE:")
    try:
        precio_doble_input = input(f"Precio doble [${grupo['precio_noche_doble']:.2f}]: $").strip()
        precio_doble = float(precio_doble_input) if precio_doble_input else grupo['precio_noche_doble']
        
        precio_triple_input = input(f"Precio triple [${grupo['precio_noche_triple']:.2f}]: $").strip()
        precio_triple = float(precio_triple_input) if precio_triple_input else grupo['precio_noche_triple']
        
        precio_cuadruple_input = input(f"Precio cuádruple [${grupo['precio_noche_cuadruple']:.2f}]: $").strip()
        precio_cuadruple = float(precio_cuadruple_input) if precio_cuadruple_input else grupo['precio_noche_cuadruple']
        
        costo_real_input = input(f"\nCosto real [${grupo['costo_real']:.2f}]: $").strip()
        costo_real = float(costo_real_input) if costo_real_input else grupo['costo_real']
        
    except ValueError:
        print("❌ Valores numéricos inválidos.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE grupos
        SET nombre_grupo = ?, hotel = ?,
            precio_noche_doble = ?, precio_noche_triple = ?, precio_noche_cuadruple = ?,
            costo_real = ?
        WHERE id = ?
    """, (nombre, hotel, precio_doble, precio_triple, precio_cuadruple, costo_real, grupo_id))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Grupo actualizado correctamente.")


def cambiar_estado_grupo():
    """Cierra o reabre un grupo"""
    ver_grupos()
    
    try:
        grupo_id = int(input("\nID del grupo: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    grupo = obtener_grupo_por_id(grupo_id)
    
    if not grupo:
        print("❌ Grupo no encontrado.")
        return
    
    nuevo_estado = 'CERRADO' if grupo['estado'] == 'ACTIVO' else 'ACTIVO'
    accion = "cerrar" if nuevo_estado == 'CERRADO' else "reabrir"
    
    print(f"\nGrupo: {grupo['nombre_grupo']}")
    print(f"Estado actual: {grupo['estado']}")
    
    confirmar = input(f"\n¿Seguro que deseas {accion} este grupo? (s/n): ").lower()
    
    if confirmar not in ['s', 'si', 'sí', 'yes', 'y']:
        print("\n❌ Operación cancelada.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("UPDATE grupos SET estado = ? WHERE id = ?", (nuevo_estado, grupo_id))
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Grupo {accion}.")


def descontar_habitacion_grupo(grupo_id, cantidad=1):
    """Descuenta habitaciones disponibles de un grupo"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE grupos
        SET habitaciones_vendidas = habitaciones_vendidas + ?,
            habitaciones_disponibles = habitaciones_disponibles - ?
        WHERE id = ? AND habitaciones_disponibles >= ?
    """, (cantidad, cantidad, grupo_id, cantidad))
    
    affected = cursor.rowcount
    conexion.commit()
    conexion.close()
    
    return affected > 0


def reporte_grupos():
    """Genera reporte de todos los grupos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_grupos,
            SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN estado = 'CERRADO' THEN 1 ELSE 0 END) as cerrados,
            SUM(habitaciones_totales) as total_habitaciones,
            SUM(habitaciones_vendidas) as vendidas,
            SUM(habitaciones_disponibles) as disponibles
        FROM grupos
    """)
    
    resumen = cursor.fetchone()
    
    print("\n" + "="*60)
    print("📊 REPORTE DE GRUPOS")
    print("="*60)
    
    print(f"\n📦 RESUMEN:")
    print(f"   Total grupos: {resumen[0]}")
    print(f"   Activos: {resumen[1]}")
    print(f"   Cerrados: {resumen[2]}")
    
    print(f"\n🏨 HABITACIONES:")
    print(f"   Total: {resumen[3]}")
    print(f"   Vendidas: {resumen[4]}")
    print(f"   Disponibles: {resumen[5]}")
    
    if resumen[3] and resumen[3] > 0:
        ocupacion = (resumen[4] / resumen[3] * 100)
        print(f"   Ocupación: {ocupacion:.1f}%")
    
    # Grupos activos detallados
    cursor.execute("""
        SELECT nombre_grupo, hotel, habitaciones_vendidas, habitaciones_totales,
               precio_noche_doble, noches, costo_real
        FROM grupos
        WHERE estado = 'ACTIVO'
        ORDER BY fecha_inicio
    """)
    
    grupos_activos = cursor.fetchall()
    
    if grupos_activos:
        print(f"\n📋 GRUPOS ACTIVOS:")
        for g in grupos_activos:
            ocupacion = (g[2] / g[3] * 100) if g[3] > 0 else 0
            ingreso_proyectado = g[2] * 2 * g[4] * g[5]  # habitaciones * 2 personas * precio * noches
            ganancia = ingreso_proyectado - g[6]
            
            print(f"\n   {g[0]} - {g[1]}")
            print(f"   Ocupación: {g[2]}/{g[3]} hab ({ocupacion:.0f}%)")
            print(f"   Ingreso proyectado: ${ingreso_proyectado:,.2f}")
            print(f"   Costo: ${g[6]:,.2f}")
            print(f"   Ganancia proyectada: ${ganancia:,.2f}")
    
    conexion.close()


def menu_grupos():
    """Menú principal de gestión de grupos"""
    while True:
        print("\n" + "="*60)
        print("📦 GESTIÓN DE GRUPOS")
        print("="*60)
        print("\n1. Registrar grupo")
        print("2. Ver grupos")
        print("3. Ver grupos activos")
        print("4. Editar grupo")
        print("5. Cerrar/Reabrir grupo")
        print("6. Reporte de grupos")
        print("7. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            registrar_grupo()
        elif opcion == "2":
            ver_grupos(solo_activos=False)
        elif opcion == "3":
            ver_grupos(solo_activos=True)
        elif opcion == "4":
            editar_grupo()
        elif opcion == "5":
            cambiar_estado_grupo()
        elif opcion == "6":
            reporte_grupos()
        elif opcion == "7":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_grupos()
