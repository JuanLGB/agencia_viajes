from database import conectar
from datetime import datetime


def registrar_pago():
    """Registra un pago parcial o total de un viaje"""
    try:
        id_viaje = int(input("ID del viaje: "))
        monto_pago = float(input("Monto del pago: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    if monto_pago <= 0:
        print("❌ El monto debe ser mayor a cero.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener datos del viaje
    cursor.execute("""
        SELECT id, saldo, pagado, precio_total, ganancia, estado
        FROM ventas
        WHERE id = ?
    """, (id_viaje,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ No se encontró el viaje.")
        conexion.close()
        return
    
    viaje_id, saldo, pagado, precio_total, ganancia, estado = viaje
    
    if estado == "CERRADO":
        print("❌ Este viaje ya está cerrado.")
        conexion.close()
        return
    
    if monto_pago > saldo:
        print(f"❌ El pago (${monto_pago}) no puede ser mayor al saldo (${saldo}).")
        conexion.close()
        return
    
    # Actualizar pagos
    nuevo_pagado = pagado + monto_pago
    nuevo_saldo = saldo - monto_pago
    
    # Registrar abono
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO abonos (venta_id, fecha, monto)
        VALUES (?, ?, ?)
    """, (id_viaje, fecha_actual, monto_pago))
    
    # Actualizar venta
    if nuevo_saldo == 0:
        # Viaje liquidado - calcular comisión (10% de la ganancia)
        comision_vendedora = round(ganancia * 0.10, 2)
        
        cursor.execute("""
            UPDATE ventas
            SET pagado = ?, saldo = ?, estado = 'LIQUIDADO', comision_vendedora = ?
            WHERE id = ?
        """, (nuevo_pagado, nuevo_saldo, comision_vendedora, id_viaje))
        
        print(f"✅ Pago registrado. Saldo restante: ${nuevo_saldo}")
        print("🎉 Viaje LIQUIDADO.")
        print(f"💰 Comisión de la vendedora: ${comision_vendedora}")
    else:
        cursor.execute("""
            UPDATE ventas
            SET pagado = ?, saldo = ?
            WHERE id = ?
        """, (nuevo_pagado, nuevo_saldo, id_viaje))
        
        print(f"✅ Pago registrado. Saldo restante: ${nuevo_saldo}")
    
    conexion.commit()
    conexion.close()


def pagar_comision():
    """Marca la comisión de un viaje como pagada"""
    try:
        id_viaje = int(input("ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, estado, comision_vendedora, comision_pagada
        FROM ventas
        WHERE id = ?
    """, (id_viaje,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    viaje_id, estado, comision, comision_pagada = viaje
    
    if estado != "LIQUIDADO":
        print("❌ El viaje no está liquidado.")
        conexion.close()
        return
    
    if comision_pagada == 1:
        print("❌ Comisión ya pagada.")
        conexion.close()
        return
    
    # Registrar fecha y hora de pago
    fecha_pago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Marcar comisión como pagada y cerrar viaje
    cursor.execute("""
        UPDATE ventas
        SET comision_pagada = 1, estado = 'CERRADO', fecha_pago_comision = ?
        WHERE id = ?
    """, (fecha_pago, id_viaje))
    
    conexion.commit()
    conexion.close()
    
    print("✅ Comisión pagada correctamente.")
    print(f"💰 Comisión: ${comision}")
    print(f"📅 Fecha de pago: {fecha_pago}")
    print("📦 Viaje enviado al HISTORIAL.")


def ver_abonos(id_viaje):
    """Muestra el historial de abonos de un viaje"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT fecha, monto
        FROM abonos
        WHERE venta_id = ?
        ORDER BY fecha
    """, (id_viaje,))
    
    abonos = cursor.fetchall()
    conexion.close()
    
    if not abonos:
        print("No hay abonos registrados.")
        return
    
    print(f"\n💵 HISTORIAL DE ABONOS - Viaje #{id_viaje}\n")
    total = 0
    for abono in abonos:
        fecha, monto = abono
        total += monto
        print(f"{fecha} - ${monto}")
    
    print(f"\nTotal abonado: ${total}")
