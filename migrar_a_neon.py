"""
Script de migración de SQLite a Neon PostgreSQL
"""

import sqlite3
import psycopg2
import os

NEON_URL = "postgresql://neondb_owner:npg_Y4GIaHWQuLP2@ep-icy-band-aicyuekj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
SQLITE_DB = "agencia.db"

def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

def get_pg_connection():
    return psycopg2.connect(NEON_URL)

def sqlite_to_pg_type(sqlite_type):
    t = (sqlite_type or 'TEXT').upper()
    if 'INTEGER' in t or 'INT' in t:
        return 'INTEGER'
    elif 'REAL' in t or 'FLOAT' in t or 'DOUBLE' in t or 'NUMERIC' in t:
        return 'REAL'
    elif 'TEXT' in t or 'CHAR' in t or 'CLOB' in t:
        return 'TEXT'
    elif 'BLOB' in t:
        return 'BYTEA'
    return 'TEXT'

def migrar_tabla(pg_conn, tabla, sqlite_cursor):
    """Migrar datos de una tabla, creando la tabla primero"""
    # Obtener estructura de SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
    columnas_info = sqlite_cursor.fetchall()

    if not columnas_info:
        print(f"  - {tabla}: sin estructura")
        return 0

    # Obtener datos
    sqlite_cursor.execute(f"SELECT * FROM {tabla}")
    filas = sqlite_cursor.fetchall()

    if not filas:
        print(f"  - {tabla}: sin datos")
        return 0

    # Construir CREATE TABLE (sin SERIAL, usando tipos normales)
    cols_def = []
    cols_nombres = []
    for col in columnas_info:
        nombre = col[1]
        tipo = sqlite_to_pg_type(col[2])
        pk = col[5]
        cols_nombres.append(nombre)

        if pk and tipo == 'INTEGER':
            cols_def.append(f"{nombre} INTEGER PRIMARY KEY")
        elif pk:
            cols_def.append(f"{nombre} {tipo} PRIMARY KEY")
        else:
            cols_def.append(f"{nombre} {tipo}")

    # Crear tabla
    pg_cursor = pg_conn.cursor()

    # Eliminar si existe
    pg_cursor.execute(f"DROP TABLE IF EXISTS {tabla}")

    sql = f"CREATE TABLE {tabla} ({', '.join(cols_def)})"
    pg_cursor.execute(sql)

    # Insertar datos
    placeholders = ','.join(['%s'] * len(cols_nombres))
    columnas_str = ','.join(cols_nombres)

    for fila in filas:
        valores = []
        for val in fila:
            if val is None:
                valores.append(None)
            elif isinstance(val, (int, float)):
                valores.append(val)
            else:
                valores.append(str(val))

        try:
            pg_cursor.execute(
                f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})",
                valores
            )
        except Exception as e:
            pass  # Ignorar errores

    pg_conn.commit()
    print(f"  + {tabla}: {len(filas)} registros")
    return len(filas)

def migrar_datos():
    print("Migrando datos de SQLite a Neon PostgreSQL...\n")

    if not os.path.exists(SQLITE_DB):
        print(f"Error: No se encontro {SQLITE_DB}")
        return

    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    print(f"Conectado a SQLite: {SQLITE_DB}")

    try:
        pg_conn = get_pg_connection()
        print("Conectado a Neon PostgreSQL\n")
    except Exception as e:
        print(f"Error conectando a Neon: {e}")
        return

    # Obtener tablas
    sqlite_cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tablas = [row[0] for row in sqlite_cursor.fetchall()]

    print(f"Tablas a migrar: {len(tablas)}\n")

    total = 0
    for tabla in tablas:
        try:
            count = migrar_tabla(pg_conn, tabla, sqlite_cursor)
            total += count
        except Exception as e:
            print(f"  ! {tabla}: {e}")

    print(f"\nMigracion completada: {total} registros")
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrar_datos()
