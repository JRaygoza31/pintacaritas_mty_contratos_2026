# base_de_datos.py
from flask import Blueprint, render_template_string, request, redirect, url_for, flash, send_file
from extensiones import db
from models import Evento
from io import BytesIO
from datetime import datetime
import csv
import math
from flask_login import login_required
from auth import auth_bp
from flask import session
CLAVE_BASE_DATOS = "pcmty"



# Intentar cargar pandas para exportar XLSX
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except Exception:
    PANDAS_AVAILABLE = False

base_de_datos_bp = Blueprint('base_de_datos', __name__, url_prefix='/base-de-datos')

@base_de_datos_bp.before_request
def proteger_base_datos():
    # permitir acceder a la página de contraseña
    if request.endpoint == 'base_de_datos.password':
        return

    if not session.get("acceso_base_datos"):
        return redirect(url_for("base_de_datos.password"))


# =====================================================
#                 FILTROS
# =====================================================
def aplicar_filtros(query, tipo_evento, fecha_desde, fecha_hasta, qsearch):
    if tipo_evento:
        query = query.filter(Evento.tipo_evento == tipo_evento)
    if fecha_desde:
        try:
            fd = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            query = query.filter(Evento.fecha_evento >= fd)
        except:
            pass
    if fecha_hasta:
        try:
            fh = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            query = query.filter(Evento.fecha_evento <= fh)
        except:
            pass
    if qsearch:
        like = f"%{qsearch}%"
        query = query.filter(
            db.or_(
                Evento.nombre_cliente.ilike(like),
                Evento.nombre_salon.ilike(like),
                Evento.direccion.ilike(like)
            )
        )
    return query

@base_de_datos_bp.route('/password', methods=['GET', 'POST'])
def password():
    if request.method == 'POST':
        if request.form.get('password') == CLAVE_BASE_DATOS:
            session['acceso_base_datos'] = True
            return redirect(url_for('base_de_datos.lista_eventos'))
        else:
            flash("❌ Contraseña incorrecta", "error")

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Acceso restringido</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-blue-100 flex items-center justify-center h-screen">

        <form method="POST" class="bg-white p-8 rounded-xl shadow-lg w-80">
            <h2 class="text-xl font-bold mb-4 text-center text-blue-700">
                🔐 Acceso a Base de Datos
            </h2>

            <input type="password"
                   name="password"
                   placeholder="Contraseña"
                   class="w-full p-2 border rounded mb-4"
                   required>

            <button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded">
                Entrar
            </button>
        </form>

    </body>
    </html>
    """)


# =====================================================
#                 LISTA DE EVENTOS
# =====================================================
@base_de_datos_bp.route('/', methods=['GET'])
def lista_eventos():
    tipo_evento = request.args.get('tipo_evento', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    qsearch = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Evento.query.order_by(Evento.fecha_evento.asc(), Evento.id.asc())
    query = aplicar_filtros(query, tipo_evento or None, fecha_desde or None, fecha_hasta or None, qsearch or None)

    total = query.count()
    pages = max(1, math.ceil(total / per_page))
    eventos = query.offset((page - 1) * per_page).limit(per_page).all()

    # enviar datetime al template
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>📊 Base de Datos</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

<style>
  body { background: linear-gradient(135deg, #bfdbfe, #93c5fd); min-height: 100vh; }
  th { background-color: #e0f2fe; position: sticky; top: 0; }
</style>

<script>
function confirmarEliminacion() {
  return confirm("❗ ¿Seguro que deseas eliminar este registro?\\nEsta acción NO se puede deshacer.");
}

// =====================
//  HABILITAR EDICIÓN
// =====================
function enableEdit(id) {
    const fields = document.querySelectorAll('.editable-' + id);
    fields.forEach(f => {
        f.disabled = false;
        f.classList.remove("bg-gray-100");
        f.classList.add("bg-white", "border-blue-500");
    });

    document.getElementById('edit-btn-' + id).classList.add("hidden");
    document.getElementById('save-btn-' + id).classList.remove("hidden");
}
</script>

</head>

<body class="p-6">

<div class="max-w-7xl mx-auto bg-white p-6 rounded-2xl shadow-lg">
    
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-2xl font-bold text-blue-700">📋 Base de datos de eventos</h1>

    <div>
      <a href="{{ url_for('home') }}" 
         class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg mr-2">⬅️ Inicio</a>

    <a href="{{ url_for('generar_contrato.generar_contrato') }}"
   class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mr-2">
    📝 Generar contrato
</a>


      <a href="{{ url_for('base_de_datos.exportar',
                           tipo_evento=tipo_evento,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           q=qsearch) }}"
         class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">📥 Exportar</a>
    </div>
  </div>

  <!-- FILTROS -->
  <form method="GET" class="bg-blue-50 p-4 rounded-lg shadow mb-4 grid grid-cols-1 md:grid-cols-6 gap-3">
    <div>
      <label class="block text-sm font-semibold">Tipo de evento</label>
      <select name="tipo_evento" class="mt-1 block w-full p-2 border rounded">
        <option value="">Todos</option>
        <option value="Pintacaritas" {% if tipo_evento == 'Pintacaritas' %}selected{% endif %}>Pintacaritas</option>
        <option value="Glitter" {% if tipo_evento == 'Glitter' %}selected{% endif %}>Glitter</option>
      </select>
    </div>

    <div>
      <label class="block text-sm font-semibold">Desde</label>
      <input type="date" name="fecha_desde" value="{{ fecha_desde }}" class="mt-1 block w-full p-2 border rounded">
    </div>

    <div>
      <label class="block text-sm font-semibold">Hasta</label>
      <input type="date" name="fecha_hasta" value="{{ fecha_hasta }}" class="mt-1 block w-full p-2 border rounded">
    </div>

    <div class="md:col-span-2">
      <label class="block text-sm font-semibold">Buscar</label>
      <input type="text" name="q" value="{{ qsearch }}" placeholder="Cliente / Salón / Dirección"
             class="mt-1 block w-full p-2 border rounded">
    </div>

    <div class="flex items-end">
      <button type="submit"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
        Filtrar
      </button>
    </div>
  </form>

  <!-- TABLA -->
<div class="overflow-auto rounded-lg shadow">
<table class="min-w-full divide-y divide-gray-300 text-xs">

<thead>
<tr class="bg-blue-100 font-semibold text-gray-700 text-center">
    <th class="px-2 py-2">ID</th>
    <th class="px-2 py-2">Cliente</th>
    <th class="px-2 py-2">Tipo</th>
    <th class="px-2 py-2">Tipo de Fiesta</th>
    <th class="px-2 py-2">Fecha</th>
    <th class="px-2 py-2">Inicio</th>
    <th class="px-2 py-2">Fin</th>
    <th class="px-2 py-2">Horas</th>
    <th class="px-2 py-2">Municipio</th>
    <th class="px-2 py-2">Salón</th>
    <th class="px-2 py-2">Dirección</th>
    <th class="px-2 py-2">Total</th>
    <th class="px-2 py-2">Anticipo</th>
    <th class="px-2 py-2">Restan</th>
    <th class="px-2 py-2">Comentarios</th>
    <th class="px-2 py-2">Folio</th>
    <th class="px-2 py-2">Editar</th>
    <th class="px-2 py-2">Eliminar</th>
</tr>
</thead>

<tbody>
{% for ev in eventos %}
<tr class="hover:bg-blue-50 text-center">

<form method="POST" action="{{ url_for('base_de_datos.editar_evento', evento_id=ev.id) }}">

<td class="px-2 py-2">{{ ev.id }}</td>

<td class="px-2 py-2">
  <input type="text" name="nombre_cliente" value="{{ ev.nombre_cliente }}"
         class="editable-{{ ev.id }} w-full border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <select name="tipo_evento"
          class="editable-{{ ev.id }} border rounded bg-gray-100" disabled>
    <option value="Pintacaritas" {% if ev.tipo_evento=='Pintacaritas' %}selected{% endif %}>Pintacaritas</option>
    <option value="Glitter" {% if ev.tipo_evento=='Glitter' %}selected{% endif %}>Glitter</option>
  </select>
</td>

<td class="px-2 py-2">
  <input type="text" name="tipo_fiesta" value="{{ ev.tipo_fiesta}}"
         class="editable-{{ ev.id }} border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="date" name="fecha_evento"
         value="{{ ev.fecha_evento.strftime('%Y-%m-%d') if ev.fecha_evento }}"
         class="editable-{{ ev.id }} border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="text" name="hora_inicio" value="{{ ev.hora_inicio }}"
         class="editable-{{ ev.id }} w-16 border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="text" name="hora_termino" value="{{ ev.hora_termino }}"
         class="editable-{{ ev.id }} w-16 border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input name="cantidad_horas" value="{{ ev.cantidad_horas }}"
         class="editable-{{ ev.id }} w-16 border rounded bg-gray-100 text-center" disabled>
</td>


<td class="px-2 py-2">
  <input type="text" name="municipio" value="{{ ev.municipio }}"
         class="editable-{{ ev.id }} border rounded bg-gray-100" disabled>
</td>


<td class="px-2 py-2">
  <input type="text" name="nombre_salon" value="{{ ev.nombre_salon }}"
         class="editable-{{ ev.id }} border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="text" name="direccion" value="{{ ev.direccion }}"
         class="editable-{{ ev.id }} w-full border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="number" step="0.01" name="total" value="{{ ev.total }}"
         class="editable-{{ ev.id }} w-20 text-center border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="number" step="0.01" name="anticipo" value="{{ ev.anticipo }}"
         class="editable-{{ ev.id }} w-20 text-center border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <input type="number" step="0.01" name="restan" value="{{ ev.restan }}"
         class="editable-{{ ev.id }} w-20 text-center border rounded bg-gray-100" disabled>
</td>

<td class="px-2 py-2">
  <textarea name="comentarios"
            class="editable-{{ ev.id }} w-32 border rounded bg-gray-100" disabled>{{ ev.comentarios }}</textarea>
</td>

<td class="px-2 py-2">
  <input type="text" name="folio_manual" value="{{ ev.folio_manual }}"
         class="editable-{{ ev.id }} w-20 border rounded bg-gray-100" disabled>
</td>

<td class="px-1 py-2">
  <button type="button"
          onclick="enableEdit({{ ev.id }})"
          id="edit-btn-{{ ev.id }}"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-2 py-1 rounded text-xs">
      ✏️
  </button>

  <button type="submit"
          id="save-btn-{{ ev.id }}"
          class="hidden bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs">
      💾
  </button>
</td>

</form>

<td class="px-1 py-2">
  <form method="POST"
        action="{{ url_for('base_de_datos.eliminar_evento', evento_id=ev.id) }}"
        onsubmit="return confirmarEliminacion()">
      <button type="submit"
              class="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs">
          🗑️
      </button>
  </form>
</td>

</tr>
{% endfor %}
</tbody>


</table>
</div>

        
  <!-- PAGINACIÓN -->
  <div class="flex justify-between items-center mt-4 text-sm">
    {% if page > 1 %}
      <a href="{{ url_for('base_de_datos.lista_eventos',
                          page=page-1,
                          tipo_evento=tipo_evento,
                          fecha_desde=fecha_desde,
                          fecha_hasta=fecha_hasta,
                          q=qsearch) }}"
         class="px-3 py-1 bg-gray-200 rounded">« Anterior</a>
    {% else %}
      <span></span>
    {% endif %}

    <span>Página {{ page }} de {{ pages }}</span>

    {% if page < pages %}
      <a href="{{ url_for('base_de_datos.lista_eventos',
                          page=page+1,
                          tipo_evento=tipo_evento,
                          fecha_desde=fecha_desde,
                          fecha_hasta=fecha_hasta,
                          q=qsearch) }}"
         class="px-3 py-1 bg-gray-200 rounded">Siguiente »</a>
    {% endif %}
  </div>

</div>

</body>
</html>
""",
        eventos=eventos,
        total=total,
        page=page,
        pages=pages,
        tipo_evento=tipo_evento,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        qsearch=qsearch,
        datetime=datetime
    )


# =====================================================
#                 GUARDAR CAMBIOS
# =====================================================
@base_de_datos_bp.route('/editar/<int:evento_id>', methods=['POST'])

def editar_evento(evento_id):
    ev = Evento.query.get_or_404(evento_id)

    def safe_float(v):
        try:
            return float(v)
        except:
            return None

    ev.nombre_cliente = request.form.get('nombre_cliente')
    ev.tipo_evento = request.form.get('tipo_evento')
    ev.tipo_fiesta = request.form.get('tipo_fiesta')
    ev.fecha_evento = datetime.strptime(request.form.get('fecha_evento'), "%Y-%m-%d")
    ev.hora_inicio = request.form.get('hora_inicio')
    ev.hora_termino = request.form.get('hora_termino')
    ev.municipio = request.form.get('municipio')
    ev.nombre_salon = request.form.get('nombre_salon')
    ev.direccion = request.form.get('direccion')

    ev.total = safe_float(request.form.get('total'))
    ev.anticipo = safe_float(request.form.get('anticipo'))
    ev.restan = safe_float(request.form.get('restan'))
    ev.comentarios = request.form.get('comentarios')
    ev.folio_manual = request.form.get('folio_manual')

    if ev.total is not None and ev.anticipo is not None:
        ev.restan = ev.total - ev.anticipo

    db.session.commit()
    flash("✅ Registro actualizado correctamente", "success")

    return redirect(request.referrer)



# =====================================================
#                 ELIMINAR EVENTO
# =====================================================
@base_de_datos_bp.route('/eliminar/<int:evento_id>', methods=['POST'])

def eliminar_evento(evento_id):
    ev = Evento.query.get_or_404(evento_id)

    try:
        db.session.delete(ev)
        db.session.commit()
        flash("🗑️ Registro eliminado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al eliminar: {e}", "error")

    return redirect(url_for('base_de_datos.lista_eventos'))


# =====================================================
#                 EXPORTAR
# =====================================================
@base_de_datos_bp.route('/exportar')


def exportar():
    tipo_evento = request.args.get('tipo_evento', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    qsearch = request.args.get('q', '')

    query = aplicar_filtros(Evento.query,
                            tipo_evento or None,
                            fecha_desde or None,
                            fecha_hasta or None,
                            qsearch or None)

    eventos = query.all()

    headers = [
        "id", "tipo_evento", "tipo_fiesta", "nombre_cliente", "whatsapp", "fecha_evento",
        "hora_inicio", "hora_termino", "cantidad_horas", "servicios_interes",
        "municipio","nombre_salon", "direccion", "fecha_registro",
        "folio_manual", "total", "anticipo", "restan", "comentarios"
    ]

    if PANDAS_AVAILABLE:
        df = pd.DataFrame([{h: getattr(e, h) for h in headers} for e in eventos])
        bio = BytesIO()
        df.to_excel(bio, index=False)
        bio.seek(0)
        return send_file(
            bio,
            download_name=f"eventos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            as_attachment=True
        )

    bio = BytesIO()
    writer = csv.writer(bio)
    writer.writerow(headers)
    for e in eventos:
        writer.writerow([getattr(e, h) for h in headers])
    bio.seek(0)

    return send_file(
        bio,
        download_name=f"eventos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        as_attachment=True
    )
