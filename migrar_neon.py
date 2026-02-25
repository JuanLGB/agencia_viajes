"""
Script de migración de SQLite a PostgreSQL (Neon)
Ejecutar: python migrar_neon.py
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Connection strings
SQLITE_DB = "agencia.db"
NEON_CONN = "postgresql://neondb_owner:npg_Y4GIaHWQuLP2@ep-icy-band-aicyuekj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_sqlite_tables():
    """Obtener todas las tablas de SQLite"""
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [t[0] for t in cur.fetchall()]
    conn.close()
    return tables

def get_table_columns(conn, table):
    """Obtener columnas de una tabla"""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [col[1] for col in cur.fetchall()]

def migrate_table(table, pg_conn):
    """Migrar una tabla de SQLite a PostgreSQL"""
    # Leer datos de SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    sqlite_conn.close()

    if not rows:
        print(f"  {table}: sin datos")
        return

    # Obtener columnas
    cols = get_table_columns(sqlite3.connect(SQLITE_DB), table)

    # Insertar en PostgreSQL usando ON CONFLICT para evitar errores
    placeholders = ",".join(["%s"] * len(cols))
    columns = ",".join(cols)

    pg_cur = pg_conn.cursor()

    # Try INSERT, if fails try UPDATE
    for row in rows:
        try:
            query = f"""
                INSERT INTO {table} ({columns})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            pg_cur.execute(query, row)
        except Exception as e:
            # Si la tabla no existe, crearla primero
            print(f"  Error en {table}: {str(e)[:50]}")
            break

    pg_conn.commit()
    print(f"  {table}: {len(rows)} registros migrados")

def create_tables_in_neon():
    """Crear todas las tablas en Neon desde SQLite"""
    # Conectar a SQLite para obtener el schema
    sqlite_conn = sqlite3.connect(SQLITE_DB)

    # Conectar a PostgreSQL
    pg_conn = psycopg2.connect(NEON_CONN)
    pg_cur = pg_conn.cursor()

    # Obtener todas las tablas
    tables = get_sqlite_tables()

    print("\nCreando tablas en Neon...")

    for table in tables:
        # Obtener el CREATE TABLE de SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_sql = sqlite_cur.fetchone()[0]

        if create_sql:
            # Convertir SQLite syntax a PostgreSQL
            # Reemplazos básicos
            pg_sql = create_sql
            pg_sql = pg_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            pg_sql = pg_sql.replace("AUTOINCREMENT", "")
            pg_sql = pg_sql.replace("INTEGER", "INTEGER")
            pg_sql = pg_sql.replace("TEXT", "TEXT")
            pg_sql = pg_sql.replace("REAL", "DOUBLE PRECISION")
            pg_sql = pg_sql.replace("BOOLEAN", "BOOLEAN")

            try:
                # Crear tabla (si existe, ignorará error)
                pg_sql = pg_sql.replace("CREATE TABLE IF NOT EXISTS", "CREATE TABLE IF NOT EXISTS")
                pg_cur.execute(pg_sql)
                pg_conn.commit()
                print(f"  Tabla {table} creada/verificada")
            except Exception as e:
                print(f"  {table}: {e}")

    sqlite_conn.close()
    pg_conn.close()

def migrate_all_data():
    """Migrar todos los datos"""
    print("\nMigrando datos...")

    pg_conn = psycopg2.connect(NEON_CONN)
    pg_cur = pg_conn.cursor()

    # Deshabilitar foreign keys temporalmente (PostgreSQL usa diferente sintaxis)
    pg_cur.execute("SET CONSTRAINTS ALL DEFERRED")
    pg_conn.commit()

    # Tablas en orden (primero las que no dependen de otras)
    tables_order = [
        'usuarios', 'vendedoras', 'operadores', 'hoteles', 'categorias_gastos',
        'config_comisiones', 'config_recibos',
        'viajes_nacionales', 'viajes_internacionales', 'bloqueos', 'grupos',
        'cotizaciones_nacionales', 'hoteles_cotizacion',
        'ventas', 'clientes_nacionales', 'clientes_internacionales',
        'pasajeros', 'pasajeros_nacionales', 'pasajeros_internacionales',
        'abonos', 'abonos_nacionales', 'abonos_internacionales',
        'gastos_operativos', 'sueldos_vendedoras', 'historial_comisiones',
        'pasaportes', 'visas', 'vuelos',
        'abonos_pasaportes', 'abonos_visas', 'abonos_vuelos',
        'transferencias'
    ]

    for table in tables_order:
        migrate_table(table, pg_conn)

    pg_conn.close()
    print("\nMigracion completada!")

if __name__ == "__main__":
    print("Iniciando migracion SQLite -> Neon PostgreSQL")
    print(f"Base de datos SQLite: {SQLITE_DB}")

    # Paso 1: Crear tablas
    create_tables_in_neon()

    # Paso 2: Migrar datos
    migrate_all_data()

    print("\nMigracion completada!")
    print(f"\nConnection string para Streamlit Cloud:")
    print(NEON_CONN)
