"""
PARCHE PARA app_streamlit.py  –  Localización + Cupones Turismar
================================================================
Este archivo contiene los TRES bloques de código que debes copiar
y pegar en tu app_streamlit.py existente:

  CAMBIO 1 → Al inicio del archivo: import del generador de cupones
  CAMBIO 2 → En inicializar_base_datos(): nuevas migraciones
  CAMBIO 3 → Reemplaza la función formulario_nueva_venta() completa
  CAMBIO 4 → En pagina_ventas_riviera() → tab "Ver Ventas": agrega botón cupón
  CAMBIO 5 → En pagina_configuracion() → tab Hoteles: agrega campos dirección/tel/estrellas

Instrucciones al final de cada bloque.
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 1 — Pega esto justo después del bloque try/except de generar_recibo
#            (alrededor de la línea 18)
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_1 = """
# ── Generador de cupones Turismar ─────────────────────────────────────────
try:
    from generar_cupon import generar_cupon_pdf
    CUPONES_DISPONIBLES = True
except ImportError:
    CUPONES_DISPONIBLES = False
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 2 — Pega estas migraciones dentro de la lista `migraciones`
#            en la función inicializar_base_datos() (~línea 545)
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_2_MIGRACIONES = """
        # ── Nuevas columnas para localización y cupones ──
        "ALTER TABLE ventas ADD COLUMN no_localizador TEXT",
        "ALTER TABLE ventas ADD COLUMN clave_confirmacion TEXT",
        "ALTER TABLE ventas ADD COLUMN plan_alimento TEXT DEFAULT 'Todo incluido'",
        "ALTER TABLE ventas ADD COLUMN requerimientos_especiales TEXT",
        "ALTER TABLE ventas ADD COLUMN edades_menores TEXT",
        # ── Hoteles: ampliar catálogo ──
        "ALTER TABLE hoteles ADD COLUMN direccion TEXT",
        "ALTER TABLE hoteles ADD COLUMN telefono TEXT",
        "ALTER TABLE hoteles ADD COLUMN estrellas INTEGER DEFAULT 4",
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 3 — Reemplaza la función obtener_hoteles() (~línea 683) con esta:
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_3_OBTENER_HOTELES = """
def obtener_hoteles():
    \"\"\"Devuelve lista de nombres de hoteles activos.\"\"\"
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM hoteles WHERE activo = 1 ORDER BY veces_usado DESC, nombre")
    hoteles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return hoteles


def obtener_hoteles_completos():
    \"\"\"Devuelve lista de dicts con todos los datos del hotel para el cupón.\"\"\"
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute(\"\"\"
            SELECT nombre,
                   COALESCE(direccion,'') AS direccion,
                   COALESCE(telefono,'') AS telefono,
                   COALESCE(estrellas, 4) AS estrellas
            FROM hoteles WHERE activo = 1
            ORDER BY veces_usado DESC, nombre
        \"\"\")
        cols = ['nombre','direccion','telefono','estrellas']
        rows = cursor.fetchall()
    except Exception:
        cursor.execute("SELECT nombre FROM hoteles WHERE activo = 1 ORDER BY nombre")
        rows  = [(r[0],'','',4) for r in cursor.fetchall()]
        cols  = ['nombre','direccion','telefono','estrellas']
    conn.close()
    return [dict(zip(cols, r)) for r in rows]
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 4 — Sección nueva que va DENTRO de formulario_nueva_venta(),
#            justo ANTES del st.divider() que precede al botón guardar
#            (~línea 1010). Busca la línea:
#               st.divider()
#            seguida de:
#               if st.button("💾 Registrar Venta" ...
#            y pega este bloque entre ambas.
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_4_CAMPOS_NUEVOS = """
    # ── Localización y datos para cupón ──────────────────────────────────
    st.markdown("#### 🔑 Localización y Datos del Cupón")
    col1, col2 = st.columns(2)
    with col1:
        no_localizador = st.text_input(
            "No. de Localizador",
            placeholder="Ej: ABC123456",
            help="Número de referencia que da el mayorista al reservar",
            key="rv_localizador"
        )
    with col2:
        clave_confirmacion = st.text_input(
            "Clave de Confirmación",
            placeholder="Ej: 69-7543060",
            help="Se obtiene cuando el viaje está pagado al 100%. Puedes dejarla vacía y agregarla después.",
            key="rv_clave_confirm"
        )
    if clave_confirmacion:
        st.success("✅ Con clave de confirmación — se podrá generar el cupón al guardar.")
    elif no_localizador:
        st.info("💡 La clave de confirmación puede agregarse después cuando el cliente liquide.")

    # Plan de alimento y requerimientos
    col1, col2 = st.columns(2)
    with col1:
        plan_alimento = st.selectbox(
            "Plan de alimento",
            ["Todo incluido", "Solo desayuno", "Media pensión", "Solo alojamiento", "Otro"],
            key="rv_plan_alimento"
        )
    with col2:
        edades_menores_txt = st.text_input(
            "Edades de menores",
            placeholder="Ej: 5 y 8 años",
            key="rv_edades_menores"
        ) if menores > 0 else ""

    requerimientos_esp = st.text_area(
        "Requerimientos especiales (opcional)",
        placeholder="Ej: Luna de miel, solicito habitación planta baja, etc.",
        height=70,
        key="rv_requerimientos"
    )
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 5 — Dentro del bloque cursor.execute(INSERT INTO ventas ...),
#            añade estas columnas. Busca la línea:
#               operador, fecha_registro
#            y cámbiala por:
#               operador, no_localizador, clave_confirmacion, plan_alimento,
#               edades_menores, requerimientos_especiales, fecha_registro
#            Y en los VALUES agrega al final (antes de operador):
#               operador, no_localizador or None, clave_confirmacion or None,
#               plan_alimento, edades_menores_txt or None,
#               requerimientos_esp or None, fecha_registro
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_5_INSERT_VENTAS = """
# Reemplaza el cursor.execute INSERT INTO ventas por este:

            cursor.execute(\"\"\"
                INSERT INTO ventas (
                    cliente, celular_responsable, tipo_venta, destino,
                    fecha_inicio, fecha_fin, noches,
                    adultos, menores, tipo_habitacion,
                    precio_adulto, precio_menor, precio_total,
                    porcentaje_ganancia, ganancia, costo_mayorista,
                    pagado, saldo, estado, vendedora_id, usuario_id,
                    es_bloqueo, bloqueo_id, es_grupo, grupo_id,
                    operador, no_localizador, clave_confirmacion,
                    plan_alimento, edades_menores, requerimientos_especiales,
                    fecha_registro
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            \"\"\", (
                cliente.strip(), celular.strip(), tipo_venta_db, destino,
                fecha_i_str, fecha_f_str, noches,
                adultos, menores, tipo_habitacion,
                precio_adulto, precio_menor, precio_total,
                porcentaje_ganancia, ganancia, costo_mayorista,
                abono_inicial, saldo_inicial, estado_inicial,
                id_vendedora, usuario.get("id_vendedora", id_vendedora),
                es_bloqueo_db, bloqueo_id_db, es_grupo_db, grupo_id_db,
                operador,
                no_localizador.strip() or None,
                clave_confirmacion.strip() or None,
                plan_alimento,
                edades_menores_txt.strip() or None if menores > 0 else None,
                requerimientos_esp.strip() or None,
                fecha_registro
            ))
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 6 — En pagina_ventas_riviera(), dentro del expander de detalle
#            de venta (~línea 1567), añade esto DESPUÉS del bloque de
#            pasajeros y abonos. Busca la línea:
#               csv = df_show.to_csv ...
#            y pega ANTES de ella este bloque de cupón:
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_6_BOTON_CUPON = """
            # ── Botón para editar localización / generar cupón ────────────
            st.divider()
            st.markdown("#### 🔑 Localización y Cupón")

            # Leer datos actuales de la venta seleccionada
            conn3 = conectar_db()
            try:
                row_extra = conn3.execute(\"\"\"
                    SELECT no_localizador, clave_confirmacion,
                           plan_alimento, edades_menores,
                           requerimientos_especiales
                    FROM ventas WHERE id = ?
                \"\"\", (id_sel,)).fetchone()
            except Exception:
                row_extra = None
            conn3.close()

            loc_actual   = row_extra[0] if row_extra else ""
            clave_actual = row_extra[1] if row_extra else ""
            plan_actual  = row_extra[2] if row_extra else "Todo incluido"
            edad_actual  = row_extra[3] if row_extra else ""
            req_actual   = row_extra[4] if row_extra else ""

            col_loc1, col_loc2 = st.columns(2)
            with col_loc1:
                ed_localizador = st.text_input(
                    "No. de Localizador",
                    value=loc_actual or "",
                    key=f"ed_loc_{id_sel}"
                )
            with col_loc2:
                ed_clave = st.text_input(
                    "Clave de Confirmación",
                    value=clave_actual or "",
                    key=f"ed_clave_{id_sel}"
                )

            col_loc3, col_loc4 = st.columns(2)
            with col_loc3:
                planes = ["Todo incluido","Solo desayuno","Media pensión","Solo alojamiento","Otro"]
                plan_idx = planes.index(plan_actual) if plan_actual in planes else 0
                ed_plan = st.selectbox("Plan de alimento", planes,
                                       index=plan_idx, key=f"ed_plan_{id_sel}")
            with col_loc4:
                ed_edades = st.text_input("Edades de menores",
                                          value=edad_actual or "",
                                          key=f"ed_edades_{id_sel}")

            ed_req = st.text_area("Requerimientos especiales",
                                  value=req_actual or "",
                                  height=60, key=f"ed_req_{id_sel}")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 Guardar cambios", key=f"save_loc_{id_sel}"):
                    try:
                        conn_upd = conectar_db()
                        conn_upd.execute(\"\"\"
                            UPDATE ventas
                            SET no_localizador = ?,
                                clave_confirmacion = ?,
                                plan_alimento = ?,
                                edades_menores = ?,
                                requerimientos_especiales = ?
                            WHERE id = ?
                        \"\"\", (
                            ed_localizador.strip() or None,
                            ed_clave.strip() or None,
                            ed_plan,
                            ed_edades.strip() or None,
                            ed_req.strip() or None,
                            id_sel
                        ))
                        conn_upd.commit()
                        conn_upd.close()
                        st.success("✅ Datos actualizados correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

            with col_b2:
                if ed_clave.strip() and CUPONES_DISPONIBLES:
                    # Obtener datos completos del hotel
                    hoteles_full = obtener_hoteles_completos()
                    hotel_data   = next((h for h in hoteles_full
                                        if h['nombre'] == row['Destino']), {})

                    pdf_cupon = generar_cupon_pdf(
                        titular         = row['Cliente'],
                        clave_confirm   = ed_clave.strip(),
                        hotel_nombre    = row['Destino'],
                        hotel_direccion = hotel_data.get('direccion', ''),
                        hotel_telefono  = hotel_data.get('telefono', ''),
                        hotel_estrellas = hotel_data.get('estrellas', 4),
                        tipo_habitacion = row['Habitación'],
                        plan_alimento   = ed_plan,
                        fecha_entrada   = row['Salida'],
                        fecha_salida    = row['Regreso'],
                        adultos         = int(row['Adultos']),
                        menores         = int(row['Menores']),
                        edades_menores  = ed_edades or "",
                        requerimientos  = ed_req or "",
                        logo_path       = LOGO_PATH,
                    )
                    st.download_button(
                        label    = "🎫 Descargar Cupón de Acceso",
                        data     = pdf_cupon,
                        file_name= f"cupon_{row['Cliente'].replace(' ','_')[:20]}.pdf",
                        mime     = "application/pdf",
                        key      = f"cupon_{id_sel}",
                        use_container_width=True,
                        type     = "primary"
                    )
                elif not ed_clave.strip():
                    st.warning("⚠️ Agrega la Clave de Confirmación para generar el cupón.")
                elif not CUPONES_DISPONIBLES:
                    st.caption("⚠️ generar_cupon.py no encontrado junto a app_streamlit.py")
"""

# ══════════════════════════════════════════════════════════════════════════
# CAMBIO 7 — Reemplaza el formulario "Nuevo Hotel" en pagina_configuracion
#            (subtabs_hot[0], ~línea 5136) por este bloque ampliado:
# ══════════════════════════════════════════════════════════════════════════
CAMBIO_7_NUEVO_HOTEL = """
        with subtabs_hot[0]:
            st.markdown("#### ➕ Registrar Nuevo Hotel")
            col1, col2 = st.columns(2)
            with col1:
                nh_nombre = st.text_input("Nombre del hotel *",
                    placeholder="Ej: Barceló Maya Grand", key="nh_nombre")
            with col2:
                nh_estrellas = st.selectbox("Estrellas", [3, 4, 5], index=1, key="nh_estrellas")

            nh_direccion = st.text_input("Dirección",
                placeholder="Ej: Carr. Cancún-Tulum Km. 266,3, Xpu Ha, Q.R.",
                key="nh_direccion")
            nh_telefono = st.text_input("Teléfono",
                placeholder="Ej: 984 875 1500", key="nh_telefono")

            if st.button("💾 Agregar Hotel", type="primary",
                         use_container_width=True, key="nh_guardar"):
                if not nh_nombre.strip():
                    st.error("❌ El nombre es obligatorio.")
                else:
                    try:
                        conn = conectar_db()
                        cursor = conn.cursor()
                        try:
                            cursor.execute(
                                \"\"\"INSERT INTO hoteles
                                   (nombre, direccion, telefono, estrellas, activo, veces_usado)
                                   VALUES (?, ?, ?, ?, 1, 0)\"\"\",
                                (nh_nombre.strip(),
                                 nh_direccion.strip() or None,
                                 nh_telefono.strip() or None,
                                 nh_estrellas)
                            )
                        except Exception:
                            cursor.execute(
                                "INSERT INTO hoteles (nombre, activo, veces_usado) VALUES (?, 1, 0)",
                                (nh_nombre.strip(),)
                            )
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Hotel **{nh_nombre}** agregado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

        with subtabs_hot[1]:
            conn = conectar_db()
            try:
                df_hoteles = pd.read_sql_query(
                    \"\"\"SELECT id, nombre,
                              COALESCE(estrellas,4) as estrellas,
                              COALESCE(direccion,'—') as direccion,
                              COALESCE(telefono,'—') as telefono,
                              activo, veces_usado
                       FROM hoteles ORDER BY nombre\"\"\", conn)
            except Exception:
                df_hoteles = pd.DataFrame()
            conn.close()

            if df_hoteles.empty:
                st.info("No hay hoteles en el catálogo.")
            else:
                df_hoteles["activo"] = df_hoteles["activo"].apply(
                    lambda x: "Activo" if x else "Inactivo")
                df_hoteles["estrellas"] = df_hoteles["estrellas"].apply(
                    lambda x: "★" * int(x) if x else "")
                df_hoteles.columns = ["ID","Hotel","Estrellas",
                                      "Dirección","Teléfono","Estado","Veces usado"]
                st.dataframe(df_hoteles, use_container_width=True, hide_index=True)
"""

if __name__ == "__main__":
    print("=" * 60)
    print("GUÍA DE INTEGRACIÓN — Cupones Turismar")
    print("=" * 60)
    print("""
PASO 1 — Copia generar_cupon.py a la carpeta de tu app.

PASO 2 — En app_streamlit.py, cerca de la línea 18, agrega:
""")
    print(CAMBIO_1)
    print("""
PASO 3 — En inicializar_base_datos(), dentro de la lista migraciones,
          agrega estas líneas:
""")
    print(CAMBIO_2_MIGRACIONES)
    print("""
PASO 4 — Después de obtener_hoteles(), agrega obtener_hoteles_completos():
""")
    print(CAMBIO_3_OBTENER_HOTELES)
    print("""
PASO 5 — En formulario_nueva_venta(), antes del st.divider() que precede
          al botón "Registrar Venta", pega:
""")
    print(CAMBIO_4_CAMPOS_NUEVOS)
    print("""
PASO 6 — Reemplaza el INSERT INTO ventas con el nuevo que incluye
          los campos de localización:
""")
    print(CAMBIO_5_INSERT_VENTAS)
    print("""
PASO 7 — En pagina_ventas_riviera(), dentro del expander de detalle,
          antes de la línea csv = df_show.to_csv, pega:
""")
    print(CAMBIO_6_BOTON_CUPON)
    print("""
PASO 8 — Reemplaza el bloque subtabs_hot[0] y subtabs_hot[1]
          en pagina_configuracion() con:
""")
    print(CAMBIO_7_NUEVO_HOTEL)
    print("""
¡Listo! Con estos 8 cambios tendrás:
  ✅ Campos No. Localizador y Clave de Confirmación en toda venta Riviera
  ✅ Plan de alimento, edades de menores y requerimientos especiales
  ✅ Botón "Guardar cambios" para editar/completar datos después
  ✅ Botón "Generar Cupón" que aparece cuando hay clave de confirmación
  ✅ Catálogo de hoteles con dirección, teléfono y estrellas
""")
