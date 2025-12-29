from flask import Blueprint, render_template_string, request, redirect, url_for, flash
from models import Servicio, Municipio, Tipo_fiesta
from extensiones import db

gestion_bp = Blueprint('gestion', __name__, url_prefix='/gestion')

# -----------------------------
# SERVICIOS INICIALES
# -----------------------------
SERVICIOS_PINTA = [
    "Pintacaritas Básico", "Pintacaritas Profesional", "Talle de Caritas de Pasto",
    "Taller de Decoración de Espejos", "Taller de Slime", "Taller de Yesitos",
    "Taller de Pulseritas", "Taller de Globos Sensoriales", "Taller de Glitter Tatto",
    "Taller Decoración de Lentes", "Pintauñitas", "Caballetes", "Perfume Bar",
    "Glitter Bar Kids", "Charola de Glitter", "Carrito de Glitter",
    "Promo especial 2 horas Pintacaritas Pro y Taller",
    "Promo especial 2 horas Glitter Bar Kids y Taller",
    "Promo especial 1 hora Pintacaritas Pro y Taller"
]

SERVICIOS_GLITTER = [
    "Charola Neon de Glitter", "Carrito de Glitter",
    "Glitter Bar", "Glitter Party", "Glitter Bar Deluxe"
]

# -----------------------------
# MUNICIPIOS INICIALES
# -----------------------------
MUNICIPIOS_INICIALES = [
    "MONTERREY",
    "SPGG",
    "GUADALUPE",
    "SAN NICOLAS",
    "APODACA",
    "SANTIAGO"
]

# -----------------------------
# TIPOS DE FIESTA INICIALES
# -----------------------------
TIPOS_FIESTA_INICIALES = [
    "BODA",
    "CUMPLEAÑOS",
    "QUINCEAÑERA"
]

# -----------------------------
# INICIALIZADORES
# -----------------------------
def inicializar_servicios():
    for nombre in SERVICIOS_PINTA:
        if not Servicio.query.filter_by(nombre=nombre, tipo="Pintacaritas").first():
            db.session.add(Servicio(nombre=nombre, tipo="Pintacaritas"))

    for nombre in SERVICIOS_GLITTER:
        if not Servicio.query.filter_by(nombre=nombre, tipo="Glitter").first():
            db.session.add(Servicio(nombre=nombre, tipo="Glitter"))

    db.session.commit()


def inicializar_municipios():
    for nombre in MUNICIPIOS_INICIALES:
        if not Municipio.query.filter_by(nombre=nombre).first():
            db.session.add(Municipio(nombre=nombre))
    db.session.commit()


def inicializar_tipos_fiesta():
    for nombre in TIPOS_FIESTA_INICIALES:
        if not Tipo_fiesta.query.filter_by(nombre=nombre).first():
            db.session.add(Tipo_fiesta(nombre=nombre))
    db.session.commit()

# -----------------------------
# INDEX
# -----------------------------
@gestion_bp.route('/')
def index():
    inicializar_servicios()
    inicializar_municipios()
    inicializar_tipos_fiesta()

    servicios = Servicio.query.order_by(Servicio.tipo, Servicio.nombre).all()
    municipios = Municipio.query.order_by(Municipio.nombre).all()
    tipos_fiesta = Tipo_fiesta.query.order_by(Tipo_fiesta.nombre).all()

    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Gestión</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">

<h1 class="text-3xl font-bold mb-6">Gestión de Información</h1>

<!-- SERVICIOS -->
<h2 class="text-2xl font-semibold mb-4">Servicios</h2>
<a href="{{ url_for('gestion.agregar_servicio') }}"
class="bg-blue-500 text-white px-4 py-2 rounded mb-4 inline-block">➕ Servicio</a>

<table class="w-full bg-white shadow rounded mb-10">
<thead class="bg-gray-200">
<tr>
<th>ID</th><th>Nombre</th><th>Tipo</th><th>Acciones</th>
</tr>
</thead>
<tbody>
{% for s in servicios %}
<tr class="border-b">
<td class="px-2">{{ s.id }}</td>
<td>{{ s.nombre }}</td>
<td>{{ s.tipo }}</td>
<td class="flex gap-2">
<a href="{{ url_for('gestion.editar_servicio', id=s.id) }}" class="text-yellow-600">✏️</a>
<a href="{{ url_for('gestion.eliminar_servicio', id=s.id) }}" class="text-red-600"
onclick="return confirm('¿Eliminar servicio?')">🗑️</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>

<!-- MUNICIPIOS -->
<h2 class="text-2xl font-semibold mb-4">Municipios</h2>
<a href="{{ url_for('gestion.agregar_municipio') }}"
class="bg-blue-500 text-white px-4 py-2 rounded mb-4 inline-block">➕ Municipio</a>

<table class="w-full bg-white shadow rounded mb-10">
<thead class="bg-gray-200">
<tr>
<th>ID</th><th>Nombre</th><th>Acciones</th>
</tr>
</thead>
<tbody>
{% for m in municipios %}
<tr class="border-b">
<td class="px-2">{{ m.id }}</td>
<td>{{ m.nombre }}</td>
<td class="flex gap-2">
<a href="{{ url_for('gestion.editar_municipio', id=m.id) }}" class="text-yellow-600">✏️</a>
<a href="{{ url_for('gestion.eliminar_municipio', id=m.id) }}" class="text-red-600"
onclick="return confirm('¿Eliminar municipio?')">🗑️</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>

<!-- TIPOS DE FIESTA -->
<h2 class="text-2xl font-semibold mb-4">Tipos de Fiesta</h2>
<a href="{{ url_for('gestion.agregar_tipo_fiesta') }}"
class="bg-blue-500 text-white px-4 py-2 rounded mb-4 inline-block">➕ Tipo de fiesta</a>

<table class="w-full bg-white shadow rounded">
<thead class="bg-gray-200">
<tr>
<th>ID</th><th>Nombre</th><th>Acciones</th>
</tr>
</thead>
<tbody>
{% for t in tipos_fiesta %}
<tr class="border-b">
<td class="px-2">{{ t.id }}</td>
<td>{{ t.nombre }}</td>
<td class="flex gap-2">
<a href="{{ url_for('gestion.editar_tipo_fiesta', id=t.id) }}" class="text-yellow-600">✏️</a>
<a href="{{ url_for('gestion.eliminar_tipo_fiesta', id=t.id) }}" class="text-red-600"
onclick="return confirm('¿Eliminar tipo de fiesta?')">🗑️</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>

</body>
</html>
""", servicios=servicios, municipios=municipios, tipos_fiesta=tipos_fiesta)

# -----------------------------
# CRUD SERVICIOS
# -----------------------------
@gestion_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_servicio():
    if request.method == 'POST':
        nuevo = Servicio(
            nombre=request.form['nombre'],
            tipo=request.form['tipo'],
            descripcion=request.form.get('descripcion'),
            materiales=request.form.get('materiales')
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" placeholder="Nombre" required>
<select name="tipo">
<option>Pintacaritas</option>
<option>Glitter</option>
</select>
<button>Guardar</button>
</form>
""")

@gestion_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    if request.method == 'POST':
        servicio.nombre = request.form['nombre']
        servicio.tipo = request.form['tipo']
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" value="{{ s.nombre }}">
<select name="tipo">
<option {% if s.tipo=='Pintacaritas' %}selected{% endif %}>Pintacaritas</option>
<option {% if s.tipo=='Glitter' %}selected{% endif %}>Glitter</option>
</select>
<button>Guardar</button>
</form>
""", s=servicio)

@gestion_bp.route('/eliminar/<int:id>')
def eliminar_servicio(id):
    s = Servicio.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for('gestion.index'))

# -----------------------------
# CRUD MUNICIPIOS
# -----------------------------
@gestion_bp.route('/municipio/agregar', methods=['GET', 'POST'])
def agregar_municipio():
    if request.method == 'POST':
        db.session.add(Municipio(nombre=request.form['nombre'].upper()))
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" placeholder="Municipio" required>
<button>Guardar</button>
</form>
""")

@gestion_bp.route('/municipio/editar/<int:id>', methods=['GET', 'POST'])
def editar_municipio(id):
    m = Municipio.query.get_or_404(id)
    if request.method == 'POST':
        m.nombre = request.form['nombre'].upper()
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" value="{{ m.nombre }}">
<button>Guardar</button>
</form>
""", m=m)

@gestion_bp.route('/municipio/eliminar/<int:id>')
def eliminar_municipio(id):
    m = Municipio.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    return redirect(url_for('gestion.index'))

# -----------------------------
# CRUD TIPOS DE FIESTA
# -----------------------------
@gestion_bp.route('/tipo-fiesta/agregar', methods=['GET', 'POST'])
def agregar_tipo_fiesta():
    if request.method == 'POST':
        db.session.add(Tipo_fiesta(nombre=request.form['nombre'].upper()))
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" placeholder="Tipo de fiesta" required>
<button>Guardar</button>
</form>
""")

@gestion_bp.route('/tipo-fiesta/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_fiesta(id):
    t = Tipo_fiesta.query.get_or_404(id)
    if request.method == 'POST':
        t.nombre = request.form['nombre'].upper()
        db.session.commit()
        return redirect(url_for('gestion.index'))

    return render_template_string("""
<form method="POST">
<input name="nombre" value="{{ t.nombre }}">
<button>Guardar</button>
</form>
""", t=t)

@gestion_bp.route('/tipo-fiesta/eliminar/<int:id>')
def eliminar_tipo_fiesta(id):
    t = Tipo_fiesta.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('gestion.index'))