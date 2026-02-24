from database import conectar
from datetime import datetime


def reporte_viaje_riviera_detallado():
    """Reporte detallado de un viaje de Riviera Maya"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Mostrar viajes activos
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin,
               v.estado, vd.nombre, v.es_bloqueo
        FROM ventas v
        JOIN vendedoras vd ON v.vendedora_id = vd.id
        WHERE v.estado != 'CERRADO'
        ORDER BY v.fecha_inicio
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes activos.")
        conexion.close()
        return
    
    print("\n📋 VIAJES ACTIVOS:\n")
    for v in viajes:
        tipo = "📦 BLOQUEO" if v[7] == 1 else "🏖️ REGULAR"
        print(f"{v[0]}. {v[1]} - {v[2]} | {v[3]} al {v[4]} {tipo}")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener datos completos del viaje
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin,
               v.adultos, v.menores, v.tipo_habitacion,
               v.precio_total, v.pagado, v.saldo,
               v.ganancia, v.porcentaje_ganancia,
               v.comision_vendedora, v.comision_pagada, v.estado,
               vd.nombre, v.es_bloqueo, v.tipo_venta, v.noches,
               v.precio_adulto, v.precio_menor
        FROM ventas v
        JOIN vendedoras vd ON v.vendedora_id = vd.id
        WHERE v.id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    # Extraer datos
    vid, cliente, destino, fecha_inicio, fecha_fin = viaje[0:5]
    adultos, menores, tipo_hab = viaje[5:8]
    precio_total, pagado, saldo = viaje[8:11]
    ganancia, porcentaje, comision, comision_pagada, estado = viaje[11:16]
    vendedora, es_bloqueo, tipo_venta, noches = viaje[16:20]
    precio_adulto, precio_menor = viaje[20:22]
    
    total_personas = adultos + menores
    
    # MOSTRAR REPORTE
    print("\n" + "="*70)
    print(f"📊 REPORTE DETALLADO - VIAJE #{vid}")
    print("="*70)
    
    tipo_icon = "📦 BLOQUEO" if es_bloqueo == 1 else "🏖️ REGULAR"
    print(f"Tipo: {tipo_venta} {tipo_icon}")
    print(f"Cliente: {cliente}")
    print(f"Destino: {destino}")
    print(f"Fechas: {fecha_inicio} al {fecha_fin} ({noches} noches)")
    print(f"Vendedora: {vendedora}")
    
    # Calcular días restantes
    try:
        fecha_dt = datetime.strptime(fecha_inicio, "%d-%m-%Y")
        hoy = datetime.now()
        dias_restantes = (fecha_dt - hoy).days
        
        if dias_restantes > 0:
            print(f"⏰ Faltan {dias_restantes} días para el viaje")
        elif dias_restantes == 0:
            print(f"🎉 ¡El viaje es HOY!")
        else:
            print(f"✅ Viaje realizado hace {abs(dias_restantes)} días")
    except:
        pass
    
    print(f"\n👥 PASAJEROS:")
    print(f"   Total: {total_personas} personas")
    print(f"   Adultos: {adultos}")
    print(f"   Menores: {menores}")
    print(f"   Habitación: {tipo_hab}")
    
    # Obtener lista de pasajeros
    cursor.execute("""
        SELECT nombre, tipo
        FROM pasajeros
        WHERE venta_id = ?
        ORDER BY tipo DESC, nombre
    """, (viaje_id,))
    
    pasajeros = cursor.fetchall()
    
    if pasajeros:
        print(f"\n   📋 Lista de pasajeros:")
        for p in pasajeros:
            print(f"      • {p[0]} ({p[1]})")
    
    print(f"\n💰 FINANCIERO:")
    print(f"   Precio total: ${precio_total:,.2f}")
    print(f"   Abonado: ${pagado:,.2f}")
    print(f"   Saldo: ${saldo:,.2f}")
    porcentaje_pagado = (pagado / precio_total * 100) if precio_total > 0 else 0
    print(f"   % Pagado: {porcentaje_pagado:.1f}%")
    
    print(f"\n   Precio adulto: ${precio_adulto:,.2f}")
    print(f"   Precio menor: ${precio_menor:,.2f}")
    
    print(f"\n📈 GANANCIA:")
    print(f"   Ganancia agencia: ${ganancia:,.2f} ({porcentaje}%)")
    
    if comision > 0:
        estado_comision = "✅ PAGADA" if comision_pagada == 1 else "⏳ PENDIENTE"
        print(f"   Comisión vendedora: ${comision:,.2f} - {estado_comision}")
    
    print(f"\n📅 ESTADO: {estado}")
    
    # Historial de abonos
    cursor.execute("""
        SELECT fecha, monto
        FROM abonos
        WHERE venta_id = ?
        ORDER BY fecha
    """, (viaje_id,))
    
    abonos = cursor.fetchall()
    
    if abonos:
        print(f"\n💵 HISTORIAL DE ABONOS:")
        for abono in abonos:
            print(f"   • {abono[0]}: ${abono[1]:,.2f}")
    
    # Alertas
    print(f"\n⚠️  ALERTAS:")
    alertas = []
    
    if saldo > 20000:
        alertas.append(f"   • ⚠️  Saldo alto: ${saldo:,.2f}")
    
    if porcentaje_pagado < 50 and estado == "ACTIVO":
        alertas.append(f"   • ⚠️  Solo {porcentaje_pagado:.0f}% pagado")
    
    try:
        if 0 < dias_restantes <= 30:
            alertas.append(f"   • ⏰ Viaje en {dias_restantes} días")
    except:
        pass
    
    if estado == "LIQUIDADO" and comision_pagada == 0:
        alertas.append(f"   • 💰 Comisión pendiente de pago")
    
    if alertas:
        for alerta in alertas:
            print(alerta)
    else:
        print("   ✅ Sin alertas")
    
    print("\n" + "="*70)
    
    conexion.close()


def lista_pasajeros_riviera():
    """Lista de pasajeros para imprimir (hotel/aerolínea)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Seleccionar viaje
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin
        FROM ventas v
        WHERE v.estado != 'CERRADO'
        ORDER BY v.fecha_inicio
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes activos.")
        conexion.close()
        return
    
    print("\n📋 VIAJES ACTIVOS:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]} - {v[2]} ({v[3]} al {v[4]})")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener info del viaje
    cursor.execute("""
        SELECT v.cliente, v.destino, v.fecha_inicio, v.fecha_fin, v.adultos, v.menores
        FROM ventas v
        WHERE v.id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    # Obtener pasajeros
    cursor.execute("""
        SELECT nombre, tipo
        FROM pasajeros
        WHERE venta_id = ?
        ORDER BY tipo DESC, nombre
    """, (viaje_id,))
    
    pasajeros = cursor.fetchall()
    
    print("\n" + "="*70)
    print(f"✈️  LISTA DE PASAJEROS - RIVIERA MAYA")
    print("="*70)
    print(f"Cliente: {viaje[0]}")
    print(f"Destino: {viaje[1]}")
    print(f"Fechas: {viaje[2]} al {viaje[3]}")
    print(f"Total pasajeros: {viaje[4] + viaje[5]} ({viaje[4]} adultos, {viaje[5]} menores)")
    print("="*70)
    
    if not pasajeros:
        print("\n⚠️  No hay pasajeros registrados.")
    else:
        print(f"\n{'#':<4} {'NOMBRE COMPLETO':<40} {'TIPO':<10}")
        print("-"*70)
        
        for i, p in enumerate(pasajeros, 1):
            print(f"{i:<4} {p[0]:<40} {p[1]:<10}")
    
    print("\n" + "="*70)
    
    conexion.close()


def reporte_bloqueos():
    """Reporte de rentabilidad y disponibilidad de bloqueos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*70)
    print("📦 REPORTE DE BLOQUEOS")
    print("="*70)
    
    # Obtener todos los bloqueos
    cursor.execute("""
        SELECT id, hotel, fecha_inicio, fecha_fin, noches,
               habitaciones_totales, habitaciones_vendidas, habitaciones_disponibles,
               precio_noche_doble, costo_real, estado
        FROM bloqueos
        ORDER BY estado, fecha_inicio
    """)
    
    bloqueos = cursor.fetchall()
    
    if not bloqueos:
        print("\nNo hay bloqueos registrados.")
        conexion.close()
        return
    
    # Separar por estado
    activos = [b for b in bloqueos if b[10] == 'ACTIVO']
    agotados = [b for b in bloqueos if b[10] == 'AGOTADO']
    
    print(f"\n📊 RESUMEN GENERAL:")
    print(f"   Total bloqueos: {len(bloqueos)}")
    print(f"   Activos: {len(activos)}")
    print(f"   Agotados: {len(agotados)}")
    
    total_hab = sum(b[5] for b in bloqueos)
    total_vendidas = sum(b[6] for b in bloqueos)
    
    print(f"   Habitaciones totales: {total_hab}")
    print(f"   Habitaciones vendidas: {total_vendidas}")
    print(f"   Disponibles: {total_hab - total_vendidas}")
    
    if total_hab > 0:
        print(f"   % Vendido: {(total_vendidas/total_hab*100):.1f}%")
    
    # BLOQUEOS ACTIVOS
    if activos:
        print(f"\n🟢 BLOQUEOS ACTIVOS:")
        print("-"*70)
        
        for b in activos:
            ocupacion = (b[6]/b[5]*100) if b[5] > 0 else 0
            
            # Calcular ganancia estimada
            precio_venta_estimado = b[8]  # precio_noche_doble
            costo_real = b[9]
            ganancia_por_hab = (precio_venta_estimado * b[4]) - costo_real if costo_real else 0
            ganancia_total = ganancia_por_hab * b[6]
            
            print(f"\n📦 {b[1]}")
            print(f"   Fechas: {b[2]} al {b[3]} ({b[4]} noches)")
            print(f"   Disponibles: {b[7]} / {b[5]} habitaciones")
            print(f"   Vendidas: {b[6]} ({ocupacion:.0f}%)")
            print(f"   Costo real: ${costo_real:,.2f}")
            
            if ganancia_total > 0:
                print(f"   💰 Ganancia generada: ${ganancia_total:,.2f}")
    
    # BLOQUEOS AGOTADOS
    if agotados:
        print(f"\n🔴 BLOQUEOS AGOTADOS:")
        print("-"*70)
        
        for b in agotados:
            print(f"\n📦 {b[1]}")
            print(f"   Fechas: {b[2]} al {b[3]}")
            print(f"   Vendidas: {b[6]}/{b[5]} habitaciones (100%)")
    
    # Obtener ventas de bloqueos
    cursor.execute("""
        SELECT COUNT(*), SUM(precio_total), SUM(ganancia)
        FROM ventas
        WHERE es_bloqueo = 1
    """)
    
    ventas_bloqueo = cursor.fetchone()
    
    if ventas_bloqueo[0]:
        print(f"\n💵 VENTAS DE BLOQUEOS:")
        print(f"   Total ventas: {ventas_bloqueo[0]}")
        print(f"   Ingreso total: ${ventas_bloqueo[1]:,.2f}")
        print(f"   Ganancia total: ${ventas_bloqueo[2]:,.2f}")
    
    print("\n" + "="*70)
    
    conexion.close()


def viajes_proximos():
    """Muestra viajes en los próximos 30 días con alertas"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*70)
    print("📅 VIAJES PRÓXIMOS (30 DÍAS)")
    print("="*70)
    
    cursor.execute("""
        SELECT v.id, v.cliente, v.destino, v.fecha_inicio, v.fecha_fin,
               v.saldo, v.estado, vd.nombre, v.adultos, v.menores
        FROM ventas v
        JOIN vendedoras vd ON v.vendedora_id = vd.id
        WHERE v.estado != 'CERRADO'
        ORDER BY v.fecha_inicio
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\nNo hay viajes activos.")
        conexion.close()
        return
    
    hoy = datetime.now()
    viajes_proximos = []
    
    for v in viajes:
        try:
            fecha_viaje = datetime.strptime(v[3], "%d-%m-%Y")
            dias_restantes = (fecha_viaje - hoy).days
            
            if 0 <= dias_restantes <= 30:
                viajes_proximos.append((v, dias_restantes))
        except:
            continue
    
    if not viajes_proximos:
        print("\n✅ No hay viajes en los próximos 30 días.")
        conexion.close()
        return
    
    # Ordenar por días restantes
    viajes_proximos.sort(key=lambda x: x[1])
    
    for viaje, dias in viajes_proximos:
        alerta_icon = "🔴" if dias <= 7 else "🟡" if dias <= 15 else "🟢"
        
        print(f"\n{alerta_icon} VIAJE #{viaje[0]} - En {dias} días")
        print(f"   Cliente: {viaje[1]}")
        print(f"   Destino: {viaje[2]}")
        print(f"   Salida: {viaje[3]}")
        print(f"   Vendedora: {viaje[7]}")
        print(f"   Pasajeros: {viaje[8] + viaje[9]} personas")
        print(f"   Saldo: ${viaje[5]:,.2f}")
        
        if viaje[5] > 0:
            print(f"   ⚠️  Tiene saldo pendiente")
        
        # Verificar si tiene pasajeros registrados
        cursor.execute("""
            SELECT COUNT(*) FROM pasajeros WHERE venta_id = ?
        """, (viaje[0],))
        
        num_pasajeros = cursor.fetchone()[0]
        
        if num_pasajeros == 0:
            print(f"   ⚠️  Sin pasajeros registrados")
        
        print("-"*70)
    
    conexion.close()


def comparativa_por_hotel():
    """Compara ventas por hotel a lo largo del tiempo"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener hoteles con múltiples ventas
    cursor.execute("""
        SELECT destino, COUNT(*) as cantidad
        FROM ventas
        GROUP BY destino
        HAVING cantidad > 1
        ORDER BY cantidad DESC
        LIMIT 10
    """)
    
    hoteles = cursor.fetchall()
    
    if not hoteles:
        print("\n❌ No hay suficientes datos para comparar.")
        conexion.close()
        return
    
    print("\n📊 HOTELES CON MÚLTIPLES VENTAS:\n")
    for i, h in enumerate(hoteles, 1):
        print(f"{i}. {h[0]} ({h[1]} viajes)")
    
    try:
        opcion = int(input("\nSelecciona hotel: "))
        hotel_elegido = hoteles[opcion-1][0]
    except:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    # Obtener ventas de ese hotel
    cursor.execute("""
        SELECT v.id, v.cliente, v.fecha_inicio, v.fecha_fin,
               v.precio_total, v.ganancia, v.estado,
               vd.nombre, v.adultos, v.menores
        FROM ventas v
        JOIN vendedoras vd ON v.vendedora_id = vd.id
        WHERE v.destino = ?
        ORDER BY v.fecha_inicio DESC
    """, (hotel_elegido,))
    
    ventas = cursor.fetchall()
    
    print("\n" + "="*70)
    print(f"📊 COMPARATIVA: {hotel_elegido}")
    print("="*70)
    
    total_ingresos = 0
    total_ganancia = 0
    total_personas = 0
    
    for v in ventas:
        personas = v[8] + v[9]
        total_personas += personas
        total_ingresos += v[4]
        total_ganancia += v[5]
        
        print(f"\n🎫 Viaje #{v[0]} - {v[1]}")
        print(f"   Fechas: {v[2]} al {v[3]}")
        print(f"   Vendedora: {v[7]}")
        print(f"   Pasajeros: {personas}")
        print(f"   Ingreso: ${v[4]:,.2f}")
        print(f"   Ganancia: ${v[5]:,.2f}")
        print(f"   Estado: {v[6]}")
        print("-"*70)
    
    print(f"\n📈 TOTALES:")
    print(f"   Viajes: {len(ventas)}")
    print(f"   Personas: {total_personas}")
    print(f"   Ingreso total: ${total_ingresos:,.2f}")
    print(f"   Ganancia total: ${total_ganancia:,.2f}")
    
    if len(ventas) > 0:
        print(f"   Promedio por viaje: ${total_ingresos/len(ventas):,.2f}")
        print(f"   Promedio por persona: ${total_ingresos/total_personas:,.2f}")
    
    print("\n" + "="*70)
    
    conexion.close()
