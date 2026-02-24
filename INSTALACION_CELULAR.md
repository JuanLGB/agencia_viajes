# 📱 INSTALACIÓN - ARCHIVOS CON CAMPO CELULAR

## ✅ ARCHIVOS CORREGIDOS INCLUIDOS:

1. **viajes_corregido.py** - Riviera Maya con celular y operador
2. **nacionales_corregido.py** - Viajes nacionales con celular
3. **bloqueos_corregido.py** - Bloqueos con celular y operador

---

## 🚀 INSTRUCCIONES DE INSTALACIÓN (2 minutos):

### **Paso 1: Hacer BACKUP** ⚠️
```bash
cd C:\Users\marcos.estrella\Documents\agencia_viajes

copy viajes.py viajes_backup.py
copy nacionales.py nacionales_backup.py
copy bloqueos.py bloqueos_backup.py
```

### **Paso 2: Reemplazar archivos**

Descarga los 3 archivos corregidos y:

1. **Renombra:**
   - `viajes_corregido.py` → `viajes.py`
   - `nacionales_corregido.py` → `nacionales.py`
   - `bloqueos_corregido.py` → `bloqueos.py`

2. **Cópialos** a:
   ```
   C:\Users\marcos.estrella\Documents\agencia_viajes\
   ```

3. **Reemplaza** los archivos existentes cuando te pregunte

### **Paso 3: Probar**
```bash
python main.py
```

---

## ✅ AHORA CUANDO REGISTRES:

### **Riviera Maya (Bloqueos):**
```
📦 SELECCIÓN DE BLOQUEO
...
Nombre del cliente: Juan Pérez
Celular del cliente: 9999123456  ← ¡NUEVO!
Número de adultos: 2
...
```

### **Viajes Nacionales:**
```
👤 REGISTRAR CLIENTE EN VIAJE NACIONAL
...
Nombre del cliente: María García
Celular del cliente: 9998765432  ← ¡NUEVO!
...
```

### **Bloqueos (al crearlos):**
```
📦 REGISTRAR NUEVO BLOQUEO
Nombre del bloqueo: Cancún Marzo

🏢 SELECCIONA OPERADOR:        ← ¡NUEVO!
1. Magnicharters
2. Amstar
...

Hotel: Grand Oasis
Celular del responsable: 9997654321  ← ¡NUEVO!
...
```

---

## 🔍 VERIFICACIÓN:

Para confirmar que todo funciona:

1. **Registra un viaje de prueba**
2. **Verifica que te pida el celular**
3. **Verifica que te pida el operador (en bloqueos)**

---

## 📋 CAMBIOS REALIZADOS EN CADA ARCHIVO:

### **viajes.py:**
- ✅ Agrega campo `celular_cliente` en registro de bloqueos
- ✅ Agrega campo `celular_cliente` en registro de viajes normales
- ✅ Guarda el celular en la tabla `ventas` (campo `celular_responsable`)

### **nacionales.py:**
- ✅ Agrega campo `celular_cliente` en registro de clientes
- ✅ Guarda el celular en la tabla `clientes_nacionales` (campo `celular_responsable`)

### **bloqueos.py:**
- ✅ Agrega selección de `operador` (usa el módulo operadores.py)
- ✅ Agrega campo `celular_responsable` en registro de bloqueos
- ✅ Guarda ambos campos en la tabla `bloqueos`

---

## ⚠️ NOTA IMPORTANTE:

**Los viajes internacionales YA tienen el celular incluido** ✅
Si descargaste el archivo `internacionales.py` mejorado que te envié ayer, ya tiene el campo celular integrado.

---

## 🆘 SI ALGO FALLA:

1. **Error de importación** (operadores.py):
   - Asegúrate de que `operadores.py` esté en la misma carpeta

2. **Error de columna no existe**:
   - Ejecuta de nuevo `migracion_fase1.py`

3. **No aparece el operador en bloqueos**:
   - Verifica que tengas el archivo `operadores.py`

---

## ✅ RESUMEN:

1. ✅ Haz backup de los archivos actuales
2. ✅ Descarga los 3 archivos corregidos
3. ✅ Renómbralos (quita "_corregido")
4. ✅ Reemplaza en tu carpeta
5. ✅ Prueba registrando un viaje

**¡Listo! Ahora todos los módulos pedirán celular y operador** 🎉
