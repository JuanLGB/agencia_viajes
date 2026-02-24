from database import conectar
from datetime import datetime
from vendedoras import obtener_vendedora_por_id, ver_vendedoras
from bloqueos import ver_bloqueos, obtener_bloqueo_por_id, descontar_habitacion
from hoteles import seleccionar_hotel


def validar_habitacion(adultos, menores):
    """
    Valida y retorna el tipo de habitación según las reglas de hoteles todo incluido Riviera Maya
    
    Reglas:
    - 2 adultos: Doble (acepta hasta 2 menores)
    - 3 adultos: Triple (acepta solo 1 menor)
    - 4 adultos: Cuádruple (NO acepta menores)
    
    Returns:
        tuple: (es_valido, tipo_habitacion, mensaje_error)
    """
    if adultos == 2:
        if menores > 2:
            return False, None, "❌ Habitación DOBLE acepta máximo 2 menores"
        return True, "DOBLE", None
    
    elif adultos == 3:
        if menores > 1:
            return False, None, "❌ Habitación TRIPLE acepta máximo 1 menor"
        return True, "TRIPLE", None
    
    elif adultos == 4:
        if menores > 0:
            return False, None, "❌ Habitación CUÁDRUPLE NO acepta menores"
        return True, "CUÁDRUPLE", None
    
    else:
        return False, None, f"❌ Configuración no válida: {adultos} adultos. Debe ser 2, 3 o 4 adultos."


def registrar_viaje(usuario_actual):
    """Registra un nuevo viaje en la base de datos"""
    
    # ===== PREGUNTAR SI ES BLOQUEO =====
    es_bloqueo_input = input("\n¿Es bloqueo? (s/n): ").strip().lower()
    
    # Aceptar: s, si, sí, yes, y
    if es_bloqueo_input in ['s', 'si', 'sí', 'yes', 'y']:
        registrar_viaje_bloqueo(usuario_actual)
    else:
        registrar_viaje_normal(usuario_actual)


def registrar_viaje_bloqueo(usuario_actual):
    """Registra un viaje usando un bloqueo existente"""
    
    print("\n" + "="*50)
    print("📦 SELECCIÓN DE BLOQUEO")
    print("="*50)
    
    # Mostrar bloqueos disponibles
    bloqueos = ver_bloqueos(solo_activos=True)
    
    if not bloqueos:
        print("\n❌ No hay bloqueos disponibles.")
        input("\nPresiona ENTER para continuar...")
        return
    
    print("\n" + "="*50)
    
    try:
        id_bloqueo = int(input("Selecciona ID del bloqueo: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    bloqueo = obtener_bloqueo_por_id(id_bloqueo)
    
    if not bloqueo:
        print("❌ Bloqueo no encontrado.")
        return
    
    if bloqueo['estado'] != 'ACTIVO':
        print(f"❌ El bloqueo está {bloqueo['estado']}.")
        return
    
    if bloqueo['habitaciones_disponibles'] <= 0:
        print("❌ No hay habitaciones disponibles en este bloqueo.")
        return
    
    print(f"\n✅ Bloqueo seleccionado: {bloqueo['hotel']}")
    print(f"📅 Fechas: {bloqueo['fecha_inicio']} al {bloqueo['fecha_fin']} ({bloqueo['noches']} noches)")
    
    # ===== DATOS DEL CLIENTE =====
    cliente = input("\nNombre del cliente: ").strip()
    celular_cliente = input("Celular del cliente: ").strip()
    
    try:
        adultos = int(input("Número de adultos: "))
        menores = int(input("Número de menores: "))
    except ValueError:
        print("❌ Número de pasajeros inválido.")
        return
    
    # ===== VALIDAR TIPO DE HABITACIÓN =====
    es_valido, tipo_habitacion, mensaje_error = validar_habitacion(adultos, menores)
    
    if not es_valido:
        print(mensaje_error)
        return
    
    print(f"\n✅ Configuración válida: Habitación {tipo_habitacion}")
    
    # ===== ASIGNAR VENDEDORA =====
    if usuario_actual["rol"] == "ADMIN":
        ver_vendedoras()
        try:
            id_vendedora = int(input("ID de la vendedora: "))
        except ValueError:
            print("❌ ID inválido.")
            return
    else:
        id_vendedora = usuario_actual["id_vendedora"]
    
    vendedora = obtener_vendedora_por_id(id_vendedora)
    
    if not vendedora or not vendedora["activa"]:
        print("❌ Vendedora no válida o inactiva.")
        return
    
    # ===== CALCULAR PRECIOS SEGÚN BLOQUEO =====
    noches = bloqueo['noches']
    
    # Seleccionar precios según tipo de habitación
    if tipo_habitacion == "DOBLE":
        precio_noche_hab = bloqueo['precio_noche_doble']
        precio_menor_noche = bloqueo['precio_menor_doble']
        divisor_adultos = 2
    elif tipo_habitacion == "TRIPLE":
        precio_noche_hab = bloqueo['precio_noche_triple']
        precio_menor_noche = bloqueo['precio_menor_triple']
        divisor_adultos = 3
    else:  # CUÁDRUPLE
        precio_noche_hab = bloqueo['precio_noche_cuadruple']
        precio_menor_noche = bloqueo['precio_menor_cuadruple']
        divisor_adultos = 4
    
    # Calcular precio por adulto
    precio_por_adulto = (precio_noche_hab / divisor_adultos) * noches
    precio_por_menor = precio_menor_noche * noches
    
    total_adultos = adultos * precio_por_adulto
    total_menores = menores * precio_por_menor
    precio_total = total_adultos + total_menores
    
    print("\n--- DESGLOSE ---")
    print(f"Precio noche habitación {tipo_habitacion}: ${precio_noche_hab}")
    print(f"Precio por adulto: ${precio_noche_hab} ÷ {divisor_adultos} = ${precio_noche_hab/divisor_adultos} / noche")
    print(f"{adultos} adultos x ${precio_por_adulto} = ${total_adultos}")
    print(f"{menores} menores x ${precio_por_menor} = ${total_menores}")
    print(f"TOTAL VIAJE: ${precio_total}")
    print("-----------------\n")
    
    try:
        porcentaje_ganancia = float(input("Porcentaje de ganancia (%): "))
    except ValueError:
        print("❌ Porcentaje inválido.")
        return
    
    if porcentaje_ganancia <= 0 or porcentaje_ganancia >= 100:
        print("❌ El porcentaje debe estar entre 0 y 100.")
        return
    
    ganancia = precio_total * (porcentaje_ganancia / 100)
    costo_mayorista = precio_total - ganancia
    saldo = precio_total
    
    # ===== GUARDAR VENTA EN BD =====
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO ventas (
            cliente, celular_responsable, tipo_venta, destino, fecha_inicio, fecha_fin, noches,
            adultos, menores, tipo_habitacion, precio_adulto, precio_menor, precio_total,
            porcentaje_ganancia, ganancia, costo_mayorista, saldo, estado,
            vendedora_id, usuario_id, es_bloqueo, bloqueo_id, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (
        cliente, celular_cliente, "Bloqueo", bloqueo['hotel'], bloqueo['fecha_inicio'], bloqueo['fecha_fin'], noches,
        adultos, menores, tipo_habitacion, precio_por_adulto, precio_por_menor, precio_total,
        porcentaje_ganancia, ganancia, costo_mayorista, saldo, "ACTIVO",
        id_vendedora, usuario_actual["id_vendedora"], id_bloqueo, fecha_registro
    ))
    
    venta_id = cursor.lastrowid
    
    # ===== REGISTRAR PASAJEROS =====
    print("\n--- REGISTRO DE PASAJEROS ---")
    
    for i in range(adultos):
        nombre = input(f"Nombre del adulto {i+1}: ").strip()
        cursor.execute("""
            INSERT INTO pasajeros (venta_id, nombre, tipo)
            VALUES (?, ?, ?)
        """, (venta_id, nombre, "ADULTO"))
    
    for i in range(menores):
        nombre = input(f"Nombre del menor {i+1}: ").strip()
        cursor.execute("""
            INSERT INTO pasajeros (venta_id, nombre, tipo)
            VALUES (?, ?, ?)
        """, (venta_id, nombre, "MENOR"))
    
    conexion.commit()
    conexion.close()
    
    # ===== DESCONTAR HABITACIÓN DEL BLOQUEO =====
    descontar_habitacion(id_bloqueo)
    
    print("\n✅ Viaje de bloqueo registrado correctamente.")
    print(f"📦 Habitaciones restantes en bloqueo: {bloqueo['habitaciones_disponibles'] - 1}")


def registrar_viaje_normal(usuario_actual):
    """Registra un nuevo viaje en la base de datos"""
    
    # ===== DATOS GENERALES =====
    cliente = input("Nombre del cliente: ").strip()
    celular_cliente = input("Celular del cliente: ").strip()
    
    # Seleccionar hotel con autocompletado
    destino = seleccionar_hotel()
    
    if not destino:
        return
    fecha_salida = input("Fecha de salida (DD-MM-YYYY): ").strip()
    fecha_regreso = input("Fecha de regreso (DD-MM-YYYY): ").strip()
    
    try:
        adultos = int(input("Número de adultos: "))
        menores = int(input("Número de menores: "))
    except ValueError:
        print("❌ Número de pasajeros inválido.")
        return
    
    # ===== VALIDAR TIPO DE HABITACIÓN =====
    es_valido, tipo_habitacion, mensaje_error = validar_habitacion(adultos, menores)
    
    if not es_valido:
        print(mensaje_error)
        return
    
    print(f"\n✅ Configuración válida: Habitación {tipo_habitacion}")
    
    # ===== VALIDAR FECHAS =====
    fecha_salida = fecha_salida.replace("/", "-")
    fecha_regreso = fecha_regreso.replace("/", "-")
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_salida, "%d-%m-%Y")
        fecha_fin_dt = datetime.strptime(fecha_regreso, "%d-%m-%Y")
    except ValueError:
        print("❌ Formato de fecha inválido. Use DD-MM-YYYY")
        return
    
    noches = (fecha_fin_dt - fecha_inicio_dt).days
    
    if noches < 0:
        print("❌ La fecha de regreso no puede ser antes de la salida.")
        return
    
    fecha_inicio = fecha_salida
    fecha_fin = fecha_regreso
    
    # ===== ASIGNAR VENDEDORA =====
    if usuario_actual["rol"] == "ADMIN":
        ver_vendedoras()
        try:
            id_vendedora = int(input("ID de la vendedora: "))
        except ValueError:
            print("❌ ID inválido.")
            return
    else:
        id_vendedora = usuario_actual["id_vendedora"]
    
    vendedora = obtener_vendedora_por_id(id_vendedora)
    
    if not vendedora:
        print("❌ Vendedora no válida o inactiva.")
        return
    
    if not vendedora["activa"]:
        print("❌ La vendedora está INACTIVA.")
        return
    
    # ===== COSTOS =====
    try:
        precio_adulto = float(input("Precio por adulto: "))
        precio_menor = float(input("Precio por menor: "))
    except ValueError:
        print("❌ Precio inválido.")
        return
    
    total_adultos = adultos * precio_adulto
    total_menores = menores * precio_menor
    precio_total = total_adultos + total_menores
    
    print("\n--- DESGLOSE ---")
    print(f"{adultos} adultos x ${precio_adulto} = ${total_adultos}")
    print(f"{menores} menores x ${precio_menor} = ${total_menores}")
    print(f"TOTAL VIAJE: ${precio_total}")
    print("-----------------\n")
    
    try:
        porcentaje_ganancia = float(input("Porcentaje de ganancia (%): "))
    except ValueError:
        print("❌ Porcentaje inválido.")
        return
    
    if porcentaje_ganancia <= 0 or porcentaje_ganancia >= 100:
        print("❌ El porcentaje debe estar entre 0 y 100.")
        return
    
    ganancia = precio_total * (porcentaje_ganancia / 100)
    costo_mayorista = precio_total - ganancia
    saldo = precio_total
    
    # ===== GUARDAR VENTA EN BD =====
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO ventas (
            cliente, celular_responsable, tipo_venta, destino, fecha_inicio, fecha_fin, noches,
            adultos, menores, tipo_habitacion, precio_adulto, precio_menor, precio_total,
            porcentaje_ganancia, ganancia, costo_mayorista, saldo, estado,
            vendedora_id, usuario_id, es_bloqueo, bloqueo_id, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
    """, (
        cliente, celular_cliente, "General", destino, fecha_inicio, fecha_fin, noches,
        adultos, menores, tipo_habitacion, precio_adulto, precio_menor, precio_total,
        porcentaje_ganancia, ganancia, costo_mayorista, saldo, "ACTIVO",
        id_vendedora, usuario_actual["id_vendedora"], 0, fecha_registro
    ))
    
    venta_id = cursor.lastrowid
    
    # ===== REGISTRAR PASAJEROS =====
    print("\n--- REGISTRO DE PASAJEROS ---")
    
    for i in range(adultos):
        nombre = input(f"Nombre del adulto {i+1}: ").strip()
        cursor.execute("""
            INSERT INTO pasajeros (venta_id, nombre, tipo)
            VALUES (?, ?, ?)
        """, (venta_id, nombre, "ADULTO"))
    
    for i in range(menores):
        nombre = input(f"Nombre del menor {i+1}: ").strip()
        cursor.execute("""
            INSERT INTO pasajeros (venta_id, nombre, tipo)
            VALUES (?, ?, ?)
        """, (venta_id, nombre, "MENOR"))
    
    conexion.commit()
    conexion.close()
    
    print("\n✅ Viaje y pasajeros registrados correctamente.")


def ver_viajes(usuario_actual):
    """Muestra los viajes activos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n📋 VIAJES ACTIVOS\n")
    
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin,
                   v.adultos, v.menores, v.tipo_habitacion, v.precio_adulto, v.precio_menor,
                   v.precio_total, v.saldo, v.porcentaje_ganancia, v.estado,
                   vd.nombre, v.es_bloqueo, v.tipo_venta, v.pagado,
                   v.comision_vendedora, v.comision_pagada, v.operador
            FROM ventas v
            JOIN vendedoras vd ON v.vendedora_id = vd.id
            WHERE v.usuario_id = ? AND v.estado != 'CERRADO'
            ORDER BY v.id DESC
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin,
                   v.adultos, v.menores, v.tipo_habitacion, v.precio_adulto, v.precio_menor,
                   v.precio_total, v.saldo, v.porcentaje_ganancia, v.estado,
                   vd.nombre, v.es_bloqueo, v.tipo_venta, v.pagado,
                   v.comision_vendedora, v.comision_pagada, v.operador
            FROM ventas v
            JOIN vendedoras vd ON v.vendedora_id = vd.id
            WHERE v.estado != 'CERRADO'
            ORDER BY v.id DESC
        """)
    
    ventas = cursor.fetchall()
    
    if not ventas:
        print("No hay viajes registrados.")
        conexion.close()
        return
    
    for venta in ventas:
        venta_id = venta[0]
        es_bloqueo = venta[15]
        tipo_venta = venta[16]
        pagado = venta[17]
        comision_vendedora = venta[18]
        comision_pagada = venta[19]
        precio_total = venta[10]
        saldo = venta[11]
        operador = venta[20]
        
        print(f"ID: {venta[0]}")
        print(f"Tipo: {tipo_venta} {'📦 BLOQUEO' if es_bloqueo else ''}")
        print(f"Cliente: {venta[1]}")
        print(f"Destino: {venta[2]}")
        if operador:
            print(f"🏢 Operador: {operador}")
        print(f"Salida: {venta[3]}")
        print(f"Regreso: {venta[4]}")
        print(f"🏨 Habitación: {venta[7]}")
        print(f"Adultos: {venta[5]} x ${venta[8]}")
        print(f"Menores: {venta[6]} x ${venta[9]}")
        
        # DESGLOSE DE PAGOS
        print(f"\n💰 DESGLOSE:")
        print(f"   Precio total:  ${precio_total:,.2f}")
        print(f"   Abonado:       ${pagado:,.2f}")
        print(f"   Saldo:         ${saldo:,.2f}")
        
        print(f"\nGanancia: {venta[12]}%")
        print(f"Estado: {venta[13]}")
        print(f"Vendedora: {venta[14]}")
        
        # Mostrar comisión si está liquidado
        if venta[13] == "LIQUIDADO":
            estado_comision = "✅ PAGADA" if comision_pagada == 1 else "⏳ PENDIENTE"
            print(f"💵 Comisión: ${comision_vendedora:,.2f} - {estado_comision}")
        
        # Mostrar pasajeros
        cursor.execute("""
            SELECT nombre, tipo
            FROM pasajeros
            WHERE venta_id = ?
        """, (venta_id,))
        
        pasajeros = cursor.fetchall()
        
        print("\n👥 Pasajeros:")
        if pasajeros:
            for p in pasajeros:
                print(f" - {p[0]} ({p[1]})")
        else:
            print(" - Sin pasajeros registrados")
        
        # Mostrar historial de abonos con fecha/hora
        cursor.execute("""
            SELECT fecha, monto
            FROM abonos
            WHERE venta_id = ?
            ORDER BY fecha
        """, (venta_id,))
        
        abonos = cursor.fetchall()
        
        if abonos:
            print("\n📅 Historial de abonos:")
            for abono in abonos:
                print(f" - {abono[0]}: ${abono[1]:,.2f}")
        
        print("-" * 60)
    
    conexion.close()


def ver_mis_comisiones(usuario_actual):
    """Muestra las comisiones de la vendedora (pendientes y pagadas)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*60)
    print("💵 MIS COMISIONES")
    print("="*60)
    
    # Comisiones pendientes
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.comision_vendedora, v.fecha_inicio
        FROM ventas v
        WHERE v.usuario_id = ? AND v.estado = 'LIQUIDADO' AND v.comision_pagada = 0
        ORDER BY v.fecha_inicio DESC
    """, (usuario_actual["id_vendedora"],))
    
    pendientes = cursor.fetchall()
    
    print("\n⏳ COMISIONES PENDIENTES:\n")
    
    if pendientes:
        total_pendiente = 0
        for c in pendientes:
            print(f"Viaje #{c[0]} | {c[1]} - {c[2]}")
            print(f"   Comisión: ${c[3]:,.2f}")
            print(f"   Fecha viaje: {c[4]}")
            print("-" * 60)
            total_pendiente += c[3]
        
        print(f"\n💰 TOTAL PENDIENTE: ${total_pendiente:,.2f}\n")
    else:
        print("No hay comisiones pendientes.\n")
    
    # Comisiones pagadas
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.comision_vendedora, 
               v.fecha_inicio, v.fecha_pago_comision
        FROM ventas v
        WHERE v.usuario_id = ? AND v.estado = 'CERRADO' AND v.comision_pagada = 1
        ORDER BY v.fecha_pago_comision DESC
        LIMIT 10
    """, (usuario_actual["id_vendedora"],))
    
    pagadas = cursor.fetchall()
    
    print("✅ ÚLTIMAS COMISIONES PAGADAS:\n")
    
    if pagadas:
        total_pagado = 0
        for c in pagadas:
            print(f"Viaje #{c[0]} | {c[1]} - {c[2]}")
            print(f"   Comisión: ${c[3]:,.2f}")
            print(f"   Fecha viaje: {c[4]}")
            print(f"   📅 Pagada: {c[5]}")
            print("-" * 60)
            total_pagado += c[3]
        
        print(f"\n✅ TOTAL MOSTRADO: ${total_pagado:,.2f}")
    else:
        print("No hay comisiones pagadas aún.")
    
    conexion.close()


def editar_viaje(usuario_actual):
    """Edita un viaje existente"""
    try:
        id_viaje = int(input("ID del viaje a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Verificar que el viaje existe y pertenece al usuario (si es vendedora)
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT * FROM ventas
            WHERE id = ? AND usuario_id = ?
        """, (id_viaje, usuario_actual["id_vendedora"]))
    else:
        cursor.execute("SELECT * FROM ventas WHERE id = ?", (id_viaje,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    # Verificar que no tenga pagos
    cursor.execute("SELECT COUNT(*) FROM abonos WHERE venta_id = ?", (id_viaje,))
    tiene_pagos = cursor.fetchone()[0] > 0
    
    if tiene_pagos:
        print("❌ No se puede editar un viaje con pagos registrados.")
        conexion.close()
        return
    
    print("\n--- DATOS ACTUALES ---")
    print(f"Cliente: {viaje[1]}")
    print(f"Destino: {viaje[3]}")
    print(f"Precio total: ${viaje[11]}")
    print(f"Ganancia: {viaje[12]}%")
    print("\nENTER para no cambiar\n")
    
    # Obtener nuevos valores
    nuevo_cliente = input(f"Nuevo cliente: ").strip() or viaje[1]
    nuevo_destino = input(f"Nuevo destino: ").strip() or viaje[3]
    
    nuevo_precio = input(f"Nuevo precio total: ").strip()
    nuevo_porcentaje = input(f"Nuevo % ganancia: ").strip()
    
    precio_total = float(nuevo_precio) if nuevo_precio else viaje[11]
    porcentaje_ganancia = float(nuevo_porcentaje) if nuevo_porcentaje else viaje[12]
    
    ganancia = precio_total * (porcentaje_ganancia / 100)
    costo_mayorista = precio_total - ganancia
    saldo = precio_total
    
    cursor.execute("""
        UPDATE ventas
        SET cliente = ?, destino = ?, precio_total = ?,
            porcentaje_ganancia = ?, ganancia = ?,
            costo_mayorista = ?, saldo = ?
        WHERE id = ?
    """, (nuevo_cliente, nuevo_destino, precio_total, porcentaje_ganancia,
          ganancia, costo_mayorista, saldo, id_viaje))
    
    conexion.commit()
    conexion.close()
    
    print("✅ Viaje editado correctamente.")
