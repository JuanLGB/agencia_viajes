"""
Script de migración de datos de SQLite a PostgreSQL (Neon)
Usage: python migrar_a_neon.py
"""

import sqlite3
import psycopg2
import os

# URL de Neon
NEON_URL = "postgresql://neondb_owner:npg_Y4GIaHWQuLP2@ep-icy-band-aicyuekj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

SQLITE_DB = "agencia.db"

def get_sqlite_connection():
    return sqlite3.connect(SQLITE_DB)

def get_pg_connection():
    return psycopg2.connect(NEON_URL)

def sqlite_to_pg_type(sqlite_type):
    """Convertir tipo SQLite a PostgreSQL"""
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

def crear_tabla_desde_sqlite(pg_cursor, tabla, sqlite_cursor):
    """Crear tabla en PostgreSQL basándose en la estructura de SQLite"""
    sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = sqlite_cursor.fetchall()

    cols_def = []
    for col in columnas:
        nombre = col[1]
        tipo = sqlite_to_pg_type(col[2])
        pk = col[5]

        if pk and tipo == 'INTEGER':
            cols_def.append(f"{nombre} SERIAL PRIMARY KEY")
        elif pk:
            cols_def.append(f"{nombre} {tipo} PRIMARY KEY")
        else:
            cols_def.append(f"{nombre} {tipo}")

    sql = f"CREATE TABLE IF NOT EXISTS {tabla} ({', '.join(cols_def)})"
    pg_cursor.execute(sql)

def migrar_tabla(pg_conn, tabla, sqlite_cursor):
    """Migrar datos de una tabla"""
    sqlite_cursor.execute(f"SELECT * FROM {tabla}")
    filas = sqlite_cursor.fetchall()

    if not filas:
        print(f"  - {tabla}: sin datos")
        return 0

    sqlite_cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [row[1] for row in sqlite_cursor.fetchall()]

    placeholders = ','.join(['%s'] * len(columnas))
    columnas_str = ','.join(columnas)

    insertados = 0
    pg_cursor = pg_conn.cursor()

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
            insertados += 1
        except Exception:
            pass  # Ignorar duplicados

    pg_conn.commit()
    print(f"  + {tabla}: {insertados} registros")
    return insertados

def migrar_datos():
    """Ejecutar la migración"""
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

    # Obtener tablas (excluir sqlite internal)
    sqlite_cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tablas = [row[0] for row in sqlite_cursor.fetchall()]

    print(f"Tablas a migrar: {len(tablas)}\n")

    total = 0
    for tabla in tablas:
        try:
            crear_tabla_desde_sqlite(pg_conn.cursor(), tabla, sqlite_cursor)
            pg_conn.commit()
            count = migrar_tabla(pg_conn, tabla, sqlite_cursor)
            total += count
        except Exception as e:
            print(f"  ! {tabla}: {e}")

    print(f"\nMigracion completada: {total} registros")
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrar_datos()
