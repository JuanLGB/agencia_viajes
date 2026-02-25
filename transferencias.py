import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime

def mostrar_pagina_transferencias():
    """Página principal de control de transferencias"""
    st.title("💸 Control de Transferencias")

    # Obtener vendedoras para el select
    conexion = conectar()
    cursor = conexion.cursor()

    # ===== DASHBOARD DE RESUMEN =====
    cursor.execute("""
        SELECT
            COALESCE(SUM(cantidad), 0) as total_recibido,
            COALESCE(SUM(CASE WHEN estado = 'PENDIENTE' THEN cantidad ELSE 0 END), 0) as total_pendiente,
            COALESCE(SUM(CASE WHEN estado = 'APLICADO' THEN cantidad ELSE 0 END), 0) as total_aplicado,
            COUNT(*) as total_registros
        FROM transferencias
    """)
    stats = cursor.fetchone()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Registrado", f"${stats[0]:,.2f}")
    with col2:
        st.metric("Pendiente de Aplicar", f"${stats[1]:,.2f}")
    with col3:
        st.metric("Ya Aplicado", f"${stats[2]:,.2f}")
    with col4:
        st.metric("Total Registros", stats[3])

    st.markdown("---")

    # ===== TABS PARA LAS FUNCIONES =====
    tab1, tab2, tab3 = st.tabs(["📝 Registrar Transferencia", "🔍 Ver Historial", "✅ Aplicar a Viaje"])

    # ===== TAB 1: REGISTRAR TRANSFERENCIA =====
    with tab1:
        st.subheader("Registrar Nueva Transferencia")

        with st.form("form_registro_transferencia"):
            col_fecha, col_nombre = st.columns(2)

            with col_fecha:
                fecha_transferencia = st.date_input("Fecha de Transferencia", value=datetime.now().date())

            with col_nombre:
                nombre_envia = st.text_input("Nombre de quien envía", placeholder="Ej: Pedro González")

            cantidad = st.number_input("Cantidad transferida ($)", min_value=0.01, value=1000.0, step=100.0)

            observaciones = st.text_area("Observaciones (opcional)", placeholder="Notas adicionales sobre la transferencia...")

            submitted = st.form_submit_button("💾 Registrar Transferencia", type="primary")

            if submitted:
                if not nombre_envia.strip():
                    st.error("⚠️ El nombre de quien envía es obligatorio")
                elif cantidad <= 0:
                    st.error("⚠️ La cantidad debe ser mayor a cero")
                else:
                    # Obtener ID de vendedora logueada
                    id_vendedora = st.session_state.get("id_vendedora", 1)

                    cursor.execute("""
                        INSERT INTO transferencias (fecha, nombre_envia, cantidad, estado, observaciones, id_vendedora)
                        VALUES (?, ?, ?, 'PENDIENTE', ?, ?)
                    """, (str(fecha_transferencia), nombre_envia.strip(), cantidad, observaciones.strip() if observaciones else None, id_vendedora))

                    conexion.commit()
                    st.success(f"✅ Transferencia registrada: {nombre_envia} - ${cantidad:,.2f}")
                    st.rerun()

    # ===== TAB 2: VER HISTORIAL =====
    with tab2:
        st.subheader("Historial de Transferencias")

        # Filtros
        col_filtro1, col_filtro2, col_filtro3 = st.columns(3)

        with col_filtro1:
            filtro_estado = st.selectbox("Filtrar por estado", ["TODOS", "PENDIENTE", "APLICADO", "CANCELADO"])

        with col_filtro2:
            # Obtener lista de nombres para el filtro
            cursor.execute("SELECT DISTINCT nombre_envia FROM transferencias ORDER BY nombre_envia")
            nombres = ["TODOS"] + [r[0] for r in cursor.fetchall()]
            filtro_nombre = st.selectbox("Filtrar por nombre", nombres)

        with col_filtro3:
            # Obtener años disponibles
            cursor.execute("SELECT DISTINCT substr(fecha, 1, 4) as año FROM transferencias ORDER BY año DESC")
            años = ["TODOS"] + [r[0] for r in cursor.fetchall()]
            filtro_año = st.selectbox("Filtrar por año", años)

        # Construir query con filtros
        query = "SELECT id, fecha, nombre_envia, cantidad, estado, aplicado_en, fecha_aplicacion, observaciones, created_at FROM transferencias WHERE 1=1"
        params = []

        if filtro_estado != "TODOS":
            query += " AND estado = ?"
            params.append(filtro_estado)

        if filtro_nombre != "TODOS":
            query += " AND nombre_envia = ?"
            params.append(filtro_nombre)

        if filtro_año != "TODOS":
            query += " AND substr(fecha, 1, 4) = ?"
            params.append(filtro_año)

        query += " ORDER BY fecha DESC, id DESC"

        df = pd.read_sql_query(query, conexion, params=params)

        if not df.empty:
            # Formatear para mostrar
            df_display = df.copy()
            df_display['cantidad'] = df_display['cantidad'].apply(lambda x: f"${x:,.2f}")

            # Color según estado
            def estado_color(estado):
                if estado == "PENDIENTE":
                    return "🟡 PENDIENTE"
                elif estado == "APLICADO":
                    return "🟢 APLICADO"
                else:
                    return "🔴 CANCELADO"

            df_display['estado'] = df_display['estado'].apply(estado_color)

            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "fecha": "Fecha",
                    "nombre_envia": "Nombre",
                    "cantidad": "Cantidad",
                    "estado": "Estado",
                    "aplicado_en": "Aplicado en",
                    "fecha_aplicacion": "Fecha aplicación",
                    "observaciones": "Observaciones"
                }
            )

            # Opción para exportar
            if st.button("📥 Exportar a Excel"):
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Transferencias')
                st.download_button(
                    label="Descargar Excel",
                    data=output.getvalue(),
                    file_name=f"transferencias_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("ℹ️ No hay transferencias registradas con los filtros seleccionados.")

    # ===== TAB 3: APLICAR A VIAJE =====
    with tab3:
        st.subheader("Aplicar Transferencia a un Viaje")

        # Obtener transferencias pendientes
        cursor.execute("""
            SELECT id, fecha, nombre_envia, cantidad
            FROM transferencias
            WHERE estado = 'PENDIENTE'
            ORDER BY fecha DESC
        """)
        pendientes = cursor.fetchall()

        if not pendientes:
            st.info("ℹ️ No hay transferencias pendientes de aplicar.")
        else:
            # Seleccionar transferencia
            opciones_transferencia = [f"#{t[0]} - {t[2]} - ${t[3]:,.2f} ({t[1]})" for t in pendientes]
            seleccion = st.selectbox("Seleccionar transferencia a aplicar", opciones_transferencia)

            if seleccion:
                id_transferencia = int(seleccion.split("#")[1].split(" -")[0])

                # Mostrar detalle de la transferencia seleccionada
                cursor.execute("SELECT id, fecha, nombre_envia, cantidad, observaciones FROM transferencias WHERE id = ?", (id_transferencia,))
                t = cursor.fetchone()

                st.markdown("### Transferencia Seleccionada")
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.metric("Fecha", t[1])
                with col_t2:
                    st.metric("Nombre", t[2])
                with col_t3:
                    st.metric("Cantidad", f"${t[3]:,.2f}")

                if t[4]:
                    st.caption(f"Obs: {t[4]}")

                st.markdown("---")

                # Buscar localizador
                st.markdown("### Buscar Localizador")
                busqueda = st.text_input("Ingrese número de localizador", placeholder="Ej: 307254")

                if busqueda:
                    # Buscar en la tabla de ventas
                    cursor.execute("""
                        SELECT id, cliente, destino, fecha_inicio, precio_total, pagado, saldo, estado
                        FROM ventas
                        WHERE no_localizador = ? OR CAST(id AS TEXT) = ?
                    """, (busqueda, busqueda))
                    venta = cursor.fetchone()

                    if venta:
                        st.success(f"✅ Localizador encontrado: #{venta[0]}")

                        # Mostrar info de la venta
                        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
                        with col_v1:
                            st.metric("Cliente", venta[1][:20] + "..." if len(venta[1]) > 20 else venta[1])
                        with col_v2:
                            st.metric("Destino", venta[2])
                        with col_v3:
                            st.metric("Total", f"${venta[4]:,.2f}")
                        with col_v4:
                            st.metric("Saldo", f"${venta[6]:,.2f}")

                        # Botón para aplicar
                        if st.button("✅ Confirmar Aplicación", type="primary"):
                            fecha_aplicacion = datetime.now().strftime("%Y-%m-%d")

                            cursor.execute("""
                                UPDATE transferencias
                                SET estado = 'APLICADO',
                                    aplicado_en = ?,
                                    fecha_aplicacion = ?
                                WHERE id = ?
                            """, (busqueda, fecha_aplicacion, id_transferencia))

                            conexion.commit()
                            st.success(f"✅ Transferencia #{id_transferencia} aplicada al localizador {busqueda}")
                            st.rerun()
                    else:
                        st.warning("⚠️ No se encontró ningún viaje con ese localizador.")

        # Mostrar aplicaciones recientes
        st.markdown("---")
        st.subheader("Aplicaciones Recientes")

        cursor.execute("""
            SELECT id, fecha, nombre_envia, cantidad, aplicado_en, fecha_aplicacion
            FROM transferencias
            WHERE estado = 'APLICADO'
            ORDER BY fecha_aplicacion DESC
            LIMIT 10
        """)
        aplicados = cursor.fetchall()

        if aplicados:
            for a in aplicados:
                st.markdown(f"""
                <div style="background:#e8f5e9; padding:10px; border-radius:8px; margin:5px 0;">
                    <strong>#{a[0]}</strong> - {a[2]} - <strong>${a[3]:,.2f}</strong>
                    <br>✅ Aplicado en: <code>{a[4]}</code> el {a[5]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay aplicaciones registradas.")

    conexion.close()
