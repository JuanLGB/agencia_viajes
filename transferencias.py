import streamlit as st
import pandas as pd
from database import conectar
from datetime import datetime

def mostrar_pagina_transferencias():
    """Página principal de control de transferencias"""
    st.title("💸 Control de Transferencias")

    # Obtener conexión
    conexion = conectar()
    cursor = conexion.cursor()

    # Obtener lista de mayoristas para selects
    cursor.execute("SELECT id, nombre FROM operadores WHERE activo = 1 ORDER BY nombre")
    mayoristas = cursor.fetchall()
    dict_mayoristas = {m[1]: m[0] for m in mayoristas}

    # Obtener lista de vendedoras
    cursor.execute("SELECT id, nombre FROM vendedoras WHERE activa = 1 ORDER BY nombre")
    vendedoras = cursor.fetchall()

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
            col_fecha, col_mayorista = st.columns(2)

            with col_fecha:
                fecha_transferencia = st.date_input("Fecha de Transferencia", value=datetime.now().date())

            with col_mayorista:
                empresa_mayorista = st.selectbox(
                    "Empresa Mayorista",
                    options=[""] + [m[1] for m in mayoristas],
                    index=0
                )

            col_nombre, col_vendedora = st.columns(2)
            with col_nombre:
                nombre_envia = st.text_input("Nombre de quien envía", placeholder="Ej: Pedro González")

            with col_vendedora:
                # Obtener vendedoras para el select
                opciones_vendedoras = [""] + [v[1] for v in vendedoras]
                nombre_vendedora = st.selectbox("Vendedora que registra", opciones_vendedoras, index=0)

            cantidad = st.number_input("Cantidad transferida ($)", min_value=0.01, value=1000.0, step=100.0)

            observaciones = st.text_area("Observaciones (opcional)", placeholder="Notas adicionales sobre la transferencia...")

            submitted = st.form_submit_button("💾 Registrar Transferencia", type="primary")

            if submitted:
                if not nombre_envia.strip():
                    st.error("⚠️ El nombre de quien envía es obligatorio")
                elif cantidad <= 0:
                    st.error("⚠️ La cantidad debe ser mayor a cero")
                elif not empresa_mayorista:
                    st.error("⚠️ Selecciona la empresa mayorista")
                elif not nombre_vendedora:
                    st.error("⚠️ Selecciona la vendedora que registra")
                else:
                    # Obtener ID de vendedora seleccionada
                    id_vendedora = None
                    for v in vendedoras:
                        if v[1] == nombre_vendedora:
                            id_vendida = v[0]
                            break

                    cursor.execute("""
                        INSERT INTO transferencias (fecha, nombre_envia, cantidad, estado, observaciones, id_vendedora, empresa_mayorista)
                        VALUES (?, ?, ?, 'PENDIENTE', ?, ?, ?)
                    """, (str(fecha_transferencia), nombre_envia.strip(), cantidad, observaciones.strip() if observaciones else None, id_vendedora, empresa_mayorista))

                    conexion.commit()
                    st.success(f"✅ Transferencia registrada: {nombre_envia} - ${cantidad:,.2f} - Mayorista: {empresa_mayorista} - Registró: {nombre_vendedora}")
                    st.rerun()

    # ===== TAB 2: VER HISTORIAL =====
    with tab2:
        st.subheader("Historial de Transferencias")

        # Filtros
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)

        with col_filtro1:
            filtro_estado = st.selectbox("Filtrar por estado", ["TODOS", "PENDIENTE", "APLICADO", "CANCELADO"])

        with col_filtro2:
            cursor.execute("SELECT DISTINCT nombre_envia FROM transferencias ORDER BY nombre_envia")
            nombres = ["TODOS"] + [r[0] for r in cursor.fetchall()]
            filtro_nombre = st.selectbox("Filtrar por nombre", nombres)

        with col_filtro3:
            cursor.execute("SELECT DISTINCT empresa_mayorista FROM transferencias WHERE empresa_mayorista IS NOT NULL ORDER BY empresa_mayorista")
            filter_may = ["TODOS"] + [r[0] for r in cursor.fetchall()]
            filtro_mayorista = st.selectbox("Filtrar por mayorista", filter_may)

        with col_filtro4:
            # Filtro por vendedora
            cursor.execute("""
                SELECT DISTINCT v.nombre
                FROM transferencias t
                LEFT JOIN vendedoras v ON t.id_vendedora = v.id
                WHERE t.id_vendedora IS NOT NULL
                ORDER BY v.nombre
            """)
            filtro_vend = ["TODOS"] + [r[0] for r in cursor.fetchall() if r[0]]
            if filtro_vend:
                filtro_vendedora = st.selectbox("Filtrar por vendedora", filtro_vend)
            else:
                filtro_vendedora = "TODOS"

        # Construir query con filtros
        query = """
            SELECT t.id, t.fecha, t.nombre_envia, t.cantidad, t.empresa_mayorista, t.estado,
                   t.aplicado_en, t.fecha_aplicacion, t.observaciones, v.nombre as nombre_vendedora,
                   (SELECT cliente FROM ventas WHERE no_localizador = t.aplicado_en LIMIT 1) as responsable_localizador
            FROM transferencias t
            LEFT JOIN vendedoras v ON t.id_vendedora = v.id
            WHERE 1=1
        """
        params = []

        if filtro_estado != "TODOS":
            query += " AND t.estado = ?"
            params.append(filtro_estado)

        if filtro_nombre != "TODOS":
            query += " AND t.nombre_envia = ?"
            params.append(filtro_nombre)

        if filtro_mayorista != "TODOS":
            query += " AND t.empresa_mayorista = ?"
            params.append(filtro_mayorista)

        if filtro_vendedora != "TODOS":
            query += " AND v.nombre = ?"
            params.append(filtro_vendedora)

        query += " ORDER BY t.fecha DESC, t.id DESC"

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
                    "nombre_envia": "Cliente que paga",
                    "cantidad": "Cantidad",
                    "empresa_mayorista": "Mayorista",
                    "nombre_vendedora": "Vendedora",
                    "estado": "Estado",
                    "aplicado_en": "Aplicado en",
                    "responsable_localizador": "Responsable localizador",
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

        # Obtener transferencias pendientes con nombre de vendedora
        cursor.execute("""
            SELECT t.id, t.fecha, t.nombre_envia, t.cantidad, t.empresa_mayorista, v.nombre as nombre_vendedora
            FROM transferencias t
            LEFT JOIN vendedoras v ON t.id_vendedora = v.id
            WHERE t.estado = 'PENDIENTE'
            ORDER BY t.fecha DESC
        """)
        pendientes = cursor.fetchall()

        if not pendientes:
            st.info("ℹ️ No hay transferencias pendientes de aplicar.")
        else:
            # Seleccionar transferencia
            opciones_transferencia = [f"#{t[0]} - {t[2]} - ${t[3]:,.2f} - {t[4]} ({t[1]}) - Registró: {t[5]}" for t in pendientes]
            seleccion = st.selectbox("Seleccionar transferencia a aplicar", opciones_transferencia)

            if seleccion:
                id_transferencia = int(seleccion.split("#")[1].split(" -")[0])

                # Mostrar detalle de la transferencia seleccionada
                cursor.execute("""
                    SELECT t.id, t.fecha, t.nombre_envia, t.cantidad, t.observaciones, t.empresa_mayorista, v.nombre as nombre_vendedora
                    FROM transferencias t
                    LEFT JOIN vendedoras v ON t.id_vendedora = v.id
                    WHERE t.id = ?
                """, (id_transferencia,))
                t = cursor.fetchone()

                st.markdown("### Transferencia Seleccionada")
                col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                with col_t1:
                    st.metric("Fecha", t[1])
                with col_t2:
                    st.metric("Nombre", t[2])
                with col_t3:
                    st.metric("Cantidad", f"${t[3]:,.2f}")
                with col_t4:
                    st.metric("Mayorista", t[5])

                st.markdown(f"**Regístró:** {t[6]}")

                if t[4]:
                    st.caption(f"Obs: {t[4]}")

                st.markdown("---")

                # Seleccionar mayorista para filtrar viajes
                st.markdown("### Buscar Viaje para Aplicar")

                mayorista_seleccionado = t[5]

                st.info(f"💡 Solo se mostrarán viajes del mayorista: **{mayorista_seleccionado}**")

                # Obtener viajes de ese mayorista
                cursor.execute("""
                    SELECT DISTINCT no_localizador, cliente, destino, fecha_inicio, precio_total, pagado, saldo, estado, id
                    FROM ventas
                    WHERE no_localizador IS NOT NULL AND no_localizador != ''
                    ORDER BY fecha_inicio DESC
                    LIMIT 50
                """)
                todos_viajes = cursor.fetchall()

                # También buscar por localizador específico
                col_buscar1, col_buscar2 = st.columns([2, 1])

                with col_buscar1:
                    busqueda = st.text_input("Buscar por número de localizador", placeholder="Ej: 307254")

                with col_buscar2:
                    ver_todos = st.checkbox("Ver todos los viajes", value=False)

                if busqueda:
                    # Buscar en la tabla de ventas
                    cursor.execute("""
                        SELECT no_localizador, cliente, destino, fecha_inicio, precio_total, pagado, saldo, estado, id
                        FROM ventas
                        WHERE no_localizador = ? OR CAST(id AS TEXT) = ?
                    """, (busqueda, busqueda))
                    venta = cursor.fetchone()

                    if venta:
                        st.success(f"✅ Localizador encontrado: #{venta[0]}")

                        # Mostrar info de la venta con el RESPONSABLE
                        col_v1, col_v2, col_v3, col_v4 = st.columns(4)
                        with col_v1:
                            st.metric("Responsable", venta[1][:25] + "..." if len(venta[1]) > 25 else venta[1])
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
                            st.success(f"✅ Transferencia #{id_transferencia} aplicada al localizador {busqueda} (Responsable: {venta[1]})")
                            st.rerun()
                    else:
                        st.warning("⚠️ No se encontró ningún viaje con ese localizador.")

                elif ver_todos:
                    # Mostrar lista de viajes disponibles
                    if todos_viajes:
                        st.write("#### Viajes Disponibles")
                        for v in todos_viajes:
                            with st.expander(f"📍 {v[0]} - {v[1]} - ${v[6]:,.2f} saldo"):
                                col_v1, col_v2, col_v3 = st.columns(3)
                                with col_v1:
                                    st.write(f"**Cliente/Responsable:** {v[1]}")
                                    st.write(f"**Destino:** {v[2]}")
                                with col_v2:
                                    st.write(f"**Fecha:** {v[3]}")
                                    st.write(f"**Total:** ${v[4]:,.2f}")
                                with col_v3:
                                    st.write(f"**Pagado:** ${v[5]:,.2f}")
                                    st.write(f"**Saldo:** ${v[6]:,.2f}")

                                # Botón de aplicar rápido
                                if st.button(f"Aplicar a {v[0]}", key=f"aplicar_{v[8]}"):
                                    fecha_aplicacion = datetime.now().strftime("%Y-%m-%d")
                                    cursor.execute("""
                                        UPDATE transferencias
                                        SET estado = 'APLICADO',
                                            aplicado_en = ?,
                                            fecha_aplicacion = ?
                                        WHERE id = ?
                                    """, (v[0], fecha_aplicacion, id_transferencia))
                                    conexion.commit()
                                    st.success(f"✅ Aplicado al localizador {v[0]} (Responsable: {v[1]})")
                                    st.rerun()
                    else:
                        st.info("No hay viajes registrados.")

        # Mostrar aplicaciones recientes
        st.markdown("---")
        st.subheader("Aplicaciones Recientes")

        cursor.execute("""
            SELECT t.id, t.fecha, t.nombre_envia, t.cantidad, t.empresa_mayorista, t.aplicado_en, t.fecha_aplicacion,
                   (SELECT cliente FROM ventas WHERE no_localizador = t.aplicado_en LIMIT 1) as responsable
            FROM transferencias t
            WHERE t.estado = 'APLICADO'
            ORDER BY t.fecha_aplicacion DESC
            LIMIT 10
        """)
        aplicados = cursor.fetchall()

        if aplicados:
            for a in aplicados:
                st.markdown(f"""
                <div style="background:#e8f5e9; padding:10px; border-radius:8px; margin:5px 0;">
                    <strong>#{a[0]}</strong> - {a[2]} - <strong>${a[3]:,.2f}</strong> - {a[4]}
                    <br>✅ Aplicado en: <code>{a[5]}</code> - Responsable: <strong>{a[7]}</strong> el {a[6]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay aplicaciones registradas.")

    conexion.close()
