"""
generar_recibo.py  –  Turismar Agencia de Viajes  (v2 – Rediseño 2026)
=======================================================================
Coloca este archivo en la MISMA carpeta que app_streamlit.py junto con:
  - logo_turismar_clean.png   (logo principal)
  - sello_abono.jpg           (sello opcional – ya no se usa nina)

Uso:
    from generar_recibo import generar_recibo_pdf
    pdf_bytes = generar_recibo_pdf(
        numero=1, fecha="21-febrero-2026",
        recibide="María González", cantidad=2500.0,
        concepto="Viaje Riviera Maya", forma_pago="Efectivo",
        agente="Laura", logo_path="logo_turismar_clean.png",
        total_viaje=15000.0, pagado_acumulado=2500.0, nuevo_saldo=12500.0,
    )
"""

import io
import os
import math
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ── Paleta de colores Turismar ─────────────────────────────────────────────
PINK        = colors.HexColor("#E91E8C")
PINK_MID    = colors.HexColor("#C2185B")
PINK_LIGHT  = colors.HexColor("#FDE8F3")
PINK_XLIGHT = colors.HexColor("#FFF5FB")
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


# ── Helpers ────────────────────────────────────────────────────────────────
def _cantidad_en_letras(monto: float) -> str:
    """Convierte un número a letras en español (MXN) sin dependencias externas."""
    try:
        UNIDADES = ["","UNO","DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE",
                    "DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISÉIS","DIECISIETE",
                    "DIECIOCHO","DIECINUEVE","VEINTE"]
        DECENAS  = ["","","VEINTI","TREINTA","CUARENTA","CINCUENTA","SESENTA","SETENTA","OCHENTA","NOVENTA"]
        CENTENAS = ["","CIENTO","DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS",
                    "SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]

        def _cientos(n):
            if n == 0: return ""
            if n == 100: return "CIEN"
            c = CENTENAS[n // 100]
            resto = n % 100
            if resto == 0: return c
            if resto <= 20: return (c + " " + UNIDADES[resto]).strip()
            d = DECENAS[resto // 10]
            u = UNIDADES[resto % 10]
            if d == "VEINTI": return (c + " " + d + u.lower()).strip()
            return (c + " " + d + (" Y " + u if u else "")).strip()

        def _miles(n):
            if n == 0: return "CERO"
            miles = n // 1000
            resto = n % 1000
            partes = []
            if miles == 1: partes.append("MIL")
            elif miles > 1: partes.append(_cientos(miles) + " MIL")
            if resto: partes.append(_cientos(resto))
            return " ".join(partes)

        entero   = int(monto)
        centavos = round((monto - entero) * 100)

        if entero >= 1_000_000:
            millones = entero // 1_000_000
            resto    = entero % 1_000_000
            base     = ("UN MILLÓN" if millones == 1 else _miles(millones) + " MILLONES")
            base     = (base + " " + _miles(resto)).strip() if resto else base
        else:
            base = _miles(entero)

        return f"{base} PESOS {centavos:02d}/100 M.N."
    except Exception:
        return f"{monto:,.2f} PESOS M.N."


def _fmt_monto(v):
    """Formatea un monto como $ x,xxx.xx o — si es None."""
    if v is None:
        return "—"
    try:
        return f"$ {float(v):,.2f}"
    except Exception:
        return str(v)


def _draw_rounded_rect_fill(c, x, y, w, h, r, fill_color, stroke_color=None, line_width=0.5):
    """Dibuja un rectángulo redondeado con relleno y opcionalmente borde."""
    c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(line_width)
        c.roundRect(x, y, w, h, r, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, r, fill=1, stroke=0)


def _draw_separator_line(c, x1, x2, y, color=None, dashed=False):
    """Línea separadora decorativa."""
    if color:
        c.setStrokeColor(color)
    c.setLineWidth(0.5)
    if dashed:
        c.setDash(3, 3)
    c.line(x1, y, x2, y)
    c.setDash()


# ── Función principal ──────────────────────────────────────────────────────
def generar_recibo_pdf(
    numero,
    fecha,
    recibide,
    cantidad,
    concepto,
    forma_pago,
    agente,
    logo_path="logo_turismar_clean.png",
    nina_path=None,         # ya no se usa, se mantiene por compatibilidad
    sello_path=None,        # ya no se usa como imagen, se dibuja nativamente
    total_viaje=None,
    pagado_acumulado=None,
    nuevo_saldo=None,
) -> bytes:
    """
    Genera el recibo de abono en PDF y devuelve los bytes.

    Parámetros
    ----------
    numero            : int  – número de recibo (4 dígitos con ceros)
    fecha             : str  – fecha formateada, p.ej. "21-febrero-2026"
    recibide          : str  – nombre del responsable del viaje
    cantidad          : float – monto del abono
    concepto          : str  – descripción del viaje / concepto
    forma_pago        : str  – "Efectivo", "Transferencia", etc.
    agente            : str  – nombre del agente / vendedora
    logo_path         : str  – ruta al logo PNG
    nina_path         : ignorado (compatibilidad)
    sello_path        : ignorado (compatibilidad)
    total_viaje       : float|None
    pagado_acumulado  : float|None
    nuevo_saldo       : float|None
    """

    buf = io.BytesIO()
    W, H = A4          # 595.28 x 841.89 pts
    cv   = canvas.Canvas(buf, pagesize=A4)

    num_str    = str(int(numero)).zfill(4)
    cantidad_f = float(cantidad)
    en_letras  = _cantidad_en_letras(cantidad_f)
    pago_acum  = pagado_acumulado if pagado_acumulado is not None else cantidad_f

    MARGIN = 14 * mm
    BODY_W = W - 2 * MARGIN

    # ══════════════════════════════════════════════════════════════════════
    # 1. FONDO GENERAL
    # ══════════════════════════════════════════════════════════════════════
    cv.setFillColor(GRAY_XLIGHT)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # ══════════════════════════════════════════════════════════════════════
    # 2. HEADER  –  Layout en 3 zonas:
    #    [ORILLA ROSA] [LOGO | INFO AGENCIA (fondo blanco)] [FOLIO AZUL]
    # ══════════════════════════════════════════════════════════════════════
    HEADER_H   = 76 * mm

    # Zonas horizontales (en puntos)
    ORILLA_W   = 10 * mm          # franja rosa izquierda
    FOLIO_W    = 58 * mm          # zona azul derecha con número
    WHITE_W    = W - ORILLA_W - FOLIO_W   # zona central blanca

    # ── 2a. Fondo blanco completo del header ──────────────────────────
    cv.setFillColor(WHITE)
    cv.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)

    # ── 2b. Orilla rosa izquierda ─────────────────────────────────────
    cv.setFillColor(PINK)
    cv.rect(0, H - HEADER_H, ORILLA_W, HEADER_H, fill=1, stroke=0)

    # Detalle: pequeños puntos decorativos en la orilla rosa
    cv.setFillColor(colors.HexColor("#F06DB0"))
    for dot_y in [H - 15*mm, H - 30*mm, H - 45*mm, H - 60*mm]:
        cv.circle(ORILLA_W / 2, dot_y, 1.5, fill=1, stroke=0)

    # ── 2c. Zona azul del folio (derecha) ─────────────────────────────
    FOLIO_X = W - FOLIO_W
    cv.setFillColor(BLUE_DARK)
    cv.rect(FOLIO_X, H - HEADER_H, FOLIO_W, HEADER_H, fill=1, stroke=0)

    # Línea de acento azul claro en el borde interior del folio
    cv.setFillColor(BLUE)
    cv.rect(FOLIO_X, H - HEADER_H, 2.5, HEADER_H, fill=1, stroke=0)

    # Burbujas decorativas en zona azul
    cv.saveState()
    cv.setFillColor(WHITE)
    cv.setFillAlpha(0.07)
    cv.circle(W - 12*mm, H - 10*mm, 30*mm, fill=1, stroke=0)
    cv.circle(W - 20*mm, H - 65*mm, 20*mm, fill=1, stroke=0)
    cv.setFillAlpha(1)
    cv.restoreState()

    # ── 2d. Franja amarilla en la parte inferior del header ───────────
    cv.setFillColor(YELLOW)
    cv.rect(0, H - HEADER_H, W, 3.5, fill=1, stroke=0)

    # ── 2e. Línea divisora vertical entre zona blanca y folio ─────────
    cv.setStrokeColor(GRAY_LIGHT)
    cv.setLineWidth(0.5)
    cv.line(FOLIO_X, H - HEADER_H + 6*mm, FOLIO_X, H - 6*mm)

    # ── 2f. Logo (zona blanca, lado izquierdo) ────────────────────────
    LOGO_SIZE  = 48 * mm
    LOGO_X     = ORILLA_W + 4 * mm
    LOGO_Y     = H - HEADER_H + (HEADER_H - LOGO_SIZE) / 2 + 1.5*mm

    if os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            cv.drawImage(img, LOGO_X, LOGO_Y,
                         width=LOGO_SIZE, height=LOGO_SIZE,
                         preserveAspectRatio=True, mask="auto")
        except Exception:
            pass

    # ── 2g. Información de la agencia (zona blanca, lado derecho del logo) ─
    INFO_X     = LOGO_X + LOGO_SIZE + 5 * mm
    INFO_MAX_X = FOLIO_X - 4 * mm
    INFO_CX    = (INFO_X + INFO_MAX_X) / 2   # centro del bloque de texto

    # Nombre de la agencia – "TURISMAR" en rosa y "Agencia de Viajes" en azul
    cv.setFillColor(PINK)
    cv.setFont("Helvetica-Bold", 22)
    cv.drawCentredString(INFO_CX, H - 14 * mm, "TURISMAR")

    cv.setFillColor(BLUE_DARK)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(INFO_CX, H - 22 * mm, "AGENCIA DE VIAJES")

    # Línea decorativa con los dos colores
    SEP_Y  = H - 26.5 * mm
    SEP_MX = (INFO_X + INFO_MAX_X) / 2
    SEP_HW = (INFO_MAX_X - INFO_X) / 2 - 2*mm
    cv.setFillColor(PINK)
    cv.rect(SEP_MX - SEP_HW, SEP_Y, SEP_HW, 2, fill=1, stroke=0)
    cv.setFillColor(BLUE)
    cv.rect(SEP_MX,           SEP_Y, SEP_HW, 2, fill=1, stroke=0)

    # Eslogan en gris oscuro
    cv.setFillColor(GRAY_DARK)
    cv.setFont("Helvetica-BoldOblique", 9)
    cv.drawCentredString(INFO_CX, H - 32 * mm, '"Viajar es un placer"')

    # Datos de contacto – negrita, color oscuro, legible
    cv.setFillColor(DARK)
    cv.setFont("Helvetica-Bold", 8.5)
    cv.drawCentredString(INFO_CX, H - 40 * mm,
                         "Calle 21 #188-D entre 22 y 24, Col. Centro, Ticul, Yucatan")
    cv.drawCentredString(INFO_CX, H - 48 * mm,
                         "Tel: (997) 107 33 47   |   turismar.viajes@hotmail.com")

    # ── Redes sociales (texto plano, dos líneas) ───────────────────────
    cv.setFillColor(DARK)
    cv.setFont("Helvetica-Bold", 8.5)
    cv.drawCentredString(INFO_CX, H - 57 * mm,
                         "Instagram: @agencia_turismar")
    cv.drawCentredString(INFO_CX, H - 65 * mm,
                         "Facebook: Turismar Agencia de Viajes")

    # ── 2h. Folio / Número de recibo (zona azul derecha) ──────────────
    NUM_CX = FOLIO_X + FOLIO_W / 2
    NUM_CY = H - HEADER_H / 2

    cv.setFillColor(colors.HexColor("#CCE8F4"))
    cv.setFont("Helvetica-Bold", 6.5)
    cv.drawCentredString(NUM_CX, H - 12 * mm, "RECIBO DE ABONO")

    # Línea decorativa bajo el título del folio
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(0.8)
    cv.line(FOLIO_X + 6*mm, H - 14.5*mm, W - 6*mm, H - 14.5*mm)

    # Número en grande
    cv.setFillColor(YELLOW)
    cv.setFont("Helvetica-Bold", 28)
    cv.drawCentredString(NUM_CX, NUM_CY + 2 * mm, f"# {num_str}")

    # Fecha
    cv.setFillColor(colors.HexColor("#CCE8F4"))
    cv.setFont("Helvetica", 6.5)
    cv.drawCentredString(NUM_CX, NUM_CY - 8 * mm, fecha)

    # Pequeño ícono de avión decorativo
    cv.setFillColor(colors.HexColor("#5BC8E8"))
    cv.setFont("Helvetica-Bold", 16)
    cv.drawCentredString(NUM_CX, NUM_CY - 20 * mm, "✈")

    # ══════════════════════════════════════════════════════════════════════
    # 3. TARJETA PRINCIPAL (cuerpo blanco con sombra)
    # ══════════════════════════════════════════════════════════════════════
    CARD_TOP    = H - HEADER_H - 4 * mm
    CARD_BOTTOM = 55 * mm
    CARD_H      = CARD_TOP - CARD_BOTTOM
    CARD_X      = MARGIN - 2 * mm
    CARD_W      = W - 2 * (MARGIN - 2 * mm)

    # Sombra
    cv.setFillColor(colors.HexColor("#C8D8E8"))
    cv.roundRect(CARD_X + 1.5, CARD_BOTTOM - 1.5, CARD_W, CARD_H, 6, fill=1, stroke=0)

    # Tarjeta blanca
    _draw_rounded_rect_fill(cv, CARD_X, CARD_BOTTOM, CARD_W, CARD_H, 6, WHITE,
                            stroke_color=GRAY_LIGHT, line_width=0.5)

    # ── Sección "DATOS DEL ABONO" ──────────────────────────────────────
    INNER_X = CARD_X + 6 * mm
    INNER_W = CARD_W - 12 * mm
    y = CARD_TOP - 8 * mm

    # Título de sección
    _draw_rounded_rect_fill(cv, INNER_X, y - 6 * mm, INNER_W, 7.5 * mm, 3, PINK_LIGHT)
    cv.setFillColor(PINK_MID)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(INNER_X + 3 * mm, y - 1.5 * mm, "  DATOS DEL ABONO")
    y -= 10 * mm

    # ── Función interna para campos ────────────────────────────────────
    def draw_field(label, value, y_pos, highlight=False, value_color=None, multiline=False):
        ROW_H   = 8.5 * mm
        LABEL_W = 56 * mm
        GAP     = 2 * mm

        # Fondo etiqueta
        lbl_color = PINK_LIGHT if not highlight else colors.HexColor("#E8F5E9")
        _draw_rounded_rect_fill(cv, INNER_X, y_pos - ROW_H, LABEL_W, ROW_H, 2, lbl_color)

        # Texto etiqueta
        lbl_text_color = PINK_MID if not highlight else GREEN_DARK
        cv.setFillColor(lbl_text_color)
        cv.setFont("Helvetica-Bold", 6.8)
        cv.drawString(INNER_X + 2.5 * mm, y_pos - ROW_H / 2 - 1.5, label)

        # Fondo valor
        val_x = INNER_X + LABEL_W + GAP
        val_w = INNER_W - LABEL_W - GAP
        _draw_rounded_rect_fill(cv, val_x, y_pos - ROW_H, val_w, ROW_H, 2,
                                GRAY_XLIGHT, stroke_color=GRAY_LIGHT, line_width=0.4)

        # Texto valor
        draw_color = value_color if value_color else DARK
        cv.setFillColor(draw_color)

        if multiline:
            # Para texto largo: máximo 2 líneas
            text  = str(value)
            words = text.split()
            lines, line = [], ""
            max_chars = 68
            for w in words:
                if len(line) + len(w) + 1 <= max_chars:
                    line = (line + " " + w).strip()
                else:
                    lines.append(line); line = w
            if line:
                lines.append(line)
            cv.setFont("Helvetica", 7.5)
            for i, ln in enumerate(lines[:2]):
                cv.drawString(val_x + 2.5 * mm, y_pos - 3.5 * mm - i * 5, ln)
        else:
            cv.setFont("Helvetica-Bold" if highlight else "Helvetica", 8.2)
            cv.drawString(val_x + 2.5 * mm, y_pos - ROW_H / 2 - 1.5, str(value))

        return y_pos - ROW_H - 1.8 * mm

    # Campos
    y = draw_field("FECHA",                   fecha,        y)
    y = draw_field("RECIBÍ DE",               recibide,     y)
    y = draw_field("CANTIDAD",
                   f"$ {cantidad_f:,.2f}",    y,
                   highlight=True,
                   value_color=GREEN_DARK)
    y = draw_field("SON (EN LETRAS)",         en_letras,    y, multiline=True)
    y = draw_field("CONCEPTO",                concepto,     y, multiline=True)
    y = draw_field("FORMA DE PAGO",           forma_pago,   y)
    y = draw_field("AGENTE / VENDEDOR(A)",    agente,       y)

    y -= 5 * mm

    # ══════════════════════════════════════════════════════════════════════
    # 4. DESGLOSE DE PAGOS  (3 tarjetas horizontales)
    # ══════════════════════════════════════════════════════════════════════
    TILES_H  = 30 * mm
    GAP_TILE = 3 * mm
    TILE_W   = (INNER_W - GAP_TILE * 2) / 3

    tile_configs = [
        {
            "label": "TOTAL DEL VIAJE",
            "value": _fmt_monto(total_viaje),
            "bg":    BLUE_LIGHT,
            "accent": BLUE_DARK,
            "val_color": BLUE_DARK,
            "icon":  "TOTAL",
        },
        {
            "label": "ABONADO HOY",
            "value": _fmt_monto(pago_acum),
            "bg":    colors.HexColor("#E8FFF3"),
            "accent": GREEN_DARK,
            "val_color": GREEN_DARK,
            "icon":  "ABONO",
        },
        {
            "label": "SALDO RESTANTE",
            "value": _fmt_monto(nuevo_saldo),
            "bg":    PINK_XLIGHT,
            "accent": PINK_MID,
            "val_color": PINK,
            "icon":  "SALDO",
        },
    ]

    for i, tile in enumerate(tile_configs):
        tx = INNER_X + i * (TILE_W + GAP_TILE)
        ty = y

        # Sombra
        cv.setFillColor(GRAY_LIGHT)
        cv.roundRect(tx + 1, ty - TILES_H - 1, TILE_W, TILES_H, 5, fill=1, stroke=0)

        # Fondo tarjeta
        _draw_rounded_rect_fill(cv, tx, ty - TILES_H, TILE_W, TILES_H, 5,
                                tile["bg"], stroke_color=tile["accent"], line_width=0.7)

        # Barra de acento superior
        path_bar = cv.beginPath()
        path_bar.moveTo(tx + 5,          ty)
        path_bar.lineTo(tx + TILE_W - 5, ty)
        path_bar.arcTo(tx + TILE_W - 10, ty - 10, tx + TILE_W, ty, 0, 90)
        path_bar.lineTo(tx + 5,          ty - 5)
        cv.setFillColor(tile["accent"])
        cv.roundRect(tx, ty - 4 * mm, TILE_W, 4 * mm, 4, fill=1, stroke=0)

        # Etiqueta
        cv.setFillColor(WHITE)
        cv.setFont("Helvetica-Bold", 6)
        cv.drawCentredString(tx + TILE_W / 2, ty - 2.5 * mm, tile["label"])

        # Valor
        cv.setFillColor(tile["val_color"])
        val_text = tile["value"]
        font_size = 14 if len(val_text) <= 12 else 11
        cv.setFont("Helvetica-Bold", font_size)
        cv.drawCentredString(tx + TILE_W / 2, ty - 16 * mm, val_text)

        # Ícono textual pequeño
        cv.setFillColor(tile["accent"])
        cv.setFont("Helvetica", 6.5)
        cv.setFillAlpha(0.4)
        cv.drawCentredString(tx + TILE_W / 2, ty - 24 * mm, tile["icon"])
        cv.setFillAlpha(1)

    y -= TILES_H + 6 * mm

    # ══════════════════════════════════════════════════════════════════════
    # 5. CÓDIGO DE VERIFICACIÓN ÚNICO
    # ══════════════════════════════════════════════════════════════════════
    import hashlib

    # Generar código: TUR-AÑO-NUMERO-HASH4
    año_str  = str(fecha).split("-")[-1] if "-" in str(fecha) else "2026"
    raw      = f"{numero}-{fecha}-{cantidad_f}-{recibide}"
    hash4    = hashlib.md5(raw.encode()).hexdigest()[:4].upper()
    cod_ver  = f"TUR-{año_str}-{str(int(numero)).zfill(4)}-{hash4}"

    VERIF_Y  = CARD_BOTTOM + 5 * mm
    VERIF_H  = 18 * mm
    VERIF_X  = INNER_X
    VERIF_W  = INNER_W

    # Fondo de la banda de verificación
    _draw_rounded_rect_fill(cv, VERIF_X, VERIF_Y, VERIF_W, VERIF_H, 4,
                            colors.HexColor("#F0FFF8"),
                            stroke_color=GREEN_DARK, line_width=0.8)

    # Acento verde izquierdo
    cv.setFillColor(GREEN_DARK)
    cv.roundRect(VERIF_X, VERIF_Y, 3.5, VERIF_H, 4, fill=1, stroke=0)

    # Checkmark  ✓  dibujado
    CHECK_CX = VERIF_X + 10 * mm
    CHECK_CY = VERIF_Y + VERIF_H / 2
    cv.setFillColor(GREEN_DARK)
    cv.circle(CHECK_CX, CHECK_CY, 5.5, fill=1, stroke=0)
    cv.setStrokeColor(WHITE)
    cv.setLineWidth(1.4)
    cv.setLineCap(1)
    cv.line(CHECK_CX - 2.5, CHECK_CY,     CHECK_CX - 0.5, CHECK_CY - 2.2)
    cv.line(CHECK_CX - 0.5, CHECK_CY - 2.2, CHECK_CX + 3,  CHECK_CY + 2.5)
    cv.setLineCap(0)

    # Etiqueta
    cv.setFillColor(GREEN_DARK)
    cv.setFont("Helvetica-Bold", 7)
    cv.drawString(VERIF_X + 18 * mm, VERIF_Y + VERIF_H - 5.5 * mm,
                  "ABONO REGISTRADO DIGITALMENTE")

    # Código en grande y monoespaciado (simulado con Courier)
    cv.setFillColor(DARK)
    cv.setFont("Courier-Bold", 12)
    cv.drawString(VERIF_X + 18 * mm, VERIF_Y + 4 * mm, cod_ver)

    # Leyenda derecha
    cv.setFillColor(GRAY_MID)
    cv.setFont("Helvetica", 6)
    cv.drawRightString(VERIF_X + VERIF_W - 3 * mm,
                       VERIF_Y + VERIF_H - 5.5 * mm,
                       "Codigo de verificacion Turismar")
    cv.setFont("Helvetica-Oblique", 5.8)
    cv.drawRightString(VERIF_X + VERIF_W - 3 * mm,
                       VERIF_Y + 4 * mm,
                       "Conserva este recibo como comprobante de pago")

    # ══════════════════════════════════════════════════════════════════════
    # 6. FOOTER
    # ══════════════════════════════════════════════════════════════════════
    FOOTER_H = 22 * mm

    # Fondo degradado simulado (dos rectángulos)
    cv.setFillColor(PINK_MID)
    cv.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
    cv.setFillColor(BLUE_DARK)
    path_f = cv.beginPath()
    path_f.moveTo(W * 0.5, 0)
    path_f.lineTo(W,       0)
    path_f.lineTo(W,       FOOTER_H)
    path_f.lineTo(W * 0.62, FOOTER_H)
    path_f.close()
    cv.drawPath(path_f, fill=1, stroke=0)

    # Línea amarilla separadora
    cv.setFillColor(YELLOW)
    cv.rect(0, FOOTER_H - 2, W, 2, fill=1, stroke=0)

    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 7.5)
    cv.drawCentredString(W / 2, FOOTER_H - 7 * mm,
                         "Este recibo es comprobante de abono. No válido como factura fiscal.")

    cv.setFont("Helvetica", 6.5)
    cv.setFillColor(colors.HexColor("#FFD6EE"))
    cv.drawCentredString(W / 2, FOOTER_H - 12 * mm,
                         "turismar.viajes@hotmail.com   |   (997) 107 33 47   |   Ticul, Yucatán")

    cv.setFillColor(colors.HexColor("#CCE8F4"))
    cv.setFont("Helvetica-Oblique", 6.2)
    cv.drawCentredString(W / 2, FOOTER_H - 17 * mm,
                         "¡Gracias por viajar con Turismar!  ✈  @agencia_turismar")

    # ══════════════════════════════════════════════════════════════════════
    cv.save()
    buf.seek(0)
    return buf.read()
