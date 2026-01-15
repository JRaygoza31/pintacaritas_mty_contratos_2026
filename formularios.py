from flask import Blueprint, render_template_string, request, redirect, url_for
from extensiones import db
from models import Evento, Servicio, Municipio, Tipo_fiesta
from datetime import datetime

formularios_bp = Blueprint('formularios', __name__)

# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------

def calcular_horas(hora_inicio, hora_termino):
    try:
        formato = "%I:%M%p"
        inicio = datetime.strptime(hora_inicio, formato)
        fin = datetime.strptime(hora_termino, formato)
        duracion = (fin - inicio).seconds / 3600
        if duracion < 0:  # Por si termina después de medianoche
            duracion += 24
        return round(duracion, 1)
    except:
        return None


def lista_horas():
    horas = []
    hora = datetime.strptime("10:00AM", "%I:%M%p")
    for i in range(20):  # Hasta más o menos las 8 PM
        horas.append(hora.strftime("%I:%M%p"))
        hora = hora.replace(minute=(hora.minute + 30) % 60)
        if hora.minute == 0:
            hora = hora.replace(hour=(hora.hour + 1))
    return horas


# ---------------------------
# MENÚ DE FORMULARIOS
# ---------------------------
@formularios_bp.route('/formulario-evento')
def seleccionar_formulario():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Seleccionar formulario</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <style>
body {
    background: linear-gradient(135deg, #2563eb, #7c3aed, #ec4899);
    background-size: 200% 200%;
    animation: fondomove 12s ease infinite;
    min-height: 100vh;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
}

@keyframes fondomove {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 0%; }
}

.overlay {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(8px);
    border-radius: 1rem;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    width: 100%;
    max-width: 900px;
}
</style>


<body>
  <div class="overlay text-white rounded-2xl p-8 w-full max-w-4xl mx-auto">
    <div class="text-center">
      <h1 class="text-4xl font-bold mb-2">🖌️ Selecciona el tipo de formulario</h1>
      <p class="text-lg mb-10 opacity-90">Escoge qué servicio deseas registrar</p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <a href="{{ url_for('formularios.formulario_pintacaritas') }}"
           class="bg-pink-500 hover:bg-pink-600 transition rounded-2xl p-6 flex flex-col items-center shadow-xl">
          <div class="text-5xl mb-3">🎨</div>
          <h2 class="text-xl font-semibold mb-1">Formulario Pintacaritas</h2>
        </a>

        <a href="{{ url_for('formularios.formulario_glitter') }}"
           class="bg-blue-500 hover:bg-blue-600 transition rounded-2xl p-6 flex flex-col items-center shadow-xl">
          <div class="text-5xl mb-3">✨</div>
          <h2 class="text-xl font-semibold mb-1">Formulario Glitter</h2>
        </a>
      </div>
    </div>
  </div>
</body>
</html>
""")


# ---------------------------
# PANTALLA DE REGISTRO EXITOSO — AHORA CON RESUMEN
# ---------------------------
@formularios_bp.route('/registro-exitoso')
def registro_exitoso():

    evento_id = request.args.get("evento_id")

    if not evento_id:
        return "Error: no se recibió ID del evento."

    evento = Evento.query.get(evento_id)
    if not evento:
        return "Evento no encontrado."

    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Registro Exitoso</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

  <style>
    body {
            background: linear-gradient(135deg, #3b82f6, #9333ea, #ec4899);
            background-size: 200% 200%;
            animation: fondomove 8s ease infinite;
        }
        @keyframes fondomove {
            0% { background-position: 0% 0%; }
            50% { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }


  </style>
  
  
</head>

<body>
  <div class="bg-white bg-opacity-10 p-10 rounded-2xl shadow-lg text-center max-w-xl w-full">

    <div class="text-6xl mb-4">🎉</div>
    <h1 class="text-3xl font-bold mb-3">¡Evento registrado con éxito!</h1>

    <h2 class="text-xl font-semibold mb-4">Resumen del evento:</h2>

    <div class="bg-white bg-opacity-20 p-4 rounded-lg text-left space-y-2">
      <p><strong>Cliente:</strong> {{ evento.nombre_cliente }}</p>
      <p><strong>WhatsApp:</strong> {{ evento.whatsapp }}</p>
      <p><strong>Fecha:</strong> {{ evento.fecha_evento.strftime('%d/%m/%Y') }}</p>
      <p><strong>Horario:</strong> {{ evento.hora_inicio }} - {{ evento.hora_termino }}</p>
      <p><strong>Horas:</strong> {{ evento.cantidad_horas }}</p>
      <p><strong>Servicios:</strong> {{ evento.servicios_interes }}</p>
      <p><strong>Municipio:</strong> {{ evento.municipio }}</p>
      <p><strong>Salón:</strong> {{ evento.nombre_salon or 'N/A' }}</p>
      <p><strong>Dirección:</strong> {{ evento.direccion or 'N/A' }}</p>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 justify-center mt-6">

      <a href="{{ url_for('formularios.seleccionar_formulario') }}"
         class="bg-blue-500 hover:bg-blue-600 transition text-white font-semibold px-6 py-3 rounded-lg">
          🏠 Volver al menú
      </a>

      <a href="{{ url_for('formularios.formulario_pintacaritas') }}"
         class="bg-pink-500 hover:bg-pink-600 transition text-white font-semibold px-6 py-3 rounded-lg">
          ➕ Registrar otro evento
      </a>

      <!-- 📲 BOTÓN WHATSAPP SIN %0A -->
      <button id="whatsappBtn"
              class="bg-green-500 hover:bg-green-600 transition text-white font-semibold px-6 py-3 rounded-lg">
          📲 Compartir por WhatsApp
      </button>

    </div>

  </div>

<script>
(function(){
  const nombreCliente = "{{ evento.nombre_cliente|e }}";
  let phoneRaw = "{{ evento.whatsapp|e }}";
  const fecha = "{{ evento.fecha_evento.strftime('%d/%m/%Y') }}";
  const horaInicio = "{{ evento.hora_inicio|e }}";
  const horaTermino = "{{ evento.hora_termino|e }}";
  const horas = "{{ evento.cantidad_horas|e }}";
  const servicios = "{{ evento.servicios_interes|e }}";
  const municipio = "{{ evento.municipio|e }}";
  const tipo_fiesta = "{{ evento.tipo_fiesta|e }}";
  const salon = "{{ (evento.nombre_salon or 'N/A')|e }}";
  const direccion = "{{ (evento.direccion or 'N/A')|e }}";

  function normalizePhone(p) {
    let digits = p.replace(/\\D/g, '');
    if (!digits) return '';
    if (digits.length === 10) return '52' + digits;
    return digits;
  }

  document.getElementById('whatsappBtn').addEventListener('click', function(){
    const phone = normalizePhone(phoneRaw);
    if (!phone) {
      alert("El número de WhatsApp no es válido.");
      return;
    }

    const plural = parseFloat(horas) > 1 ? "s" : "";
    const duracion = horas ? `${horas} hora${plural}` : "N/A";

    const mensaje = [
      `✨ ¡Hola ${nombreCliente}! ✨`,
      ``,
      `Aquí tienes el resumen de tu evento:`,
      ``,
      `📅 Fecha: ${fecha}`,
      `⏰ Horario: ${horaInicio} - ${horaTermino}`,
      `⏳ Duración: ${duracion}`,
      `🎨 Servicios: ${servicios}`,
      `📍 Municipio: ${municipio}`,
      `🏨 Salón: ${salon}`,
      `📌 Dirección: ${direccion}`,
      ``,
      `¡Gracias por registrar tu evento con nosotros! 🎉`
    ].join("\\n");

    const url = "https://api.whatsapp.com/send?phone=" + phone + "&text=" + encodeURIComponent(mensaje);
    window.open(url, "_blank");
  });
})();
</script>

</body>
</html>
""", evento=evento)



# ---------------------------
# FORMULARIO BASE
# ---------------------------
def generar_formulario_html(tipo, servicios):
    horas = []
    for h in range(24):
        for m in ["00", "30"]:
            horas.append(f"{h:02d}:{m}")

    municipios = [m.nombre for m in Municipio.query.order_by(Municipio.nombre).all()]
    tipo_fiesta = [m.nombre for m in Tipo_fiesta.query.order_by(Tipo_fiesta.nombre).all()]


    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Formulario {{ tipo }}</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <script>
    function calcularHoras() {
      const inicio = document.getElementById("hora_inicio").value;
      const fin = document.getElementById("hora_termino").value;
      if (!inicio || !fin) return;
      const parse = (t) => {
        let [h,m] = t.split(":");
        let ampm = t.includes("AM") ? "AM" : "PM";
        h = parseInt(h); m = parseInt(m);
        if (ampm === "PM" && h !== 12) h += 12;
        if (ampm === "AM" && h === 12) h = 0;
        return h + m/60;
      }
      let dur = parse(fin) - parse(inicio);
      if (dur < 0) dur += 24;
      document.getElementById("cantidad_horas").value = dur.toFixed(1);
    }
  </script>
</head>

<body class="bg-gradient-to-br from-blue-900 via-purple-800 to-pink-700 text-white">
  <div class="min-h-screen flex flex-col items-center justify-center p-6">
    <div class="bg-white bg-opacity-10 p-8 rounded-2xl shadow-lg w-full max-w-2xl">
      <h1 class="text-3xl font-bold mb-6 text-center">{{ tipo }} 🎉</h1>

      <form method="POST" class="space-y-4">
        <input name="nombre_cliente" placeholder="Nombre del cliente" required class="w-full p-3 rounded-lg text-black focus:outline-none">
        <input
            name="whatsapp"
            placeholder="WhatsApp"
            required
            class="w-full p-3 rounded-lg text-black focus:outline-none"
            pattern="\\d{10}"
            maxlength="10"
            inputmode="numeric"
        />
        <input name="fecha_evento" type="date" required class="w-full p-3 rounded-lg text-black focus:outline-none">

        <div class="flex gap-4">
          <select name="hora_inicio" id="hora_inicio" onchange="calcularHoras()" required class="w-1/2 p-3 rounded-lg text-black">
            <option value="">Hora de inicio</option>
            {% for h in horas %}
              <option>{{ h }}</option>
            {% endfor %}
          </select>
          <select name="hora_termino" id="hora_termino" onchange="calcularHoras()" required class="w-1/2 p-3 rounded-lg text-black">
            <option value="">Hora de término</option>
            {% for h in horas %}
              <option>{{ h }}</option>
            {% endfor %}
          </select>
        </div>

        <input id="cantidad_horas" name="cantidad_horas" readonly placeholder="Cantidad de horas" class="w-full p-3 rounded-lg text-black focus:outline-none bg-gray-100">

        <label class="block font-semibold mt-3 mb-2">Servicios de interés:</label>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 bg-white bg-opacity-10 p-3 rounded-lg">
        {% for s in servicios %}
            <label class="flex items-center space-x-2 text-sm">
            <input type="checkbox" name="servicios_interes" value="{{ s }}" class="form-checkbox text-pink-500">
            <span>{{ s }}</span>
            </label>
        {% endfor %}
        </div>

        <select name="municipio" required class="w-full p-3 rounded-lg text-black focus:outline-none">
          <option value="">Municipio del evento</option>
          {% for m in municipios %}
            <option>{{ m }}</option>
          {% endfor %}
        </select>
        
        <select name="tipo_fiesta" required class="w-full p-3 rounded-lg text-black focus:outline-none">
          <option value="">Tipo de fiesta</option>
          {% for m in tipo_fiesta %}
            <option>{{ m }}</option>
          {% endfor %}
        </select>

        <input name="nombre_salon" placeholder="Nombre del salón" class="w-full p-3 rounded-lg text-black focus:outline-none">
        <input name="direccion" placeholder="Dirección (calle y número)" class="w-full p-3 rounded-lg text-black focus:outline-none">

        <button class="w-full bg-pink-500 hover:bg-pink-600 text-white font-semibold p-3 rounded-lg transition">
          Guardar evento
        </button>
      </form>

      <div class="mt-6 text-center">
        <a href="{{ url_for('formularios.seleccionar_formulario') }}" class="text-sm text-purple-300 hover:text-purple-100">⬅️ Volver</a>
      </div>
    </div>
  </div>
</body>
</html>
""", tipo=tipo, horas=horas, servicios=servicios, tipo_fiesta=tipo_fiesta, municipios=municipios)


# ---------------------------
# FORMULARIO PINTACARITAS
# ---------------------------
@formularios_bp.route('/formulario-pintacaritas', methods=['GET', 'POST'])
def formulario_pintacaritas():
    servicios_pinta = [s.nombre for s in Servicio.query.order_by(Servicio.nombre).all()]

    if request.method == 'POST':
        evento = Evento(
            tipo_evento="Pintacaritas",
            nombre_cliente=request.form['nombre_cliente'],
            whatsapp=request.form['whatsapp'],
            fecha_evento=datetime.strptime(request.form['fecha_evento'], '%Y-%m-%d'),
            hora_inicio=request.form['hora_inicio'],
            hora_termino=request.form['hora_termino'],
            cantidad_horas=request.form.get('cantidad_horas'),
            servicios_interes=", ".join(request.form.getlist('servicios_interes')),
            municipio=request.form['municipio'],
            tipo_fiesta=request.form['tipo_fiesta'],
            nombre_salon=request.form.get('nombre_salon'),
            direccion=request.form.get('direccion')
        )
        db.session.add(evento)
        db.session.commit()
        return redirect(url_for('formularios.registro_exitoso', evento_id=evento.id))

    return generar_formulario_html("Formulario Pintacaritas", servicios_pinta)


# ---------------------------
# FORMULARIO GLITTER
# ---------------------------
@formularios_bp.route('/formulario-glitter', methods=['GET', 'POST'])
def formulario_glitter():
    servicios_glitter = [s.nombre for s in Servicio.query.filter_by(tipo="Glitter").order_by(Servicio.nombre).all()]

    if request.method == 'POST':
        evento = Evento(
            tipo_evento="Glitter",
            nombre_cliente=request.form['nombre_cliente'],
            whatsapp=request.form['whatsapp'],
            fecha_evento=datetime.strptime(request.form['fecha_evento'], '%Y-%m-%d'),
            hora_inicio=request.form['hora_inicio'],
            hora_termino=request.form['hora_termino'],
            cantidad_horas=request.form.get('cantidad_horas'),
            servicios_interes=", ".join(request.form.getlist('servicios_interes')),
            municipio=request.form['municipio'],
            tipo_fiesta=request.form['tipo_fiesta'],
            nombre_salon=request.form.get('nombre_salon'),
            direccion=request.form.get('direccion')
        )
        db.session.add(evento)
        db.session.commit()
        return redirect(url_for('formularios.registro_exitoso', evento_id=evento.id))

    return generar_formulario_html("Formulario Glitter", servicios_glitter)
