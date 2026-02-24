from database import conectar
from datetime import datetime
from vendedoras import ver_vendedoras, obtener_vendedora_por_id
import calendar


def registrar_sueldo_mes():
    """Registra el sueldo mensual de una vendedora"""
    print("\n" + "="*60)
    print("👥 REGISTRAR SUELDO MENSUAL")
    print("="*60)
    
    # Seleccionar vendedora
    ver_vendedoras()
    
    try:
        vendedora_id = int(input("\nID de la vendedora: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    vendedora = obtener_vendedora_por_id(vendedora_id)
    
    if not vendedora or not vendedora["activa"]:
        print("❌ Vendedora no válida o inactiva.")
        return
    
    # Mes y año
    try:
        mes = int(input("Mes (1-12): "))
        anio = int(input("Año: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    # Verificar si ya existe sueldo para este mes
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id FROM sueldos_vendedoras
        WHERE vendedora_id = ? AND mes = ? AND anio = ?
    """, (vendedora_id, mes, anio))
    
    if cursor.fetchone():
        print(f"\n⚠️  Ya existe un registro de sueldo para {vendedora['nombre']} en {calendar.month_name[mes]} {anio}")
        sobrescribir = input("¿Deseas sobrescribir? (s/n): ").lower()
        
        if sobrescribir not in ['s', 'si', 'sí', 'yes', 'y']:
            print("\n❌ Operación cancelada.")
            conexion.close()
            return
        
        # Eliminar el registro anterior
        cursor.execute("""
            DELETE FROM sueldos_vendedoras
            WHERE vendedora_id = ? AND mes = ? AND anio = ?
        """, (vendedora_id, mes, anio))
    
    print(f"\n💼 Sueldo para: {vendedora['nombre']}")
    print(f"📅 Periodo: {calendar.month_name[mes]} {anio}")
    
    # Componentes del sueldo
    try:
        sueldo_base = float(input("\nSueldo base: $"))
        comisiones = float(input("Comisiones: $"))
        bonos = float(input("Bonos (opcional): $") or "0")
        deducciones = float(input("Deducciones (opcional): $") or "0")
    except ValueError:
        print("❌ Valores numéricos inválidos.")
        conexion.close()
        return
    
    total_pagar = sueldo_base + comisiones + bonos - deducciones
    
    print(f"\n--- RESUMEN ---")
    print(f"Sueldo base:    ${sueldo_base:>10,.2f}")
    print(f"Comisiones:     ${comisiones:>10,.2f}")
    if bonos > 0:
        print(f"Bonos:          ${bonos:>10,.2f}")
    if deducciones > 0:
        print(f"Deducciones:   -${deducciones:>10,.2f}")
    print(f"{'─'*35}")
    print(f"TOTAL A PAGAR:  ${total_pagar:>10,.2f}")
    
    confirmar = input("\n¿Confirmar registro? (s/n): ").lower()
    
    if confirmar not in ['s', 'si', 'sí', 'yes', 'y']:
        print("\n❌ Operación cancelada.")
        conexion.close()
        return
    
    # Fecha de pago
    fecha_pago = input("\nFecha de pago (DD-MM-YYYY) [Enter = pendiente]: ").strip()
    estado = "PAGADO" if fecha_pago else "PENDIENTE"
    
    notas = input("Notas (opcional): ").strip()
    
    # Guardar en BD
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO sueldos_vendedoras (
            vendedora_id, mes, anio, sueldo_base, comisiones, bonos, deducciones,
            total_pagar, fecha_pago, estado, notas, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vendedora_id, mes, anio, sueldo_base, comisiones, bonos, deducciones,
        total_pagar, fecha_pago, estado, notas, fecha_registro
    ))
    
    sueldo_id = cursor.lastrowid
    
    # También registrar como gasto operativo
    cursor.execute("""
        INSERT INTO gastos_operativos (
            categoria, descripcion, monto, fecha_gasto, mes, anio,
            frecuencia, recurrente, proveedor, notas, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, 'MENSUAL', 1, ?, ?, ?)
    """, (
        "Sueldos y Nómina",
        f"Sueldo {vendedora['nombre']} - {calendar.month_name[mes]} {anio}",
        total_pagar,
        fecha_pago if fecha_pago else datetime.now().strftime("%d-%m-%Y"),
        mes,
        anio,
        vendedora['nombre'],
        f"Base: ${sueldo_base:,.2f}, Com: ${comisiones:,.2f}",
        fecha_registro
    ))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Sueldo registrado correctamente (ID: {sueldo_id})")
    print(f"💰 Total: ${total_pagar:,.2f}")


def ver_sueldos():
    """Muestra los sueldos registrados"""
    print("\n" + "="*60)
    print("👥 SUELDOS DE VENDEDORAS")
    print("="*60)
    
    print("\n📅 FILTRAR POR:")
    print("1. Todos los sueldos")
    print("2. Mes específico")
    print("3. Vendedora específica")
    print("4. Pendientes de pago")
    
    opcion = input("\nOpción: ").strip()
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    if opcion == "1":
        cursor.execute("""
            SELECT s.id, v.nombre, s.mes, s.anio, s.total_pagar, s.estado
            FROM sueldos_vendedoras s
            JOIN vendedoras v ON s.vendedora_id = v.id
            ORDER BY s.anio DESC, s.mes DESC
            LIMIT 50
        """)
        titulo = "ÚLTIMOS 50 SUELDOS"
    
    elif opcion == "2":
        try:
            mes = int(input("Mes (1-12): "))
            anio = int(input("Año: "))
        except ValueError:
            print("❌ Valores inválidos.")
            conexion.close()
            return
        
        cursor.execute("""
            SELECT s.id, v.nombre, s.mes, s.anio, s.total_pagar, s.estado
            FROM sueldos_vendedoras s
            JOIN vendedoras v ON s.vendedora_id = v.id
            WHERE s.mes = ? AND s.anio = ?
            ORDER BY v.nombre
        """, (mes, anio))
        titulo = f"SUELDOS - {calendar.month_name[mes].upper()} {anio}"
    
    elif opcion == "3":
        ver_vendedoras()
        try:
            vendedora_id = int(input("\nID de la vendedora: "))
        except ValueError:
            print("❌ ID inválido.")
            conexion.close()
            return
        
        cursor.execute("""
            SELECT s.id, v.nombre, s.mes, s.anio, s.total_pagar, s.estado
            FROM sueldos_vendedoras s
            JOIN vendedoras v ON s.vendedora_id = v.id
            WHERE s.vendedora_id = ?
            ORDER BY s.anio DESC, s.mes DESC
        """, (vendedora_id,))
        
        vendedora = obtener_vendedora_por_id(vendedora_id)
        titulo = f"SUELDOS - {vendedora['nombre'].upper()}" if vendedora else "SUELDOS"
    
    elif opcion == "4":
        cursor.execute("""
            SELECT s.id, v.nombre, s.mes, s.anio, s.total_pagar, s.estado
            FROM sueldos_vendedoras s
            JOIN vendedoras v ON s.vendedora_id = v.id
            WHERE s.estado = 'PENDIENTE'
            ORDER BY s.anio DESC, s.mes DESC
        """)
        titulo = "SUELDOS PENDIENTES DE PAGO"
    
    else:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    sueldos = cursor.fetchall()
    
    print("\n" + "="*60)
    print(titulo)
    print("="*60)
    
    if not sueldos:
        print("\nNo hay sueldos registrados con estos filtros.")
        conexion.close()
        return
    
    total = 0
    
    for s in sueldos:
        estado_icon = "✅" if s[5] == "PAGADO" else "⏳"
        mes_nombre = calendar.month_name[s[2]]
        
        print(f"\n{estado_icon} ID: {s[0]} | {s[1]}")
        print(f"   📅 {mes_nombre} {s[3]} | 💵 ${s[4]:,.2f} | {s[5]}")
        total += s[4]
        print("-" * 60)
    
    print(f"\n💰 TOTAL: ${total:,.2f}")
    
    conexion.close()


def marcar_sueldo_pagado():
    """Marca un sueldo como pagado"""
    ver_sueldos()
    
    try:
        sueldo_id = int(input("\nID del sueldo a marcar como pagado: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    fecha_pago = input("Fecha de pago (DD-MM-YYYY): ").strip()
    
    if not fecha_pago:
        print("❌ La fecha es obligatoria.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE sueldos_vendedoras
        SET estado = 'PAGADO', fecha_pago = ?
        WHERE id = ?
    """, (fecha_pago, sueldo_id))
    
    if cursor.rowcount > 0:
        conexion.commit()
        print(f"\n✅ Sueldo ID {sueldo_id} marcado como PAGADO")
    else:
        print(f"\n❌ Sueldo ID {sueldo_id} no encontrado.")
    
    conexion.close()


def reporte_sueldos_mes():
    """Genera reporte de sueldos por mes"""
    try:
        mes = int(input("\nMes (1-12): "))
        anio = int(input("Año: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT v.nombre, s.sueldo_base, s.comisiones, s.bonos, s.deducciones,
               s.total_pagar, s.estado
        FROM sueldos_vendedoras s
        JOIN vendedoras v ON s.vendedora_id = v.id
        WHERE s.mes = ? AND s.anio = ?
        ORDER BY v.nombre
    """, (mes, anio))
    
    sueldos = cursor.fetchall()
    
    print("\n" + "="*60)
    print(f"💼 REPORTE DE NÓMINA - {calendar.month_name[mes].upper()} {anio}")
    print("="*60)
    
    if not sueldos:
        print("\nNo hay sueldos registrados para este mes.")
        conexion.close()
        return
    
    total_base = 0
    total_comisiones = 0
    total_bonos = 0
    total_deducciones = 0
    total_pagar = 0
    
    for s in sueldos:
        estado_icon = "✅" if s[6] == "PAGADO" else "⏳"
        
        print(f"\n{estado_icon} {s[0]}")
        print(f"   Base:        ${s[1]:>10,.2f}")
        print(f"   Comisiones:  ${s[2]:>10,.2f}")
        if s[3] > 0:
            print(f"   Bonos:       ${s[3]:>10,.2f}")
        if s[4] > 0:
            print(f"   Deducciones: ${s[4]:>10,.2f}")
        print(f"   {'─'*30}")
        print(f"   TOTAL:       ${s[5]:>10,.2f}")
        
        total_base += s[1]
        total_comisiones += s[2]
        total_bonos += s[3]
        total_deducciones += s[4]
        total_pagar += s[5]
    
    print("\n" + "="*60)
    print("📊 TOTALES DEL MES:")
    print(f"   Sueldos base:     ${total_base:>12,.2f}")
    print(f"   Comisiones:       ${total_comisiones:>12,.2f}")
    if total_bonos > 0:
        print(f"   Bonos:            ${total_bonos:>12,.2f}")
    if total_deducciones > 0:
        print(f"   Deducciones:      ${total_deducciones:>12,.2f}")
    print(f"   {'─'*40}")
    print(f"   TOTAL A PAGAR:    ${total_pagar:>12,.2f}")
    print("="*60)
    
    conexion.close()


def menu_sueldos():
    """Menú principal de gestión de sueldos"""
    while True:
        print("\n" + "="*60)
        print("👥 GESTIÓN DE SUELDOS")
        print("="*60)
        print("\n1. Registrar sueldo mensual")
        print("2. Ver sueldos")
        print("3. Marcar como pagado")
        print("4. Reporte mensual de nómina")
        print("5. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            registrar_sueldo_mes()
        elif opcion == "2":
            ver_sueldos()
        elif opcion == "3":
            marcar_sueldo_pagado()
        elif opcion == "4":
            reporte_sueldos_mes()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_sueldos()
