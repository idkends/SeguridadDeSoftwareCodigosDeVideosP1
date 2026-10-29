from flask import Flask, render_template_string

# Flask sirve automaticamente la carpeta "static" en la ruta /static/...
app = Flask(__name__, static_folder="static")

# Plantilla unica (HTML + CSS) usada por todas las paginas
PLANTILLA = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FoodExpress</title>
  <style>
    body { font-family: Arial, sans-serif; background: #fff4e6; margin: 0;
           display: flex; flex-direction: column; align-items: center; padding: 40px 16px; }
    h1 { color: #e8590c; font-size: 48px; margin-bottom: 4px; }
    p { color: #495057; font-size: 18px; }
    .botones { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-top: 24px; }
    .boton { background: #e8590c; color: #fff; text-decoration: none; font-size: 20px;
             padding: 18px 36px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,.15); }
    .boton:hover { background: #d9480f; }
    .tarjeta { background: #fff; padding: 32px 48px; border-radius: 16px;
               box-shadow: 0 4px 12px rgba(0,0,0,.1); text-align: center; }
  </style>
</head>
<body>
  <h1>FoodExpress</h1>
  {% if producto %}
    <div class="tarjeta">
      <p>&#10003; Pedido de <strong>{{ producto }}</strong> registrado.</p>
      <p>Tu repartidor va en camino.</p>
      <a class="boton" href="/">Volver al inicio</a>
    </div>
  {% else %}
    <p>Elige tu comida favorita y haz tu pedido.</p>
    <div class="botones">
      <a class="boton" href="/pedido/Pizza">Pizza</a>
      <a class="boton" href="/pedido/Hamburguesa">Hamburguesa</a>
      <a class="boton" href="/pedido/Ensalada">Ensalada</a>
    </div>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def inicio():
    # Pagina principal con los tres botones de productos
    return render_template_string(PLANTILLA, producto=None)


@app.route("/pedido/<producto>")
def pedido(producto):
    # Muestra la confirmacion del pedido (Jinja escapa el texto automaticamente)
    return render_template_string(PLANTILLA, producto=producto)


if __name__ == "__main__":
    # Solo accesible desde esta computadora (localhost)
    app.run(host="127.0.0.1", port=5000)
