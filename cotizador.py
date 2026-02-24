from database import conectar
from datetime import datetime


def calcular_dias_noches(fecha_salida, fecha_regreso):
    """Calcula días y noches entre dos fechas"""
    try:
        salida = datetime.strptime(fecha_salida, "%d-%m-%Y")
        regreso = datetime.strptime(fecha_regreso, "%d-%m-%Y")
        dias = (regreso - salida).days + 1
        noches = dias - 1
        return dias, noches
    except:
        return 0, 0


def crear_cotizacion():
    """Crea una nueva cotización de viaje nacional"""
    print("\n" + "="*60)
    print("📝 NUEVA COTIZACIÓN - VIAJE NACIONAL")
    print("="*60)
    
    # ===== DATOS GENERALES =====
    nombre_viaje = input("\nNombre del viaje: ").strip()
    destino = input("Destino: ").strip()
    
    fecha_salida = input("Fecha de salida (DD-MM-YYYY): ").strip().replace("/", "-")
    fecha_regreso = input("Fecha de regreso (DD-MM-YYYY): ").strip().replace("/", "-")
    
    dias, noches = calcular_dias_noches(fecha_salida, fecha_regreso)
    
    if dias <= 0:
        print("❌ Fechas inválidas.")
        return
    
    print(f"\n✅ {dias} días / {noches} noches")
    
    try:
        personas_proyectadas = int(input("Personas proyectadas: "))
    except ValueError:
        print("❌ Número inválido.")
        return
    
    # ===== VUELOS =====
    print("\n" + "-"*60)
    print("✈️ VUELOS")
    print("-"*60)
    
    try:
        costo_vuelo_real = float(input("Costo real por persona: $"))
        precio_vuelo_venta = float(input("Precio venta por persona: $"))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    ganancia_vuelo_persona = precio_vuelo_venta - costo_vuelo_real
    ganancia_vuelo_total = ganancia_vuelo_persona * personas_proyectadas
    
    print(f"💰 Ganancia: ${ganancia_vuelo_persona} x persona | Total: ${ganancia_vuelo_total}")
    
    # ===== HOSPEDAJE =====
    print("\n" + "-"*60)
    print("🏨 HOSPEDAJE")
    print("-"*60)
    
    cantidad_hoteles = input("¿Un solo hotel o varios? (1/2): ").strip()
    
    hoteles = []
    
    if cantidad_hoteles == "1":
        num_hoteles = 1
    elif cantidad_hoteles == "2":
        try:
            num_hoteles = int(input("¿Cuántos hoteles?: "))
        except ValueError:
            num_hoteles = 1
    else:
        num_hoteles = 1
    
    costo_total_doble = 0
    precio_total_doble = 0
    costo_total_triple = 0
    precio_total_triple = 0
    
    for i in range(num_hoteles):
        print(f"\n--- Hotel {i+1} ---")
        nombre_hotel = input("Nombre del hotel: ").strip()
        
        try:
            noches_hotel = int(input(f"Noches en este hotel: "))
            
            print("\n💰 Base DOBLE:")
            costo_doble_noche = float(input("  Costo real por noche: $"))
            precio_doble_noche = float(input("  Precio venta por noche: $"))
            
            # Calcular total
            costo_doble_total = costo_doble_noche * noches_hotel
            precio_doble_total = precio_doble_noche * noches_hotel
            
            print(f"  ✅ Total {noches_hotel} noches: ${costo_doble_total:,.2f} / ${precio_doble_total:,.2f}")
            
            print("\n💰 Base TRIPLE:")
            costo_triple_noche = float(input("  Costo real por noche: $"))
            precio_triple_noche = float(input("  Precio venta por noche: $"))
            
            # Calcular total
            costo_triple_total = costo_triple_noche * noches_hotel
            precio_triple_total = precio_triple_noche * noches_hotel
            
            print(f"  ✅ Total {noches_hotel} noches: ${costo_triple_total:,.2f} / ${precio_triple_total:,.2f}")
            
            hoteles.append({
                "nombre": nombre_hotel,
                "noches": noches_hotel,
                "costo_doble": costo_doble_total,
                "precio_doble": precio_doble_total,
                "costo_triple": costo_triple_total,
                "precio_triple": precio_triple_total
            })
            
            costo_total_doble += costo_doble_total
            precio_total_doble += precio_doble_total
            costo_total_triple += costo_triple_total
            precio_total_triple += precio_triple_total
            
        except ValueError:
            print("❌ Valores inválidos.")
            return
    
    # ===== TRASLADOS =====
    print("\n" + "-"*60)
    print("🚌 TRASLADOS")
    print("-"*60)
    
    try:
        costo_traslados_total = float(input("Costo TOTAL del transporte: $"))
        precio_traslados_persona = float(input("Precio venta por persona: $"))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    costo_traslados_persona = costo_traslados_total / personas_proyectadas
    ganancia_traslados_persona = precio_traslados_persona - costo_traslados_persona
    ganancia_traslados_total = ganancia_traslados_persona * personas_proyectadas
    
    print(f"💰 Costo real x pax: ${costo_traslados_persona:.2f} | Ganancia: ${ganancia_traslados_persona:.2f} x persona")
    
    # ===== ENTRADAS/TOURS =====
    print("\n" + "-"*60)
    print("🎫 ENTRADAS/TOURS")
    print("-"*60)
    
    try:
        costo_entradas_real = float(input("Costo real por persona: $"))
        precio_entradas_venta = float(input("Precio venta por persona: $"))
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    ganancia_entradas_persona = precio_entradas_venta - costo_entradas_real
    ganancia_entradas_total = ganancia_entradas_persona * personas_proyectadas
    
    print(f"💰 Ganancia: ${ganancia_entradas_persona} x persona | Total: ${ganancia_entradas_total}")
    
    # ===== CALCULAR TOTALES =====
    precio_persona_doble = precio_vuelo_venta + precio_total_doble + precio_traslados_persona + precio_entradas_venta
    precio_persona_triple = precio_vuelo_venta + precio_total_triple + precio_traslados_persona + precio_entradas_venta
    
    # Inversión total (asumiendo mezcla de dobles y triples)
    inversion_vuelos = costo_vuelo_real * personas_proyectadas
    inversion_hoteles = (costo_total_doble * (personas_proyectadas / 2))  # Aproximado
    inversion_traslados = costo_traslados_total
    inversion_entradas = costo_entradas_real * personas_proyectadas
    
    inversion_total = inversion_vuelos + inversion_hoteles + inversion_traslados + inversion_entradas
    
    ganancia_proyectada = (ganancia_vuelo_total + ganancia_traslados_total + 
                           ganancia_entradas_total + 
                           ((precio_total_doble - costo_total_doble) * (personas_proyectadas / 2)))
    
    # ===== MOSTRAR RESUMEN =====
    print("\n" + "="*60)
    print("📊 RESUMEN DE COTIZACIÓN")
    print("="*60)
    
    print(f"\n🎯 PRECIO POR PERSONA (Base Doble):")
    print(f"   Vuelo:      ${precio_vuelo_venta}")
    print(f"   Hotel:      ${precio_total_doble}")
    print(f"   Traslados:  ${precio_traslados_persona}")
    print(f"   Entradas:   ${precio_entradas_venta}")
    print(f"   {'─'*30}")
    print(f"   TOTAL:      ${precio_persona_doble:.2f}")
    
    print(f"\n🎯 PRECIO POR PERSONA (Base Triple):")
    print(f"   Vuelo:      ${precio_vuelo_venta}")
    print(f"   Hotel:      ${precio_total_triple}")
    print(f"   Traslados:  ${precio_traslados_persona}")
    print(f"   Entradas:   ${precio_entradas_venta}")
    print(f"   {'─'*30}")
    print(f"   TOTAL:      ${precio_persona_triple:.2f}")
    
    print(f"\n💰 INVERSIÓN TOTAL: ${inversion_total:,.2f}")
    print(f"📈 GANANCIA PROYECTADA: ${ganancia_proyectada:,.2f}")
    
    # ===== GUARDAR =====
    guardar = input("\n¿Guardar cotización? (s/n): ").strip().lower()
    
    if guardar not in ['s', 'si', 'sí', 'yes', 'y']:
        print("❌ Cotización no guardada.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO cotizaciones_nacionales (
            nombre_viaje, destino, fecha_salida, fecha_regreso, dias, noches,
            personas_proyectadas, costo_vuelo_real, precio_vuelo_venta,
            costo_traslados_total, precio_traslados_persona,
            costo_entradas_real, precio_entradas_venta,
            precio_persona_doble, precio_persona_triple,
            inversion_total, ganancia_proyectada, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'BORRADOR', ?)
    """, (
        nombre_viaje, destino, fecha_salida, fecha_regreso, dias, noches,
        personas_proyectadas, costo_vuelo_real, precio_vuelo_venta,
        costo_traslados_total, precio_traslados_persona,
        costo_entradas_real, precio_entradas_venta,
        precio_persona_doble, precio_persona_triple,
        inversion_total, ganancia_proyectada, fecha_registro
    ))
    
    cotizacion_id = cursor.lastrowid
    
    # Guardar hoteles
    for hotel in hoteles:
        cursor.execute("""
            INSERT INTO hoteles_cotizacion (
                cotizacion_id, nombre_hotel, noches,
                costo_doble_real, precio_doble_venta,
                costo_triple_real, precio_triple_venta
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cotizacion_id, hotel["nombre"], hotel["noches"],
            hotel["costo_doble"], hotel["precio_doble"],
            hotel["costo_triple"], hotel["precio_triple"]
        ))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Cotización guardada con ID: {cotizacion_id}")


def ver_cotizaciones():
    """Muestra todas las cotizaciones"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre_viaje, destino, fecha_salida, fecha_regreso,
               dias, noches, personas_proyectadas,
               precio_persona_doble, precio_persona_triple,
               inversion_total, ganancia_proyectada, estado
        FROM cotizaciones_nacionales
        ORDER BY fecha_registro DESC
    """)
    
    cotizaciones = cursor.fetchall()
    conexion.close()
    
    print("\n" + "="*60)
    print("📋 COTIZACIONES DE VIAJES NACIONALES")
    print("="*60)
    
    if not cotizaciones:
        print("\nNo hay cotizaciones registradas.")
        return []
    
    for c in cotizaciones:
        print(f"\nID: {c[0]} | {c[12]}")
        print(f"Viaje: {c[1]}")
        print(f"Destino: {c[2]}")
        print(f"Fechas: {c[3]} al {c[4]} ({c[5]} días / {c[6]} noches)")
        print(f"Personas proyectadas: {c[7]}")
        print(f"Precio base doble: ${c[8]:,.2f}")
        print(f"Precio base triple: ${c[9]:,.2f}")
        print(f"Inversión: ${c[10]:,.2f} | Ganancia: ${c[11]:,.2f}")
        print("-" * 60)
    
    return cotizaciones


def obtener_cotizacion_por_id(id_cotizacion):
    """Obtiene una cotización completa por ID"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT * FROM cotizaciones_nacionales WHERE id = ?
    """, (id_cotizacion,))
    
    cotizacion = cursor.fetchone()
    conexion.close()
    
    if not cotizacion:
        return None
    
    return {
        "id": cotizacion[0],
        "nombre_viaje": cotizacion[1],
        "destino": cotizacion[2],
        "fecha_salida": cotizacion[3],
        "fecha_regreso": cotizacion[4],
        "dias": cotizacion[5],
        "noches": cotizacion[6],
        "personas_proyectadas": cotizacion[7],
        "precio_persona_doble": cotizacion[14],
        "precio_persona_triple": cotizacion[15]
    }
