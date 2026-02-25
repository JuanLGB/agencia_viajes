import sqlite3

DB_NAME = "agencia.db"

def conectar():
    """Establece conexión con la base de datos"""
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    """Crea todas las tablas necesarias para el sistema"""
    conexion = conectar()
    cursor = conexion.cursor()

    # ===== TABLA USUARIOS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # ===== TABLA VENDEDORAS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            activa INTEGER DEFAULT 1,
            fecha_registro TEXT NOT NULL
        )
    """)

    # ===== TABLA BLOQUEOS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bloqueos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            noches INTEGER NOT NULL,
            habitaciones_totales INTEGER NOT NULL,
            habitaciones_vendidas INTEGER DEFAULT 0,
            habitaciones_disponibles INTEGER NOT NULL,
            precio_noche_doble REAL NOT NULL,
            precio_noche_triple REAL NOT NULL,
            precio_noche_cuadruple REAL NOT NULL,
            precio_menor_doble REAL DEFAULT 0,
            precio_menor_triple REAL DEFAULT 0,
            precio_menor_cuadruple REAL DEFAULT 0,
            costo_real REAL,
            estado TEXT DEFAULT 'ACTIVO',
            fecha_registro TEXT NOT NULL
        )
    """)

    # ===== TABLA HOTELES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoteles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            destino TEXT DEFAULT 'Riviera Maya',
            all_inclusive INTEGER DEFAULT 1,
            activo INTEGER DEFAULT 1,
            veces_usado INTEGER DEFAULT 0,
            fecha_registro TEXT NOT NULL
        )
    """)

    # ===== TABLA COTIZACIONES NACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_nacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_viaje TEXT NOT NULL,
            destino TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            fecha_regreso TEXT NOT NULL,
            dias INTEGER NOT NULL,
            noches INTEGER NOT NULL,
            personas_proyectadas INTEGER NOT NULL,
            
            costo_vuelo_real REAL DEFAULT 0,
            precio_vuelo_venta REAL DEFAULT 0,
            
            costo_traslados_total REAL DEFAULT 0,
            precio_traslados_persona REAL DEFAULT 0,
            
            costo_entradas_real REAL DEFAULT 0,
            precio_entradas_venta REAL DEFAULT 0,
            
            precio_persona_doble REAL DEFAULT 0,
            precio_persona_triple REAL DEFAULT 0,
            
            inversion_total REAL DEFAULT 0,
            ganancia_proyectada REAL DEFAULT 0,
            
            estado TEXT DEFAULT 'BORRADOR',
            fecha_registro TEXT NOT NULL
        )
    """)

    # ===== TABLA HOTELES COTIZACION =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoteles_cotizacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cotizacion_id INTEGER NOT NULL,
            nombre_hotel TEXT NOT NULL,
            noches INTEGER NOT NULL,
            costo_doble_real REAL NOT NULL,
            precio_doble_venta REAL NOT NULL,
            costo_triple_real REAL NOT NULL,
            precio_triple_venta REAL NOT NULL,
            FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones_nacionales(id)
        )
    """)

    # ===== TABLA VIAJES NACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viajes_nacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cotizacion_id INTEGER,
            nombre_viaje TEXT NOT NULL,
            destino TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            fecha_regreso TEXT NOT NULL,
            dias INTEGER NOT NULL,
            noches INTEGER NOT NULL,
            cupos_totales INTEGER NOT NULL,
            cupos_vendidos INTEGER DEFAULT 0,
            cupos_disponibles INTEGER NOT NULL,
            precio_persona_doble REAL NOT NULL,
            precio_persona_triple REAL NOT NULL,
            estado TEXT DEFAULT 'ACTIVO',
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones_nacionales(id)
        )
    """)

    # ===== TABLA CLIENTES NACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_nacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viaje_id INTEGER NOT NULL,
            vendedora_id INTEGER NOT NULL,
            nombre_cliente TEXT NOT NULL,
            adultos INTEGER NOT NULL,
            menores INTEGER DEFAULT 0,
            habitaciones_doble INTEGER DEFAULT 0,
            habitaciones_triple INTEGER DEFAULT 0,
            total_pagar REAL NOT NULL,
            total_abonado REAL DEFAULT 0,
            saldo REAL NOT NULL,
            estado TEXT DEFAULT 'ADEUDO',
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (viaje_id) REFERENCES viajes_nacionales(id),
            FOREIGN KEY (vendedora_id) REFERENCES vendedoras(id)
        )
    """)

    # ===== TABLA PASAJEROS NACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasajeros_nacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            nombre_completo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            habitacion_asignada TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes_nacionales(id)
        )
    """)

    # ===== TABLA ABONOS NACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos_nacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            vendedora_id INTEGER NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes_nacionales(id),
            FOREIGN KEY (vendedora_id) REFERENCES vendedoras(id)
        )
    """)

    # ===== TABLA VIAJES INTERNACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viajes_internacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destino TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            fecha_regreso TEXT NOT NULL,
            dias INTEGER NOT NULL,
            noches INTEGER NOT NULL,
            cupos_totales INTEGER NOT NULL,
            cupos_vendidos INTEGER DEFAULT 0,
            cupos_disponibles INTEGER NOT NULL,
            precio_adulto_doble_usd REAL NOT NULL,
            precio_adulto_triple_usd REAL NOT NULL,
            precio_menor_doble_usd REAL NOT NULL,
            precio_menor_triple_usd REAL NOT NULL,
            porcentaje_ganancia REAL DEFAULT 0,
            estado TEXT DEFAULT 'ACTIVO',
            fecha_registro TEXT NOT NULL
        )
    """)

    # ===== TABLA CLIENTES INTERNACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_internacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viaje_id INTEGER NOT NULL,
            nombre_cliente TEXT NOT NULL,
            adultos INTEGER NOT NULL,
            menores INTEGER DEFAULT 0,
            habitaciones_doble INTEGER DEFAULT 0,
            habitaciones_triple INTEGER DEFAULT 0,
            total_usd REAL NOT NULL,
            abonado_usd REAL DEFAULT 0,
            saldo_usd REAL NOT NULL,
            ganancia_usd REAL DEFAULT 0,
            estado TEXT DEFAULT 'ADEUDO',
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (viaje_id) REFERENCES viajes_internacionales(id)
        )
    """)

    # ===== TABLA PASAJEROS INTERNACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasajeros_internacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            nombre_completo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            habitacion_asignada TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes_internacionales(id)
        )
    """)

    # ===== TABLA ABONOS INTERNACIONALES =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos_internacionales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            moneda TEXT NOT NULL,
            monto_original REAL NOT NULL,
            tipo_cambio REAL DEFAULT 1.0,
            monto_usd REAL NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes_internacionales(id)
        )
    """)

    # ===== TABLA VENTAS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            tipo_venta TEXT NOT NULL,
            destino TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            noches INTEGER NOT NULL,
            adultos INTEGER NOT NULL,
            menores INTEGER NOT NULL,
            tipo_habitacion TEXT,
            precio_adulto REAL NOT NULL,
            precio_menor REAL NOT NULL,
            precio_total REAL NOT NULL,
            porcentaje_ganancia REAL NOT NULL,
            ganancia REAL NOT NULL,
            costo_mayorista REAL NOT NULL,
            pagado REAL DEFAULT 0,
            saldo REAL NOT NULL,
            comision_vendedora REAL DEFAULT 0,
            comision_pagada INTEGER DEFAULT 0,
            estado TEXT NOT NULL,
            vendedora_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            es_bloqueo INTEGER DEFAULT 0,
            bloqueo_id INTEGER,
            fecha_registro TEXT NOT NULL,
            FOREIGN KEY (vendedora_id) REFERENCES vendedoras(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (bloqueo_id) REFERENCES bloqueos(id)
        )
    """)

    # ===== TABLA PASAJEROS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasajeros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    """)

    # ===== TABLA ABONOS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    """)

    # ===== TABLA TRANSFERENCIAS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nombre_envia TEXT NOT NULL,
            cantidad REAL NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            aplicado_en TEXT,
            fecha_aplicacion TEXT,
            observaciones TEXT,
            id_vendedora INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_vendedora) REFERENCES vendedoras(id)
        )
    """)

    # ===== AGREGAR COLUMNA fecha_pago_comision SI NO EXISTE =====
    try:
        cursor.execute("ALTER TABLE ventas ADD COLUMN fecha_pago_comision TEXT")
        conexion.commit()
    except:
        pass  # La columna ya existe

    conexion.commit()
    conexion.close()
    print("✅ Base de datos creada correctamente.")


if __name__ == "__main__":
    crear_tablas()
