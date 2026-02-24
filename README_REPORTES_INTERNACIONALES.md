# 📊 MÓDULO DE REPORTES - VIAJES INTERNACIONALES

## 📋 Descripción

Este módulo proporciona reportes completos y detallados para los viajes internacionales de la agencia Riviera Maya, con dos modalidades:

1. **Reporte en Consola** - Vista detallada en la terminal
2. **Exportación a Excel** - Archivo completo con múltiples hojas organizadas

---

## 🚀 Instalación

### Requisito: openpyxl (para exportar a Excel)

```bash
pip install openpyxl --break-system-packages
```

---

## 📁 Integración con tu sistema

### Opción 1: Archivo independiente

Puedes ejecutar el módulo directamente:

```bash
python reportes_internacionales.py
```

### Opción 2: Integrar con tu menú principal

Agrega esta opción a tu archivo `main.py` o donde tengas el menú de viajes internacionales:

```python
# Importar al inicio del archivo
from reportes_internacionales import menu_reportes_internacionales

# Agregar en el menú de viajes internacionales
print("X. Ver reportes detallados")

# En el switch/if de opciones:
elif opcion == "X":  # O el número que elijas
    menu_reportes_internacionales()
```

---

## 📊 Funcionalidades

### 1. Reporte en Consola

Muestra en la terminal:

✅ **Información del Viaje**
- Fechas, duración, estado
- Cupos totales, vendidos y disponibles
- Precios base por tipo de habitación

✅ **Clientes Registrados**
- Datos de cada cliente
- Distribución de habitaciones con nombres de pasajeros
- Estado de pagos (total, abonado, saldo)
- Historial detallado de abonos (con tipo de cambio si aplica)

✅ **Resumen General**
- Total de habitaciones por tipo
- Financiero: vendido, abonado, saldo, % cobrado
- Ganancia total y margen promedio

✅ **Alertas**
- Clientes con saldo alto
- Porcentaje de cobro bajo
- Cupos disponibles

### 2. Exportación a Excel

Genera un archivo `.xlsx` con 4 hojas:

#### 📄 Hoja 1: Información General
- Datos del viaje
- Cupos y ocupación
- Precios base

#### 📄 Hoja 2: Clientes y Pagos
- Listado completo de clientes
- Pasajeros por cliente
- Habitaciones asignadas
- Estado de pagos
- Totales generales

#### 📄 Hoja 3: Distribución de Habitaciones
- Desglose por habitación
- Nombres de todos los pasajeros
- Tipo de pasajero (adulto/menor)
- Organizado por cliente

#### 📄 Hoja 4: Historial de Pagos
- Todos los abonos realizados
- Fecha y hora de cada pago
- Moneda original (USD/MXN)
- Tipo de cambio aplicado
- Monto en USD

---

## 💡 Ejemplo de uso

### Desde el menú:

```
═══════════════════════════════════════════════════════════
📊 REPORTES - VIAJES INTERNACIONALES
═══════════════════════════════════════════════════════════

1. Ver reporte en consola
2. Exportar reporte a Excel
3. Volver

Selecciona una opción: 1

═══════════════════════════════════════════════════════════
🌎 VIAJES INTERNACIONALES DISPONIBLES
═══════════════════════════════════════════════════════════
✅ 1. Europa (15-06-2025 al 25-06-2025) - ACTIVO
✅ 2. Nueva York (01-07-2025 al 08-07-2025) - ACTIVO

Selecciona ID del viaje para ver reporte: 1
```

### El reporte mostrará:

```
═══════════════════════════════════════════════════════════
🌎 REPORTE DETALLADO - EUROPA
═══════════════════════════════════════════════════════════

📅 INFORMACIÓN DEL VIAJE:
   Fechas: 15-06-2025 al 25-06-2025
   Duración: 11 días / 10 noches
   Estado: ACTIVO

👥 CUPOS:
   Total: 50 personas
   Vendidos: 35 (70.0%)
   Disponibles: 15

💵 PRECIOS BASE (USD):
   Adulto doble: $3,500.00
   Adulto triple: $3,200.00
   Menor doble: $2,800.00
   Menor triple: $2,500.00
   Margen de ganancia: 15.0%

═══════════════════════════════════════════════════════════
👥 CLIENTES REGISTRADOS (8)
═══════════════════════════════════════════════════════════

✅ María García
   Pasajeros: 2 adultos + 1 menores = 3 total
   Habitaciones: 1 doble(s) + 0 triple(s)

   📋 DISTRIBUCIÓN DE HABITACIONES:
      Doble 1:
         • María García (ADULTO)
         • Juan García (ADULTO)
         • Sofía García (MENOR)

   💵 PAGOS (USD):
      Total: $9,800.00
      Abonado: $5,000.00
      Saldo: $4,800.00
      Ganancia: $1,470.00

   📅 Historial de pagos:
      15-01-2025: $3,000.00 USD
      01-02-2025: $50,000.00 MXN (TC: 20.00) = $2,000.00 USD

──────────────────────────────────────────────────────────

[... más clientes ...]

═══════════════════════════════════════════════════════════
📊 RESUMEN GENERAL
═══════════════════════════════════════════════════════════

🏨 HABITACIONES:
   Dobles: 12
   Triples: 3
   Total: 15

💰 FINANCIERO (USD):
   Total vendido: $118,500.00
   Total abonado: $75,200.00
   Total saldo: $43,300.00
   % Cobrado: 63.5%

📈 GANANCIA:
   Ganancia total: $17,775.00
   Margen promedio: 15.0%

⚠️  ALERTAS:
   • 3 cliente(s) con saldo > $1,000 USD
   • ⚠️  Solo 64% cobrado del total
   • 15 cupos aún disponibles para venta

═══════════════════════════════════════════════════════════
```

---

## 📦 Archivos Excel generados

Los archivos se guardan con el formato:

```
Reporte_[Destino]_[FechaHora].xlsx
```

Ejemplo:
```
Reporte_Europa_20250216_143025.xlsx
```

El archivo incluye:
- ✅ Formato profesional con colores
- ✅ Bordes en todas las celdas
- ✅ Formato de moneda automático
- ✅ Anchos de columna ajustados
- ✅ Fácil de imprimir o compartir

---

## 🔧 Funciones disponibles

### Para usar en tu código:

```python
from reportes_internacionales import (
    reporte_viaje_internacional_consola,  # Reporte en terminal
    exportar_reporte_excel,               # Exportar a Excel
    menu_reportes_internacionales         # Menú completo
)

# Llamar directamente al reporte en consola
reporte_viaje_internacional_consola()

# O exportar a Excel
archivo = exportar_reporte_excel()

# O mostrar el menú completo
menu_reportes_internacionales()
```

---

## ✨ Ventajas

1. **Información Completa**: Todo en un solo lugar
2. **Fácil de usar**: Menú intuitivo con opciones claras
3. **Múltiples formatos**: Consola para revisión rápida, Excel para compartir
4. **Organizado**: Hojas separadas por tipo de información
5. **Profesional**: Formato de Excel listo para presentar
6. **Control financiero**: Estado de pagos siempre visible
7. **Trazabilidad**: Historial completo de abonos con tipo de cambio

---

## 🆘 Soporte

Si tienes problemas:

1. **Error de openpyxl**: Instala con `pip install openpyxl --break-system-packages`
2. **No se guardan archivos**: Verifica permisos en la carpeta `/mnt/user-data/outputs/`
3. **No aparecen viajes**: Asegúrate de tener viajes internacionales registrados en la BD

---

## 📝 Notas importantes

- Los reportes muestran todos los viajes (ACTIVOS e inactivos)
- Los archivos Excel se guardan en `/mnt/user-data/outputs/`
- El historial de pagos muestra conversiones MXN→USD con el tipo de cambio usado
- Las alertas ayudan a identificar problemas de cobranza rápidamente

---

¡Listo para usar! 🚀
