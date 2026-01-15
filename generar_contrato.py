from flask import Blueprint, render_template_string, request, send_file
from extensiones import db
from models import Evento
from io import BytesIO
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF
import requests
import unicodedata

generar_contrato_bp = Blueprint("generar_contrato", __name__)

# -----------------------------
# Diccionario de meses en español
# -----------------------------
MESES_ES = {
    "January": "ENERO","February": "FEBRERO","March": "MARZO","April": "ABRIL",
    "May": "MAYO","June": "JUNIO","July": "JULIO","August": "AGOSTO",
    "September": "SEPTIEMBRE","October": "OCTUBRE","November": "NOVIEMBRE","December": "DICIEMBRE"
}

# -----------------------------
# Función para quitar acentos
# -----------------------------
def quitar_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# ============================================================
# Generación de contratos
# ============================================================
def generar_contrato_pintacaritas(evento):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFont("Helvetica-Bold", 22)
    can.setFillColor(colors.red)
    can.drawString(436, 623, str(evento.folio_manual or ""))

    mes = MESES_ES[evento.fecha_evento.strftime("%B")]
    fecha_larga = f"{evento.fecha_evento.day} DE {mes} DE {evento.fecha_evento.year}"
    can.setFont("Helvetica-Bold", 12)
    can.setFillColor(colors.blue)
    can.drawString(240, 543, fecha_larga)

   # Horario
    texto = (
        f"{evento.hora_inicio or ''} - {evento.hora_termino or ''}"
        f"     ({evento.cantidad_horas or ''} HORAS)"
    ).upper()

    can.drawString(240, 498, texto)



    can.drawString(240, 452, (str(evento.nombre_salon or "")).upper())
    
    can.setFont("Helvetica-Bold", 10)
    can.setFillColor(colors.blue)
    def wrap_text_by_space(texto, max_chars=3):
        palabras = texto.split(" ")
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_chars:
                linea_actual += (palabra + " ")
            else:
                lineas.append(linea_actual.strip())
                linea_actual = palabra + " "

        if linea_actual:
            lineas.append(linea_actual.strip())

        return lineas
      
    texto = f"{(evento.municipio or '').upper()} - {(evento.direccion or '').upper()}"

    lineas = wrap_text_by_space(texto, 38)

    y = 423
    for linea in lineas:
        can.drawString(240, y, linea)
        y -= 12  # espacio entre líneas

    can.setFont("Helvetica-Bold", 10)

    def w(t,m=40):
        p=t.split(" ");l=[];c=""
        for x in p:
            if len(c)+len(x)+1<=m:c+=x+" "
            else:l.append(c.strip());c=x+" "
        if c:l.append(c.strip())
        return l

    can.setFont("Helvetica-Bold",10)
    s=str(evento.servicios_interes or "").upper().replace(",","\n").split("\n")
    lf=[]
    for x in s:lf+=w(x.strip(),40)
    y=386
    for i,l in enumerate(lf):
        ya=y-i*10
        can.setFont("ZapfDingbats",7);can.drawString(230,ya,"n")
        can.setFont("Helvetica-Bold",10);can.drawString(240,ya,l)

    yc=y-len(lf)*10
    c=str(evento.comentarios or "").upper().replace(",","\n").split("\n")
    cf=[]
    for x in c:cf+=w(x.strip(),40)
    for i,l in enumerate(cf):
        can.drawString(240,yc-i*10,("NOTA: "+l) if i==0 else l)




    can.setFont("Helvetica-Bold", 12)
    can.drawString(240, 320, str(evento.nombre_cliente or "").upper())
    can.drawString(240, 287, str(evento.whatsapp or "").upper())

    can.setFillColor(colors.black)
    can.drawString(153, 215, f"${evento.total if evento.total is not None else 0}")
    can.drawString(278, 215, f"${evento.anticipo if evento.anticipo is not None else 0}")
    can.drawString(403, 215, f"${evento.restan if evento.restan is not None else 0}")
    can.save()

    packet.seek(0)
    overlay = PdfReader(packet)
    url = "https://drive.google.com/uc?export=download&id=1Y-WP09PuwrkBI9qWLKmiS1EsKjesu_aa"
    plantilla = PdfReader(BytesIO(requests.get(url).content))

    salida = PdfWriter()
    pagina = plantilla.pages[0]
    pagina.merge_page(overlay.pages[0])
    salida.add_page(pagina)

    output = BytesIO()
    salida.write(output)
    output.seek(0)
    return output

### GLITTER ###

def generar_contrato_glitter(evento):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFont("Helvetica-Bold", 22)
    can.setFillColor(colors.black)
    can.drawString(430, 550, str(evento.folio_manual or ""))

    mes = MESES_ES[evento.fecha_evento.strftime("%B")]
    fecha_larga = f"{evento.fecha_evento.day} DE {mes} DE {evento.fecha_evento.year}"
    can.setFont("Helvetica-Bold", 12)
    can.drawString(230, 492, fecha_larga)

    texto_horario = (
        f"{str(evento.hora_inicio or '').upper()} - "
        f"{str(evento.hora_termino or '').upper()} "
        f"({str(evento.cantidad_horas or '')} HORAS)"
    )
    can.drawString(230, 445, texto_horario)
    
    can.setFont("Helvetica-Bold", 10)
    can.drawString(230, 395, (str(evento.nombre_salon or "") ).upper())
    def wrap40(t):
        p=t.split(" ");l=[];c=""
        for w in p:
            if len(c)+len(w)+1<=40:c+=w+" "
            else:l.append(c.strip());c=w+" "
        if c:l.append(c.strip())
        return l

    texto=f"{(evento.municipio or '').upper()} - {(evento.direccion or '').upper()}"
    lineas=wrap40(texto)
    y=380
    for i,l in enumerate(lineas):
        can.drawString(230,y-i*10,l)

    def wrap_text_by_space(texto, max_chars=40):
        palabras = texto.split(" ")
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_chars:
                linea_actual += palabra + " "
            else:
                lineas.append(linea_actual.strip())
                linea_actual = palabra + " "
        if linea_actual:
            lineas.append(linea_actual.strip())
        return lineas

    # Servicios con viñeta
    servicios = str(evento.servicios_interes or "").upper().replace(",", "\n").split("\n")
    y = 325
    salto = 10
    lineas_totales = []

    for servicio in servicios:
        lineas = wrap_text_by_space(servicio.strip(), 40)
        for l in lineas:
            can.setFont("ZapfDingbats", 6)
            can.drawString(220, y, "n")
            can.setFont("Helvetica-Bold", 10)
            can.drawString(230, y, l)
            y -= salto
        lineas_totales.extend(lineas)

    # Comentarios sin viñeta, pero con salto automático
    comentarios = str(evento.comentarios or "").upper().replace(",", "\n").split("\n")
    for comentario in comentarios:
        lineas = wrap_text_by_space(comentario.strip(), 40)
        for i, l in enumerate(lineas):
            texto = f"NOTA: {l}" if i == 0 else l
            can.setFont("Helvetica-Bold", 10)
            can.drawString(230, y, texto)
            y -= salto

    

    can.setFont("Helvetica-Bold", 12)
    can.drawString(230, 267, str(evento.nombre_cliente or "").upper())
    can.drawString(230, 247, str(evento.whatsapp or "").upper())
    can.drawString(123, 163, f"${evento.total if evento.total is not None else 0}")
    can.drawString(248, 163, f"${evento.anticipo if evento.anticipo is not None else 0}")
    can.drawString(373, 163, f"${evento.restan if evento.restan is not None else 0}")
    can.save()

    packet.seek(0)
    overlay = PdfReader(packet)
    url = "https://drive.google.com/uc?export=download&id=17njLY9vWvS2Vhv7Q0l1aXbcY94l5p_Sh"
    plantilla = PdfReader(BytesIO(requests.get(url).content))

    salida = PdfWriter()
    pagina = plantilla.pages[0]
    pagina.merge_page(overlay.pages[0])
    salida.add_page(pagina)

    output = BytesIO()
    salida.write(output)
    output.seek(0)
    return output

# ============================================================
# Convertir PDF a PNG
# ============================================================
def convertir_pdf_a_png(pdf_bytes, nombre_archivo):
    pdf_bytes.seek(0)
    pdf_document = fitz.open(stream=pdf_bytes.read(), filetype="pdf")
    page = pdf_document.load_page(0)
    pix = page.get_pixmap(dpi=300)
    png_bytes = BytesIO(pix.tobytes("png"))
    png_bytes.seek(0)
    nombre_png = nombre_archivo.replace(".pdf", ".png")
    return png_bytes, nombre_png

# ============================================================
# HTML del formulario
# ============================================================
html_formulario = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Generar Contrato</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">

  <style>
    body {
      min-height: 100vh;
      font-family: 'Inter', sans-serif;
      background: linear-gradient(45deg, #3b82f6, #9333ea, #ec4899, #22c55e);
      background-size: 400% 400%;
      animation: gradientBG 10s ease infinite;
    }
    @keyframes gradientBG {
      0% {background-position: 0% 50%;}
      50% {background-position: 100% 50%;}
      100% {background-position: 0% 50%;}
    }
  </style>

</head>
<body>

<nav class="w-full bg-white bg-opacity-20 backdrop-blur-lg shadow-lg py-4 px-6 flex justify-between items-center">
  <h1 class="text-white text-xl font-semibold drop-shadow">Sistema de Contratos</h1>
  <a href="{{ url_for('home') }}" 
     class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg shadow">
     ⬅️ Inicio
  </a>
</nav>

<div class="flex justify-center items-center mt-10">
  <div class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-lg card">
    <h2 class="text-3xl font-bold text-center text-indigo-600 mb-6">📝 Generar Contrato</h2>

    <form id="contrato-form" class="space-y-4">
      <div>
        <label class="font-semibold text-gray-700">Folio Manual:</label>
        <input type="text" name="folio_manual" required class="w-full mt-2 p-2 border rounded-lg focus:ring-2 focus:ring-indigo-400">
      </div>

      <div>
        <label class="font-semibold text-gray-700">Tipo de Evento:</label>
        <select name="tipo_evento" required class="w-full mt-2 p-2 border rounded-lg focus:ring-2 focus:ring-indigo-400">
          <option value="">Selecciona...</option>
          <option value="pintacaritas">🎨 Pintacaritas</option>
          <option value="glitter">✨ Glitter</option>
        </select>
      </div>

      <div>
        <label class="font-semibold text-gray-700">Formato:</label>
        <select name="formato" required class="w-full mt-2 p-2 border rounded-lg focus:ring-2 focus:ring-indigo-400">
          <option value="png">🖼️ PNG</option>
          <option value="pdf">📄 PDF</option>
        </select>
      </div>

      <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition shadow-md">
        Generar Contrato
      </button>
    </form>

    {% if mensaje %}
      <p class="mt-4 text-center text-red-600 font-semibold">{{ mensaje }}</p>
    {% endif %}

    <div id="preview-container" class="text-center hidden">
      <h2 class="text-lg font-semibold text-gray-700 mb-3">Vista Previa:</h2>
      <img id="preview" class="max-w-full rounded-lg shadow-lg">

      <div class="mt-4">
        <a id="download-btn" href="#" download class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg hidden">
          📥 Descargar
        </a>
      </div>
    </div>
  </div>
</div>

<script>
document.getElementById('contrato-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const formato = formData.get('formato');
  const previewContainer = document.getElementById('preview-container');
  const preview = document.getElementById('preview');
  const downloadBtn = document.getElementById('download-btn');

  previewContainer.classList.add('hidden');
  downloadBtn.classList.add('hidden');

  const response = await fetch('/generar-contrato', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    alert('⚠️ Error al generar el contrato.');
    return;
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);

 if (formato === 'png') {

    // Leer nombre desde los headers
    const disposition = response.headers.get("Content-Disposition");
    let filename = "contrato.png";

    if (disposition && disposition.includes("filename=")) {
      filename = disposition.split("filename=")[1].replace(/"/g, "");
    }

    // Mostrar vista previa
    preview.src = url;
    previewContainer.classList.remove('hidden');

    // Botón de descarga con nombre correcto
    downloadBtn.href = url;
    downloadBtn.download = filename;
    downloadBtn.classList.remove('hidden');

  } 
  // ==========================
  // PDF
  // ==========================
  else {

    const disposition = response.headers.get("Content-Disposition");
    let filename = "contrato.pdf";

    if (disposition && disposition.includes("filename=")) {
      filename = disposition.split("filename=")[1].replace(/"/g, "");
    }

    // Forzar descarga con el nombre real
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
});
</script>

</body>
</html>
"""

# ============================================================
# Ruta principal
# ============================================================
@generar_contrato_bp.route("/generar-contrato", methods=["GET", "POST"])
def generar_contrato():
    mensaje = None
    if request.method == "POST":
        folio_manual = request.form.get("folio_manual").strip().upper()
        tipo_evento = request.form.get("tipo_evento")
        formato = request.form.get("formato")

        evento = Evento.query.filter_by(folio_manual=folio_manual).first()
        if not evento:
            mensaje = f"❌ No se encontró el folio {folio_manual}"
        else:
            try:
                # Generar contrato según tipo
                output_pdf = generar_contrato_pintacaritas(evento) if tipo_evento=="pintacaritas" else generar_contrato_glitter(evento)

                # Nombre dinámico
                dia = evento.fecha_evento.day
                mes_es = MESES_ES[evento.fecha_evento.strftime("%B")]
                nombre_cliente = quitar_acentos((evento.nombre_cliente or "").replace(" ", "_").upper())
                nombre_final = f"{folio_manual}_{dia}_{mes_es}_{nombre_cliente}.pdf"

                # Enviar archivo
                if formato == "pdf":
                    return send_file(output_pdf, as_attachment=True, download_name=nombre_final, mimetype="application/pdf")
                else:
                    png_bytes, nombre_png = convertir_pdf_a_png(output_pdf, nombre_final)
                    return send_file(png_bytes, as_attachment=True, download_name=nombre_png, mimetype="image/png")
            except Exception as e:
                mensaje = f"⚠️ Error: {str(e)}"

    return render_template_string(html_formulario, mensaje=mensaje)
