"""
Script de migración de datos de SQLite a PostgreSQL (Neon)
Usage: python migrar_a_neon.py
"""

import sqlite3
import psycopg2
import os
import sys

# URL de Neon - REEMPLAZA ESTO CON TU URL
NEON_URL = "postgresql://neondb_owner:npg_Y4GIaHWQuLP2@ep-icy-band-aicyuekj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

SQLITE_DB = "agencia.db"

def get_sqlite_connection():
    """Conectar a SQLite local"""
    return sqlite3.connect(SQLITE_DB)

def get_pg_connection():
    """Conectar a Neon PostgreSQL"""
    return psycopg2.connect(NEON_URL)

def crear_tablas_pg(cursor):
    """Crear tablas en PostgreSQL"""
    # Tabla usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    # Tabla vendedoras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedoras (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            activa INTEGER DEFAULT 1,
            fecha_registro TEXT
        )
    """)

    # Tabla hoteles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hoteles (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            destino TEXT DEFAULT 'Riviera Maya',
            all_inclusive INTEGER DEFAULT 1,
            activo INTEGER DEFAULT 1,
            veces_usado INTEGER DEFAULT 0,
            fecha_registro TEXT
        )
    """)

    # Tabla bloqueos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bloqueos (
            id SERIAL PRIMARY KEY,
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

    # Tabla ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id SERIAL PRIMARY KEY,
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
            vendedora_id INTEGER,
            usuario_id INTEGER,
            es_bloqueo INTEGER DEFAULT 0,
            bloqueo_id INTEGER,
            fecha_pago_comision TEXT,
            fecha_registro TEXT NOT NULL
        )
    """)

    # Tabla abonos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abonos (
            id SERIAL PRIMARY KEY,
            venta_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)

    # Tabla pasajeros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasajeros (
            id SERIAL PRIMARY KEY,
            venta_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)

    # Tabla grupos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            fecha_salida TEXT NOT NULL,
            fecha_regreso TEXT NOT NULL,
            hotel TEXT NOT NULL,
            adultos INTEGER NOT NULL,
            menores INTEGER NOT NULL,
            precio_total REAL NOT NULL,
            estado TEXT DEFAULT 'ACTIVO',
            observaciones TEXT,
            fecha_registro TEXT NOT NULL
        )
    """)

    # Tabla ventas_grupos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas_grupos (
            id SERIAL PRIMARY KEY,
            grupo_id INTEGER NOT NULL,
            cliente TEXT NOT NULL,
            adultos INTEGER NOT NULL,
            menores INTEGER NOT NULL,
            precio REAL NOT NULL,
            pagado REAL DEFAULT 0,
            saldo REAL NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            fecha_registro TEXT NOT NULL
        )
    """)

    # Tabla config_comisiones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_comisiones (
            id SERIAL PRIMARY KEY,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            meta_ventas REAL NOT NULL,
            comision_porcentaje REAL NOT NULL,
            UNIQUE(anio, mes)
        )
    """)

    # Tabla historial_comisiones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_comisiones (
            id SERIAL PRIMARY KEY,
            vendedora_id INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            ventas_totales REAL NOT NULL,
            comision REAL NOT NULL,
            pagada INTEGER DEFAULT 0,
            fecha_pago TEXT,
            fecha_registro TEXT NOT NULL
        )
    """)

    print("✅ Tablas creadas en PostgreSQL")

def migrar_tabla(sqlite_conn, pg_conn, tabla):
    """Migrar una tabla de SQLite a PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()

    # Obtener datos de SQLite
    sqlite_cursor.execute(f"SELECT * FROM {tabla}")
    filas = sqlite_cursor.fetchall()

    if not filas:
        print(f"  ⏭️ {tabla}: Sin datos")
        return 0

    # Obtener nombres de columnas
    columnas = [desc[0] for desc in sqlite_cursor.description]

    # Obtener tipos de columnas de SQLite para conversión
    sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
    info_columnas = {row[1]: row[2] for row in sqlite_cursor.fetchall()}

    # Obtener estructura de PostgreSQL
    pg_cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tabla}'")
    pg_columnas = {row[0]: row[1] for row in pg_cursor.fetchall()}

    # Insertar datos
    placeholders = ','.join(['%s'] * len(columnas))
    columnas_str = ','.join(columnas)

    insertados = 0
    for fila in filas:
        try:
            valores = []
            for i, col in enumerate(columnas):
                val = fila[i]
                # Convertir tipos si es necesario
                if val is None:
                    valores.append(None)
                elif 'INTEGER' in info_columnas.get(col, '').upper():
                    valores.append(int(val) if val else 0)
                elif 'REAL' in info_columnas.get(col, '').upper() or 'FLOAT' in info_columnas.get(col, '').upper():
                    valores.append(float(val) if val else 0.0)
                else:
                    valores.append(str(val) if val else '')

            pg_cursor.execute(f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})", valores)
            insertados += 1
        except Exception as e:
            # Ignorar errores de duplicados o tipos
            pass

    pg_conn.commit()
    print(f"  ✅ {tabla}: {insertados} registros migrados")
    return insertados

def migrar_datos():
    """Ejecutar la migración completa"""
    print("🔄 Iniciando migración de SQLite a Neon PostgreSQL...")
    print()

    # Conectar a SQLite
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Error: No se encontró {SQLITE_DB}")
        return

    sqlite_conn = get_sqlite_connection()
    print(f"✅ Conectado a SQLite: {SQLITE_DB}")

    # Conectar a PostgreSQL
    try:
        pg_conn = get_pg_connection()
        print("✅ Conectado a Neon PostgreSQL")
    except Exception as e:
        print(f"❌ Error conectando a Neon: {e}")
        return

    # Crear tablas
    pg_cursor = pg_conn.cursor()
    crear_tablas_pg(pg_cursor)
    pg_conn.commit()

    # Lista de tablas a migrar (en orden para respetar foreign keys)
    tablas = [
        'usuarios',
        'vendedoras',
        'operadores',
        'hoteles',
        'bloqueos',
        'ventas',
        'abonos',
        'pasajeros',
        'grupos',
        'ventas_grupos',
        'config_comisiones',
        'historial_comisiones',
        'transferencias',
    ]

    print()
    print("📦 Migrando datos...")
    print()

    total = 0
    for tabla in tablas:
        try:
            count = migrar_tabla(sqlite_conn, pg_conn, tabla)
            total += count
        except Exception as e:
            print(f"  ⚠️ {tabla}: {e}")

    print()
    print(f"🎉 Migración completada: {total} registros transferidos")

    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrar_datos()
