import csv
from datetime import datetime
from app import app          # importa la app Flask ya creada
from extensiones import db
from models import Evento


# =====================================================
# HELPERS
# =====================================================

def parse_float(valor):
    """
    Convierte:
    $5,000.00 -> 5000.0
    5000 -> 5000.0
    "" -> None
    """
    if not valor:
        return None
    try:
        valor = valor.replace("$", "").replace(",", "").strip()
        return float(valor)
    except:
        return None


def parse_fecha(valor):
    """
    Convierte:
    17/01/2026 -> date
    """
    if not valor or not valor.strip():
        return None
    try:
        return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
    except:
        return None


def parse_fecha_hora(valor):
    """
    Convierte:
    2025-12-30 00:40:42 -> datetime
    """
    if not valor or not valor.strip():
        return None
    try:
        return datetime.strptime(valor.strip(), "%Y-%m-%d %H:%M:%S")
    except:
        return None


# =====================================================
# CARGA DE EVENTOS
# =====================================================

with app.app_context():
    with open("eventos_iniciales.csv", newline="", encoding="utf-8") as archivo:
        reader = csv.DictReader(archivo)

        cargados = 0
        ignorados = 0

        for i, row in enumerate(reader, start=1):

            fecha_evento = parse_fecha(row.get("fecha_evento"))

            # ❌ fecha_evento es obligatoria
            if not fecha_evento:
                print(f"⚠️ Fila {i} ignorada (fecha_evento inválida): {row.get('fecha_evento')}")
                ignorados += 1
                continue

            evento = Evento(
                tipo_evento=row.get("tipo_evento"),
                tipo_fiesta=row.get("tipo_fiesta"),
                nombre_cliente=row.get("nombre_cliente"),
                whatsapp=row.get("whatsapp"),

                fecha_evento=fecha_evento,
                hora_inicio=row.get("hora_inicio"),
                hora_termino=row.get("hora_termino"),
                cantidad_horas=parse_float(row.get("cantidad_horas")),

                servicios_interes=row.get("servicios_interes"),
                municipio=row.get("municipio"),
                nombre_salon=row.get("nombre_salon"),
                direccion=row.get("direccion"),

                fecha_registro=parse_fecha_hora(row.get("fecha_registro")),

                folio_manual=row.get("folio_manual"),
                total=parse_float(row.get("total")),
                anticipo=parse_float(row.get("anticipo")),
                restan=parse_float(row.get("restan")),
                comentarios=row.get("comentarios")
            )

            db.session.add(evento)
            cargados += 1

        db.session.commit()

        print("===================================")
        print(f"✅ Eventos cargados: {cargados}")
        print(f"⚠️ Eventos ignorados: {ignorados}")
        print("===================================")
