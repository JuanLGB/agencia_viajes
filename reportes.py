from database import conectar


def ver_historial(usuario_actual):
    """Muestra el historial de ventas cerradas"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n📚 HISTORIAL DE VENTAS\n")
    
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT v.id, v.cliente, v.destino, vd.nombre, v.comision_vendedora, v.precio_total
            FROM ventas v
            JOIN vendedoras vd ON v.vendedora_id = vd.id
            WHERE v.estado = 'CERRADO' AND v.usuario_id = ?
            ORDER BY v.id DESC
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT v.id, v.cliente, v.destino, vd.nombre, v.comision_vendedora, v.precio_total
            FROM ventas v
            JOIN vendedoras vd ON v.vendedora_id = vd.id
            WHERE v.estado = 'CERRADO'
            ORDER BY v.id DESC
        """)
    
    ventas = cursor.fetchall()
    conexion.close()
    
    if not ventas:
        print("El historial está vacío.")
        return
    
    for venta in ventas:
        print(f"ID: {venta[0]}")
        print(f"Cliente: {venta[1]}")
        print(f"Destino: {venta[2]}")
        print(f"Vendedora: {venta[3]}")
        print(f"Precio total: ${venta[5]:.2f}")
        print(f"Comisión pagada: ${venta[4]:.2f}")
        print("-" * 40)


def reporte_general(usuario_actual):
    """Genera un reporte general de ventas mejorado"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*70)
    print("📊 REPORTE GENERAL - RIVIERA MAYA")
    print("="*70)
    
    if usuario_actual["rol"] == "VENDEDORA":
        print(f"Vendedora: {usuario_actual['nombre']}")
        filtro_usuario = f"WHERE usuario_id = {usuario_actual['id_vendedora']}"
    else:
        filtro_usuario = ""
    
    # ===== VIAJES ACTIVOS =====
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ventas,
                SUM(precio_total) as total_vendido,
                SUM(pagado) as total_cobrado,
                SUM(saldo) as total_pendiente,
                SUM(ganancia) as ganancia_total,
                SUM(adultos + menores) as total_personas
            FROM ventas
            WHERE usuario_id = ? AND estado != 'CERRADO'
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ventas,
                SUM(precio_total) as total_vendido,
                SUM(pagado) as total_cobrado,
                SUM(saldo) as total_pendiente,
                SUM(ganancia) as ganancia_total,
                SUM(adultos + menores) as total_personas
            FROM ventas
            WHERE estado != 'CERRADO'
        """)
    
    activos = cursor.fetchone()
    
    total_ventas = activos[0] or 0
    total_vendido = activos[1] or 0
    total_cobrado = activos[2] or 0
    total_pendiente = activos[3] or 0
    ganancia_total = activos[4] or 0
    total_personas = activos[5] or 0
    
    # INICIALIZAR porcentaje_cobrado AQUÍ (FIX DEL ERROR)
    porcentaje_cobrado = (total_cobrado / total_vendido * 100) if total_vendido > 0 else 0
    
    print(f"\n🖋️  VIAJES ACTIVOS: {total_ventas}")
    
    if total_ventas > 0:
        print(f"   Pasajeros: {total_personas}")
        print(f"   Promedio por viaje: {total_personas/total_ventas:.1f} personas")
        
        print(f"\n💰 FINANCIERO:")
        print(f"   Total vendido: ${total_vendido:,.2f}")
        print(f"   Cobrado: ${total_cobrado:,.2f}")
        print(f"   Pendiente: ${total_pendiente:,.2f}")
        print(f"   % Cobrado: {porcentaje_cobrado:.1f}%")
        
        print(f"\n📈 GANANCIA:")
        print(f"   Ganancia total: ${ganancia_total:,.2f}")
        
        if total_vendido > 0:
            margen = (ganancia_total / total_vendido * 100)
            print(f"   Margen promedio: {margen:.1f}%")
        
        # Desglose por tipo
        if usuario_actual["rol"] == "VENDEDORA":
            cursor.execute("""
                SELECT 
                    COUNT(*) as cantidad,
                    SUM(precio_total) as total,
                    tipo_venta
                FROM ventas
                WHERE usuario_id = ? AND estado != 'CERRADO'
                GROUP BY tipo_venta
            """, (usuario_actual["id_vendedora"],))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as cantidad,
                    SUM(precio_total) as total,
                    tipo_venta
                FROM ventas
                WHERE estado != 'CERRADO'
                GROUP BY tipo_venta
            """)
        
        desglose = cursor.fetchall()
        
        if desglose:
            print(f"\n📋 DESGLOSE POR TIPO:")
            for d in desglose:
                tipo = "📦 Bloqueos" if d[2] == "Bloqueo" else "🖋️ Generales"
                print(f"   {tipo}: {d[0]} viajes | ${d[1]:,.2f}")
        
        # Estados
        if usuario_actual["rol"] == "VENDEDORA":
            cursor.execute("""
                SELECT estado, COUNT(*), SUM(saldo)
                FROM ventas
                WHERE usuario_id = ? AND estado != 'CERRADO'
                GROUP BY estado
            """, (usuario_actual["id_vendedora"],))
        else:
            cursor.execute("""
                SELECT estado, COUNT(*), SUM(saldo)
                FROM ventas
                WHERE estado != 'CERRADO'
                GROUP BY estado
            """)
        
        estados = cursor.fetchall()
        
        if estados:
            print(f"\n📊 ESTADOS:")
            for e in estados:
                saldo_estado = e[2] or 0
                print(f"   {e[0]}: {e[1]} viajes | Saldo: ${saldo_estado:,.2f}")
    else:
        print("   No hay viajes activos.")
    
    # ===== COMISIONES =====
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT 
                SUM(comision_vendedora) as comisiones_pagadas,
                COUNT(*) as viajes_cerrados
            FROM ventas
            WHERE usuario_id = ? AND estado = 'CERRADO'
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT 
                SUM(comision_vendedora) as comisiones_pagadas,
                COUNT(*) as viajes_cerrados
            FROM ventas
            WHERE estado = 'CERRADO'
        """)
    
    cerrados_data = cursor.fetchone()
    comisiones_pagadas = cerrados_data[0] or 0
    viajes_cerrados = cerrados_data[1] or 0
    
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT 
                SUM(comision_vendedora) as comisiones_pendientes
            FROM ventas
            WHERE usuario_id = ? AND estado = 'LIQUIDADO'
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT 
                SUM(comision_vendedora) as comisiones_pendientes
            FROM ventas
            WHERE estado = 'LIQUIDADO'
        """)
    
    comisiones_pendientes = cursor.fetchone()[0] or 0
    
    print(f"\n💵 COMISIONES:")
    print(f"   ✅ Pagadas: ${comisiones_pagadas:,.2f} ({viajes_cerrados} viajes)")
    print(f"   ⏳ Pendientes: ${comisiones_pendientes:,.2f}")
    print(f"   Total: ${comisiones_pagadas + comisiones_pendientes:,.2f}")
    
    # ===== BLOQUEOS (solo ADMIN) =====
    if usuario_actual["rol"] == "ADMIN":
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(habitaciones_totales) as hab_totales,
                SUM(habitaciones_vendidas) as hab_vendidas,
                SUM(habitaciones_disponibles) as hab_disponibles
            FROM bloqueos
            WHERE estado = 'ACTIVO'
        """)
        
        bloqueos = cursor.fetchone()
        
        if bloqueos[0]:
            ocupacion = (bloqueos[2] / bloqueos[1] * 100) if bloqueos[1] > 0 else 0
            
            print(f"\n📦 BLOQUEOS:")
            print(f"   Activos: {bloqueos[0]}")
            print(f"   Habitaciones vendidas: {bloqueos[2]} / {bloqueos[1]}")
            print(f"   Disponibles: {bloqueos[3]}")
            print(f"   Ocupación: {ocupacion:.1f}%")
    
    # ===== ALERTAS =====
    print(f"\n⚠️  ALERTAS:")
    
    alertas = []
    
    # Viajes con saldo alto
    if usuario_actual["rol"] == "VENDEDORA":
        cursor.execute("""
            SELECT COUNT(*) FROM ventas
            WHERE usuario_id = ? AND saldo > 20000 AND estado != 'CERRADO'
        """, (usuario_actual["id_vendedora"],))
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM ventas
            WHERE saldo > 20000 AND estado != 'CERRADO'
        """)
    
    viajes_saldo_alto = cursor.fetchone()[0]
    if viajes_saldo_alto > 0:
        alertas.append(f"   • {viajes_saldo_alto} viaje(s) con saldo > $20,000")
    
    # Comisiones pendientes
    if comisiones_pendientes > 0:
        alertas.append(f"   • Comisiones pendientes por pagar")
    
    # % Cobrado bajo - AHORA porcentaje_cobrado ESTÁ INICIALIZADO
    if porcentaje_cobrado < 70 and total_ventas > 0:
        alertas.append(f"   • ⚠️  Solo {porcentaje_cobrado:.0f}% cobrado del total")
    
    if alertas:
        for alerta in alertas:
            print(alerta)
    else:
        print("   ✅ Sin alertas")
    
    print("\n" + "="*70)
    
    conexion.close()


def reporte_por_vendedora():
    """Reporte detallado por vendedora (solo ADMIN)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT 
            vd.id,
            vd.nombre,
            COUNT(v.id) as total_ventas,
            SUM(v.precio_total) as total_vendido,
            SUM(v.ganancia) as ganancia_generada,
            SUM(CASE WHEN v.estado = 'CERRADO' THEN v.comision_vendedora ELSE 0 END) as comisiones_pagadas,
            SUM(CASE WHEN v.estado = 'LIQUIDADO' THEN v.comision_vendedora ELSE 0 END) as comisiones_pendientes
        FROM vendedoras vd
        LEFT JOIN ventas v ON vd.id = v.vendedora_id
        WHERE vd.activa = 1
        GROUP BY vd.id, vd.nombre
        ORDER BY total_vendido DESC
    """)
    
    resultados = cursor.fetchall()
    
    print("\n📊 REPORTE POR VENDEDORA\n")
    
    if not resultados:
        print("No hay datos para mostrar.")
        conexion.close()
        return
    
    for r in resultados:
        vendedora_id, nombre, total_ventas, total_vendido, ganancia, com_pagadas, com_pendientes = r
        
        # Manejar valores NULL
        total_ventas = total_ventas or 0
        total_vendido = total_vendido or 0
        ganancia = ganancia or 0
        com_pagadas = com_pagadas or 0
        com_pendientes = com_pendientes or 0
        
        print(f"👩‍💼 {nombre} (ID: {vendedora_id})")
        print(f"   Ventas: {total_ventas}")
        print(f"   Total vendido: ${total_vendido:,.2f}")
        print(f"   Ganancia generada: ${ganancia:,.2f}")
        print(f"   ✅ Comisiones pagadas: ${com_pagadas:,.2f}")
        print(f"   ⏳ Comisiones pendientes: ${com_pendientes:,.2f}")
        
        # Detalle de comisiones pagadas
        cursor.execute("""
            SELECT v.id, v.cliente, v.destino, v.comision_vendedora, v.fecha_pago_comision
            FROM ventas v
            WHERE v.vendedora_id = ? AND v.estado = 'CERRADO' AND v.comision_pagada = 1
            ORDER BY v.fecha_pago_comision DESC
            LIMIT 5
        """, (vendedora_id,))
        
        comisiones = cursor.fetchall()
        
        if comisiones:
            print(f"\n   📋 Últimas comisiones pagadas:")
            for c in comisiones:
                print(f"      • Viaje #{c[0]} - {c[1]} ({c[2]})")
                print(f"        Comisión: ${c[3]:,.2f} | Pagada: {c[4]}")
        
        print("-" * 60)
    
    conexion.close()
