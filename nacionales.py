from database import conectar
from datetime import datetime
from cotizador import ver_cotizaciones, obtener_cotizacion_por_id
from vendedoras import ver_vendedoras, obtener_vendedora_por_id


def registrar_viaje_nacional():
    """Registra un nuevo viaje nacional"""
    print("\n" + "="*60)
    print("🎫 REGISTRAR VIAJE NACIONAL")
    print("="*60)
    
    # ===== OPCIÓN: CARGAR DESDE COTIZACIÓN =====
    cargar = input("\n¿Cargar desde cotización? (s/n): ").strip().lower()
    
    if cargar in ['s', 'si', 'sí', 'yes', 'y']:
        cotizaciones = ver_cotizaciones()
        
        if not cotizaciones:
            print("\n❌ No hay cotizaciones disponibles.")
            return
        
        try:
            id_cot = int(input("\nSelecciona ID de cotización: "))
        except ValueError:
            print("❌ ID inválido.")
            return
        
        cotizacion = obtener_cotizacion_por_id(id_cot)
        
        if not cotizacion:
            print("❌ Cotización no encontrada.")
            return
        
        # Cargar datos
        nombre_viaje = cotizacion["nombre_viaje"]
        destino = cotizacion["destino"]
        fecha_salida = cotizacion["fecha_salida"]
        fecha_regreso = cotizacion["fecha_regreso"]
        dias = cotizacion["dias"]
        noches = cotizacion["noches"]
        cupos_totales = cotizacion["personas_proyectadas"]
        precio_doble = cotizacion["precio_persona_doble"]
        precio_triple = cotizacion["precio_persona_triple"]
        cotizacion_id = cotizacion["id"]
        
        print(f"\n✅ DATOS CARGADOS:")
        print(f"   Nombre: {nombre_viaje}")
        print(f"   Fechas: {fecha_salida} al {fecha_regreso} ({dias} días / {noches} noches)")
        print(f"   Cupos totales: {cupos_totales}")
        print(f"   Precio base doble: ${precio_doble:,.2f}")
        print(f"   Precio base triple: ${precio_triple:,.2f}")
    
    else:
        # Registro manual
        nombre_viaje = input("\nNombre del viaje: ").strip()
        destino = input("Destino: ").strip()
        fecha_salida = input("Fecha salida (DD-MM-YYYY): ").strip().replace("/", "-")
        fecha_regreso = input("Fecha regreso (DD-MM-YYYY): ").strip().replace("/", "-")
        
        try:
            salida = datetime.strptime(fecha_salida, "%d-%m-%Y")
            regreso = datetime.strptime(fecha_regreso, "%d-%m-%Y")
            dias = (regreso - salida).days + 1
            noches = dias - 1
        except:
            print("❌ Fechas inválidas.")
            return
        
        try:
            cupos_totales = int(input("Cupos totales: "))
            precio_doble = float(input("Precio por persona base doble: $"))
            precio_triple = float(input("Precio por persona base triple: $"))
        except ValueError:
            print("❌ Valores inválidos.")
            return
        
        cotizacion_id = None
    
    # ===== GUARDAR VIAJE =====
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO viajes_nacionales (
            cotizacion_id, nombre_viaje, destino, fecha_salida, fecha_regreso,
            dias, noches, cupos_totales, cupos_vendidos, cupos_disponibles,
            precio_persona_doble, precio_persona_triple, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 'ACTIVO', ?)
    """, (
        cotizacion_id, nombre_viaje, destino, fecha_salida, fecha_regreso,
        dias, noches, cupos_totales, cupos_totales,
        precio_doble, precio_triple, fecha_registro
    ))
    
    viaje_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Viaje nacional registrado con ID: {viaje_id}")


def ver_viajes_nacionales(usuario_actual):
    """Muestra todos los viajes nacionales activos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre_viaje, destino, fecha_salida, fecha_regreso,
               cupos_totales, cupos_vendidos, cupos_disponibles, estado
        FROM viajes_nacionales
        WHERE estado = 'ACTIVO'
        ORDER BY fecha_salida
    """)
    
    viajes = cursor.fetchall()
    conexion.close()
    
    print("\n" + "="*60)
    print("🎫 VIAJES NACIONALES ACTIVOS")
    print("="*60)
    
    if not viajes:
        print("\nNo hay viajes nacionales activos.")
        return
    
    for v in viajes:
        print(f"\nID: {v[0]}")
        print(f"Viaje: {v[1]}")
        print(f"Destino: {v[2]}")
        print(f"Fechas: {v[3]} al {v[4]}")
        print(f"Cupos: {v[6]} vendidos / {v[5]} totales ({v[7]} disponibles)")
        print(f"Estado: {v[8]}")
        print("-" * 60)


def registrar_cliente_nacional():
    """Registra un cliente en un viaje nacional"""
    print("\n" + "="*60)
    print("👤 REGISTRAR CLIENTE EN VIAJE NACIONAL")
    print("="*60)
    
    # Mostrar viajes disponibles
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre_viaje, cupos_disponibles, 
               precio_persona_doble, precio_persona_triple
        FROM viajes_nacionales
        WHERE estado = 'ACTIVO' AND cupos_disponibles > 0
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes disponibles.")
        conexion.close()
        return
    
    print("\n📋 VIAJES DISPONIBLES:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]} | Disponibles: {v[2]} cupos")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener datos del viaje
    cursor.execute("""
        SELECT nombre_viaje, cupos_disponibles, precio_persona_doble, precio_persona_triple
        FROM viajes_nacionales
        WHERE id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    print(f"\n✅ Viaje: {viaje[0]}")
    print(f"Precio base doble: ${viaje[2]:,.2f}")
    print(f"Precio base triple: ${viaje[3]:,.2f}")
    
    # ===== DATOS DEL CLIENTE =====
    print("\n--- DATOS DEL CLIENTE ---")
    
    nombre_cliente = input("Nombre del cliente: ").strip()
    celular_cliente = input("Celular del cliente: ").strip()
    
    # Seleccionar vendedora
    ver_vendedoras()
    try:
        vendedora_id = int(input("\nID de la vendedora: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    vendedora = obtener_vendedora_por_id(vendedora_id)
    if not vendedora or not vendedora["activa"]:
        print("❌ Vendedora no válida.")
        conexion.close()
        return
    
    try:
        adultos = int(input("Número de adultos: "))
        menores = int(input("Número de menores: "))
    except ValueError:
        print("❌ Números inválidos.")
        conexion.close()
        return
    
    total_personas = adultos + menores
    
    if total_personas > viaje[1]:
        print(f"❌ Solo hay {viaje[1]} cupos disponibles.")
        conexion.close()
        return
    
    # ===== DISTRIBUCIÓN DE HABITACIONES =====
    print("\n--- DISTRIBUCIÓN DE HABITACIONES ---")
    
    try:
        hab_dobles = int(input("Habitaciones dobles: "))
        hab_triples = int(input("Habitaciones triples: "))
    except ValueError:
        print("❌ Valores inválidos.")
        conexion.close()
        return
    
    # Calcular total
    total_dobles = hab_dobles * 2 * viaje[2]
    total_triples = hab_triples * 3 * viaje[3]
    total_pagar = total_dobles + total_triples
    
    print(f"\n--- RESUMEN ---")
    print(f"{hab_dobles} habitación(es) doble x ${viaje[2]:,.2f} x 2 = ${total_dobles:,.2f}")
    print(f"{hab_triples} habitación(es) triple x ${viaje[3]:,.2f} x 3 = ${total_triples:,.2f}")
    print(f"TOTAL A PAGAR: ${total_pagar:,.2f}")
    
    try:
        abono_inicial = float(input("\nAbono inicial: $"))
    except ValueError:
        print("❌ Monto inválido.")
        conexion.close()
        return
    
    saldo = total_pagar - abono_inicial
    
    # ===== GUARDAR CLIENTE =====
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO clientes_nacionales (
            viaje_id, vendedora_id, nombre_cliente, celular_responsable, adultos, menores,
            habitaciones_doble, habitaciones_triple, total_pagar,
            total_abonado, saldo, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ADEUDO', ?)
    """, (
        viaje_id, vendedora_id, nombre_cliente, celular_cliente, adultos, menores,
        hab_dobles, hab_triples, total_pagar,
        abono_inicial, saldo, fecha_registro
    ))
    
    cliente_id = cursor.lastrowid
    
    # Registrar abono inicial
    cursor.execute("""
        INSERT INTO abonos_nacionales (cliente_id, monto, fecha, vendedora_id)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, abono_inicial, fecha_registro, vendedora_id))
    
    # ===== REGISTRAR PASAJEROS =====
    print("\n--- REGISTRO DE PASAJEROS ---")
    
    pasajeros_registrados = []
    
    # Registrar por habitaciones DOBLES
    for i in range(hab_dobles):
        print(f"\n--- HABITACIÓN DOBLE {i+1} ---")
        for j in range(2):
            nombre = input(f"Pasajero {j+1}: ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "ADULTO",
                "habitacion": f"Doble {i+1}"
            })
    
    # Registrar por habitaciones TRIPLES
    for i in range(hab_triples):
        print(f"\n--- HABITACIÓN TRIPLE {i+1} ---")
        for j in range(3):
            nombre = input(f"Pasajero {j+1}: ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "ADULTO",
                "habitacion": f"Triple {i+1}"
            })
    
    # Registrar MENORES (si hay)
    if menores > 0:
        print(f"\n--- MENORES ({menores}) ---")
        for i in range(menores):
            nombre = input(f"Menor {i+1}: ").strip()
            hab = input(f"  ¿En qué habitación? (ej: Doble 1): ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "MENOR",
                "habitacion": hab
            })
    
    # Guardar en BD
    for pasajero in pasajeros_registrados:
        cursor.execute("""
            INSERT INTO pasajeros_nacionales (cliente_id, nombre_completo, tipo, habitacion_asignada)
            VALUES (?, ?, ?, ?)
        """, (cliente_id, pasajero["nombre"], pasajero["tipo"], pasajero["habitacion"]))
    
    # Actualizar cupos del viaje
    cursor.execute("""
        UPDATE viajes_nacionales
        SET cupos_vendidos = cupos_vendidos + ?,
            cupos_disponibles = cupos_disponibles - ?
        WHERE id = ?
    """, (total_personas, total_personas, viaje_id))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Cliente registrado correctamente.")
    print(f"Saldo restante: ${saldo:,.2f}")


def ver_clientes_viaje():
    """Muestra todos los clientes de un viaje"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Mostrar viajes
    cursor.execute("""
        SELECT id, nombre_viaje FROM viajes_nacionales
        WHERE estado = 'ACTIVO'
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes activos.")
        conexion.close()
        return
    
    print("\n📋 VIAJES ACTIVOS:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]}")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener clientes
    cursor.execute("""
        SELECT c.id, c.nombre_cliente, v.nombre AS vendedora,
               c.adultos, c.menores, c.total_pagar, c.total_abonado, c.saldo, c.estado
        FROM clientes_nacionales c
        JOIN vendedoras v ON c.vendedora_id = v.id
        WHERE c.viaje_id = ?
        ORDER BY c.fecha_registro
    """, (viaje_id,))
    
    clientes = cursor.fetchall()
    
    print("\n" + "="*60)
    print("👥 CLIENTES DEL VIAJE")
    print("="*60)
    
    if not clientes:
        print("\nNo hay clientes registrados.")
        conexion.close()
        return
    
    for c in clientes:
        cliente_id = c[0]
        estado_pago = "✅ LIQUIDADO" if c[8] == "LIQUIDADO" else "⏳ ADEUDO"
        
        print(f"\nID: {cliente_id} | {c[1]} (Vendedora: {c[2]})")
        print(f"{c[3]} adultos, {c[4]} menores")
        
        # DESGLOSE
        print(f"\n💰 DESGLOSE:")
        print(f"   Total a pagar: ${c[5]:,.2f}")
        print(f"   Abonado:       ${c[6]:,.2f}")
        print(f"   Saldo:         ${c[7]:,.2f}")
        print(f"   Estado: {estado_pago}")
        
        # Mostrar historial de abonos
        cursor.execute("""
            SELECT a.fecha, a.monto, v.nombre
            FROM abonos_nacionales a
            JOIN vendedoras v ON a.vendedora_id = v.id
            WHERE a.cliente_id = ?
            ORDER BY a.fecha
        """, (cliente_id,))
        
        abonos = cursor.fetchall()
        
        if abonos:
            print(f"\n📅 Historial de abonos:")
            for abono in abonos:
                print(f"   {abono[0]} - ${abono[1]:,.2f} (por {abono[2]})")
        
        print("-" * 60)
    
    conexion.close()


def registrar_abono_nacional():
    """Registra un abono de un cliente"""
    ver_clientes_viaje()
    
    try:
        cliente_id = int(input("\nID del cliente: "))
        monto = float(input("Monto del abono: $"))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener datos del cliente
    cursor.execute("""
        SELECT nombre_cliente, saldo FROM clientes_nacionales WHERE id = ?
    """, (cliente_id,))
    
    cliente = cursor.fetchone()
    
    if not cliente:
        print("❌ Cliente no encontrado.")
        conexion.close()
        return
    
    if monto > cliente[1]:
        print(f"❌ El abono (${monto:,.2f}) es mayor al saldo (${cliente[1]:,.2f}).")
        conexion.close()
        return
    
    # Obtener vendedora actual (la que hace el abono)
    ver_vendedoras()
    try:
        vendedora_id = int(input("\nID de la vendedora que registra: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Registrar abono
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO abonos_nacionales (cliente_id, monto, fecha, vendedora_id)
        VALUES (?, ?, ?, ?)
    """, (cliente_id, monto, fecha_actual, vendedora_id))
    
    # Actualizar cliente
    nuevo_saldo = cliente[1] - monto
    nuevo_abonado = cliente[1] + monto  # Se calcula desde el total
    
    cursor.execute("""
        UPDATE clientes_nacionales
        SET total_abonado = total_abonado + ?,
            saldo = saldo - ?
        WHERE id = ?
    """, (monto, monto, cliente_id))
    
    # Si liquidó, cambiar estado
    if nuevo_saldo == 0:
        cursor.execute("""
            UPDATE clientes_nacionales
            SET estado = 'LIQUIDADO'
            WHERE id = ?
        """, (cliente_id,))
        print(f"\n🎉 {cliente[0]} ha LIQUIDADO su viaje!")
    else:
        print(f"\n✅ Abono registrado. Saldo restante: ${nuevo_saldo:,.2f}")
    
    conexion.commit()
    conexion.close()
