# 🌐 GUÍA DE DESPLIEGUE - Sistema Web Agencia Riviera Maya

## 📋 ¿Qué acabas de recibir?

Has recibido una **versión web completa** de tu sistema de agencia de viajes que funciona en cualquier navegador. Esta aplicación permite:

✅ Acceso desde cualquier dispositivo (PC, tablet, móvil)
✅ Dashboard interactivo con gráficas
✅ Gestión de ventas Riviera Maya
✅ Viajes nacionales e internacionales
✅ Sistema de login seguro
✅ Reportes visuales

---

## 🚀 OPCIÓN 1: Ejecutar en tu Computadora (Local)

### Paso 1: Instalar dependencias

```bash
cd C:\Users\marcos.estrella\Documents\agencia_viajes
pip install -r requirements.txt
```

### Paso 2: Ejecutar la aplicación

```bash
streamlit run app_streamlit.py
```

### Paso 3: Abrir en el navegador

Se abrirá automáticamente en: `http://localhost:8501`

**Usuario de prueba:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🌐 OPCIÓN 2: Publicar en Internet (GRATIS)

### Método A: Streamlit Cloud (RECOMENDADO - GRATIS)

#### Paso 1: Crear cuenta en GitHub
1. Ve a https://github.com
2. Crea una cuenta gratuita si no tienes

#### Paso 2: Subir tu proyecto a GitHub
1. Instala Git en tu computadora: https://git-scm.com/downloads
2. Abre la terminal en tu carpeta del proyecto:
   ```bash
   cd C:\Users\marcos.estrella\Documents\agencia_viajes
   git init
   git add .
   git commit -m "Sistema Agencia Riviera Maya"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/agencia-riviera.git
   git push -u origin main
   ```

#### Paso 3: Desplegar en Streamlit Cloud
1. Ve a https://share.streamlit.io
2. Conecta tu cuenta de GitHub
3. Selecciona tu repositorio: `agencia-riviera`
4. Archivo principal: `app_streamlit.py`
5. Click en "Deploy"

**¡Listo!** Tu app estará en: `https://tu-usuario-agencia-riviera.streamlit.app`

**GRATIS** incluye:
- ✅ URL personalizada
- ✅ SSL/HTTPS automático
- ✅ Actualizaciones automáticas cuando cambies código
- ✅ 1GB de recursos (suficiente para tu sistema)

---

### Método B: Render (Alternativa GRATIS)

1. Ve a https://render.com
2. Crea cuenta gratuita
3. "New" → "Web Service"
4. Conecta GitHub
5. Selecciona tu repositorio
6. Build command: `pip install -r requirements.txt`
7. Start command: `streamlit run app_streamlit.py --server.port=$PORT --server.address=0.0.0.0`
8. Click "Create Web Service"

**URL:** `https://agencia-riviera.onrender.com`

---

### Método C: Railway (Alternativa)

1. Ve a https://railway.app
2. "Start a New Project"
3. "Deploy from GitHub repo"
4. Selecciona tu repositorio
5. Railway detectará Streamlit automáticamente

---

## 💰 OPCIÓN 3: Hosting Profesional (PAGO)

### Opción A: Heroku ($7/mes)
- Más confiable
- Mejor rendimiento
- Base de datos PostgreSQL incluida

### Opción B: DigitalOcean ($6/mes)
- Servidor VPS completo
- Control total
- Escalable

### Opción C: AWS ($5-10/mes)
- Infraestructura empresarial
- Muy escalable

---

## 🔧 CONFIGURACIÓN ADICIONAL

### Para usar PostgreSQL en lugar de SQLite (Recomendado para producción)

1. Instala psycopg2:
```bash
pip install psycopg2-binary
```

2. Modifica la conexión en `app_streamlit.py`:
```python
import psycopg2

def conectar_db():
    return psycopg2.connect(
        host="tu-host.postgres.database.azure.com",
        database="agencia",
        user="tu_usuario",
        password="tu_password"
    )
```

3. Servicios de PostgreSQL gratuitos:
   - **Supabase**: https://supabase.com (500MB gratis)
   - **ElephantSQL**: https://www.elephantsql.com (20MB gratis)
   - **Neon**: https://neon.tech (3GB gratis)

---

## 📱 CARACTERÍSTICAS DE LA APLICACIÓN WEB

### Dashboard
- 📊 Métricas en tiempo real
- 📈 Gráficas interactivas
- 💰 Estado de cobranza visual
- 🎯 KPIs principales

### Ventas Riviera Maya
- 📋 Listado de ventas activas
- 💵 Estado de pagos
- 📥 Descarga de reportes CSV
- 🔍 Búsqueda y filtros

### Viajes Nacionales/Internacionales
- 🗺️ Viajes activos
- 👥 Gestión de clientes
- 📊 Ocupación de cupos

### Reportes
- 📊 Reportes visuales
- 📥 Exportación a Excel/CSV
- 📈 Análisis de tendencias

---

## 🔐 SEGURIDAD

La aplicación incluye:
- ✅ Sistema de login
- ✅ Roles de usuario (Admin/Vendedora)
- ✅ Sesiones seguras
- ✅ Validación de datos

### Para mejorar seguridad en producción:

1. **Cambiar contraseñas por defecto**
2. **Usar variables de entorno para credenciales**
3. **Habilitar HTTPS** (automático en Streamlit Cloud)
4. **Implementar rate limiting**
5. **Agregar autenticación de dos factores**

---

## 🎨 PERSONALIZACIÓN

### Cambiar colores/tema:

Crea archivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Agregar logo:

Reemplaza la línea en `app_streamlit.py`:
```python
st.image("ruta/a/tu/logo.png", use_container_width=True)
```

---

## 📞 SOPORTE Y ACTUALIZACIONES

### Agregar nuevas funcionalidades:

1. Modifica `app_streamlit.py`
2. Si usas Streamlit Cloud, los cambios se publican automáticamente al hacer:
   ```bash
   git add .
   git commit -m "Nueva funcionalidad"
   git push
   ```

### Backup de base de datos:

```bash
# Backup
sqlite3 agencia.db .dump > backup.sql

# Restaurar
sqlite3 agencia_nueva.db < backup.sql
```

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

1. ✅ **Probar local** - Ejecuta `streamlit run app_streamlit.py`
2. ✅ **Subir a GitHub** - Para control de versiones
3. ✅ **Desplegar en Streamlit Cloud** - Para acceso en internet GRATIS
4. ✅ **Migrar a PostgreSQL** - Para mejor rendimiento
5. ✅ **Personalizar colores** - Con tu marca
6. ✅ **Agregar dominio personalizado** - ej: `sistema.agenciariviera.com`

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Puedo usar mi propio dominio?**
R: Sí, en Streamlit Cloud puedes configurar un dominio personalizado.

**P: ¿Cuántos usuarios pueden usarlo simultáneamente?**
R: En el plan gratuito de Streamlit Cloud: ~10-20 usuarios simultáneos.

**P: ¿Los datos están seguros?**
R: Sí, todas las conexiones usan HTTPS. Para mayor seguridad usa PostgreSQL con encriptación.

**P: ¿Puedo hacer la app privada?**
R: Sí, en Streamlit Cloud puedes hacerla privada y requerir autenticación de GitHub.

**P: ¿Funciona en celular?**
R: Sí, la interfaz es responsive y funciona en móviles y tablets.

---

## 📧 CONTACTO

Para soporte adicional o personalizaciones, contáctame.

---

**¡Tu sistema está listo para el mundo! 🌍✈️**
