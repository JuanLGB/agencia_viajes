"""
Script para arreglar las secuencias de auto-incremento en PostgreSQL
"""

import psycopg2

NEON_URL = "postgresql://neondb_owner:npg_Y4GIaHWQuLP2@ep-icy-band-aicyuekj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def arreglar_secuencias():
    print("Arreglando secuencias...\n")

    conn = psycopg2.connect(NEON_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    tablas = [
        'usuarios', 'vendedoras', 'operadores', 'hoteles', 'bloqueos',
        'ventas', 'abonos', 'pasajeros', 'grupos',
        'cotizaciones_nacionales', 'hoteles_cotizacion',
        'viajes_nacionales', 'clientes_nacionales', 'pasajeros_nacionales', 'abonos_nacionales',
        'viajes_internacionales', 'clientes_internacionales', 'pasajeros_internacionales', 'abonos_internacionales',
        'config_comisiones', 'historial_comisiones', 'config_recibos', 'transferencias',
        'gastos_operativos', 'categorias_gastos'
    ]

    for tabla in tablas:
        try:
            # Obtener el maximo ID
            cursor.execute(f"SELECT MAX(id) FROM {tabla}")
            max_id = cursor.fetchone()[0]
            siguiente = (max_id or 0) + 1

            # Crear secuencia con CASCADE
            secuencia = f"{tabla}_id_seq"
            cursor.execute(f"DROP SEQUENCE IF EXISTS {secuencia} CASCADE")
            cursor.execute(f"CREATE SEQUENCE {secuencia} START {siguiente}")

            # Cambiar columna para usar secuencia
            cursor.execute(f"ALTER TABLE {tabla} ALTER COLUMN id SET DEFAULT nextval('{secuencia}')")

            print(f"{tabla}: OK (siguiente: {siguiente})")
        except Exception as e:
            print(f"{tabla}: ERROR - {e}")

    conn.close()
    print("\nListo!")

if __name__ == "__main__":
    arreglar_secuencias()
