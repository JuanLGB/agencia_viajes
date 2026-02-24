from database import conectar
from datetime import datetime
import calendar


def registrar_gasto():
    """Registra un nuevo gasto operativo"""
    print("\n" + "="*60)
    print("💰 REGISTRAR GASTO OPERATIVO")
    print("="*60)
    
    # Seleccionar categoría
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, icono
        FROM categorias_gastos
        WHERE activa = 1
        ORDER BY nombre
    """)
    
    categorias = cursor.fetchall()
    
    if not categorias:
        print("\n❌ No hay categorías disponibles.")
        conexion.close()
        return
    
    print("\n📋 CATEGORÍAS:")
    for cat in categorias:
        print(f"{cat[0]}. {cat[2]} {cat[1]}")
    print("0. Otra categoría")
    
    try:
        cat_id = int(input("\nSelecciona categoría: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    if cat_id == 0:
        categoria = input("Nombre de la categoría: ").strip()
    else:
        # Buscar el nombre de la categoría
        categoria = None
        for cat in categorias:
            if cat[0] == cat_id:
                categoria = cat[1]
                break
        
        if not categoria:
            print("❌ Categoría no encontrada.")
            conexion.close()
            return
    
    # Datos del gasto
    print(f"\n📝 Categoría: {categoria}")
    
    descripcion = input("Descripción del gasto: ").strip()
    
    try:
        monto = float(input("Monto: $"))
    except ValueError:
        print("❌ Monto inválido.")
        conexion.close()
        return
    
    # Fecha del gasto
    fecha_gasto = input("Fecha del gasto (DD-MM-YYYY) [Enter = hoy]: ").strip()
    
    if not fecha_gasto:
        fecha_dt = datetime.now()
        fecha_gasto = fecha_dt.strftime("%d-%m-%Y")
    else:
        try:
            fecha_dt = datetime.strptime(fecha_gasto, "%d-%m-%Y")
        except:
            print("❌ Fecha inválida.")
            conexion.close()
            return
    
    mes = fecha_dt.month
    anio = fecha_dt.year
    
    # Frecuencia
    print("\n🔄 FRECUENCIA:")
    print("1. Único")
    print("2. Mensual")
    print("3. Bimestral")
    print("4. Trimestral")
    print("5. Anual")
    
    freq_opcion = input("Selecciona (1-5) [1]: ").strip() or "1"
    
    frecuencias = {
        "1": "UNICO",
        "2": "MENSUAL",
        "3": "BIMESTRAL",
        "4": "TRIMESTRAL",
        "5": "ANUAL"
    }
    
    frecuencia = frecuencias.get(freq_opcion, "UNICO")
    recurrente = 1 if freq_opcion != "1" else 0
    
    # Datos opcionales
    proveedor = input("\nProveedor (opcional): ").strip()
    metodo_pago = input("Método de pago (opcional): ").strip()
    notas = input("Notas (opcional): ").strip()
    
    # Guardar en BD
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO gastos_operativos (
            categoria, descripcion, monto, fecha_gasto, mes, anio,
            frecuencia, recurrente, proveedor, metodo_pago, notas, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        categoria, descripcion, monto, fecha_gasto, mes, anio,
        frecuencia, recurrente, proveedor, metodo_pago, notas, fecha_registro
    ))
    
    conexion.commit()
    gasto_id = cursor.lastrowid
    conexion.close()
    
    print(f"\n✅ Gasto registrado correctamente (ID: {gasto_id})")
    print(f"💰 Monto: ${monto:,.2f}")
    print(f"📅 Fecha: {fecha_gasto}")


def ver_gastos():
    """Muestra todos los gastos registrados"""
    print("\n" + "="*60)
    print("💰 GASTOS OPERATIVOS")
    print("="*60)
    
    print("\n📅 FILTRAR POR:")
    print("1. Ver todos")
    print("2. Mes específico")
    print("3. Categoría específica")
    print("4. Año completo")
    
    opcion = input("\nOpción: ").strip()
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    if opcion == "1":
        # Ver todos
        cursor.execute("""
            SELECT id, categoria, descripcion, monto, fecha_gasto, frecuencia
            FROM gastos_operativos
            ORDER BY fecha_gasto DESC
            LIMIT 50
        """)
        titulo = "ÚLTIMOS 50 GASTOS"
    
    elif opcion == "2":
        # Mes específico
        try:
            mes = int(input("Mes (1-12): "))
            anio = int(input("Año: "))
        except ValueError:
            print("❌ Valores inválidos.")
            conexion.close()
            return
        
        cursor.execute("""
            SELECT id, categoria, descripcion, monto, fecha_gasto, frecuencia
            FROM gastos_operativos
            WHERE mes = ? AND anio = ?
            ORDER BY fecha_gasto DESC
        """, (mes, anio))
        titulo = f"GASTOS - {calendar.month_name[mes].upper()} {anio}"
    
    elif opcion == "3":
        # Categoría específica
        cursor.execute("SELECT DISTINCT categoria FROM gastos_operativos ORDER BY categoria")
        cats = cursor.fetchall()
        
        print("\n📋 CATEGORÍAS:")
        for i, cat in enumerate(cats, 1):
            print(f"{i}. {cat[0]}")
        
        try:
            cat_idx = int(input("\nSelecciona: ")) - 1
            categoria = cats[cat_idx][0]
        except:
            print("❌ Selección inválida.")
            conexion.close()
            return
        
        cursor.execute("""
            SELECT id, categoria, descripcion, monto, fecha_gasto, frecuencia
            FROM gastos_operativos
            WHERE categoria = ?
            ORDER BY fecha_gasto DESC
        """, (categoria,))
        titulo = f"GASTOS - {categoria.upper()}"
    
    elif opcion == "4":
        # Año completo
        try:
            anio = int(input("Año: "))
        except ValueError:
            print("❌ Año inválido.")
            conexion.close()
            return
        
        cursor.execute("""
            SELECT id, categoria, descripcion, monto, fecha_gasto, frecuencia
            FROM gastos_operativos
            WHERE anio = ?
            ORDER BY fecha_gasto DESC
        """, (anio,))
        titulo = f"GASTOS - AÑO {anio}"
    
    else:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    gastos = cursor.fetchall()
    
    print("\n" + "="*60)
    print(titulo)
    print("="*60)
    
    if not gastos:
        print("\nNo hay gastos registrados con estos filtros.")
        conexion.close()
        return
    
    total = 0
    
    for g in gastos:
        freq_icon = "🔄" if g[5] != "UNICO" else "📌"
        print(f"\n{freq_icon} ID: {g[0]} | {g[1]}")
        print(f"   {g[2]}")
        print(f"   💵 ${g[3]:,.2f} | 📅 {g[4]} | {g[5]}")
        total += g[3]
        print("-" * 60)
    
    print(f"\n💰 TOTAL: ${total:,.2f}")
    
    conexion.close()


def editar_gasto():
    """Edita un gasto existente"""
    ver_gastos()
    
    try:
        gasto_id = int(input("\nID del gasto a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT categoria, descripcion, monto, fecha_gasto, proveedor, notas
        FROM gastos_operativos
        WHERE id = ?
    """, (gasto_id,))
    
    gasto = cursor.fetchone()
    
    if not gasto:
        print("❌ Gasto no encontrado.")
        conexion.close()
        return
    
    print(f"\n📝 Editando gasto ID: {gasto_id}")
    print("(Presiona Enter para mantener el valor actual)\n")
    
    descripcion = input(f"Descripción [{gasto[1]}]: ").strip() or gasto[1]
    
    try:
        monto_input = input(f"Monto [${gasto[2]:,.2f}]: $").strip()
        monto = float(monto_input) if monto_input else gasto[2]
    except ValueError:
        print("❌ Monto inválido.")
        conexion.close()
        return
    
    proveedor = input(f"Proveedor [{gasto[4] or ''}]: ").strip() or gasto[4]
    notas = input(f"Notas [{gasto[5] or ''}]: ").strip() or gasto[5]
    
    cursor.execute("""
        UPDATE gastos_operativos
        SET descripcion = ?, monto = ?, proveedor = ?, notas = ?
        WHERE id = ?
    """, (descripcion, monto, proveedor, notas, gasto_id))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Gasto actualizado correctamente.")


def eliminar_gasto():
    """Elimina un gasto"""
    ver_gastos()
    
    try:
        gasto_id = int(input("\nID del gasto a eliminar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    confirmar = input(f"¿Seguro que deseas eliminar el gasto ID {gasto_id}? (s/n): ").lower()
    
    if confirmar not in ['s', 'si', 'sí', 'yes', 'y']:
        print("\n❌ Operación cancelada.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("DELETE FROM gastos_operativos WHERE id = ?", (gasto_id,))
    
    if cursor.rowcount > 0:
        conexion.commit()
        print(f"\n✅ Gasto eliminado correctamente.")
    else:
        print(f"\n❌ Gasto ID {gasto_id} no encontrado.")
    
    conexion.close()


def reporte_gastos_mes():
    """Genera reporte de gastos por mes"""
    try:
        mes = int(input("\nMes (1-12): "))
        anio = int(input("Año: "))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*60)
    print(f"📊 REPORTE DE GASTOS - {calendar.month_name[mes].upper()} {anio}")
    print("="*60)
    
    # Gastos por categoría
    cursor.execute("""
        SELECT categoria, SUM(monto) as total, COUNT(*) as cantidad
        FROM gastos_operativos
        WHERE mes = ? AND anio = ?
        GROUP BY categoria
        ORDER BY total DESC
    """, (mes, anio))
    
    gastos_cat = cursor.fetchall()
    
    if not gastos_cat:
        print("\nNo hay gastos registrados para este mes.")
        conexion.close()
        return
    
    print("\n📋 POR CATEGORÍA:")
    total_mes = 0
    
    for cat in gastos_cat:
        print(f"\n   {cat[0]}:")
        print(f"      💵 ${cat[1]:,.2f} ({cat[2]} gastos)")
        total_mes += cat[1]
    
    print(f"\n{'='*60}")
    print(f"💰 TOTAL DEL MES: ${total_mes:,.2f}")
    print("="*60)
    
    # Promedio diario
    dias_mes = calendar.monthrange(anio, mes)[1]
    promedio_dia = total_mes / dias_mes
    print(f"\n📊 Promedio diario: ${promedio_dia:,.2f}")
    
    # Gastos recurrentes vs únicos
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN recurrente = 1 THEN monto ELSE 0 END) as recurrentes,
            SUM(CASE WHEN recurrente = 0 THEN monto ELSE 0 END) as unicos
        FROM gastos_operativos
        WHERE mes = ? AND anio = ?
    """, (mes, anio))
    
    rec_data = cursor.fetchone()
    
    print(f"\n🔄 Gastos recurrentes: ${rec_data[0]:,.2f}")
    print(f"📌 Gastos únicos: ${rec_data[1]:,.2f}")
    
    conexion.close()


def reporte_gastos_anual():
    """Genera reporte anual de gastos"""
    try:
        anio = int(input("\nAño: "))
    except ValueError:
        print("❌ Año inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    print("\n" + "="*60)
    print(f"📊 REPORTE ANUAL DE GASTOS - {anio}")
    print("="*60)
    
    # Total por mes
    print("\n📅 POR MES:")
    
    cursor.execute("""
        SELECT mes, SUM(monto) as total
        FROM gastos_operativos
        WHERE anio = ?
        GROUP BY mes
        ORDER BY mes
    """, (anio,))
    
    gastos_mes = cursor.fetchall()
    
    if not gastos_mes:
        print("\nNo hay gastos registrados para este año.")
        conexion.close()
        return
    
    total_anual = 0
    
    for gm in gastos_mes:
        mes_nombre = calendar.month_name[gm[0]]
        print(f"   {mes_nombre:12} ${gm[1]:>12,.2f}")
        total_anual += gm[1]
    
    print(f"\n{'='*60}")
    print(f"💰 TOTAL ANUAL: ${total_anual:,.2f}")
    print(f"📊 Promedio mensual: ${total_anual/12:,.2f}")
    print("="*60)
    
    # Por categoría anual
    print("\n📋 POR CATEGORÍA (AÑO COMPLETO):")
    
    cursor.execute("""
        SELECT categoria, SUM(monto) as total, COUNT(*) as cantidad
        FROM gastos_operativos
        WHERE anio = ?
        GROUP BY categoria
        ORDER BY total DESC
    """, (anio,))
    
    cats_anual = cursor.fetchall()
    
    for cat in cats_anual:
        porcentaje = (cat[1] / total_anual * 100)
        print(f"\n   {cat[0]}:")
        print(f"      💵 ${cat[1]:,.2f} ({porcentaje:.1f}%) - {cat[2]} gastos")
    
    conexion.close()


def menu_gastos():
    """Menú principal de gestión de gastos"""
    while True:
        print("\n" + "="*60)
        print("💰 GESTIÓN DE GASTOS OPERATIVOS")
        print("="*60)
        print("\n1. Registrar gasto")
        print("2. Ver gastos")
        print("3. Editar gasto")
        print("4. Eliminar gasto")
        print("5. Reporte mensual")
        print("6. Reporte anual")
        print("7. Volver")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            registrar_gasto()
        elif opcion == "2":
            ver_gastos()
        elif opcion == "3":
            editar_gasto()
        elif opcion == "4":
            eliminar_gasto()
        elif opcion == "5":
            reporte_gastos_mes()
        elif opcion == "6":
            reporte_gastos_anual()
        elif opcion == "7":
            break
        else:
            print("❌ Opción inválida.")


if __name__ == "__main__":
    menu_gastos()
