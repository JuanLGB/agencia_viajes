from database import conectar
from datetime import datetime
import calendar


def obtener_ingresos_riviera(mes, anio):
    """Obtiene ingresos de Riviera Maya (general, bloqueos, grupos)"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Ingresos Riviera General (ventas normales)
    cursor.execute("""
        SELECT SUM(pagado) as total
        FROM ventas
        WHERE CAST(substr(fecha_inicio, 4, 2) AS INTEGER) = ? 
        AND CAST(substr(fecha_inicio, 7, 4) AS INTEGER) = ?
        AND (es_bloqueo = 0 OR es_bloqueo IS NULL)
        AND (es_grupo = 0 OR es_grupo IS NULL)
    """, (mes, anio))
    
    riviera_general = cursor.fetchone()[0] or 0
    
    # Ingresos Riviera Bloqueos
    cursor.execute("""
        SELECT SUM(pagado) as total
        FROM ventas
        WHERE CAST(substr(fecha_inicio, 4, 2) AS INTEGER) = ? 
        AND CAST(substr(fecha_inicio, 7, 4) AS INTEGER) = ?
        AND es_bloqueo = 1
    """, (mes, anio))
    
    riviera_bloqueos = cursor.fetchone()[0] or 0
    
    # Ingresos Riviera Grupos
    cursor.execute("""
        SELECT SUM(pagado) as total
        FROM ventas
        WHERE CAST(substr(fecha_inicio, 4, 2) AS INTEGER) = ? 
        AND CAST(substr(fecha_inicio, 7, 4) AS INTEGER) = ?
        AND es_grupo = 1
    """, (mes, anio))
    
    riviera_grupos = cursor.fetchone()[0] or 0
    
    conexion.close()
    
    return {
        'general': riviera_general,
        'bloqueos': riviera_bloqueos,
        'grupos': riviera_grupos,
        'total': riviera_general + riviera_bloqueos + riviera_grupos
    }


def obtener_ingresos_nacionales(mes, anio):
    """Obtiene ingresos de viajes nacionales"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT SUM(c.total_abonado) as total
        FROM clientes_nacionales c
        JOIN viajes_nacionales v ON c.viaje_id = v.id
        WHERE CAST(substr(v.fecha_salida, 4, 2) AS INTEGER) = ? 
        AND CAST(substr(v.fecha_salida, 7, 4) AS INTEGER) = ?
    """, (mes, anio))
    
    total = cursor.fetchone()[0] or 0
    conexion.close()
    
    return total


def obtener_ingresos_internacionales(mes, anio):
    """Obtiene ingresos de viajes internacionales"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT SUM(c.abonado_usd) as total
        FROM clientes_internacionales c
        JOIN viajes_internacionales v ON c.viaje_id = v.id
        WHERE CAST(substr(v.fecha_salida, 4, 2) AS INTEGER) = ? 
        AND CAST(substr(v.fecha_salida, 7, 4) AS INTEGER) = ?
    """, (mes, anio))
    
    total_usd = cursor.fetchone()[0] or 0
    conexion.close()
    
    return total_usd


def obtener_gastos_operativos(mes, anio):
    """Obtiene gastos operativos del mes"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Total de gastos
    cursor.execute("""
        SELECT SUM(monto) as total
        FROM gastos_operativos
        WHERE mes = ? AND anio = ?
    """, (mes, anio))
    
    total = cursor.fetchone()[0] or 0
    
    # Gastos por categoría
    cursor.execute("""
        SELECT categoria, SUM(monto) as total
        FROM gastos_operativos
        WHERE mes = ? AND anio = ?
        GROUP BY categoria
        ORDER BY total DESC
    """, (mes, anio))
    
    por_categoria = cursor.fetchall()
    
    conexion.close()
    
    return {
        'total': total,
        'categorias': por_categoria
    }


def reporte_financiero_mensual():
    """Genera reporte financiero completo del mes"""
    print("\n" + "="*60)
    print("📊 REPORTE FINANCIERO GENERAL")
    print("="*60)
    
    try:
        mes = int(input("\nMes (1-12): "))
        anio = int(input("Año: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    if mes < 1 or mes > 12:
        print("❌ Mes inválido.")
        return
    
    mes_nombre = calendar.month_name[mes]
    
    print("\n" + "="*60)
    print(f"📊 REPORTE FINANCIERO - {mes_nombre.upper()} {anio}")
    print("="*60)
    
    # ===== INGRESOS =====
    print("\n💰 INGRESOS:")
    print("-" * 60)
    
    # Riviera Maya
    riviera = obtener_ingresos_riviera(mes, anio)
    print(f"   Riviera Maya (General):    ${riviera['general']:>15,.2f}")
    print(f"   Riviera Maya (Bloqueos):   ${riviera['bloqueos']:>15,.2f}")
    print(f"   Riviera Maya (Grupos):     ${riviera['grupos']:>15,.2f}")
    
    # Nacionales
    nacionales = obtener_ingresos_nacionales(mes, anio)
    print(f"   Viajes Nacionales:         ${nacionales:>15,.2f}")
    
    # Internacionales
    internacionales_usd = obtener_ingresos_internacionales(mes, anio)
    
    # Tipo de cambio promedio (puedes ajustarlo)
    tipo_cambio = 17.0
    internacionales_mxn = internacionales_usd * tipo_cambio
    
    print(f"   Viajes Internacionales:    ${internacionales_mxn:>15,.2f}")
    if internacionales_usd > 0:
        print(f"                              (${internacionales_usd:,.2f} USD @ ${tipo_cambio:.2f})")
    
    total_ingresos = riviera['total'] + nacionales + internacionales_mxn
    
    print(f"   {'-'*60}")
    print(f"   TOTAL INGRESOS:            ${total_ingresos:>15,.2f}")
    
    # ===== GASTOS =====
    print("\n💸 GASTOS OPERATIVOS:")
    print("-" * 60)
    
    gastos = obtener_gastos_operativos(mes, anio)
    
    if gastos['categorias']:
        for cat in gastos['categorias']:
            print(f"   {cat[0]:30} ${cat[1]:>15,.2f}")
    else:
        print("   (No hay gastos registrados)")
    
    print(f"   {'-'*60}")
    print(f"   TOTAL GASTOS:              ${gastos['total']:>15,.2f}")
    
    # ===== UTILIDAD =====
    utilidad_neta = total_ingresos - gastos['total']
    
    if total_ingresos > 0:
        margen = (utilidad_neta / total_ingresos * 100)
    else:
        margen = 0
    
    print("\n" + "="*60)
    print(f"💵 UTILIDAD NETA:              ${utilidad_neta:>15,.2f}")
    print(f"📊 Margen de Utilidad:         {margen:>15.2f}%")
    print("="*60)
    
    # ===== ANÁLISIS =====
    if total_ingresos > 0:
        print("\n📈 ANÁLISIS:")
        print("-" * 60)
        
        # Desglose de ingresos
        print("   Composición de Ingresos:")
        print(f"      Riviera Maya:    {(riviera['total']/total_ingresos*100):>6.1f}%")
        print(f"      Nacionales:      {(nacionales/total_ingresos*100):>6.1f}%")
        if internacionales_mxn > 0:
            print(f"      Internacionales: {(internacionales_mxn/total_ingresos*100):>6.1f}%")
        
        # Relación ingresos/gastos
        if gastos['total'] > 0:
            print(f"\n   Por cada $1 MXN de ingreso:")
            print(f"      Gastos:   ${gastos['total']/total_ingresos:>6.2f}")
            print(f"      Utilidad: ${utilidad_neta/total_ingresos:>6.2f}")
    
    print("\n")


def reporte_financiero_anual():
    """Genera reporte financiero del año completo"""
    print("\n" + "="*60)
    print("📊 REPORTE FINANCIERO ANUAL")
    print("="*60)
    
    try:
        anio = int(input("\nAño: "))
    except ValueError:
        print("❌ Año inválido.")
        return
    
    print("\n" + "="*60)
    print(f"📊 REPORTE FINANCIERO - AÑO {anio}")
    print("="*60)
    
    print("\n📅 POR MES:")
    print("-" * 60)
    print(f"{'Mes':12} {'Ingresos':>15} {'Gastos':>15} {'Utilidad':>15}")
    print("-" * 60)
    
    total_ingresos_anual = 0
    total_gastos_anual = 0
    
    for mes in range(1, 13):
        # Ingresos
        riviera = obtener_ingresos_riviera(mes, anio)
        nacionales = obtener_ingresos_nacionales(mes, anio)
        internacionales_usd = obtener_ingresos_internacionales(mes, anio)
        internacionales_mxn = internacionales_usd * 17.0
        
        ingresos_mes = riviera['total'] + nacionales + internacionales_mxn
        
        # Gastos
        gastos = obtener_gastos_operativos(mes, anio)
        gastos_mes = gastos['total']
        
        # Utilidad
        utilidad_mes = ingresos_mes - gastos_mes
        
        mes_nombre = calendar.month_name[mes]
        print(f"{mes_nombre:12} ${ingresos_mes:>14,.2f} ${gastos_mes:>14,.2f} ${utilidad_mes:>14,.2f}")
        
        total_ingresos_anual += ingresos_mes
        total_gastos_anual += gastos_mes
    
    utilidad_anual = total_ingresos_anual - total_gastos_anual
    
    if total_ingresos_anual > 0:
        margen_anual = (utilidad_anual / total_ingresos_anual * 100)
    else:
        margen_anual = 0
    
    print("-" * 60)
    print(f"{'TOTAL':12} ${total_ingresos_anual:>14,.2f} ${total_gastos_anual:>14,.2f} ${utilidad_anual:>14,.2f}")
    print("="*60)
    
    print(f"\n💵 UTILIDAD NETA ANUAL:        ${utilidad_anual:>15,.2f}")
    print(f"📊 Margen de Utilidad:         {margen_anual:>15.2f}%")
    
    if total_ingresos_anual > 0:
        print(f"📊 Promedio Mensual Ingresos:  ${total_ingresos_anual/12:>15,.2f}")
        print(f"📊 Promedio Mensual Gastos:    ${total_gastos_anual/12:>15,.2f}")
        print(f"📊 Promedio Mensual Utilidad:  ${utilidad_anual/12:>15,.2f}")
    
    print("\n")


def comparativa_meses():
    """Compara varios meses"""
    print("\n" + "="*60)
    print("📊 COMPARATIVA DE MESES")
    print("="*60)
    
    try:
        anio = int(input("\nAño: "))
        mes_inicio = int(input("Mes inicial (1-12): "))
        mes_fin = int(input("Mes final (1-12): "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    if mes_inicio < 1 or mes_fin > 12 or mes_inicio > mes_fin:
        print("❌ Rango de meses inválido.")
        return
    
    print("\n" + "="*60)
    print(f"📊 COMPARATIVA - {calendar.month_name[mes_inicio].upper()} a {calendar.month_name[mes_fin].upper()} {anio}")
    print("="*60)
    
    print(f"\n{'Mes':12} {'Ingresos':>15} {'Gastos':>15} {'Utilidad':>15} {'Margen':>10}")
    print("-" * 70)
    
    mejor_mes = None
    mejor_utilidad = 0
    
    for mes in range(mes_inicio, mes_fin + 1):
        riviera = obtener_ingresos_riviera(mes, anio)
        nacionales = obtener_ingresos_nacionales(mes, anio)
        internacionales_usd = obtener_ingresos_internacionales(mes, anio)
        internacionales_mxn = internacionales_usd * 17.0
        
        ingresos = riviera['total'] + nacionales + internacionales_mxn
        gastos_data = obtener_gastos_operativos(mes, anio)
        gastos = gastos_data['total']
        utilidad = ingresos - gastos
        margen = (utilidad / ingresos * 100) if ingresos > 0 else 0
        
        mes_nombre = calendar.month_name[mes]
        print(f"{mes_nombre:12} ${ingresos:>14,.2f} ${gastos:>14,.2f} ${utilidad:>14,.2f} {margen:>9.1f}%")
        
        if utilidad > mejor_utilidad:
            mejor_utilidad = utilidad
            mejor_mes = mes_nombre
    
    print("\n" + "="*60)
    if mejor_mes:
        print(f"🏆 Mejor mes: {mejor_mes} con ${mejor_utilidad:,.2f} de utilidad")
    print("\n")


def menu_reportes_financieros():
    """Menú principal de reportes financieros"""
    while True:
        print("\n" + "="*60)
        print("📊 REPORTES FINANCIEROS INTEGRADOS")
        print("="*60)
        print("\n1. Reporte mensual completo")
        print("2. Reporte anual completo")
        print("3. Comparativa de meses")
        print("4. Exportar a Excel")
        print("5. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            reporte_financiero_mensual()
        elif opcion == "2":
            reporte_financiero_anual()
        elif opcion == "3":
            comparativa_meses()
        elif opcion == "4":
            from reportes_financieros_excel import menu_reportes_excel
            menu_reportes_excel()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_reportes_financieros()
