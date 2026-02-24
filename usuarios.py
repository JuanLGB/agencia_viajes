import json
import os

RUTA_USUARIOS = "usuarios.json"


def cargar_usuarios():
    """Carga los usuarios desde el archivo JSON"""
    if not os.path.exists(RUTA_USUARIOS):
        # Crear archivo con usuario admin por defecto
        usuarios_default = [
            {
                "id_vendedora": 1,
                "usuario": "admin",
                "password": "admin123",
                "nombre": "Administrador",
                "rol": "ADMIN"
            }
        ]
        guardar_usuarios(usuarios_default)
        return usuarios_default
    
    with open(RUTA_USUARIOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_usuarios(usuarios):
    """Guarda los usuarios en el archivo JSON"""
    with open(RUTA_USUARIOS, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False)


def login(usuarios):
    """Sistema de login"""
    print("\n🔐 LOGIN")
    usuario = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()
    
    for u in usuarios:
        if u["usuario"] == usuario and u["password"] == password:
            # Obtener nombre del usuario, o usar el usuario si no tiene nombre
            nombre_mostrar = u.get("nombre", usuario)
            print(f"✅ Bienvenido {nombre_mostrar}")
            return u
    
    print("❌ Usuario o contraseña incorrectos.")
    return None


def menu(usuario_actual):
    """Muestra el menú según el rol del usuario"""
    print("\n" + "="*50)
    print("📌 SISTEMA AGENCIA DE VIAJES")
    print("="*50)
    print("--- RIVIERA MAYA ---")
    print("1. Registrar viaje")
    print("2. Registrar pago")
    print("3. Ver viajes")
    
    if usuario_actual["rol"] == "ADMIN":
        print("4. Pagar comisión")
    
    print("5. Historial de ventas")
    print("6. Editar viaje")
    
    if usuario_actual["rol"] == "ADMIN":
        print("\n--- VENDEDORAS ---")
        print("7. Registrar vendedora")
        print("8. Ver vendedoras")
        print("9. Editar vendedora")
        print("10. Activar / Desactivar vendedora")
        
        print("\n--- REPORTES RIVIERA MAYA ---")
        print("11. Reporte general")
        print("12. Reporte por vendedora")
        print("33. 📊 Reportes Riviera (Consola + Excel) ⭐ NUEVO")
        print("34. Reporte detallado de viaje")
        print("35. Lista de pasajeros (imprimir)")
        print("36. Viajes próximos (30 días)")
        print("37. Comparativa por hotel")
        
        print("\n--- BLOQUEOS ---")
        print("13. Registrar bloqueo")
        print("14. Ver bloqueos")
        print("15. Editar bloqueo")
        print("16. Cerrar bloqueo")
        print("17. Reporte de bloqueos")
        
        print("\n--- GRUPOS (MAMÁ) ---")
        print("47. 📦 Gestión de Grupos ⭐ NUEVO")
        print("48. 📦 Ventas en Grupos ⭐ NUEVO")
        
        print("\n--- OPERADORES ---")
        print("49. 🏢 Gestión de Operadores ⭐ NUEVO")
        
        print("\n--- HOTELES ---")
        print("18. Agregar hotel")
        print("19. Ver hoteles")
        print("20. Editar hotel")
        print("21. Activar / Desactivar hotel")
        
        print("\n--- VIAJES NACIONALES ---")
        print("22. Crear cotización")
        print("23. Ver cotizaciones")
        print("24. Registrar viaje nacional")
        print("25. Ver viajes nacionales")
        print("26. Registrar cliente")
        print("27. Ver clientes")
        print("28. Registrar abono")
        
        print("\n--- REPORTES NACIONALES ---")
        print("44. 📊 Reportes Nacionales (Consola + Excel) ⭐ NUEVO")
        print("29. Reporte detallado de viaje")
        print("30. Reporte general nacionales")
        print("31. Lista de pasajeros (imprimir)")
        print("32. Comparativa de viajes")
        
        print("\n--- VIAJES INTERNACIONALES ---")
        print("38. Registrar viaje internacional")
        print("39. Ver viajes internacionales")
        print("40. Registrar cliente")
        print("41. Ver clientes")
        print("42. Registrar abono")
        print("45. 📊 Reportes Internacionales (Consola + Excel) ⭐ NUEVO")
        
        print("\n--- REPORTES GENERALES ---")
        print("46. 💰 Reporte de Movimientos (Todos los abonos) ⭐ NUEVO")

        print("\n--- GASTOS OPERATIVOS ---")
        print("50. 💰 Gestión de Gastos ⭐ NUEVO")
        print("51. 👥 Gestión de Sueldos ⭐ NUEVO")

        print("\n--- REPORTES FINANCIEROS ---")
        print("52. 📊 Reporte Financiero Completo ⭐ NUEVO")
        
        print("\n43. Salir")
    else:
        print("\n--- MIS REPORTES ---")
        print("12. 📊 Reportes Riviera (Consola + Excel) ⭐ NUEVO")
        
        print("\n--- VIAJES NACIONALES ---")
        print("7. Ver viajes nacionales")
        print("8. Registrar cliente")
        print("9. Ver clientes")
        print("10. Registrar abono")
        
        print("\n--- MIS COMISIONES ---")
        print("11. Ver mis comisiones")
        
        print("\n--- VIAJES INTERNACIONALES ---")
        print("13. Ver viajes internacionales")
        print("14. Registrar cliente")
        print("15. Ver clientes")
        print("16. Registrar abono")
        
        print("\n17. Salir")
    
    print("="*50)


def registrar_usuario_vendedora(vendedora_id, nombre_vendedora):
    """Registra un usuario tipo VENDEDORA automáticamente"""
    usuarios = cargar_usuarios()
    
    # Verificar si ya existe un usuario para esta vendedora
    for u in usuarios:
        if u.get("id_vendedora") == vendedora_id:
            print(f"⚠️ Ya existe un usuario para la vendedora {nombre_vendedora}")
            return
    
    # Generar usuario automático
    usuario_base = nombre_vendedora.lower().replace(" ", "")
    usuario = usuario_base
    
    # Asegurar que el usuario sea único
    contador = 1
    while any(u["usuario"] == usuario for u in usuarios):
        usuario = f"{usuario_base}{contador}"
        contador += 1
    
    # Password temporal
    password = f"{usuario}123"
    
    nuevo_usuario = {
        "id_vendedora": vendedora_id,
        "usuario": usuario,
        "password": password,
        "nombre": nombre_vendedora,
        "rol": "VENDEDORA"
    }
    
    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)
    
    print(f"\n✅ Usuario creado automáticamente:")
    print(f"   Usuario: {usuario}")
    print(f"   Contraseña: {password}")
    print(f"   ⚠️ La vendedora debe cambiar su contraseña al iniciar sesión")
