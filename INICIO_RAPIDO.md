# ⚡ INICIO RÁPIDO - 3 Pasos

## 🖥️ Para probar en tu computadora (5 minutos):

### 1. Instalar Streamlit
```bash
pip install streamlit pandas plotly openpyxl
```

### 2. Ejecutar la aplicación
```bash
cd C:\Users\marcos.estrella\Documents\agencia_viajes
streamlit run app_streamlit.py
```

### 3. Abrir navegador
Automáticamente abre en: http://localhost:8501

**Login:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🌐 Para publicar en internet GRATIS (15 minutos):

### Opción más rápida: Streamlit Cloud

1. **Sube tu código a GitHub**
   - Crea cuenta en https://github.com
   - Crea nuevo repositorio llamado `agencia-riviera`
   - Sube estos archivos:
     - `app_streamlit.py`
     - `requirements.txt`
     - `agencia.db`
     - Todo tu proyecto

2. **Conecta con Streamlit Cloud**
   - Ve a https://share.streamlit.io
   - Click en "New app"
   - Conecta tu GitHub
   - Selecciona repositorio `agencia-riviera`
   - Archivo principal: `app_streamlit.py`
   - Click "Deploy"

3. **¡Listo!**
   Tu app estará en: `https://tu-usuario-agencia-riviera.streamlit.app`

---

## 📱 ¿Qué incluye la versión web?

✅ Dashboard con métricas y gráficas
✅ Gestión de ventas Riviera Maya
✅ Viajes nacionales e internacionales
✅ Sistema de login (Admin/Vendedora)
✅ Reportes descargables (CSV)
✅ Funciona en móviles y tablets
✅ Interfaz moderna y profesional

---

## 🆘 ¿Problemas?

**Error al instalar:**
```bash
python -m pip install --upgrade pip
pip install streamlit pandas plotly openpyxl
```

**Puerto ocupado:**
```bash
streamlit run app_streamlit.py --server.port 8502
```

**No abre navegador:**
Abre manualmente: http://localhost:8501

---

## 📚 Documentación completa

Lee `GUIA_DESPLIEGUE.md` para:
- Opciones de hosting
- Configuración avanzada
- Migración a PostgreSQL
- Personalización
- Seguridad
