from database import conectar
from datetime import datetime, timedelta
import urllib.request
import json
import re


def obtener_tipo_cambio_megatravel():
    """
    Obtiene el tipo de cambio USD/MXN desde Megatravel
    Si es sábado, usa el del viernes (restar 1 día)
    Si es domingo, usa el del viernes (restar 2 días)
    """
    try:
        # Verificar si es fin de semana
        hoy = datetime.now()
        dia_semana = hoy.weekday()  # 0=Lunes, 5=Sábado, 6=Domingo
        
        url = "https://www.megatravel.com.mx/"
        
        # Crear request con headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Buscar el tipo de cambio en el HTML
            # Patrón: "Tipo de\n\nCambio\n\n17.29" o similar
            patron = r'Tipo de\s+Cambio\s+([\d.]+)'
            match = re.search(patron, html)
            
            if match:
                tipo_cambio = float(match.group(1))
                
                # Mostrar mensaje si es fin de semana
                if dia_semana == 5:  # Sábado
                    print(f"\n📅 Hoy es sábado. Usando tipo de cambio del viernes.")
                elif dia_semana == 6:  # Domingo
                    print(f"\n📅 Hoy es domingo. Usando tipo de cambio del viernes.")
                
                print(f"💱 Tipo de cambio Megatravel: $1 USD = ${tipo_cambio:.2f} MXN")
                return tipo_cambio
            else:
                print("⚠️ No se pudo extraer el tipo de cambio de Megatravel.")
                return None
                
    except Exception as e:
        print(f"⚠️ Error al obtener tipo de cambio de Megatravel: {e}")
        return None


def obtener_tipo_cambio():
    """
    Obtiene el tipo de cambio USD/MXN
    Primero intenta desde Megatravel, luego API de respaldo
    """
    # Intentar obtener de Megatravel primero
    tipo_cambio = obtener_tipo_cambio_megatravel()
    
    if tipo_cambio:
        return tipo_cambio
    
    # Si falla, intentar API de respaldo
    try:
        print("\n⚠️ Intentando API de respaldo...")
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            tipo_cambio = data['rates']['MXN']
            print(f"💱 Tipo de cambio (API respaldo): $1 USD = ${tipo_cambio:.2f} MXN")
            return tipo_cambio
    except:
        # Si todo falla, permitir ingreso manual
        return None


def registrar_viaje_internacional():
    """Registra un nuevo viaje internacional"""
    print("\n" + "="*60)
    print("🌎 REGISTRAR NUEVO VIAJE INTERNACIONAL")
    print("="*60)
    
    destino = input("\nDestino: ").strip()
    fecha_salida = input("Fecha de salida (DD-MM-YYYY): ").strip().replace("/", "-")
    fecha_regreso = input("Fecha de regreso (DD-MM-YYYY): ").strip().replace("/", "-")
    
    try:
        salida = datetime.strptime(fecha_salida, "%d-%m-%Y")
        regreso = datetime.strptime(fecha_regreso, "%d-%m-%Y")
        dias = (regreso - salida).days + 1
        noches = dias - 1
    except:
        print("❌ Fechas inválidas.")
        return
    
    print(f"\n✅ {dias} días / {noches} noches")
    
    try:
        cupos_totales = int(input("Pasajeros proyectados: "))
        
        print("\n💵 PRECIOS (USD):")
        precio_adulto_doble = float(input("Precio adulto base doble (USD): $"))
        precio_adulto_triple = float(input("Precio adulto base triple (USD): $"))
        precio_menor_doble = float(input("Precio menor base doble (USD): $"))
        precio_menor_triple = float(input("Precio menor base triple (USD): $"))
        
        porcentaje_ganancia = float(input("\nPorcentaje de ganancia (%): "))
        
    except ValueError:
        print("❌ Valores inválidos.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO viajes_internacionales (
            destino, fecha_salida, fecha_regreso, dias, noches,
            cupos_totales, cupos_vendidos, cupos_disponibles,
            precio_adulto_doble_usd, precio_adulto_triple_usd,
            precio_menor_doble_usd, precio_menor_triple_usd,
            porcentaje_ganancia, estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, 'ACTIVO', ?)
    """, (
        destino, fecha_salida, fecha_regreso, dias, noches,
        cupos_totales, cupos_totales,
        precio_adulto_doble, precio_adulto_triple,
        precio_menor_doble, precio_menor_triple,
        porcentaje_ganancia, fecha_registro
    ))
    
    viaje_id = cursor.lastrowid
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Viaje internacional registrado con ID: {viaje_id}")


def ver_viajes_internacionales():
    """Muestra todos los viajes internacionales activos"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, destino, fecha_salida, fecha_regreso,
               cupos_totales, cupos_vendidos, cupos_disponibles, estado
        FROM viajes_internacionales
        WHERE estado = 'ACTIVO'
        ORDER BY fecha_salida
    """)
    
    viajes = cursor.fetchall()
    conexion.close()
    
    print("\n" + "="*60)
    print("🌎 VIAJES INTERNACIONALES ACTIVOS")
    print("="*60)
    
    if not viajes:
        print("\nNo hay viajes internacionales activos.")
        return
    
    for v in viajes:
        print(f"\nID: {v[0]}")
        print(f"Destino: {v[1]}")
        print(f"Fechas: {v[2]} al {v[3]}")
        print(f"Cupos: {v[5]} vendidos / {v[4]} totales ({v[6]} disponibles)")
        print(f"Estado: {v[7]}")
        print("-" * 60)


def registrar_cliente_internacional():
    """Registra un cliente en un viaje internacional"""
    print("\n" + "="*60)
    print("👤 REGISTRAR CLIENTE EN VIAJE INTERNACIONAL")
    print("="*60)
    
    # Mostrar viajes disponibles
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, destino, cupos_disponibles,
               precio_adulto_doble_usd, precio_adulto_triple_usd
        FROM viajes_internacionales
        WHERE estado = 'ACTIVO' AND cupos_disponibles > 0
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes disponibles.")
        conexion.close()
        return
    
    print("\n🌎 VIAJES DISPONIBLES:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]} | Disponibles: {v[2]} cupos")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener datos del viaje
    cursor.execute("""
        SELECT destino, cupos_disponibles,
               precio_adulto_doble_usd, precio_adulto_triple_usd,
               precio_menor_doble_usd, precio_menor_triple_usd,
               porcentaje_ganancia
        FROM viajes_internacionales
        WHERE id = ?
    """, (viaje_id,))
    
    viaje = cursor.fetchone()
    
    if not viaje:
        print("❌ Viaje no encontrado.")
        conexion.close()
        return
    
    print(f"\n✅ Destino: {viaje[0]}")
    print(f"Precio adulto doble: ${viaje[2]:,.2f} USD")
    print(f"Precio adulto triple: ${viaje[3]:,.2f} USD")
    print(f"Precio menor doble: ${viaje[4]:,.2f} USD")
    print(f"Precio menor triple: ${viaje[5]:,.2f} USD")
    
    # ===== DATOS DEL CLIENTE =====
    print("\n--- DATOS DEL CLIENTE ---")
    
    nombre_cliente = input("Nombre del cliente: ").strip()
    
    try:
        adultos = int(input("Número de adultos: "))
        menores = int(input("Número de menores: "))
    except ValueError:
        print("❌ Números inválidos.")
        conexion.close()
        return
    
    total_personas = adultos + menores
    
    if total_personas > viaje[1]:
        print(f"❌ Solo hay {viaje[1]} cupos disponibles.")
        conexion.close()
        return
    
    # ===== DISTRIBUCIÓN DE HABITACIONES =====
    print("\n--- DISTRIBUCIÓN DE HABITACIONES ---")
    
    try:
        hab_dobles = int(input("Habitaciones dobles: "))
        hab_triples = int(input("Habitaciones triples: "))
    except ValueError:
        print("❌ Valores inválidos.")
        conexion.close()
        return
    
    # Contar adultos y menores por habitación
    adultos_doble = hab_dobles * 2
    adultos_triple = hab_triples * 3
    
    # Calcular total
    total_adultos_doble = adultos_doble * viaje[2]
    total_adultos_triple = adultos_triple * viaje[3]
    total_menores_doble = 0
    total_menores_triple = 0
    
    # Distribuir menores si hay
    if menores > 0:
        print(f"\n--- DISTRIBUCIÓN DE {menores} MENORES ---")
        print("Ingresa cuántos menores van en cada tipo de habitación:")
        try:
            menores_doble = int(input(f"  Menores en habitaciones dobles (max {hab_dobles * 2}): "))
            menores_triple = int(input(f"  Menores en habitaciones triples (max {hab_triples * 1}): "))
            
            if menores_doble + menores_triple != menores:
                print("❌ La suma no coincide con el total de menores.")
                conexion.close()
                return
            
            total_menores_doble = menores_doble * viaje[4]
            total_menores_triple = menores_triple * viaje[5]
            
        except ValueError:
            print("❌ Valores inválidos.")
            conexion.close()
            return
    
    total_usd = total_adultos_doble + total_adultos_triple + total_menores_doble + total_menores_triple
    ganancia_usd = total_usd * (viaje[6] / 100)
    
    print(f"\n--- RESUMEN (USD) ---")
    if hab_dobles > 0:
        print(f"{hab_dobles} habitación(es) doble:")
        print(f"  {adultos_doble} adultos x ${viaje[2]:,.2f} = ${total_adultos_doble:,.2f}")
        if menores > 0 and total_menores_doble > 0:
            print(f"  {menores_doble} menores x ${viaje[4]:,.2f} = ${total_menores_doble:,.2f}")
    
    if hab_triples > 0:
        print(f"{hab_triples} habitación(es) triple:")
        print(f"  {adultos_triple} adultos x ${viaje[3]:,.2f} = ${total_adultos_triple:,.2f}")
        if menores > 0 and total_menores_triple > 0:
            print(f"  {menores_triple} menores x ${viaje[5]:,.2f} = ${total_menores_triple:,.2f}")
    
    print(f"\nTOTAL: ${total_usd:,.2f} USD")
    print(f"Ganancia proyectada: ${ganancia_usd:,.2f} USD ({viaje[6]:.1f}%)")
    
    # ===== ABONO INICIAL =====
    print("\n--- ABONO INICIAL ---")
    
    # Seleccionar moneda
    print("1. USD")
    print("2. MXN")
    
    moneda_opcion = input("Moneda del abono (1/2): ").strip()
    
    if moneda_opcion == "1":
        moneda = "USD"
        try:
            abono_usd = float(input("Monto del abono (USD): $"))
        except ValueError:
            print("❌ Monto inválido.")
            conexion.close()
            return
        
        tipo_cambio = 1.0
        monto_original = abono_usd
        
    elif moneda_opcion == "2":
        moneda = "MXN"
        
        # Obtener tipo de cambio de Megatravel
        tipo_cambio = obtener_tipo_cambio()
        
        if tipo_cambio:
            usar_actual = input("¿Usar este tipo de cambio? (s/n): ").strip().lower()
            
            if usar_actual not in ['s', 'si', 'sí', 'yes', 'y']:
                try:
                    tipo_cambio = float(input("Ingresa tipo de cambio manual: $"))
                except ValueError:
                    print("❌ Tipo de cambio inválido.")
                    conexion.close()
                    return
        else:
            try:
                tipo_cambio = float(input("Ingresa tipo de cambio del día: $"))
            except ValueError:
                print("❌ Tipo de cambio inválido.")
                conexion.close()
                return
        
        try:
            monto_original = float(input("Monto del abono (MXN): $"))
        except ValueError:
            print("❌ Monto inválido.")
            conexion.close()
            return
        
        abono_usd = monto_original / tipo_cambio
        
        print(f"\n💵 ${monto_original:,.2f} MXN ÷ {tipo_cambio:.2f} = ${abono_usd:.2f} USD")
    
    else:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    if abono_usd > total_usd:
        print(f"❌ El abono (${abono_usd:,.2f} USD) es mayor al total (${total_usd:,.2f} USD).")
        conexion.close()
        return
    
    saldo_usd = total_usd - abono_usd
    
    # ===== GUARDAR CLIENTE =====
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO clientes_internacionales (
            viaje_id, nombre_cliente, adultos, menores,
            habitaciones_doble, habitaciones_triple,
            total_usd, abonado_usd, saldo_usd, ganancia_usd,
            estado, fecha_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ADEUDO', ?)
    """, (
        viaje_id, nombre_cliente, adultos, menores,
        hab_dobles, hab_triples,
        total_usd, abono_usd, saldo_usd, ganancia_usd,
        fecha_registro
    ))
    
    cliente_id = cursor.lastrowid
    
    # Registrar abono inicial
    cursor.execute("""
        INSERT INTO abonos_internacionales (
            cliente_id, fecha, moneda, monto_original, tipo_cambio, monto_usd
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, fecha_registro, moneda, monto_original, tipo_cambio, abono_usd))
    
    # ===== REGISTRAR PASAJEROS =====
    print("\n--- REGISTRO DE PASAJEROS ---")
    
    pasajeros_registrados = []
    
    # Registrar por habitaciones DOBLES
    for i in range(hab_dobles):
        print(f"\n--- HABITACIÓN DOBLE {i+1} ---")
        for j in range(2):
            nombre = input(f"Pasajero {j+1}: ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "ADULTO",
                "habitacion": f"Doble {i+1}"
            })
    
    # Registrar por habitaciones TRIPLES
    for i in range(hab_triples):
        print(f"\n--- HABITACIÓN TRIPLE {i+1} ---")
        for j in range(3):
            nombre = input(f"Pasajero {j+1}: ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "ADULTO",
                "habitacion": f"Triple {i+1}"
            })
    
    # Registrar MENORES (si hay)
    if menores > 0:
        print(f"\n--- MENORES ({menores}) ---")
        for i in range(menores):
            nombre = input(f"Menor {i+1}: ").strip()
            hab = input(f"  ¿En qué habitación? (ej: Doble 1): ").strip()
            pasajeros_registrados.append({
                "nombre": nombre,
                "tipo": "MENOR",
                "habitacion": hab
            })
    
    # Guardar en BD
    for pasajero in pasajeros_registrados:
        cursor.execute("""
            INSERT INTO pasajeros_internacionales (
                cliente_id, nombre_completo, tipo, habitacion_asignada
            ) VALUES (?, ?, ?, ?)
        """, (cliente_id, pasajero["nombre"], pasajero["tipo"], pasajero["habitacion"]))
    
    # Actualizar cupos del viaje
    cursor.execute("""
        UPDATE viajes_internacionales
        SET cupos_vendidos = cupos_vendidos + ?,
            cupos_disponibles = cupos_disponibles - ?
        WHERE id = ?
    """, (total_personas, total_personas, viaje_id))
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✅ Cliente registrado correctamente.")
    print(f"💵 Total: ${total_usd:,.2f} USD")
    print(f"💰 Abonado: ${abono_usd:,.2f} USD")
    print(f"📊 Saldo: ${saldo_usd:,.2f} USD")


def ver_clientes_internacionales():
    """Muestra todos los clientes de un viaje internacional"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Mostrar viajes
    cursor.execute("""
        SELECT id, destino FROM viajes_internacionales
        WHERE estado = 'ACTIVO'
    """)
    
    viajes = cursor.fetchall()
    
    if not viajes:
        print("\n❌ No hay viajes activos.")
        conexion.close()
        return
    
    print("\n🌎 VIAJES ACTIVOS:\n")
    for v in viajes:
        print(f"{v[0]}. {v[1]}")
    
    try:
        viaje_id = int(input("\nSelecciona ID del viaje: "))
    except ValueError:
        print("❌ ID inválido.")
        conexion.close()
        return
    
    # Obtener clientes
    cursor.execute("""
        SELECT c.id, c.nombre_cliente, c.adultos, c.menores,
               c.total_usd, c.abonado_usd, c.saldo_usd, c.estado
        FROM clientes_internacionales c
        WHERE c.viaje_id = ?
        ORDER BY c.fecha_registro
    """, (viaje_id,))
    
    clientes = cursor.fetchall()
    
    print("\n" + "="*60)
    print("👥 CLIENTES DEL VIAJE")
    print("="*60)
    
    if not clientes:
        print("\nNo hay clientes registrados.")
        conexion.close()
        return
    
    for c in clientes:
        cliente_id = c[0]
        estado_icon = "✅" if c[7] == "LIQUIDADO" else "⏳"
        
        print(f"\n{estado_icon} ID: {cliente_id} | {c[1]}")
        print(f"   {c[2]} adultos, {c[3]} menores")
        
        # DESGLOSE
        print(f"\n   💵 DESGLOSE (USD):")
        print(f"      Total: ${c[4]:,.2f}")
        print(f"      Abonado: ${c[5]:,.2f}")
        print(f"      Saldo: ${c[6]:,.2f}")
        print(f"      Estado: {c[7]}")
        
        # Mostrar historial de abonos
        cursor.execute("""
            SELECT fecha, moneda, monto_original, tipo_cambio, monto_usd
            FROM abonos_internacionales
            WHERE cliente_id = ?
            ORDER BY fecha
        """, (cliente_id,))
        
        abonos = cursor.fetchall()
        
        if abonos:
            print(f"\n   📅 Historial de abonos:")
            for abono in abonos:
                if abono[1] == "USD":
                    print(f"      {abono[0]} - ${abono[4]:,.2f} USD")
                else:
                    print(f"      {abono[0]} - ${abono[2]:,.2f} MXN (@ {abono[3]:.2f}) = ${abono[4]:,.2f} USD")
        
        print("-" * 60)
    
    conexion.close()


def registrar_abono_internacional():
    """Registra un abono de un cliente internacional"""
    ver_clientes_internacionales()
    
    try:
        cliente_id = int(input("\nID del cliente: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Obtener datos del cliente
    cursor.execute("""
        SELECT nombre_cliente, saldo_usd FROM clientes_internacionales WHERE id = ?
    """, (cliente_id,))
    
    cliente = cursor.fetchone()
    
    if not cliente:
        print("❌ Cliente no encontrado.")
        conexion.close()
        return
    
    print(f"\nCliente: {cliente[0]}")
    print(f"Saldo actual: ${cliente[1]:,.2f} USD")
    
    # Seleccionar moneda
    print("\n1. USD")
    print("2. MXN")
    
    moneda_opcion = input("Moneda del abono (1/2): ").strip()
    
    if moneda_opcion == "1":
        moneda = "USD"
        try:
            monto_usd = float(input("Monto del abono (USD): $"))
        except ValueError:
            print("❌ Monto inválido.")
            conexion.close()
            return
        
        tipo_cambio = 1.0
        monto_original = monto_usd
        
    elif moneda_opcion == "2":
        moneda = "MXN"
        
        # Obtener tipo de cambio de Megatravel
        tipo_cambio = obtener_tipo_cambio()
        
        if tipo_cambio:
            usar_actual = input("¿Usar este tipo de cambio? (s/n): ").strip().lower()
            
            if usar_actual not in ['s', 'si', 'sí', 'yes', 'y']:
                try:
                    tipo_cambio = float(input("Ingresa tipo de cambio manual: $"))
                except ValueError:
                    print("❌ Tipo de cambio inválido.")
                    conexion.close()
                    return
        else:
            try:
                tipo_cambio = float(input("Ingresa tipo de cambio del día: $"))
            except ValueError:
                print("❌ Tipo de cambio inválido.")
                conexion.close()
                return
        
        try:
            monto_original = float(input("Monto del abono (MXN): $"))
        except ValueError:
            print("❌ Monto inválido.")
            conexion.close()
            return
        
        monto_usd = monto_original / tipo_cambio
        
        print(f"\n💵 ${monto_original:,.2f} MXN ÷ {tipo_cambio:.2f} = ${monto_usd:.2f} USD")
    
    else:
        print("❌ Opción inválida.")
        conexion.close()
        return
    
    if monto_usd > cliente[1]:
        print(f"❌ El abono (${monto_usd:,.2f} USD) es mayor al saldo (${cliente[1]:,.2f} USD).")
        conexion.close()
        return
    
    # Registrar abono
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO abonos_internacionales (
            cliente_id, fecha, moneda, monto_original, tipo_cambio, monto_usd
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, fecha_actual, moneda, monto_original, tipo_cambio, monto_usd))
    
    # Actualizar cliente
    nuevo_saldo = cliente[1] - monto_usd
    
    cursor.execute("""
        UPDATE clientes_internacionales
        SET abonado_usd = abonado_usd + ?,
            saldo_usd = saldo_usd - ?
        WHERE id = ?
    """, (monto_usd, monto_usd, cliente_id))
    
    # Si liquidó, cambiar estado
    if nuevo_saldo <= 0.01:  # Tolerancia de 1 centavo
        cursor.execute("""
            UPDATE clientes_internacionales
            SET estado = 'LIQUIDADO', saldo_usd = 0
            WHERE id = ?
        """, (cliente_id,))
        print(f"\n🎉 {cliente[0]} ha LIQUIDADO su viaje!")
    else:
        print(f"\n✅ Abono registrado. Saldo restante: ${nuevo_saldo:,.2f} USD")
    
    conexion.commit()
    conexion.close()
