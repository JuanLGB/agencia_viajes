from database import conectar
from datetime import datetime
from grupos import ver_grupos, obtener_grupo_por_id, descontar_habitacion_grupo
from vendedoras import ver_vendedoras, obtener_vendedora_por_id


def registrar_venta_grupo():
    """Registra una venta dentro de un grupo"""
    print("\n" + "="*60)
    print("📦 REGISTRAR VENTA EN GRUPO")
    print("="*60)
    
    # Mostrar grupos disponibles
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre_grupo, hotel, habitaciones_disponibles
        FROM grupos
        WHERE estado = 'ACTIVO' AND habitaciones_disponibles > 0
    """)
    
    grupos = cursor.fetchall()
    
    if not grupos:
        print("\n❌ No hay grupos con habitaciones disponibles.")
        conexion.close()
        return
    
    print("\n📦 GRUPOS DISPONIBLES:\n")
    for g in grupos:
        print(f"{g[0]}. {g[1]} - {g[2]} | Disponibles: {g[3]} hab")
    
    try:
        grupo_id = int(input("\nSelecciona ID del grupo: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    grupo = obtener_grupo_por_id(grupo_id)
    
    if not grupo:
        print("❌ Grupo no encontrado.")
        conexion.close()
        return
    
    if grupo['estado'] != 'ACTIVO':
        print("❌ El grupo no está activo.")
        conexion.close()
        return
    
    if grupo['habitaciones_disponibles'] <= 0:
        print("❌ No hay habitaciones disponibles.")
        conexion.close()
        return
    
    print(f"\n✅ Grupo: {grupo['nombre_grupo']} - {grupo['hotel']}")
    print(f"📅 {grupo['fecha_inicio']} al {grupo['fecha_fin']} ({grupo['noches']} noches)")
    print(f"\n💵 PRECIOS POR NOCHE:")
    print(f"   Doble: ${grupo['precio_noche_doble']:,.2f}")
    print(f"   Triple: ${grupo['precio_noche_triple']:,.2f}")
    print(f"   Cuádruple: ${grupo['precio_noche_cuadruple']:,.2f}")
    print(f"   Menor Doble: ${grupo['precio_menor_doble']:,.2f}")
    print(f"   Menor Triple: ${grupo['precio_menor_triple']:,.2f}")
    print(f"   Menor Cuádruple: ${grupo['precio_menor_cuadruple']:,.2f}")
    
    # ===== DATOS DEL CLIENTE =====
    print("\n--- DATOS DEL CLIENTE ---")
    cliente = input("Nombre del cliente: ").strip()
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
    
    # ===== TIPO DE HABITACIÓN =====
    print("\n--- TIPO DE HABITACIÓN ---")
    print("1. Doble (2 adultos + hasta 2 menores)")
    print("2. Triple (3 adultos + hasta 1 menor)")
    print("3. Cuádruple (4 adultos, sin menores)")
    
    try:
        tipo_hab = int(input("Tipo de habitación: "))
    except ValueError:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    if tipo_hab == 1:
        tipo_habitacion = "DOBLE"
        adultos = 2
        max_menores = 2
        precio_adulto = grupo['precio_noche_doble']
        precio_menor = grupo['precio_menor_doble']
    elif tipo_hab == 2:
        tipo_habitacion = "TRIPLE"
        adultos = 3
        max_menores = 1
        precio_adulto = grupo['precio_noche_triple']
        precio_menor = grupo['precio_menor_triple']
    elif tipo_hab == 3:
        tipo_habitacion = "CUÁDRUPLE"
        adultos = 4
        max_menores = 0
        precio_adulto = grupo['precio_noche_cuadruple']
        precio_menor = grupo['precio_menor_cuadruple']
    else:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    # Preguntar por menores
    try:
        menores = int(input(f"Número de menores (máximo {max_menores}): "))
    except ValueError:
        print("❌ Número inválido.")
        conexion.close()
        return
    
    if menores > max_menores:
        print(f"❌ Habitación {tipo_habitacion} solo acepta hasta {max_menores} menor(es).")
        conexion.close()
        return
    
    # ===== CALCULAR PRECIO =====
    noches = grupo['noches']
    total_adultos = adultos * precio_adulto * noches
    total_menores = menores * precio_menor * noches
    precio_total = total_adultos + total_menores
    
    print(f"\n--- RESUMEN ---")
    print(f"Habitación {tipo_habitacion}")
    print(f"{adultos} adultos x ${precio_adulto:,.2f} x {noches} noches = ${total_adultos:,.2f}")
    if menores > 0:
        print(f"{menores} menor(es) x ${precio_menor:,.2f} x {noches} noches = ${total_menores:,.2f}")
    print(f"TOTAL: ${precio_total:,.2f}")
    
    # ===== PORCENTAJE DE GANANCIA =====
    try:
        porcentaje_ganancia = float(input("\nPorcentaje de ganancia (%): "))
        ganancia = precio_total * (porcentaje_ganancia / 100)
        comision = ganancia * 0.10  # 10% de la ganancia para la vendedora
    except ValueError:
        print("❌ Porcentaje inválido.")
        conexion.close()
        return
    
    print(f"Ganancia: ${ganancia:,.2f}")
    print(f"Comisión vendedora: ${comision:,.2f}")
    
    # ===== ABONO INICIAL =====
    try:
        abono_inicial = float(input("\nAbono inicial: $"))
    except ValueError:
        print("❌ Monto inválido.")
        conexion.close()
        return
    
    if abono_inicial > precio_total:
        print(f"❌ El abono (${abono_inicial:,.2f}) es mayor al total (${precio_total:,.2f}).")
        conexion.close()
        return
    
    saldo = precio_total - abono_inicial
    
    # ===== GUARDAR VENTA =====
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Usar tabla ventas pero con campos adicionales para grupos
    cursor.execute("""
        INSERT INTO ventas (
            usuario_id, vendedora_id, cliente, destino, hotel,
            fecha_inicio, fecha_fin, noches, adultos, menores,
            tipo_habitacion, precio_total, pagado, saldo, ganancia,
            comision_vendedora, estado, operador, celular_responsable,
            es_grupo, grupo_id, es_bloqueo, tipo_venta, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 0, 'GRUPO', ?)
    """, (
        vendedora['id'], vendedora['id'], cliente, grupo['nombre_grupo'], grupo['hotel'],
        grupo['fecha_inicio'], grupo['fecha_fin'], noches, adultos, menores,
        tipo_habitacion, precio_total, abono_inicial, saldo, ganancia,
        comision, 'ADEUDO', grupo['operador'], celular_cliente,
        grupo_id, fecha_registro
    ))
    
    venta_id = cursor.lastrowid
    
    # Registrar abono inicial
    cursor.execute("""
        INSERT INTO abonos (venta_id, monto, fecha)
        VALUES (?, ?, ?)
    """, (venta_id, abono_inicial, fecha_registro))
    
    # ===== REGISTRAR PASAJEROS =====
    print("\n--- REGISTRO DE PASAJEROS ---")
    
    pasajeros = []
    
    print(f"\n👨‍👩‍👧‍👦 ADULTOS ({adultos}):")
    for i in range(adultos):
        nombre = input(f"Adulto {i+1}: ").strip()
        pasajeros.append({"nombre": nombre, "tipo": "ADULTO"})
    
    if menores > 0:
        print(f"\n👶 MENORES ({menores}):")
        for i in range(menores):
            nombre = input(f"Menor {i+1}: ").strip()
            pasajeros.append({"nombre": nombre, "tipo": "MENOR"})
    
    # Guardar pasajeros
    for pasajero in pasajeros:
        cursor.execute("""
            INSERT INTO pasajeros (venta_id, nombre, tipo)
            VALUES (?, ?, ?)
        """, (venta_id, pasajero["nombre"], pasajero["tipo"]))
    
    # Descontar habitación del grupo
    if not descontar_habitacion_grupo(grupo_id, 1):
        print("⚠️  Error al descontar habitación del grupo.")
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Venta registrada en el grupo correctamente (ID: {venta_id})")
    print(f"Saldo restante: ${saldo:,.2f}")


def ver_ventas_grupo():
    """Muestra todas las ventas de un grupo específico"""
    ver_grupos(solo_activos=True)
    
    try:
        grupo_id = int(input("\nSelecciona ID del grupo: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    grupo = obtener_grupo_por_id(grupo_id)
    
    if not grupo:
        print("❌ Grupo no encontrado.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT v.id, v.cliente, v.tipo_habitacion, v.adultos, v.menores,
               v.precio_total, v.pagado, v.saldo, v.estado, vd.nombre
        FROM ventas v
        JOIN vendedoras vd ON v.vendedora_id = vd.id
        WHERE v.grupo_id = ? AND v.es_grupo = 1
        ORDER BY v.fecha_registro
    """, (grupo_id,))
    
    ventas = cursor.fetchall()
    
    print("\n" + "="*60)
    print(f"📦 VENTAS DEL GRUPO: {grupo['nombre_grupo']}")
    print("="*60)
    
    if not ventas:
        print("\nNo hay ventas registradas en este grupo.")
        conexion.close()
        return
    
    total_vendido = 0
    total_cobrado = 0
    total_saldo = 0
    
    for v in ventas:
        estado_icon = "✅" if v[8] == "LIQUIDADO" else "⏳"
        
        print(f"\n{estado_icon} ID: {v[0]} | {v[1]}")
        print(f"   Habitación: {v[2]}")
        print(f"   Pasajeros: {v[3]} adultos + {v[4]} menores = {v[3] + v[4]} total")
        print(f"   Vendedora: {v[9]}")
        
        print(f"\n   💵 PAGOS:")
        print(f"      Total: ${v[5]:,.2f}")
        print(f"      Pagado: ${v[6]:,.2f}")
        print(f"      Saldo: ${v[7]:,.2f}")
        print(f"      Estado: {v[8]}")
        
        # Mostrar pasajeros
        cursor.execute("""
            SELECT nombre, tipo FROM pasajeros WHERE venta_id = ?
        """, (v[0],))
        pasajeros = cursor.fetchall()
        
        if pasajeros:
            print(f"\n   👥 PASAJEROS:")
            for p in pasajeros:
                print(f"      • {p[0]} ({p[1]})")
        
        print("-" * 60)
        
        total_vendido += v[5]
        total_cobrado += v[6]
        total_saldo += v[7]
    
    print(f"\n📊 TOTALES:")
    print(f"   Vendido: ${total_vendido:,.2f}")
    print(f"   Cobrado: ${total_cobrado:,.2f}")
    print(f"   Saldo: ${total_saldo:,.2f}")
    
    # Cálculo de ganancia del grupo
    ingreso_total = total_vendido
    costo_proporcional = (grupo['costo_real'] / grupo['habitaciones_totales']) * grupo['habitaciones_vendidas']
    ganancia_grupo = ingreso_total - costo_proporcional
    
    print(f"\n💰 ANÁLISIS DEL GRUPO:")
    print(f"   Habitaciones vendidas: {grupo['habitaciones_vendidas']}/{grupo['habitaciones_totales']}")
    print(f"   Ingreso total: ${ingreso_total:,.2f}")
    print(f"   Costo proporcional: ${costo_proporcional:,.2f}")
    print(f"   Ganancia del grupo: ${ganancia_grupo:,.2f}")
    
    conexion.close()


def menu_ventas_grupos():
    """Menú de ventas en grupos"""
    while True:
        print("\n" + "="*60)
        print("📦 VENTAS EN GRUPOS")
        print("="*60)
        print("\n1. Registrar venta en grupo")
        print("2. Ver ventas de un grupo")
        print("3. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            registrar_venta_grupo()
        elif opcion == "2":
            ver_ventas_grupo()
        elif opcion == "3":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_ventas_grupos()
