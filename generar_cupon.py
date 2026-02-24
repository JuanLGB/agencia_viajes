"""
generar_cupon.py  –  Turismar Agencia de Viajes
================================================
Genera el cupón de acceso al hotel en PDF, fiel al diseño Turismar.

Uso:
    from generar_cupon import generar_cupon_pdf
    pdf_bytes = generar_cupon_pdf(
        titular          = "CINDY VARGUEZ",
        clave_confirm    = "69-7543060",
        hotel_nombre     = "Barceló Maya Grand",
        hotel_direccion  = "Carr. Cancún–Tulum Km. 266,3, 77734 Xpu Ha, Q.R.",
        hotel_telefono   = "984 875 1500",
        hotel_estrellas  = 4,
        tipo_habitacion  = "Superior Room",
        plan_alimento    = "Todo incluido",
        fecha_entrada    = "2025-08-08",   # formato YYYY-MM-DD
        fecha_salida     = "2025-08-10",
        adultos          = 2,
        menores          = 2,
        edades_menores   = "5 y 4 años",
        requerimientos   = "Aniversario de bodas (10 años de matrimonio)",
        logo_path        = "logo_turismar_clean.png",
    )
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ── Paleta Turismar ────────────────────────────────────────────────────────
PINK        = colors.HexColor("#E91E8C")
PINK_MID    = colors.HexColor("#C2185B")
PINK_LIGHT  = colors.HexColor("#FDE8F3")
BLUE        = colors.HexColor("#29ABE2")
BLUE_DARK   = colors.HexColor("#0077AA")
BLUE_LIGHT  = colors.HexColor("#E5F5FC")
YELLOW      = colors.HexColor("#FDD835")
YELLOW_DARK = colors.HexColor("#F9A825")
DARK        = colors.HexColor("#1A1A2E")
GRAY_DARK   = colors.HexColor("#4A5568")
GRAY_MID    = colors.HexColor("#718096")
GRAY_LIGHT  = colors.HexColor("#E2E8F0")
GRAY_XLIGHT = colors.HexColor("#F7FAFC")
WHITE       = colors.white
GREEN       = colors.HexColor("#2ECC71")
GREEN_DARK  = colors.HexColor("#1A9B56")

# ── Días y meses en español ────────────────────────────────────────────────
DIAS_ES   = ["LUN","MAR","MIÉ","JUE","VIE","SÁB","DOM"]
MESES_ES  = ["","ENE","FEB","MAR","ABR","MAY","JUN",
             "JUL","AGO","SEP","OCT","NOV","DIC"]
MESES_FULL = ["","enero","febrero","marzo","abril","mayo","junio",
              "julio","agosto","septiembre","octubre","noviembre","diciembre"]


def _parse_fecha(fecha_str: str):
    """Parsea fecha en YYYY-MM-DD o DD-MM-YYYY. Devuelve objeto date o None."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(fecha_str), fmt).date()
        except ValueError:
            pass
    return None


def _fmt_fecha_cupon(fecha_str: str):
    """
    Devuelve (dia_num_str, dia_semana, mes_abrev, año_str)
    Ej: ("08", "VIE", "AGO", "2025")
    """
    d = _parse_fecha(fecha_str)
    if not d:
        return "??", "???", "???", "????"
    return (
        f"{d.day:02d}",
        DIAS_ES[d.weekday()],
        MESES_ES[d.month],
        str(d.year),
    )


def _draw_star(cv, cx, cy, r_outer, r_inner, n=5, fill_color=None):
    """Dibuja una estrella de n puntas centrada en (cx, cy)."""
    import math
    if fill_color:
        cv.setFillColor(fill_color)
    path = cv.beginPath()
    for i in range(n * 2):
        angle = math.pi / 2 + i * math.pi / n
        r = r_outer if i % 2 == 0 else r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.close()
    cv.drawPath(path, fill=1, stroke=0)


def generar_cupon_pdf(
    titular: str,
    clave_confirm: str,
    hotel_nombre: str,
    hotel_direccion: str = "",
    hotel_telefono: str = "",
    hotel_estrellas: int = 4,
    tipo_habitacion: str = "Superior Room",
    plan_alimento: str = "Todo incluido",
    fecha_entrada: str = "",
    fecha_salida: str = "",
    adultos: int = 2,
    menores: int = 0,
    edades_menores: str = "",
    requerimientos: str = "",
    logo_path: str = "logo_turismar_clean.png",
) -> bytes:
    """
    Genera el cupón de acceso al hotel en PDF y devuelve los bytes.
    """
    buf = io.BytesIO()
    W, H = A4
    cv  = canvas.Canvas(buf, pagesize=A4)

    MARGIN  = 14 * mm
    BODY_W  = W - 2 * MARGIN

    # ══════════════════════════════════════════════════════════════════════
    # 0. FONDO
    # ══════════════════════════════════════════════════════════════════════
    cv.setFillColor(WHITE)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # ══════════════════════════════════════════════════════════════════════
    # 1. HEADER TURISMAR  (mismo estilo que recibo)
    # ══════════════════════════════════════════════════════════════════════
    HEADER_H  = 70 * mm
    ORILLA_W  = 10 * mm
    FOLIO_W   = 0          # sin zona de folio en el cupón

    # Fondo blanco del header
    cv.setFillColor(WHITE)
    cv.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

    # Orilla rosa izquierda
    cv.setFillColor(PINK)
    cv.rect(0, H - HEADER_H, ORILLA_W, HEADER_H, fill=1, stroke=0)

    # Orilla azul derecha
    cv.setFillColor(BLUE_DARK)
    cv.rect(W - ORILLA_W, H - HEADER_H, ORILLA_W, HEADER_H, fill=1, stroke=0)

    # Línea amarilla inferior del header
    cv.setFillColor(YELLOW)
    cv.rect(0, H - HEADER_H, W, 3.5, fill=1, stroke=0)

    # Logo
    LOGO_SIZE = 44 * mm
    LOGO_X    = ORILLA_W + 4 * mm
    LOGO_Y    = H - HEADER_H + (HEADER_H - LOGO_SIZE) / 2 + 1 * mm
    if os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            cv.drawImage(img, LOGO_X, LOGO_Y,
                         width=LOGO_SIZE, height=LOGO_SIZE,
                         preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # Textos agencia (centro)
    INFO_CX = (ORILLA_W + LOGO_SIZE + 8 * mm + W - ORILLA_W) / 2

    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 22)
    cv.drawCentredString(INFO_CX, H - 14 * mm, "TURISMAR")

    cv.setFillColor(BLUE_DARK)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(INFO_CX, H - 22 * mm, "AGENCIA DE VIAJES")

    # Separador bicolor
    SEP_HW = 55 * mm
    cv.setFillColor(PINK)
    cv.rect(INFO_CX - SEP_HW, H - 26 * mm, SEP_HW, 2, fill=1, stroke=0)
    cv.setFillColor(BLUE)
    cv.rect(INFO_CX,            H - 26 * mm, SEP_HW, 2, fill=1, stroke=0)

    cv.setFillColor(DARK)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(INFO_CX, H - 33 * mm,
                         "Calle 21 #177-A entre 24 y 22, CP 97860, Ticul, Yucatan, Mexico")

    cv.setFillColor(BLUE_DARK)
    cv.setFont("Helvetica-Bold", 8.5)
    cv.drawCentredString(INFO_CX, H - 41 * mm, "WhatsApp: 997-107-3347")

    cv.setFillColor(DARK)
    cv.setFont("Helvetica-Bold", 7.8)
    cv.drawCentredString(INFO_CX, H - 49 * mm,
                         "Instagram: @agencia_turismar")
    cv.drawCentredString(INFO_CX, H - 57 * mm,
                         "Facebook: Turismar Agencia de Viajes")

    # ══════════════════════════════════════════════════════════════════════
    # 2. SECCIÓN HOTEL  (nombre grande + estrellas + dirección)
    # ══════════════════════════════════════════════════════════════════════
    HOTEL_Y_TOP = H - HEADER_H - 5 * mm
    HOTEL_H     = 30 * mm

    # Fondo sutil
    cv.setFillColor(BLUE_LIGHT)
    cv.roundRect(MARGIN, HOTEL_Y_TOP - HOTEL_H, BODY_W, HOTEL_H, 6, fill=1, stroke=0)
    cv.setFillColor(BLUE_DARK)
    cv.roundRect(MARGIN, HOTEL_Y_TOP - HOTEL_H, 4, HOTEL_H, 3, fill=1, stroke=0)

    # Ícono de edificio (dibujado como rectángulos)
    ICON_X = MARGIN + 8 * mm
    ICON_Y = HOTEL_Y_TOP - HOTEL_H + 5 * mm
    ICON_H = HOTEL_H - 10 * mm
    ICON_W = ICON_H * 0.7
    cv.setFillColor(BLUE_DARK)
    cv.roundRect(ICON_X, ICON_Y, ICON_W, ICON_H, 2, fill=1, stroke=0)
    # Ventanitas
    cv.setFillColor(WHITE)
    for vy in [ICON_Y + ICON_H * 0.65, ICON_Y + ICON_H * 0.38]:
        for vx in [ICON_X + ICON_W * 0.18, ICON_X + ICON_W * 0.52]:
            cv.rect(vx, vy, ICON_W * 0.22, ICON_H * 0.18, fill=1, stroke=0)
    # Puerta
    cv.rect(ICON_X + ICON_W * 0.32, ICON_Y,
            ICON_W * 0.36, ICON_H * 0.28, fill=1, stroke=0)

    # Nombre del hotel
    TEXT_X = ICON_X + ICON_W + 4 * mm
    cv.setFillColor(DARK)
    font_size_hotel = 16 if len(hotel_nombre) <= 25 else 13
    cv.setFont("Helvetica-Bold", font_size_hotel)
    cv.drawString(TEXT_X, HOTEL_Y_TOP - 10 * mm, hotel_nombre)

    # Estrellas
    star_y = HOTEL_Y_TOP - 18 * mm
    star_x = TEXT_X
    for _ in range(min(int(hotel_estrellas), 5)):
        _draw_star(cv, star_x + 3.5, star_y, 3.5, 1.5, fill_color=YELLOW_DARK)
        star_x += 9

    # Dirección y teléfono
    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7)
    dir_text = hotel_direccion
    if hotel_telefono:
        dir_text += f"  •  {hotel_telefono}"
    cv.drawString(TEXT_X, HOTEL_Y_TOP - HOTEL_H + 4 * mm, dir_text)

    # ══════════════════════════════════════════════════════════════════════
    # 3. DATOS PRINCIPALES  (titular + clave)
    # ══════════════════════════════════════════════════════════════════════
    y = HOTEL_Y_TOP - HOTEL_H - 7 * mm

    def draw_dato_principal(label, value, y_pos, icon_type="person",
                             label_color=None, value_color=None, value_size=14):
        """Dibuja una fila titular/clave con ícono."""
        ROW_H = 12 * mm
        lc = label_color or GRAY_DARK
        vc = value_color or DARK

        # Ícono circular
        cv.setFillColor(BLUE_LIGHT)
        cv.circle(MARGIN + 5 * mm, y_pos - ROW_H / 2, 4.5 * mm, fill=1, stroke=0)
        cv.setFillColor(BLUE_DARK)
        cv.setFont("Helvetica-Bold", 7)
        if icon_type == "person":
            # Cabeza
            cv.circle(MARGIN + 5 * mm, y_pos - ROW_H / 2 + 1.8, 2, fill=1, stroke=0)
            # Cuerpo
            cv.setFillColor(BLUE_DARK)
            cv.roundRect(MARGIN + 2.5 * mm, y_pos - ROW_H / 2 - 3.5,
                         5 * mm, 3 * mm, 1.5, fill=1, stroke=0)
        elif icon_type == "check":
            cv.setStrokeColor(BLUE_DARK)
            cv.setLineWidth(1.3)
            cv.setLineCap(1)
            cx0 = MARGIN + 5 * mm
            cy0 = y_pos - ROW_H / 2
            cv.line(cx0 - 2.2, cy0, cx0 - 0.3, cy0 - 2)
            cv.line(cx0 - 0.3, cy0 - 2, cx0 + 2.8, cy0 + 2.5)
            cv.setLineCap(0)

        # Etiqueta
        cv.setFillColor(lc)
        cv.setFont("Helvetica", 7.5)
        cv.drawString(MARGIN + 12 * mm, y_pos - 3.5 * mm, label)

        # Valor
        cv.setFillColor(vc)
        cv.setFont("Helvetica-Bold", value_size)
        cv.drawString(MARGIN + 12 * mm, y_pos - ROW_H + 1.5 * mm, value.upper())

        return y_pos - ROW_H - 2 * mm

    y = draw_dato_principal("Titular:", titular, y,
                             icon_type="person", value_color=DARK, value_size=15)

    y = draw_dato_principal("Clave de confirmacion:", clave_confirm, y,
                             icon_type="check", value_color=BLUE_DARK, value_size=16)

    y -= 3 * mm

    # ══════════════════════════════════════════════════════════════════════
    # 4. GRILLA: Habitación + Plan | Fechas | Adultos + Menores
    # ══════════════════════════════════════════════════════════════════════
    GRID_H  = 52 * mm
    GRID_Y  = y

    # ─ Panel izquierdo: Habitación + Plan + Requerimientos ─────────────
    PANEL_L_W = BODY_W * 0.38
    cv.setFillColor(GRAY_XLIGHT)
    cv.roundRect(MARGIN, GRID_Y - GRID_H, PANEL_L_W, GRID_H, 5, fill=1, stroke=0)
    cv.setFillColor(BLUE_DARK)
    cv.roundRect(MARGIN, GRID_Y - GRID_H, 3.5, GRID_H, 3, fill=1, stroke=0)

    # Habitación — ícono cama dibujado
    bed_x = MARGIN + 7 * mm
    bed_y = GRID_Y - 13 * mm
    cv.setFillColor(BLUE_DARK)
    cv.roundRect(bed_x, bed_y, 8 * mm, 4.5 * mm, 1, fill=1, stroke=0)  # colchón
    cv.roundRect(bed_x - 1 * mm, bed_y - 2.5 * mm,
                 10 * mm, 2.5 * mm, 1, fill=1, stroke=0)  # base
    cv.setFillColor(WHITE)
    cv.roundRect(bed_x + 1 * mm, bed_y + 1 * mm,
                 2.5 * mm, 2 * mm, 0.5, fill=1, stroke=0)  # almohada 1
    cv.roundRect(bed_x + 4.5 * mm, bed_y + 1 * mm,
                 2.5 * mm, 2 * mm, 0.5, fill=1, stroke=0)  # almohada 2

    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7)
    cv.drawString(MARGIN + 7 * mm, GRID_Y - 5 * mm, "Habitacion:")
    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 10)
    cv.drawString(MARGIN + 7 * mm, GRID_Y - 18 * mm, tipo_habitacion)

    # Plan de alimento — ícono tenedor/cuchillo
    plan_y = GRID_Y - 28 * mm
    fork_x = MARGIN + 8 * mm
    cv.setFillColor(BLUE_DARK)
    cv.rect(fork_x,           plan_y, 1.2, 5.5 * mm, fill=1, stroke=0)
    cv.rect(fork_x + 2.5 * mm, plan_y, 1.2, 5.5 * mm, fill=1, stroke=0)
    cv.rect(fork_x + 5 * mm,  plan_y, 1.2, 5.5 * mm, fill=1, stroke=0)
    cv.roundRect(fork_x - 0.3, plan_y + 3.5 * mm,
                 7 * mm, 2 * mm, 1, fill=1, stroke=0)

    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7)
    cv.drawString(MARGIN + 7 * mm, GRID_Y - 22 * mm, "Plan de alimento:")
    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 10)
    cv.drawString(MARGIN + 7 * mm, GRID_Y - 31 * mm, plan_alimento)

    # Requerimientos especiales
    if requerimientos:
        cv.setFillColor(GRAY_DARK)
        cv.setFont("Helvetica-Bold", 7)
        cv.drawString(MARGIN + 7 * mm, GRID_Y - 37 * mm, "Requerimientos especiales:")
        cv.setFillColor(PINK)
        cv.setFont("Helvetica-Bold", 8)
        # Wrap text
        words = requerimientos.upper().split()
        lines, line = [], ""
        for w in words:
            if len(line) + len(w) + 1 <= 28:
                line = (line + " " + w).strip()
            else:
                lines.append(line); line = w
        if line:
            lines.append(line)
        for i, ln in enumerate(lines[:3]):
            cv.drawString(MARGIN + 7 * mm, GRID_Y - 43 * mm - i * 5.5, ln)

    # ─ Panel central: Fechas ────────────────────────────────────────────
    GAP = 3 * mm
    PANEL_C_X = MARGIN + PANEL_L_W + GAP
    PANEL_C_W = BODY_W * 0.38
    cv.setFillColor(GRAY_XLIGHT)
    cv.roundRect(PANEL_C_X, GRID_Y - GRID_H, PANEL_C_W, GRID_H, 5, fill=1, stroke=0)

    d_ent, dow_ent, mes_ent, año_ent = _fmt_fecha_cupon(fecha_entrada)
    d_sal, dow_sal, mes_sal, año_sal = _fmt_fecha_cupon(fecha_salida)

    FECHA_CX_E = PANEL_C_X + PANEL_C_W * 0.27
    FECHA_CX_S = PANEL_C_X + PANEL_C_W * 0.73

    # Etiquetas "Entrada" / "Salida"
    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7.5)
    cv.drawCentredString(FECHA_CX_E, GRID_Y - 4 * mm, "Entrada:")
    cv.drawCentredString(FECHA_CX_S, GRID_Y - 4 * mm, "Salida:")

    # Número grande del día
    cv.setFillColor(BLUE)
    cv.setFont("Helvetica-Bold", 34)
    cv.drawCentredString(FECHA_CX_E, GRID_Y - 20 * mm, d_ent)
    cv.drawCentredString(FECHA_CX_S, GRID_Y - 20 * mm, d_sal)

    # Día semana
    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(FECHA_CX_E, GRID_Y - 26 * mm, dow_ent)
    cv.drawCentredString(FECHA_CX_S, GRID_Y - 26 * mm, dow_sal)

    # Mes
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(FECHA_CX_E, GRID_Y - 32 * mm, mes_ent)
    cv.drawCentredString(FECHA_CX_S, GRID_Y - 32 * mm, mes_sal)

    # Año
    cv.setFillColor(GRAY_MID)
    cv.setFont("Helvetica", 8)
    cv.drawCentredString(FECHA_CX_E, GRID_Y - 38 * mm, año_ent)
    cv.drawCentredString(FECHA_CX_S, GRID_Y - 38 * mm, año_sal)

    # Línea vertical separadora entre entrada/salida
    cv.setStrokeColor(GRAY_LIGHT)
    cv.setLineWidth(0.6)
    cv.line(PANEL_C_X + PANEL_C_W / 2, GRID_Y - 3 * mm,
            PANEL_C_X + PANEL_C_W / 2, GRID_Y - GRID_H + 4 * mm)

    # ─ Panel derecho: Adultos + Menores ─────────────────────────────────
    PANEL_R_X = PANEL_C_X + PANEL_C_W + GAP
    PANEL_R_W = BODY_W - PANEL_L_W - PANEL_C_W - GAP * 2
    cv.setFillColor(GRAY_XLIGHT)
    cv.roundRect(PANEL_R_X, GRID_Y - GRID_H, PANEL_R_W, GRID_H, 5, fill=1, stroke=0)

    R_CX = PANEL_R_X + PANEL_R_W / 2

    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7.5)
    cv.drawCentredString(R_CX, GRID_Y - 4 * mm, "Adultos:")

    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 36)
    cv.drawCentredString(R_CX, GRID_Y - 22 * mm, str(adultos))

    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica", 7.5)
    cv.drawCentredString(R_CX, GRID_Y - 28 * mm, "Menores:")

    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 28)
    cv.drawCentredString(R_CX, GRID_Y - 40 * mm, str(menores))

    if edades_menores and menores > 0:
        cv.setFillColor(GRAY_MID)
        cv.setFont("Helvetica", 6.5)
        cv.drawCentredString(R_CX, GRID_Y - GRID_H + 4 * mm, edades_menores)

    y = GRID_Y - GRID_H - 7 * mm

    # ══════════════════════════════════════════════════════════════════════
    # 5. TÉRMINOS Y CONDICIONES
    # ══════════════════════════════════════════════════════════════════════
    TERMS_H  = 58 * mm
    TERMS_Y  = y

    cv.setFillColor(GRAY_XLIGHT)
    cv.roundRect(MARGIN, TERMS_Y - TERMS_H, BODY_W, TERMS_H, 5, fill=1, stroke=0)

    cv.setFillColor(DARK)
    cv.setFont("Helvetica-Bold", 8.5)
    cv.drawCentredString(W / 2, TERMS_Y - 5 * mm, "Terminos y condiciones")

    TERMS_TEXT = (
        "EL CLIENTE declara que tiene la capacidad juridica para contratar y que tiene el interes en adquirir "
        "el paquete que se especifica en el anverso del presente instrumento, en los terminos y condiciones "
        "que en el mismo se estimula. "
        "CANCELACIONES: En caso de cancelaciones, imputablemente al CLIENTE, este pagara el 25% del costo del "
        "servicio turistico si hace la cancelacion de 20 al 16 dia antes de la salida, el 50% del costo del "
        "servicio turistico si hace cancelacion de 15 a 10 dias antes de la fecha de Salida y con el 75% del "
        "costo del referido servicio si hace la cancelacion con 9 o menos de la fecha de salida. "
        "La AGENCIA declara que actua como comisionista de los propietarios o contratistas, que proporcionan "
        "los medios de transportacion, alojamiento, alimentacion y demas servicios, por lo que el CLIENTE esta "
        "de acuerdo en que ni la AGENCIA, ni sus representantes seran responsables de los servicios, de la "
        "perdida, lesion, dano a personas y propiedades que pudieran presentarse por parte del propietario o "
        "contratista correspondiente no imputables a la AGENCIA. "
        "Leido el presente contrato de conformidad, las partes se sujetan para su presentacion y cumplimiento "
        "en primera instancia a la jurisdiccion y comparecencia de la procuraduria Federal del Consumidor y en "
        "segunda instancia a los tribunales de la Ciudad de Merida, Yucatan."
    )

    # Dividir el texto en líneas
    cv.setFillColor(DARK)
    cv.setFont("Helvetica", 6.5)
    words   = TERMS_TEXT.split()
    lines   = []
    line    = ""
    MAX_W   = BODY_W - 10 * mm
    for w in words:
        test = (line + " " + w).strip()
        if cv.stringWidth(test, "Helvetica", 6.5) <= MAX_W:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    text_start_y = TERMS_Y - 10 * mm
    line_h       = 4.2
    for i, ln in enumerate(lines):
        ty = text_start_y - i * line_h
        if ty < TERMS_Y - TERMS_H + 3 * mm:
            break
        cv.drawString(MARGIN + 5 * mm, ty, ln)

    y = TERMS_Y - TERMS_H - 5 * mm

    # ══════════════════════════════════════════════════════════════════════
    # 6. FOOTER  "¡¡TENGA UN EXCELENTE VIAJE!!"
    # ══════════════════════════════════════════════════════════════════════
    FOOTER_H = 20 * mm

    # Fondo bicolor
    cv.setFillColor(PINK_MID)
    cv.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
    path_f = cv.beginPath()
    path_f.moveTo(W * 0.52, 0)
    path_f.lineTo(W,        0)
    path_f.lineTo(W,        FOOTER_H)
    path_f.lineTo(W * 0.62, FOOTER_H)
    path_f.close()
    cv.setFillColor(BLUE_DARK)
    cv.drawPath(path_f, fill=1, stroke=0)

    # Línea amarilla separadora
    cv.setFillColor(YELLOW)
    cv.rect(0, FOOTER_H - 2.5, W, 2.5, fill=1, stroke=0)

    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 16)
    cv.drawCentredString(W / 2, FOOTER_H / 2 - 3, "¡¡TENGA UN EXCELENTE VIAJE!!")

    # ══════════════════════════════════════════════════════════════════════
    cv.save()
    buf.seek(0)
    return buf.read()
