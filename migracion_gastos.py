"""
MIGRACIÓN FASE 2 - MÓDULO DE GASTOS OPERATIVOS
Crea la tabla para registrar gastos operativos de la agencia
"""

import sqlite3
from datetime import datetime

DB_NAME = "agencia.db"

def ejecutar_migracion_gastos():
    """Ejecuta la migración para el módulo de gastos"""
    
    print("\n" + "="*60)
    print("💰 MIGRACIÓN FASE 2 - GASTOS OPERATIVOS")
    print("="*60)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # ===== TABLA DE GASTOS OPERATIVOS =====
        print("\n1️⃣ Creando tabla gastos_operativos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos_operativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                subcategoria TEXT,
                descripcion TEXT,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'MXN',
                fecha_gasto TEXT NOT NULL,
                mes INTEGER NOT NULL,
                anio INTEGER NOT NULL,
                frecuencia TEXT DEFAULT 'UNICO',
                recurrente INTEGER DEFAULT 0,
                comprobante TEXT,
                metodo_pago TEXT,
                proveedor TEXT,
                notas TEXT,
                fecha_registro TEXT NOT NULL,
                usuario_registro TEXT
            )
        """)
        print("   ✅ Tabla gastos_operativos creada")
        
        # ===== TABLA DE CATEGORÍAS DE GASTOS =====
        print("\n2️⃣ Creando tabla categorias_gastos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias_gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                activa INTEGER DEFAULT 1,
                color TEXT,
                icono TEXT,
                fecha_registro TEXT NOT NULL
            )
        """)
        print("   ✅ Tabla categorias_gastos creada")
        
        # ===== INSERTAR CATEGORÍAS INICIALES =====
        print("\n3️⃣ Insertando categorías iniciales...")
        
        categorias_iniciales = [
            ("Servicios Públicos", "Luz, agua, teléfono, internet", "#FF6B6B", "⚡"),
            ("Sueldos y Nómina", "Salarios, comisiones, prestaciones", "#4ECDC4", "👥"),
            ("Impuestos", "ISR, IVA, predial, otros impuestos", "#FFD93D", "📋"),
            ("Honorarios Profesionales", "Contador, abogado, consultores", "#95E1D3", "💼"),
            ("Renta", "Arrendamiento de oficina o local", "#6C5CE7", "🏢"),
            ("Papelería y Oficina", "Material de oficina, impresiones", "#A8E6CF", "📄"),
            ("Marketing", "Publicidad, redes sociales, promoción", "#FF8B94", "📢"),
            ("Mantenimiento", "Reparaciones, limpieza, mantenimiento", "#FFA07A", "🔧"),
            ("Tecnología", "Software, licencias, equipos", "#74B9FF", "💻"),
            ("Gastos Bancarios", "Comisiones, intereses, transferencias", "#FDCB6E", "🏦"),
            ("Viáticos", "Transporte, gasolina, comidas de trabajo", "#DFE6E9", "🚗"),
            ("Otros Gastos", "Gastos no clasificados", "#B2BEC3", "📦")
        ]
        
        for cat in categorias_iniciales:
            try:
                cursor.execute("""
                    INSERT INTO categorias_gastos (nombre, descripcion, color, icono, activa, fecha_registro)
                    VALUES (?, ?, ?, ?, 1, ?)
                """, (cat[0], cat[1], cat[2], cat[3], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            except:
                pass  # Ya existe
        
        print(f"   ✅ {len(categorias_iniciales)} categorías creadas")
        
        # ===== TABLA DE SUELDOS (para control detallado) =====
        print("\n4️⃣ Creando tabla sueldos_vendedoras...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sueldos_vendedoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendedora_id INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                anio INTEGER NOT NULL,
                sueldo_base REAL DEFAULT 0,
                comisiones REAL DEFAULT 0,
                bonos REAL DEFAULT 0,
                deducciones REAL DEFAULT 0,
                total_pagar REAL NOT NULL,
                fecha_pago TEXT,
                estado TEXT DEFAULT 'PENDIENTE',
                notas TEXT,
                fecha_registro TEXT NOT NULL,
                FOREIGN KEY (vendedora_id) REFERENCES vendedoras(id)
            )
        """)
        print("   ✅ Tabla sueldos_vendedoras creada")
        
        # Commit de todos los cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN FASE 2 COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\nNuevas funcionalidades disponibles:")
        print("  💰 Módulo de Gastos Operativos")
        print("  📊 Categorías de Gastos")
        print("  👥 Control de Sueldos de Vendedoras")
        print("  📈 Reportes Financieros Completos")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True


def verificar_migracion_gastos():
    """Verifica que la migración de gastos se haya aplicado correctamente"""
    
    print("\n🔍 Verificando migración de gastos...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar tabla gastos_operativos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gastos_operativos'")
    if cursor.fetchone():
        print("  ✅ Tabla gastos_operativos creada")
    else:
        print("  ❌ Tabla gastos_operativos NO existe")
    
    # Verificar tabla categorias_gastos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias_gastos'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM categorias_gastos")
        count = cursor.fetchone()[0]
        print(f"  ✅ Tabla categorias_gastos: {count} categorías registradas")
    else:
        print("  ❌ Tabla categorias_gastos NO existe")
    
    # Verificar tabla sueldos_vendedoras
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sueldos_vendedoras'")
    if cursor.fetchone():
        print("  ✅ Tabla sueldos_vendedoras creada")
    else:
        print("  ❌ Tabla sueldos_vendedoras NO existe")
    
    conn.close()
    
    print("\n✅ Verificación completada\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 INICIANDO MIGRACIÓN FASE 2 - GASTOS")
    print("="*60)
    print("\nEsta migración creará:")
    print("  1. Tabla de gastos operativos")
    print("  2. Tabla de categorías de gastos")
    print("  3. Tabla de control de sueldos")
    print("  4. 12 categorías predefinidas")
    print("\n⚠️  IMPORTANTE: Se recomienda hacer backup de agencia.db")
    print("="*60)
    
    respuesta = input("\n¿Continuar con la migración? (s/n): ").lower()
    
    if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
        if ejecutar_migracion_gastos():
            verificar_migracion_gastos()
            print("🎉 ¡Listo! El módulo de gastos está configurado.\n")
        else:
            print("❌ La migración falló. Revisa los errores.\n")
    else:
        print("\n❌ Migración cancelada.\n")
