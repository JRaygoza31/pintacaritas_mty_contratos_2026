from flask import Flask, render_template_string, url_for
from extensiones import db
from formularios import formularios_bp
from base_de_datos import base_de_datos_bp
from generar_contrato import generar_contrato_bp
from models import Evento
from calendario import calendario_bp
from gestion_de_informacion import gestion_bp
from ver_estadisticas import ver_estadisticas_bp
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from models import Usuario
from auth import auth_bp
from flask_login import current_user

from flask_login import login_required




app = Flask(__name__)
app.secret_key = "supersecretkey"
app.jinja_env.globals.update(str=str)


# ---------------------------
# BASE DE DATOS
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql://pintacaritas_mty_contratos_user:"
    "ptOFK2zrWL3lInvFTdBY57T1K6d5SoZb@"
    "dpg-d52str24d50c73baihhg-a.oregon-postgres.render.com/"
    "pintacaritas_mty_contratos"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ---------------------------
# BLUEPRINTS
# ---------------------------
app.register_blueprint(formularios_bp)
app.register_blueprint(base_de_datos_bp)
app.register_blueprint(generar_contrato_bp)
app.register_blueprint(gestion_bp)
app.register_blueprint(ver_estadisticas_bp)
app.register_blueprint(auth_bp)



# ---------------------------
# PANTALLA PRINCIPAL (CALENDARIO)
# ---------------------------
@app.route('/')

def home():

    eventos = []

    for e in Evento.query.all():
        if not e.fecha_evento:
            continue

        eventos.append({
            "id": e.id,
            "title": f"{e.folio_manual} • {e.tipo_evento.upper()}",
            "start": e.fecha_evento.strftime("%Y-%m-%d"),
            "tipo": e.tipo_evento,
            "nombre": e.nombre_cliente,
            "hora_inicio": e.hora_inicio,
            "hora_termino": e.hora_termino,
            "municipio": e.municipio,
            "salon": e.nombre_salon,
            "direccion": e.direccion,
            "whatsapp": e.whatsapp,
            "folio": e.folio_manual,
            "allDay": True
        })

    return render_template_string("""
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <title>Calendario - Pintacaritas</title>

    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js"></script>

    <style>
        body {
            background: linear-gradient(135deg, #3b82f6, #9333ea, #ec4899);
            background-size: 200% 200%;
            animation: fondomove 12s ease infinite;
        }
        @keyframes fondomove {
            0% { background-position: 0% 0%; }
            50% { background-position: 100% 100%; }
            100% { background-position: 0% 0%; }
        }

        .sidebar {
            width: 280px;
            background: rgba(0,0,0,0.55);
            backdrop-filter: blur(14px);
            border-right: 2px solid rgba(255,255,255,0.25);
            color: white;
            padding: 30px 20px; 
            position: fixed;
            top: 0;
            bottom: 0;
        }

        .menu-btn {
            display: block;
            padding: 18px 18px;
            margin-bottom: 16px;
            border-radius: 16px;
            font-weight: 800;
            font-size: 17px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.22);
            border: 1px solid rgba(255,255,255,0.15);
            text-align: left;
            transition: .25s;
        }

        .contenedor-cal {
            margin-left: 320px;
            padding: 40px;
        }

        .contenedor {
            background: rgba(255, 255, 255, 0.14);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.3);
        }

        .titulo {
            font-size: 48px;
            font-weight: 900;
            color: white;
            text-shadow: 0 4px 14px rgba(0,0,0,0.35);
        }
    </style>
</head>

<body>

<aside class="sidebar">
    <h2 class="text-3xl font-bold mb-8">🎨 Pintacaritas</h2>

    <a href="{{ url_for('formularios.seleccionar_formulario') }}"
       class="menu-btn bg-blue-500 hover:bg-blue-600 text-white opacity-100">🎉 Llenar formulario</a>
    
    <a href="{{ url_for('base_de_datos.lista_eventos') }}"
       class="menu-btn bg-green-500 hover:bg-green-600 text-white">📂 Ver base de datos
    </a>        
   

    <a href="{{ url_for('generar_contrato.generar_contrato') }}"
       class="menu-btn bg-pink-500 hover:bg-pink-600 text-white opacity-100">📝 Generar contrato</a>

    <a href="{{ url_for('ver_estadisticas.dashboard') }}"
       class="menu-btn bg-blue-500 hover:bg-blue-600 text-white transition rounded-lg">
       📊 Ver estadísticas
    </a>

    <a href="{{ url_for('gestion.index') }}"
       class="menu-btn bg-gray-500 text-white opacity-100">🗂️ Gestión de información</a>
</aside>


<div class="contenedor-cal min-h-screen">
    <div class="contenedor">

        <h1 class="text-center titulo mb-8">Calendario de Eventos</h1>

        <div class="flex justify-center gap-4 mb-6">
            <select id="mesSelector" class="rounded-lg px-3 py-2">
                <option value="0">Enero</option>
                <option value="1">Febrero</option>
                <option value="2">Marzo</option>
                <option value="3">Abril</option>
                <option value="4">Mayo</option>
                <option value="5">Junio</option>
                <option value="6">Julio</option>
                <option value="7">Agosto</option>
                <option value="8">Septiembre</option>
                <option value="9">Octubre</option>
                <option value="10">Noviembre</option>
                <option value="11">Diciembre</option>
            </select>

            <select id="yearSelector" class="rounded-lg px-3 py-2"></select>
        </div>

        <div id="calendar" class="rounded-3xl p-4 bg-white"></div>
    </div>
</div>


<!-- ================= MODAL ================= -->
<div id="eventoModal" class="fixed inset-0 bg-black/60 hidden justify-center items-center">
    <div class="bg-white rounded-2xl p-8 w-full max-w-md shadow-2xl border border-gray-200">

        <h2 class="text-2xl font-bold mb-1 text-purple-700" id="modalTitulo"></h2>

        <p class="text-lg font-semibold text-gray-700 mb-4" id="modalHorarioGrande"></p>

        <p class="mb-2"><strong>Folio:</strong> <span id="modalFolio"></span></p>
        <p class="mb-2"><strong>Nombre:</strong> <span id="modalNombre"></span></p>
        <p class="mb-2"><strong>Horario:</strong> <span id="modalHorario"></span></p>

        <p class="mb-2"><strong>Salón:</strong> <span id="modalSalon"></span></p>
        <p class="mb-2"><strong>Dirección:</strong> <span id="modalDireccion"></span></p>
        <p class="mb-2"><strong>Municipio:</strong> <span id="modalMunicipio"></span></p>

        <p class="mb-4"><strong>Tipo de Servicio:</strong> <span id="modalTipo"></span></p>

        <div class="flex justify-between mt-6 gap-3">

            <button onclick="cerrarModal()"
                class="px-4 py-2 rounded-xl bg-gray-300 hover:bg-gray-400">
                Cerrar
            </button>

            <a id="btnVerBase"
               class="px-4 py-2 rounded-xl bg-blue-500 text-white font-bold hover:bg-blue-600"
               target="_blank">
                Ver en la base
            </a>

            <a id="btnWhatsapp" target="_blank"
               class="px-4 py-2 rounded-xl bg-green-500 text-white font-bold hover:bg-green-600">
                Compartir por WhatsApp
            </a>

        </div>

    </div>
</div>


<script>
document.addEventListener("DOMContentLoaded", () => {

    function colorPorTipo(tipo, fecha, folio) {
        const hoy = new Date();
        const fechaEvento = new Date(fecha);

        if (fechaEvento < hoy.setHours(0,0,0,0)) return "#AAAAAA"; // verde evento pasado
        if (!folio || folio === "None") return "#dc2626"; // rojo sin folio

        tipo = tipo?.toLowerCase() || "";
        if (tipo.includes("pintacaritas")) return "#9AEF9E";
        if (tipo.includes("glitter")) return "#178C1D";

        return "#9333ea";
    }


    var calendar = new FullCalendar.Calendar(document.getElementById("calendar"), {
        initialView: "dayGridMonth",
        locale: "es",

        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: ""
        },

        events: {{ eventos | tojson }},

        eventDidMount(info) {
            const datos = info.event.extendedProps;

            const color = colorPorTipo(
                datos.tipo,
                info.event.startStr,
                datos.folio
            );

            Object.assign(info.el.style, {
                background: color,
                color: "white",
                padding: "8px 10px",
                borderRadius: "14px",
                border: "none",
                fontWeight: "700",
                boxShadow: "0 6px 16px rgba(0,0,0,0.35)"
            });
        },

        eventClick(info) {
            const datos = info.event.extendedProps;

            document.getElementById("modalTitulo").textContent =
                `FOLIO ${datos.folio} • ${datos.tipo.toUpperCase()}`;

            document.getElementById("modalHorarioGrande").textContent =
                `${datos.hora_inicio} — ${datos.hora_termino}`;

            document.getElementById("modalFolio").textContent = datos.folio;
            document.getElementById("modalNombre").textContent = datos.nombre;
            document.getElementById("modalHorario").textContent =
                `${datos.hora_inicio} a ${datos.hora_termino}`;

            document.getElementById("modalSalon").textContent = datos.salon || "No registrado";
            document.getElementById("modalDireccion").textContent = datos.direccion || "No registrada";
            document.getElementById("modalMunicipio").textContent = datos.municipio || "No registrado";
            document.getElementById("modalTipo").textContent = datos.tipo.toUpperCase();

            // WhatsApp
            const mensaje = encodeURIComponent(
                `📅 *Detalles del evento*\n` +
                `🧾 *Folio:* ${datos.folio}\n` +
                `🎨 *Servicio:* ${datos.tipo.toUpperCase()}\n` +
                `👤 *Nombre:* ${datos.nombre}\n` +
                `⏰ *Horario:* ${datos.hora_inicio} a ${datos.hora_termino}\n` +
                `🏢 *Salón:* ${datos.salon}\n` +
                `📍 *Dirección:* ${datos.direccion}\n` +
                `🌆 *Municipio:* ${datos.municipio}\n` +
                `📆 *Fecha:* ${info.event.startStr}`
            );

            document.getElementById("btnWhatsapp").href =
                `https://wa.me/?text=${mensaje}`;

            // VER EN LA BASE → va al evento específico
            document.getElementById("btnVerBase").href =
                document.getElementById("btnVerBase").href = "/base-de-datos";
                document.getElementById("eventoModal").classList.remove("hidden");
        }

    });

    calendar.render();

    const yearSelector = document.getElementById("yearSelector");
    const currentYear = new Date().getFullYear();

    for (let y = currentYear - 5; y <= currentYear + 5; y++) {
        let option = document.createElement("option");
        option.value = y;
        option.textContent = y;
        if (y === currentYear) option.selected = true;
        yearSelector.appendChild(option);
    }

    document.getElementById("mesSelector").addEventListener("change", cambiarFecha);
    yearSelector.addEventListener("change", cambiarFecha);

    function cambiarFecha() {
        const mes = parseInt(document.getElementById("mesSelector").value);
        const año = parseInt(yearSelector.value);
        calendar.gotoDate(new Date(año, mes, 1));
    }

    window.cerrarModal = function() {
        document.getElementById("eventoModal").classList.add("hidden");
    };
});
</script>

</body>
</html>
""", eventos=eventos)


# ---------------------------
# EJECUCIÓN
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
