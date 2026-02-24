# 💰 INSTALACIÓN FASE 2 - GASTOS OPERATIVOS

## 📦 ARCHIVOS INCLUIDOS:

1. **migracion_gastos.py** - Actualiza la base de datos
2. **gastos.py** - Módulo completo de gastos operativos
3. **sueldos.py** - Módulo de control de sueldos

---

## 🚀 INSTALACIÓN (5 minutos):

### **Paso 1: Hacer BACKUP**
```bash
cd C:\Users\marcos.estrella\Documents\agencia_viajes
copy agencia.db agencia_backup_fase2.db
```

### **Paso 2: Copiar archivos nuevos**
Guarda estos 3 archivos en tu carpeta:
- ✅ `migracion_gastos.py`
- ✅ `gastos.py`
- ✅ `sueldos.py`

### **Paso 3: Ejecutar migración**
```bash
python migracion_gastos.py
```

Verás:
```
✅ MIGRACIÓN FASE 2 COMPLETADA EXITOSAMENTE

Nuevas funcionalidades disponibles:
  💰 Módulo de Gastos Operativos
  📊 Categorías de Gastos
  👥 Control de Sueldos de Vendedoras
  📈 Reportes Financieros Completos
```

### **Paso 4: Actualizar main.py**

Agrega estos imports al inicio:
```python
from gastos import menu_gastos
from sueldos import menu_sueldos
```

Agrega estas opciones en el menú de ADMIN:
```python
# En la sección de opciones para ADMIN
elif opcion == "50":
    menu_gastos()

elif opcion == "51":
    menu_sueldos()
```

### **Paso 5: Actualizar usuarios.py**

Agrega en el menú de ADMIN:
```python
print("\n--- GASTOS OPERATIVOS ---")
print("50. 💰 Gestión de Gastos ⭐ NUEVO")
print("51. 👥 Gestión de Sueldos ⭐ NUEVO")
```

---

## ✅ FUNCIONALIDADES INCLUIDAS:

### **💰 MÓDULO DE GASTOS (Opción 50)**

```
💰 GESTIÓN DE GASTOS OPERATIVOS
================================
1. Registrar gasto
2. Ver gastos
3. Editar gasto
4. Eliminar gasto
5. Reporte mensual
6. Reporte anual
```

**Categorías predefinidas:**
- ⚡ Servicios Públicos (Luz, agua, internet)
- 👥 Sueldos y Nómina
- 📋 Impuestos (ISR, IVA, predial)
- 💼 Honorarios Profesionales (Contador, abogado)
- 🏢 Renta
- 📄 Papelería y Oficina
- 📢 Marketing
- 🔧 Mantenimiento
- 💻 Tecnología
- 🏦 Gastos Bancarios
- 🚗 Viáticos
- 📦 Otros Gastos

**Características:**
- ✅ Registro por categoría
- ✅ Gastos recurrentes (mensual, bimestral, etc.)
- ✅ Filtros por mes/año/categoría
- ✅ Reportes detallados
- ✅ Proveedor y método de pago
- ✅ Notas y comprobantes

---

### **👥 MÓDULO DE SUELDOS (Opción 51)**

```
👥 GESTIÓN DE SUELDOS
====================
1. Registrar sueldo mensual
2. Ver sueldos
3. Marcar como pagado
4. Reporte mensual de nómina
```

**Componentes del sueldo:**
- Sueldo base
- Comisiones
- Bonos
- Deducciones
- **Total a pagar** (calculado automáticamente)

**Características:**
- ✅ Control por vendedora
- ✅ Registro mensual
- ✅ Estados: PENDIENTE / PAGADO
- ✅ Se registra automáticamente como gasto operativo
- ✅ Reportes de nómina
- ✅ Filtros múltiples

---

## 📊 EJEMPLOS DE USO:

### **Registrar gasto de luz:**
```
Opción: 50 (Gastos)
Opción: 1 (Registrar gasto)

Categoría: 1 (Servicios Públicos)
Descripción: CFE Bimestre Enero-Febrero
Monto: $2,450.00
Fecha: 15-02-2026
Frecuencia: 3 (Bimestral)
Proveedor: CFE
```

### **Registrar sueldo de vendedora:**
```
Opción: 51 (Sueldos)
Opción: 1 (Registrar sueldo mensual)

Vendedora: Zajhia G
Mes: 2 (Febrero)
Año: 2026

Sueldo base: $8,000.00
Comisiones: $3,500.00
Bonos: $500.00
Deducciones: $0.00

TOTAL A PAGAR: $12,000.00
```

---

## 📈 REPORTES DISPONIBLES:

### **Reporte Mensual de Gastos:**
```
📊 REPORTE DE GASTOS - FEBRERO 2026
====================================

📋 POR CATEGORÍA:

   Sueldos y Nómina:
      💵 $36,000.00 (3 gastos)
   
   Servicios Públicos:
      💵 $3,200.00 (2 gastos)
   
   Renta:
      💵 $5,000.00 (1 gasto)

======================================
💰 TOTAL DEL MES: $44,200.00
======================================

📊 Promedio diario: $1,550.00

🔄 Gastos recurrentes: $41,000.00
📌 Gastos únicos: $3,200.00
```

### **Reporte Mensual de Nómina:**
```
💼 REPORTE DE NÓMINA - FEBRERO 2026
====================================

✅ Zajhia G
   Base:        $8,000.00
   Comisiones:  $3,500.00
   Bonos:         $500.00
   ──────────────────────
   TOTAL:      $12,000.00

✅ Nayeli B
   Base:        $8,000.00
   Comisiones:  $4,200.00
   ──────────────────────
   TOTAL:      $12,200.00

====================================
📊 TOTALES DEL MES:
   Sueldos base:     $16,000.00
   Comisiones:        $7,700.00
   Bonos:               $500.00
   ────────────────────────────
   TOTAL A PAGAR:    $24,200.00
====================================
```

---

## 🔗 INTEGRACIÓN CON REPORTES GENERALES:

Los gastos registrados aquí se incluirán automáticamente en:
- ✅ Reporte General Mensual
- ✅ Reporte Anual
- ✅ Cálculo de Utilidad Neta
- ✅ Reportes Excel (próximamente)

**Fórmula de Utilidad:**
```
INGRESOS TOTALES
- Riviera Maya
- Grupos
- Viajes Nacionales
- Viajes Internacionales
= TOTAL INGRESOS

GASTOS OPERATIVOS
- Sueldos y Nómina
- Servicios
- Renta
- Otros gastos
= TOTAL GASTOS

UTILIDAD NETA = INGRESOS - GASTOS
```

---

## ⚠️ NOTAS IMPORTANTES:

1. **Los sueldos se registran 2 veces:**
   - En `sueldos_vendedoras` (control detallado)
   - En `gastos_operativos` (para reportes generales)

2. **Frecuencias disponibles:**
   - UNICO: Gasto de una sola vez
   - MENSUAL: Se repite cada mes
   - BIMESTRAL: Cada 2 meses (ej: luz)
   - TRIMESTRAL: Cada 3 meses
   - ANUAL: Una vez al año

3. **Estados de sueldos:**
   - PENDIENTE: Aún no se ha pagado
   - PAGADO: Ya fue liquidado

---

## ✅ VERIFICACIÓN:

Después de instalar, verifica que:
1. ✅ La migración se ejecutó correctamente
2. ✅ Puedes acceder al menú de Gastos (opción 50)
3. ✅ Puedes acceder al menú de Sueldos (opción 51)
4. ✅ Puedes registrar un gasto de prueba
5. ✅ Puedes ver las categorías predefinidas

---

## 🎯 PRÓXIMOS PASOS:

Una vez que tengas esto funcionando:
- ✅ Registrar tus gastos operativos actuales
- ✅ Registrar sueldos de vendedoras
- ✅ Generar reportes mensuales
- ✅ Continuar con reportes Excel integrados (FASE 3)

---

**¿Listo para instalar? Solo ejecuta los 5 pasos y tendrás el control completo de gastos** 🚀
