"""
MIGRACIÓN FASE 1 - Sistema Agencia Riviera Maya
Actualiza la base de datos con nuevos campos y tablas
"""

import sqlite3
from datetime import datetime

DB_NAME = "agencia.db"

def ejecutar_migracion():
    """Ejecuta la migración de base de datos para Fase 1"""
    
    print("\n" + "="*60)
    print("🔧 MIGRACIÓN FASE 1 - BASE DE DATOS")
    print("="*60)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # ===== 1. TABLA DE OPERADORES =====
        print("\n1️⃣ Creando tabla de operadores...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                contacto TEXT,
                telefono TEXT,
                email TEXT,
                activo INTEGER DEFAULT 1,
                veces_usado INTEGER DEFAULT 0,
                fecha_registro TEXT NOT NULL
            )
        """)
        
        # Insertar operadores iniciales comunes
        operadores_iniciales = [
            "Magnicharters",
            "Amstar",
            "Best Day",
            "Viajes Beda",
            "Eurotravel",
            "Otro"
        ]
        
        for op in operadores_iniciales:
            try:
                cursor.execute("""
                    INSERT INTO operadores (nombre, activo, veces_usado, fecha_registro)
                    VALUES (?, 1, 0, ?)
                """, (op, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            except:
                pass  # Ya existe
        
        print("   ✅ Tabla operadores creada")
        
        # ===== 2. TABLA DE GRUPOS =====
        print("\n2️⃣ Creando tabla de grupos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grupos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_grupo TEXT NOT NULL,
                operador TEXT,
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
                responsable TEXT DEFAULT 'Mamá',
                celular_responsable TEXT,
                estado TEXT DEFAULT 'ACTIVO',
                fecha_registro TEXT NOT NULL
            )
        """)
        print("   ✅ Tabla grupos creada")
        
        # ===== 3. AGREGAR CAMPOS A VENTAS =====
        print("\n3️⃣ Actualizando tabla ventas...")
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN operador TEXT")
            print("   ✅ Campo 'operador' agregado a ventas")
        except:
            print("   ⚠️  Campo 'operador' ya existe en ventas")
        
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN celular_responsable TEXT")
            print("   ✅ Campo 'celular_responsable' agregado a ventas")
        except:
            print("   ⚠️  Campo 'celular_responsable' ya existe en ventas")
        
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN es_grupo INTEGER DEFAULT 0")
            print("   ✅ Campo 'es_grupo' agregado a ventas")
        except:
            print("   ⚠️  Campo 'es_grupo' ya existe en ventas")
        
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN grupo_id INTEGER")
            print("   ✅ Campo 'grupo_id' agregado a ventas")
        except:
            print("   ⚠️  Campo 'grupo_id' ya existe en ventas")
        
        # ===== 4. AGREGAR CAMPOS A BLOQUEOS =====
        print("\n4️⃣ Actualizando tabla bloqueos...")
        try:
            cursor.execute("ALTER TABLE bloqueos ADD COLUMN operador TEXT")
            print("   ✅ Campo 'operador' agregado a bloqueos")
        except:
            print("   ⚠️  Campo 'operador' ya existe en bloqueos")
        
        try:
            cursor.execute("ALTER TABLE bloqueos ADD COLUMN celular_responsable TEXT")
            print("   ✅ Campo 'celular_responsable' agregado a bloqueos")
        except:
            print("   ⚠️  Campo 'celular_responsable' ya existe en bloqueos")
        
        # ===== 5. AGREGAR CAMPOS A CLIENTES NACIONALES =====
        print("\n5️⃣ Actualizando tabla clientes_nacionales...")
        try:
            cursor.execute("ALTER TABLE clientes_nacionales ADD COLUMN celular_responsable TEXT")
            print("   ✅ Campo 'celular_responsable' agregado a clientes_nacionales")
        except:
            print("   ⚠️  Campo 'celular_responsable' ya existe en clientes_nacionales")
        
        # ===== 6. AGREGAR CAMPOS A CLIENTES INTERNACIONALES =====
        print("\n6️⃣ Actualizando tabla clientes_internacionales...")
        try:
            cursor.execute("ALTER TABLE clientes_internacionales ADD COLUMN celular_responsable TEXT")
            print("   ✅ Campo 'celular_responsable' agregado a clientes_internacionales")
        except:
            print("   ⚠️  Campo 'celular_responsable' ya existe en clientes_internacionales")
        
        # ===== 7. AGREGAR CAMPOS A VIAJES NACIONALES =====
        print("\n7️⃣ Actualizando tabla viajes_nacionales...")
        try:
            cursor.execute("ALTER TABLE viajes_nacionales ADD COLUMN operador TEXT")
            print("   ✅ Campo 'operador' agregado a viajes_nacionales")
        except:
            print("   ⚠️  Campo 'operador' ya existe en viajes_nacionales")
        
        # ===== 8. AGREGAR CAMPOS A VIAJES INTERNACIONALES =====
        print("\n8️⃣ Actualizando tabla viajes_internacionales...")
        try:
            cursor.execute("ALTER TABLE viajes_internacionales ADD COLUMN operador TEXT")
            print("   ✅ Campo 'operador' agregado a viajes_internacionales")
        except:
            print("   ⚠️  Campo 'operador' ya existe en viajes_internacionales")
        
        # Commit de todos los cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\nNuevas funcionalidades disponibles:")
        print("  📦 Módulo de GRUPOS")
        print("  🏢 Campo OPERADOR en todos los módulos")
        print("  📱 Campo CELULAR RESPONSABLE en todos los registros")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True


def verificar_migracion():
    """Verifica que la migración se haya aplicado correctamente"""
    
    print("\n🔍 Verificando migración...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar tabla operadores
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operadores'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM operadores")
        count = cursor.fetchone()[0]
        print(f"  ✅ Tabla operadores: {count} operadores registrados")
    else:
        print("  ❌ Tabla operadores NO existe")
    
    # Verificar tabla grupos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grupos'")
    if cursor.fetchone():
        print("  ✅ Tabla grupos creada")
    else:
        print("  ❌ Tabla grupos NO existe")
    
    # Verificar campos en ventas
    cursor.execute("PRAGMA table_info(ventas)")
    columnas_ventas = [col[1] for col in cursor.fetchall()]
    
    if 'operador' in columnas_ventas:
        print("  ✅ Campo 'operador' en ventas")
    else:
        print("  ❌ Campo 'operador' falta en ventas")
    
    if 'celular_responsable' in columnas_ventas:
        print("  ✅ Campo 'celular_responsable' en ventas")
    else:
        print("  ❌ Campo 'celular_responsable' falta en ventas")
    
    conn.close()
    
    print("\n✅ Verificación completada\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO MIGRACIÓN FASE 1")
    print("="*60)
    print("\nEsta migración agregará:")
    print("  1. Tabla de operadores mayoristas")
    print("  2. Tabla de grupos")
    print("  3. Campo 'operador' a ventas, bloqueos y viajes")
    print("  4. Campo 'celular_responsable' a todos los módulos")
    print("\n⚠️  IMPORTANTE: Se recomienda hacer backup de agencia.db")
    print("="*60)
    
    respuesta = input("\n¿Continuar con la migración? (s/n): ").lower()
    
    if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
        if ejecutar_migracion():
            verificar_migracion()
            print("🎉 ¡Listo! Tu base de datos está actualizada.\n")
        else:
            print("❌ La migración falló. Revisa los errores.\n")
    else:
        print("\n❌ Migración cancelada.\n")
