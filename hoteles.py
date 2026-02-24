from database import conectar
from datetime import datetime


# Lista inicial de hoteles All-Inclusive de Riviera Maya
HOTELES_INICIALES = [
    "Hard Rock Hotel Riviera Maya",
    "Hard Rock Hotel Cancún",
    "Moon Palace Cancún",
    "Moon Palace The Grand",
    "Xcaret Hotel",
    "Hotel Xcaret Arte",
    "La Casa de la Playa by Xcaret",
    "Secrets Maroma Beach",
    "Secrets Playa Mujeres",
    "Secrets Akumal",
    "Secrets Riviera Cancún",
    "Excellence Playa Mujeres",
    "Excellence Riviera Cancún",
    "Beloved Playa Mujeres",
    "Valentin Imperial Maya",
    "Grand Palladium Costa Mujeres",
    "Grand Palladium White Sand",
    "TRS Coral Hotel",
    "TRS Yucatan Hotel",
    "Catalonia Royal Tulum",
    "Catalonia Playa Maroma",
    "Hideaway at Royalton Riviera Cancún",
    "Royalton Riviera Cancún",
    "Royalton Splash Riviera Cancún",
    "Generations Riviera Maya",
    "Azul Beach Resort Riviera Cancún",
    "Azul Beach Resort Riviera Maya",
    "Hyatt Ziva Cancún",
    "Hyatt Ziva Riviera Cancún",
    "Hyatt Zilara Cancún",
    "Hyatt Zilara Riviera Maya",
    "Live Aqua Beach Resort Cancún",
    "Fiesta Americana Condesa Cancún",
    "Grand Fiesta Americana Coral Beach",
    "Finest Playa Mujeres",
    "Haven Riviera Cancún",
    "Atelier Playa Mujeres",
    "Impression Moxché",
    "Bahia Principe Grand Tulum",
    "Bahia Principe Luxury Akumal",
    "Bahia Principe Grand Coba",
    "Dreams Playa Mujeres",
    "Dreams Jade Resort",
    "Dreams Riviera Cancún",
    "Dreams Tulum",
    "Now Jade Riviera Cancún",
    "Now Sapphire Riviera Cancún",
    "Now Emerald Cancún",
    "Breathless Riviera Cancún",
    "Secrets Capri Riviera Cancún",
    "El Dorado Seaside Suites",
    "El Dorado Casitas Royale",
    "El Dorado Maroma",
    "Generations Maroma",
    "Sandos Playacar",
    "Sandos Caracol",
    "The Pyramid at Grand Oasis",
    "Grand Oasis Cancún",
    "Occidental at Xcaret Destination",
    "Barceló Maya Palace",
    "Barceló Maya Colonial",
    "Barceló Maya Tropical",
    "Ocean Riviera Paradise",
    "Ocean Coral & Turquesa",
]


def cargar_hoteles_iniciales():
    """Carga la lista inicial de hoteles si la tabla está vacía"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Verificar si ya hay hoteles
    cursor.execute("SELECT COUNT(*) FROM hoteles")
    cantidad = cursor.fetchone()[0]
    
    if cantidad == 0:
        print("\n🏨 Cargando catálogo inicial de hoteles All-Inclusive...")
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for hotel in HOTELES_INICIALES:
            cursor.execute("""
                INSERT INTO hoteles (nombre, destino, all_inclusive, activo, veces_usado, fecha_registro)
                VALUES (?, 'Riviera Maya', 1, 1, 0, ?)
            """, (hotel, fecha_actual))
        
        conexion.commit()
        print(f"✅ {len(HOTELES_INICIALES)} hoteles cargados correctamente.")
    
    conexion.close()


def buscar_hoteles(texto_busqueda, limite=5):
    """Busca hoteles que coincidan con el texto ingresado"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    # Buscar hoteles activos que contengan el texto
    cursor.execute("""
        SELECT id, nombre, veces_usado
        FROM hoteles
        WHERE activo = 1 AND nombre LIKE ?
        ORDER BY veces_usado DESC, nombre ASC
        LIMIT ?
    """, (f"%{texto_busqueda}%", limite))
    
    resultados = cursor.fetchall()
    conexion.close()
    
    return resultados


def seleccionar_hotel():
    """Permite seleccionar un hotel con autocompletado"""
    
    print("\n🏨 SELECCIÓN DE HOTEL")
    print("(Comienza a escribir para ver sugerencias)")
    
    while True:
        texto = input("\nHotel: ").strip()
        
        if not texto:
            print("❌ Debes ingresar un nombre.")
            continue
        
        if len(texto) < 3:
            print("⚠️ Escribe al menos 3 caracteres para ver sugerencias.")
            continue
        
        # Buscar coincidencias
        resultados = buscar_hoteles(texto, limite=10)
        
        if resultados:
            print(f"\n¿Te refieres a alguno de estos?")
            for i, (id_hotel, nombre, veces) in enumerate(resultados, 1):
                print(f"{i}. {nombre}")
            
            print(f"{len(resultados) + 1}. ✏️ Usar exactamente: '{texto}'")
            print(f"{len(resultados) + 2}. 🔄 Escribir de nuevo")
            
            try:
                opcion = int(input("\nSelecciona opción: "))
                
                if 1 <= opcion <= len(resultados):
                    # Seleccionó un hotel existente
                    hotel_seleccionado = resultados[opcion - 1][1]
                    incrementar_uso(resultados[opcion - 1][0])
                    return hotel_seleccionado
                
                elif opcion == len(resultados) + 1:
                    # Usar el texto exacto y agregarlo
                    agregar_hotel_automatico(texto)
                    return texto
                
                elif opcion == len(resultados) + 2:
                    # Escribir de nuevo
                    continue
                
                else:
                    print("❌ Opción inválida.")
            
            except ValueError:
                print("❌ Opción inválida.")
        
        else:
            # No hay coincidencias
            print(f"\n⚠️ No se encontraron hoteles con '{texto}'")
            respuesta = input("¿Usar este nombre y agregarlo al catálogo? (s/n): ").strip().lower()
            
            if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
                agregar_hotel_automatico(texto)
                return texto
            else:
                continue


def agregar_hotel_automatico(nombre_hotel):
    """Agrega un hotel nuevo automáticamente al catálogo"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO hoteles (nombre, destino, all_inclusive, activo, veces_usado, fecha_registro)
            VALUES (?, 'Riviera Maya', 1, 1, 1, ?)
        """, (nombre_hotel, fecha_actual))
        
        conexion.commit()
        print(f"✅ '{nombre_hotel}' agregado al catálogo.")
    
    except:
        # Ya existe, solo incrementar uso
        cursor.execute("""
            UPDATE hoteles SET veces_usado = veces_usado + 1
            WHERE nombre = ?
        """, (nombre_hotel,))
        conexion.commit()
    
    conexion.close()


def incrementar_uso(id_hotel):
    """Incrementa el contador de veces usado de un hotel"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        UPDATE hoteles
        SET veces_usado = veces_usado + 1
        WHERE id = ?
    """, (id_hotel,))
    
    conexion.commit()
    conexion.close()


def ver_hoteles():
    """Muestra todos los hoteles registrados"""
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("""
        SELECT id, nombre, veces_usado, activo
        FROM hoteles
        ORDER BY veces_usado DESC, nombre ASC
    """)
    
    hoteles = cursor.fetchall()
    conexion.close()
    
    print("\n🏨 CATÁLOGO DE HOTELES\n")
    
    if not hoteles:
        print("No hay hoteles registrados.")
        return
    
    for hotel in hoteles:
        estado = "✅ ACTIVO" if hotel[3] == 1 else "❌ INACTIVO"
        print(f"ID: {hotel[0]} | {hotel[1]}")
        print(f"   Usado: {hotel[2]} veces | {estado}")
        print("-" * 60)


def editar_hotel():
    """Edita el nombre de un hotel"""
    ver_hoteles()
    
    try:
        id_hotel = int(input("\nID del hotel a editar: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre FROM hoteles WHERE id = ?", (id_hotel,))
    resultado = cursor.fetchone()
    
    if not resultado:
        print("❌ Hotel no encontrado.")
        conexion.close()
        return
    
    nombre_actual = resultado[0]
    nuevo_nombre = input(f"Nombre actual: {nombre_actual}\nNuevo nombre: ").strip()
    
    if not nuevo_nombre:
        print("❌ El nombre no puede estar vacío.")
        conexion.close()
        return
    
    cursor.execute("""
        UPDATE hoteles
        SET nombre = ?
        WHERE id = ?
    """, (nuevo_nombre, id_hotel))
    
    conexion.commit()
    conexion.close()
    
    print("✅ Hotel actualizado.")


def cambiar_estado_hotel():
    """Activa o desactiva un hotel"""
    ver_hoteles()
    
    try:
        id_hotel = int(input("\nID del hotel: "))
    except ValueError:
        print("❌ ID inválido.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT activo FROM hoteles WHERE id = ?", (id_hotel,))
    resultado = cursor.fetchone()
    
    if not resultado:
        print("❌ Hotel no encontrado.")
        conexion.close()
        return
    
    nuevo_estado = 0 if resultado[0] == 1 else 1
    
    cursor.execute("""
        UPDATE hoteles
        SET activo = ?
        WHERE id = ?
    """, (nuevo_estado, id_hotel))
    
    conexion.commit()
    conexion.close()
    
    estado_texto = "ACTIVO" if nuevo_estado == 1 else "INACTIVO"
    print(f"✅ Hotel ahora está {estado_texto}")


def agregar_hotel_manual():
    """Agrega un hotel manualmente desde el menú"""
    nombre = input("\nNombre del hotel: ").strip()
    
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    conexion = conectar()
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        cursor.execute("""
            INSERT INTO hoteles (nombre, destino, all_inclusive, activo, veces_usado, fecha_registro)
            VALUES (?, 'Riviera Maya', 1, 1, 0, ?)
        """, (nombre, fecha_actual))
        
        conexion.commit()
        print(f"✅ Hotel '{nombre}' agregado correctamente.")
    
    except:
        print("❌ Ya existe un hotel con ese nombre.")
    
    conexion.close()
