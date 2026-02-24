from database import conectar
from datetime import datetime


def reporte_viaje_detallado():
    """Reporte detallado de un viaje nacional específico"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Mostrar viajes activos
    cursor.execute("""
        SELECT id, nombre_viaje, destino, fecha_salida, fecha_regreso
        FROM viajes_nacionales
        WHERE estado = 'ACTIVO'
        ORDER BY fecha_salida
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
    
    # Obtener datos del viaje
    cursor.execute("""
        SELECT nombre_viaje, destino, fecha_salida, fecha_regreso, dias, noches,
               cupos_totales, cupos_vendidos, cupos_disponibles,
               precio_persona_doble, precio_persona_triple
        FROM viajes_nacionales
        WHERE id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    nombre_viaje, destino, fecha_salida, fecha_regreso, dias, noches = viaje[0:6]
    cupos_totales, cupos_vendidos, cupos_disponibles = viaje[6:9]
    precio_doble, precio_triple = viaje[9:11]
    
    # Calcular datos financieros
    cursor.execute("""
        SELECT 
            SUM(total_pagar) as ingreso_total,
            SUM(total_abonado) as cobrado,
            SUM(saldo) as por_cobrar
        FROM clientes_nacionales
        WHERE viaje_id = ?
    """, (viaje_id,))
    
    financiero = cursor.fetchone()
    ingreso_total = financiero[0] or 0
    cobrado = financiero[1] or 0
    por_cobrar = financiero[2] or 0
    porcentaje_cobrado = (cobrado / ingreso_total * 100) if ingreso_total > 0 else 0
    
    # MOSTRAR REPORTE
    print("\n" + "="*70)
    print(f"📊 REPORTE DETALLADO: {nombre_viaje}")
    print("="*70)
    print(f"📍 Destino: {destino}")
    print(f"📅 Fechas: {fecha_salida} al {fecha_regreso} ({dias} días / {noches} noches)")
    
    # Calcular días restantes
    try:
        fecha_salida_dt = datetime.strptime(fecha_salida, "%d-%m-%Y")
        hoy = datetime.now()
        dias_restantes = (fecha_salida_dt - hoy).days
        
        if dias_restantes > 0:
            print(f"⏰ Faltan {dias_restantes} días para el viaje")
        elif dias_restantes == 0:
            print(f"🎉 ¡El viaje es HOY!")
        else:
            print(f"✅ Viaje realizado hace {abs(dias_restantes)} días")
    except:
        pass
    
    print(f"\n📍 OCUPACIÓN:")
    print(f"   Vendidos: {cupos_vendidos} / {cupos_totales} personas")
    print(f"   Disponibles: {cupos_disponibles} cupos")
    porcentaje_ocupacion = (cupos_vendidos / cupos_totales * 100) if cupos_totales > 0 else 0
    print(f"   Ocupación: {porcentaje_ocupacion:.1f}%")
    
    print(f"\n💰 FINANCIERO:")
    print(f"   Ingreso total: ${ingreso_total:,.2f}")
    print(f"   Cobrado: ${cobrado:,.2f}")
    print(f"   Por cobrar: ${por_cobrar:,.2f}")
    print(f"   % Cobrado: {porcentaje_cobrado:.1f}%")
    
    print(f"\n💵 PRECIOS:")
    print(f"   Base doble: ${precio_doble:,.2f} por persona")
    print(f"   Base triple: ${precio_triple:,.2f} por persona")
    
    # CLIENTES Y PASAJEROS
    cursor.execute("""
        SELECT c.id, c.nombre_cliente, v.nombre AS vendedora,
               c.adultos, c.menores, c.total_pagar, c.total_abonado, c.saldo,
               c.habitaciones_doble, c.habitaciones_triple, c.estado
        FROM clientes_nacionales c
        JOIN vendedoras v ON c.vendedora_id = v.id
        WHERE c.viaje_id = ?
        ORDER BY c.fecha_registro
    """, (viaje_id,))
    
    clientes = cursor.fetchall()
    
    if clientes:
        print(f"\n👥 PASAJEROS ({cupos_vendidos}):")
        print("="*70)
        
        for cliente in clientes:
            cliente_id, nombre_cliente, vendedora, adultos, menores = cliente[0:5]
            total_pagar, total_abonado, saldo = cliente[5:8]
            hab_dobles, hab_triples, estado = cliente[8:11]
            
            estado_icon = "✅" if estado == "LIQUIDADO" else "⏳"
            
            print(f"\n┌─ CLIENTE: {nombre_cliente} {estado_icon} ─────────────────")
            print(f"│ Vendedora: {vendedora}")
            print(f"│ {adultos} adultos, {menores} menores | Total: ${total_pagar:,.2f}")
            print(f"│ Abonado: ${total_abonado:,.2f} | Saldo: ${saldo:,.2f}")
            
            # Obtener pasajeros
            cursor.execute("""
                SELECT nombre_completo, tipo, habitacion_asignada
                FROM pasajeros_nacionales
                WHERE cliente_id = ?
                ORDER BY habitacion_asignada, tipo DESC
            """, (cliente_id,))
            
            pasajeros = cursor.fetchall()
            
            if pasajeros:
                print(f"│")
                # Agrupar por habitación
                habitaciones = {}
                for p in pasajeros:
                    hab = p[2]
                    if hab not in habitaciones:
                        habitaciones[hab] = []
                    habitaciones[hab].append(f"{p[0]} ({p[1]})")
                
                for hab, nombres in habitaciones.items():
                    print(f"│ 🏨 HABITACIÓN {hab.upper()}:")
                    for nombre in nombres:
                        print(f"│    • {nombre}")
            
            # Historial de abonos
            cursor.execute("""
                SELECT a.fecha, a.monto, v.nombre
                FROM abonos_nacionales a
                JOIN vendedoras v ON a.vendedora_id = v.id
                WHERE a.cliente_id = ?
                ORDER BY a.fecha
            """, (cliente_id,))
            
            abonos = cursor.fetchall()
            
            if abonos:
                print(f"│")
                print(f"│ 📅 Abonos:")
                for abono in abonos:
                    print(f"│    • {abono[0]}: ${abono[1]:,.2f} (por {abono[2]})")
            
            print(f"└{'─'*68}")
        
        # RESUMEN POR VENDEDORA
        cursor.execute("""
            SELECT v.nombre,
                   SUM(c.adultos + c.menores) as personas,
                   SUM(c.total_pagar) as total_vendido,
                   SUM(c.saldo) as saldo_pendiente
            FROM clientes_nacionales c
            JOIN vendedoras v ON c.vendedora_id = v.id
            WHERE c.viaje_id = ?
            GROUP BY v.nombre
            ORDER BY personas DESC
        """, (viaje_id,))
        
        resumen_vendedoras = cursor.fetchall()
        
        if resumen_vendedoras:
            print(f"\n📈 RESUMEN POR VENDEDORA:")
            print("-"*70)
            for rv in resumen_vendedoras:
                print(f"   {rv[0]}: {rv[1]} personas | ${rv[2]:,.2f} | Saldo: ${rv[3]:,.2f}")
    
    # ALERTAS
    print(f"\n⚠️  ALERTAS:")
    
    alertas = []
    
    # Clientes con saldo alto
    cursor.execute("""
        SELECT COUNT(*) FROM clientes_nacionales
        WHERE viaje_id = ? AND saldo > 20000
    """, (viaje_id,))
    
    clientes_saldo_alto = cursor.fetchone()[0]
    if clientes_saldo_alto > 0:
        alertas.append(f"   • {clientes_saldo_alto} cliente(s) con saldo > $20,000")
    
    # Cupos disponibles
    if cupos_disponibles > 0:
        alertas.append(f"   • Faltan {cupos_disponibles} cupos por vender")
    
    # Fecha próxima
    try:
        if 0 < dias_restantes <= 30:
            alertas.append(f"   • ⚠️  Viaje en {dias_restantes} días")
    except:
        pass
    
    # % Cobrado bajo
    if porcentaje_cobrado < 70 and cupos_vendidos > 0:
        alertas.append(f"   • ⚠️  Solo {porcentaje_cobrado:.1f}% cobrado")
    
    if alertas:
        for alerta in alertas:
            print(alerta)
    else:
        print("   ✅ Sin alertas")
    
    print("\n" + "="*70)
    
    conexion.close()


def reporte_general_nacionales():
    """Reporte general de todos los viajes nacionales"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*70)
    print("📊 REPORTE GENERAL - VIAJES NACIONALES")
    print("="*70)
    
    # Viajes activos
    cursor.execute("""
        SELECT COUNT(*), SUM(cupos_totales), SUM(cupos_vendidos), SUM(cupos_disponibles)
        FROM viajes_nacionales
        WHERE estado = 'ACTIVO'
    """)
    
    activos = cursor.fetchone()
    num_viajes = activos[0] or 0
    total_cupos = activos[1] or 0
    vendidos = activos[2] or 0
    disponibles = activos[3] or 0
    
    print(f"\n📍 VIAJES ACTIVOS: {num_viajes}")
    
    if num_viajes > 0:
        print(f"   Total cupos: {total_cupos}")
        print(f"   Vendidos: {vendidos}")
        print(f"   Disponibles: {disponibles}")
        print(f"   Ocupación: {(vendidos/total_cupos*100):.1f}%")
        
        # Financiero
        cursor.execute("""
            SELECT 
                SUM(c.total_pagar) as ingreso_total,
                SUM(c.total_abonado) as cobrado,
                SUM(c.saldo) as por_cobrar
            FROM clientes_nacionales c
            JOIN viajes_nacionales v ON c.viaje_id = v.id
            WHERE v.estado = 'ACTIVO'
        """)
        
        financiero = cursor.fetchone()
        ingreso = financiero[0] or 0
        cobrado = financiero[1] or 0
        por_cobrar = financiero[2] or 0
        
        print(f"\n💰 FINANCIERO:")
        print(f"   Ingreso total: ${ingreso:,.2f}")
        print(f"   Cobrado: ${cobrado:,.2f}")
        print(f"   Por cobrar: ${por_cobrar:,.2f}")
        
        if ingreso > 0:
            print(f"   % Cobrado: {(cobrado/ingreso*100):.1f}%")
        
        # Listar viajes
        cursor.execute("""
            SELECT v.id, v.nombre_viaje, v.destino, v.fecha_salida,
                   v.cupos_vendidos, v.cupos_totales,
                   COUNT(c.id) as num_clientes
            FROM viajes_nacionales v
            LEFT JOIN clientes_nacionales c ON v.id = c.viaje_id
            WHERE v.estado = 'ACTIVO'
            GROUP BY v.id
            ORDER BY v.fecha_salida
        """)
        
        viajes = cursor.fetchall()
        
        print(f"\n📋 DETALLE DE VIAJES:")
        print("-"*70)
        
        for v in viajes:
            ocupacion = (v[4]/v[5]*100) if v[5] > 0 else 0
            print(f"\n{v[0]}. {v[1]} - {v[2]}")
            print(f"   Salida: {v[3]}")
            print(f"   Ocupación: {v[4]}/{v[5]} ({ocupacion:.0f}%)")
            print(f"   Clientes: {v[6]}")
    else:
        print("   No hay viajes activos.")
    
    print("\n" + "="*70)
    
    conexion.close()


def lista_pasajeros_imprimir():
    """Genera lista de pasajeros para imprimir (aerolínea/hotel)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Seleccionar viaje
    cursor.execute("""
        SELECT id, nombre_viaje, destino
        FROM viajes_nacionales
        WHERE estado = 'ACTIVO'
        ORDER BY fecha_salida
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes activos.")
        conexion.close()
        return
    
    print("\n📋 VIAJES ACTIVOS:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]} - {v[2]}")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener info del viaje
    cursor.execute("""
        SELECT nombre_viaje, destino, fecha_salida, fecha_regreso
        FROM viajes_nacionales
        WHERE id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    # Obtener todos los pasajeros
    cursor.execute("""
        SELECT p.nombre_completo, p.tipo, p.habitacion_asignada, c.nombre_cliente
        FROM pasajeros_nacionales p
        JOIN clientes_nacionales c ON p.cliente_id = c.id
        WHERE c.viaje_id = ?
        ORDER BY p.habitacion_asignada, p.nombre_completo
    """, (viaje_id,))
    
    pasajeros = cursor.fetchall()
    
    print("\n" + "="*70)
    print(f"✈️  LISTA DE PASAJEROS")
    print(f"Viaje: {viaje[0]}")
    print(f"Destino: {viaje[1]}")
    print(f"Fechas: {viaje[2]} al {viaje[3]}")
    print("="*70)
    
    if not pasajeros:
        print("\nNo hay pasajeros registrados.")
    else:
        print(f"\nTotal de pasajeros: {len(pasajeros)}\n")
        
        print(f"{'#':<4} {'NOMBRE COMPLETO':<35} {'TIPO':<8} {'HABITACIÓN':<15}")
        print("-"*70)
        
        for i, p in enumerate(pasajeros, 1):
            print(f"{i:<4} {p[0]:<35} {p[1]:<8} {p[2]:<15}")
        
        # Agrupar por habitación
        print("\n" + "="*70)
        print("🏨 DISTRIBUCIÓN POR HABITACIONES")
        print("="*70 + "\n")
        
        habitaciones = {}
        for p in pasajeros:
            hab = p[2]
            if hab not in habitaciones:
                habitaciones[hab] = []
            habitaciones[hab].append(f"{p[0]} ({p[1]})")
        
        for hab in sorted(habitaciones.keys()):
            print(f"HABITACIÓN {hab.upper()}:")
            for nombre in habitaciones[hab]:
                print(f"  • {nombre}")
            print()
    
    print("="*70)
    
    conexion.close()


def comparativa_viajes():
    """Compara viajes al mismo destino"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener destinos con múltiples viajes
    cursor.execute("""
        SELECT destino, COUNT(*) as cantidad
        FROM viajes_nacionales
        GROUP BY destino
        HAVING cantidad > 1
        ORDER BY cantidad DESC
    """)
    
    destinos = cursor.fetchall()
    
    if not destinos:
        print("\n❌ No hay suficientes viajes para comparar.")
        conexion.close()
        return
    
    print("\n📊 DESTINOS CON MÚLTIPLES VIAJES:\n")
    for i, d in enumerate(destinos, 1):
        print(f"{i}. {d[0]} ({d[1]} viajes)")
    
    try:
        opcion = int(input("\nSelecciona destino: "))
        destino_elegido = destinos[opcion-1][0]
    except:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    # Obtener viajes de ese destino
    cursor.execute("""
        SELECT v.id, v.nombre_viaje, v.fecha_salida, v.fecha_regreso,
               v.cupos_totales, v.cupos_vendidos,
               v.precio_persona_doble, v.precio_persona_triple,
               SUM(c.total_pagar) as ingreso_total
        FROM viajes_nacionales v
        LEFT JOIN clientes_nacionales c ON v.id = c.viaje_id
        WHERE v.destino = ?
        GROUP BY v.id
        ORDER BY v.fecha_salida DESC
    """, (destino_elegido,))
    
    viajes = cursor.fetchall()
    
    print("\n" + "="*70)
    print(f"📊 COMPARATIVA: {destino_elegido}")
    print("="*70)
    
    for v in viajes:
        ocupacion = (v[5]/v[4]*100) if v[4] > 0 else 0
        ingreso = v[8] or 0
        
        print(f"\n🎫 {v[1]}")
        print(f"   Fechas: {v[2]} al {v[3]}")
        print(f"   Ocupación: {v[5]}/{v[4]} ({ocupacion:.0f}%)")
        print(f"   Precio doble: ${v[6]:,.2f}")
        print(f"   Precio triple: ${v[7]:,.2f}")
        print(f"   Ingreso total: ${ingreso:,.2f}")
        print("-"*70)
    
    conexion.close()
