from reportes_financieros import menu_reportes_financieros
from gastos import menu_gastos
from sueldos import menu_sueldos
from database import crear_tablas
from usuarios import cargar_usuarios, login, menu, registrar_usuario_vendedora
from viajes import registrar_viaje, ver_viajes, editar_viaje, ver_mis_comisiones
from pagos import registrar_pago, pagar_comision
from reportes_riviera_mejorado import menu_reportes_riviera
from reportes_nacionales_mejorado import menu_reportes_nacionales
from reportes_movimientos import menu_reportes_movimientos
from reportes import ver_historial, reporte_general, reporte_por_vendedora
from reportes_riviera import (
    reporte_viaje_riviera_detallado,
    lista_pasajeros_riviera,
    reporte_bloqueos,
    viajes_proximos,
    comparativa_por_hotel
)
from vendedoras import (
    registrar_vendedora as registrar_vendedora_db,
    ver_vendedoras,
    editar_vendedora,
    cambiar_estado_vendedora
)
from bloqueos import (
    registrar_bloqueo,
    ver_bloqueos,
    editar_bloqueo,
    cambiar_estado_bloqueo,
    reporte_bloqueos
)
from hoteles import (
    cargar_hoteles_iniciales,
    ver_hoteles,
    editar_hotel,
    cambiar_estado_hotel,
    agregar_hotel_manual
)
from cotizador import crear_cotizacion, ver_cotizaciones
from nacionales import (
    registrar_viaje_nacional,
    ver_viajes_nacionales,
    registrar_cliente_nacional,
    ver_clientes_viaje,
    registrar_abono_nacional
)
from reportes_nacionales import (
    reporte_viaje_detallado,
    reporte_general_nacionales,
    lista_pasajeros_imprimir,
    comparativa_viajes
)
from internacionales import (
    registrar_viaje_internacional,
    ver_viajes_internacionales,
    registrar_cliente_internacional,
    ver_clientes_internacionales,
    registrar_abono_internacional
)
from grupos import menu_grupos
from ventas_grupos import menu_ventas_grupos
from operadores import menu_operadores


def registrar_vendedora_completa():
    """Registra vendedora y crea su usuario automáticamente"""
    from database import conectar
    from datetime import datetime
    
    nombre = input("Nombre de la vendedora: ").strip()
    
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO vendedoras (nombre, activa, fecha_registro)
            VALUES (?, 1, ?)
        """, (nombre, fecha_actual))
        
        vendedora_id = cursor.lastrowid
        
        conexion.commit()
        conexion.close()
        
        print(f"✅ Vendedora '{nombre}' registrada correctamente.")
        
        # Crear usuario automáticamente
        registrar_usuario_vendedora(vendedora_id, nombre)
        
    except Exception as e:
        print(f"❌ Error al registrar vendedora: {e}")
        conexion.close()


def main():
    """Función principal del sistema"""
    
    # Crear tablas si no existen
    crear_tablas()
    
    # Cargar hoteles iniciales si es primera vez
    cargar_hoteles_iniciales()
    
    # Cargar usuarios
    usuarios = cargar_usuarios()
    
    # Login
    usuario_actual = None
    while not usuario_actual:
        usuario_actual = login(usuarios)
        if not usuario_actual:
            continuar = input("¿Intentar de nuevo? (s/n): ").lower()
            if continuar != 's':
                print("👋 Saliendo del sistema...")
                return
    
    # Menú principal
    while True:
        menu(usuario_actual)
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            registrar_viaje(usuario_actual)
        
        elif opcion == "2":
            registrar_pago()
        
        elif opcion == "3":
            ver_viajes(usuario_actual)
        
        elif opcion == "4":
            pagar_comision()
        
        elif opcion == "5":
            ver_historial(usuario_actual)
        
        elif opcion == "6":
            editar_viaje(usuario_actual)
        
        # Opciones solo para ADMIN
        elif usuario_actual["rol"] == "ADMIN":
            if opcion == "7":
                registrar_vendedora_completa()
            
            elif opcion == "8":
                ver_vendedoras()
            
            elif opcion == "9":
                editar_vendedora()
            
            elif opcion == "10":
                cambiar_estado_vendedora()
            
            elif opcion == "11":
                reporte_general(usuario_actual)
            
            elif opcion == "12":
                reporte_por_vendedora()
            
            elif opcion == "34":
                reporte_viaje_riviera_detallado()
            
            elif opcion == "35":
                lista_pasajeros_riviera()
            
            elif opcion == "36":
                viajes_proximos()
            
            elif opcion == "37":
                comparativa_por_hotel()
            
            elif opcion == "13":
                registrar_bloqueo()
            
            elif opcion == "14":
                ver_bloqueos()
            
            elif opcion == "15":
                editar_bloqueo()
            
            elif opcion == "16":
                cambiar_estado_bloqueo()
            
            elif opcion == "17":
                reporte_bloqueos()
            
            elif opcion == "18":
                agregar_hotel_manual()
            
            elif opcion == "19":
                ver_hoteles()
            
            elif opcion == "20":
                editar_hotel()
            
            elif opcion == "21":
                cambiar_estado_hotel()
            
            elif opcion == "22":
                crear_cotizacion()
            
            elif opcion == "23":
                ver_cotizaciones()
            
            elif opcion == "24":
                registrar_viaje_nacional()
            
            elif opcion == "25":
                ver_viajes_nacionales(usuario_actual)
            
            elif opcion == "26":
                registrar_cliente_nacional()
            
            elif opcion == "27":
                ver_clientes_viaje()
            
            elif opcion == "28":
                registrar_abono_nacional()
            
            elif opcion == "29":
                reporte_viaje_detallado()
            
            elif opcion == "30":
                reporte_general_nacionales()
            
            elif opcion == "31":
                lista_pasajeros_imprimir()
            
            elif opcion == "32":
                comparativa_viajes()
            
            elif opcion == "38":
                registrar_viaje_internacional()
            
            elif opcion == "39":
                ver_viajes_internacionales()
            
            elif opcion == "40":
                registrar_cliente_internacional()
            
            elif opcion == "41":
                ver_clientes_internacionales()
            
            elif opcion == "42":
                registrar_abono_internacional()
            
            elif opcion == "33":
                menu_reportes_riviera()
            
            elif opcion == "44":
                menu_reportes_nacionales()
            
            elif opcion == "45":
                from reportes_internacionales import menu_reportes_internacionales
                menu_reportes_internacionales()
            
            elif opcion == "46":
                menu_reportes_movimientos()
            
            elif opcion == "47":
                menu_grupos()
            
            elif opcion == "48":
                menu_ventas_grupos()
            
            elif opcion == "49":
                menu_operadores()
            
            elif opcion == "43":
                print("👋 Saliendo del sistema...")
                break

            elif opcion == "50":
                menu_gastos()

            elif opcion == "51":
                menu_sueldos()

            elif opcion == "52":
                menu_reportes_financieros()
            
            else:
                print("❌ Opción no válida.")
        
        # Opciones para VENDEDORA
        elif usuario_actual["rol"] == "VENDEDORA":
            if opcion == "7":
                ver_viajes_nacionales(usuario_actual)
            
            elif opcion == "8":
                registrar_cliente_nacional()
            
            elif opcion == "9":
                ver_clientes_viaje()
            
            elif opcion == "10":
                registrar_abono_nacional()
            
            elif opcion == "11":
                ver_mis_comisiones(usuario_actual)
            
            elif opcion == "13":
                ver_viajes_internacionales()
            
            elif opcion == "14":
                registrar_cliente_internacional()
            
            elif opcion == "15":
                ver_clientes_internacionales()
            
            elif opcion == "16":
                registrar_abono_internacional()
            
            elif opcion == "17":
                print("👋 Saliendo del sistema...")
                break
            
            else:
                print("❌ Opción no válida.")


if __name__ == "__main__":
    main()
