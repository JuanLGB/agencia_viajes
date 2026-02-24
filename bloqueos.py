from database import conectar
from operadores import seleccionar_operador
from datetime import datetime
from hoteles import seleccionar_hotel


def calcular_noches(fecha_inicio, fecha_fin):
    """Calcula el número de noches entre dos fechas"""
    try:
        inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        fin = datetime.strptime(fecha_fin, "%d-%m-%Y")
        return (fin - inicio).days
    except:
        return 0


def registrar_bloqueo():
    """Registra un nuevo bloqueo en la base de datos"""
    print("\n📦 REGISTRAR NUEVO BLOQUEO\n")
    
    # Seleccionar hotel con autocompletado
    hotel = seleccionar_hotel()
    
    if not hotel:
        return
    
    # Seleccionar operador
    print("\n🏢 OPERADOR MAYORISTA:")
    operador = seleccionar_operador()
    
    # Datos del responsable
    celular_responsable = input("\nCelular del responsable: ").strip()
    
    fecha_inicio = input("\nFecha inicio (DD-MM-YYYY): ").strip().replace("/", "-")
    fecha_fin = input("Fecha fin (DD-MM-YYYY): ").strip().replace("/", "-")
    
    # Calcular noches
    noches = calcular_noches(fecha_inicio, fecha_fin)
    
    if noches <= 0:
        print("❌ Las fechas no son válidas.")
        return
    
    print(f"\n✅ Noches calculadas: {noches}")
    
    try:
        habitaciones_totales = int(input("Número de habitaciones compradas: "))
        
        print("\n--- PRECIOS POR NOCHE ---")
        precio_noche_doble = float(input("Precio noche Habitación DOBLE: $"))
        precio_noche_triple = float(input("Precio noche Habitación TRIPLE: $"))
        precio_noche_cuadruple = float(input("Precio noche Habitación CUÁDRUPLE: $"))
        
        print("\n--- PRECIOS MENORES POR NOCHE ---")
        precio_menor_doble = float(input("Precio menor en DOBLE (0 si no aplica): $"))
        precio_menor_triple = float(input("Precio menor en TRIPLE (0 si no aplica): $"))
        precio_menor_cuadruple = float(input("Precio menor en CUÁDRUPLE (0 si no aplica): $"))
        
        costo_real = float(input("\nCosto real por habitación (referencia): $"))
        
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    # Guardar en BD
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO bloqueos (
            hotel, operador, celular_responsable, fecha_inicio, fecha_fin, noches,
            habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
            precio_noche_doble, precio_noche_triple, precio_noche_cuadruple,
            precio_menor_doble, precio_menor_triple, precio_menor_cuadruple,
            costo_real, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVO', ?)
    """, (
        hotel, operador, celular_responsable, fecha_inicio, fecha_fin, noches,
        habitaciones_totales, habitaciones_totales,
        precio_noche_doble, precio_noche_triple, precio_noche_cuadruple,
        precio_menor_doble, precio_menor_triple, precio_menor_cuadruple,
        costo_real, fecha_registro
    ))
    
    conexion.commit()
    conexion.close()
    
    print("\n✅ Bloqueo registrado correctamente.")


def ver_bloqueos(solo_activos=False):
    """Muestra todos los bloqueos o solo los activos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    if solo_activos:
        cursor.execute("""
            SELECT id, hotel, fecha_inicio, fecha_fin, noches,
                   habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
                   estado
            FROM bloqueos
            WHERE estado = 'ACTIVO' AND habitaciones_disponibles > 0
            ORDER BY fecha_inicio
        """)
        print("\n📦 BLOQUEOS DISPONIBLES\n")
    else:
        cursor.execute("""
            SELECT id, hotel, fecha_inicio, fecha_fin, noches,
                   habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
                   estado
            FROM bloqueos
            ORDER BY fecha_inicio DESC
        """)
        print("\n📦 TODOS LOS BLOQUEOS\n")
    
    bloqueos = cursor.fetchall()
    conexion.close()
    
    if not bloqueos:
        print("No hay bloqueos registrados.")
        return []
    
    for b in bloqueos:
        print(f"ID: {b[0]}")
        print(f"Hotel: {b[1]}")
        print(f"Fechas: {b[2]} al {b[3]} ({b[4]} noches)")
        print(f"Disponibles: {b[7]} / {b[5]} habitaciones")
        print(f"Vendidas: {b[6]}")
        print(f"Estado: {b[8]}")
        print("-" * 40)
    
    return bloqueos


def obtener_bloqueo_por_id(id_bloqueo):
    """Obtiene los datos completos de un bloqueo"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT * FROM bloqueos WHERE id = ?
    """, (id_bloqueo,))
    
    bloqueo = cursor.fetchone()
    conexion.close()
    
    if not bloqueo:
        return None
    
    return {
        "id": bloqueo[0],
        "hotel": bloqueo[1],
        "fecha_inicio": bloqueo[2],
        "fecha_fin": bloqueo[3],
        "noches": bloqueo[4],
        "habitaciones_totales": bloqueo[5],
        "habitaciones_vendidas": bloqueo[6],
        "habitaciones_disponibles": bloqueo[7],
        "precio_noche_doble": bloqueo[8],
        "precio_noche_triple": bloqueo[9],
        "precio_noche_cuadruple": bloqueo[10],
        "precio_menor_doble": bloqueo[11],
        "precio_menor_triple": bloqueo[12],
        "precio_menor_cuadruple": bloqueo[13],
        "costo_real": bloqueo[14],
        "estado": bloqueo[15],
        "fecha_registro": bloqueo[16]
    }


def descontar_habitacion(id_bloqueo):
    """Descuenta una habitación del inventario del bloqueo"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Actualizar vendidas y disponibles
    cursor.execute("""
        UPDATE bloqueos
        SET habitaciones_vendidas = habitaciones_vendidas + 1,
            habitaciones_disponibles = habitaciones_disponibles - 1
        WHERE id = ?
    """, (id_bloqueo,))
    
    # Verificar si se agotó
    cursor.execute("""
        SELECT habitaciones_disponibles FROM bloqueos WHERE id = ?
    """, (id_bloqueo,))
    
    disponibles = cursor.fetchone()[0]
    
    if disponibles == 0:
        cursor.execute("""
            UPDATE bloqueos SET estado = 'AGOTADO' WHERE id = ?
        """, (id_bloqueo,))
    
    conexion.commit()
    conexion.close()


def editar_bloqueo():
    """Edita un bloqueo existente"""
    ver_bloqueos()
    
    try:
        id_bloqueo = int(input("\nID del bloqueo a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    bloqueo = obtener_bloqueo_por_id(id_bloqueo)
    
    if not bloqueo:
        print("❌ Bloqueo no encontrado.")
        return
    
    print("\n--- DATOS ACTUALES ---")
    print(f"Hotel: {bloqueo['hotel']}")
    print(f"Habitaciones totales: {bloqueo['habitaciones_totales']}")
    print(f"Precio noche DOBLE: ${bloqueo['precio_noche_doble']}")
    print(f"Precio noche TRIPLE: ${bloqueo['precio_noche_triple']}")
    print(f"Precio noche CUÁDRUPLE: ${bloqueo['precio_noche_cuadruple']}")
    print("\nENTER para no cambiar\n")
    
    # Obtener nuevos valores
    nuevo_hotel = input("Nuevo hotel: ").strip() or bloqueo['hotel']
    
    nuevas_habitaciones = input(f"Nuevas habitaciones totales: ").strip()
    if nuevas_habitaciones:
        habitaciones_totales = int(nuevas_habitaciones)
        diferencia = habitaciones_totales - bloqueo['habitaciones_totales']
        habitaciones_disponibles = bloqueo['habitaciones_disponibles'] + diferencia
    else:
        habitaciones_totales = bloqueo['habitaciones_totales']
        habitaciones_disponibles = bloqueo['habitaciones_disponibles']
    
    nuevo_precio_doble = input("Nuevo precio noche DOBLE: ").strip()
    nuevo_precio_triple = input("Nuevo precio noche TRIPLE: ").strip()
    nuevo_precio_cuadruple = input("Nuevo precio noche CUÁDRUPLE: ").strip()
    
    precio_noche_doble = float(nuevo_precio_doble) if nuevo_precio_doble else bloqueo['precio_noche_doble']
    precio_noche_triple = float(nuevo_precio_triple) if nuevo_precio_triple else bloqueo['precio_noche_triple']
    precio_noche_cuadruple = float(nuevo_precio_cuadruple) if nuevo_precio_cuadruple else bloqueo['precio_noche_cuadruple']
    
    # Actualizar en BD
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE bloqueos
        SET hotel = ?, habitaciones_totales = ?, habitaciones_disponibles = ?,
            precio_noche_doble = ?, precio_noche_triple = ?, precio_noche_cuadruple = ?
        WHERE id = ?
    """, (nuevo_hotel, habitaciones_totales, habitaciones_disponibles,
          precio_noche_doble, precio_noche_triple, precio_noche_cuadruple, id_bloqueo))
    
    conexion.commit()
    conexion.close()
    
    print("✅ Bloqueo editado correctamente.")


def cambiar_estado_bloqueo():
    """Cambia el estado de un bloqueo (ACTIVO / CERRADO)"""
    ver_bloqueos()
    
    try:
        id_bloqueo = int(input("\nID del bloqueo: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    bloqueo = obtener_bloqueo_por_id(id_bloqueo)
    
    if not bloqueo:
        print("❌ Bloqueo no encontrado.")
        return
    
    nuevo_estado = "CERRADO" if bloqueo['estado'] == "ACTIVO" else "ACTIVO"
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE bloqueos SET estado = ? WHERE id = ?
    """, (nuevo_estado, id_bloqueo))
    
    conexion.commit()
    conexion.close()
    
    print(f"✅ Bloqueo ahora está {nuevo_estado}")


def reporte_bloqueos():
    """Genera un reporte de todos los bloqueos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN estado = 'AGOTADO' THEN 1 ELSE 0 END) as agotados,
            SUM(habitaciones_totales) as hab_totales,
            SUM(habitaciones_vendidas) as hab_vendidas,
            SUM(habitaciones_disponibles) as hab_disponibles
        FROM bloqueos
    """)
    
    datos = cursor.fetchone()
    conexion.close()
    
    print("\n📊 REPORTE DE BLOQUEOS")
    print(f"Total bloqueos: {datos[0]}")
    print(f"Activos: {datos[1]}")
    print(f"Agotados: {datos[2]}")
    print(f"Habitaciones totales: {datos[3]}")
    print(f"Habitaciones vendidas: {datos[4]}")
    print(f"Habitaciones disponibles: {datos[5]}")
