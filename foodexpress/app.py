from flask import Flask, render_template_string, request, session, jsonify

# Flask sirve automaticamente la carpeta "static" en la ruta /static/...
app = Flask(__name__, static_folder="static")

# Clave fija y publica SOLO para la demo (en un sistema real seria secreta y aleatoria)
app.secret_key = "clave-de-demo-foodexpress"

# Datos 100% ficticios, guardados en memoria (sin base de datos)
PEDIDOS = {
    1: {"id": 1, "cliente_id": 1, "producto": "Pizza", "precio": 12.50, "direccion": "Calle Falsa 123"},
    2: {"id": 2, "cliente_id": 2, "producto": "Hamburguesa", "precio": 9.00, "direccion": "Avenida Imaginaria 456"},
    3: {"id": 3, "cliente_id": 3, "producto": "Ensalada", "precio": 7.25, "direccion": "Pasaje Inventado 789"},
}

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
    .boton { background: #e8590c; color: #fff; text-decoration: none; font-size: 20px; border: 0;
             cursor: pointer; padding: 18px 36px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,.15); }
    .boton:hover { background: #d9480f; }
    .tarjeta { background: #fff; padding: 32px 48px; border-radius: 16px;
               box-shadow: 0 4px 12px rgba(0,0,0,.1); text-align: center; }
  </style>
</head>
<body>
  <h1>FoodExpress</h1>
  {% if vista == "inicio" %}
    <p>Elige una opcion de la demo.</p>
    <div class="botones">
      <a class="boton" href="/login/1">Iniciar sesion (cliente 1)</a>
      <a class="boton" href="/carrito">Carrito</a>
      <a class="boton" href="/reporte/10">Reporte</a>
    </div>
  {% elif vista == "login" %}
    <div class="tarjeta">
      <p>Sesion iniciada como cliente <strong>{{ cliente_id }}</strong>.</p>
      <a class="boton" href="/">Volver al inicio</a>
    </div>
  {% elif vista == "carrito" %}
    <div class="tarjeta">
      <p>Tu carrito: <strong>Pizza</strong> - $12.50</p>
      <form method="post" action="/comprar">
        <input type="hidden" name="producto" value="Pizza">
        <input type="hidden" name="precio" value="12.50">
        <button class="boton" type="submit">Comprar</button>
      </form>
    </div>
  {% elif vista == "comprado" %}
    <div class="tarjeta">
      <p>Pedido registrado por ${{ precio }}</p>
      <a class="boton" href="/">Volver al inicio</a>
    </div>
  {% elif vista == "reporte" %}
    <div class="tarjeta">
      <p>Fibonacci({{ n }}) = <strong>{{ resultado }}</strong></p>
      <a class="boton" href="/">Volver al inicio</a>
    </div>
  {% elif vista == "pedido" %}
    <div class="tarjeta">
      <p>&#10003; Pedido de <strong>{{ producto }}</strong> registrado.</p>
      <a class="boton" href="/">Volver al inicio</a>
    </div>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def inicio():
    return render_template_string(PLANTILLA, vista="inicio")


@app.route("/pedido/<producto>")
def pedido(producto):
    # Muestra la confirmacion del pedido (Jinja escapa el texto automaticamente)
    return render_template_string(PLANTILLA, vista="pedido", producto=producto)


@app.route("/login/<int:cliente_id>")
def login(cliente_id):
    # FALLA (autenticacion): cualquiera elige su identidad sin contrasena.
    # Es solo para simular una sesion en la demo.
    session["cliente_id"] = cliente_id
    return render_template_string(PLANTILLA, vista="login", cliente_id=cliente_id)


@app.route("/api/pedidos/<int:id>")
def api_pedido(id):
    # FALLA INTENCIONAL - CONFIDENCIALIDAD: no se verifica que el pedido
    # pertenezca al cliente de la sesion (control de acceso roto / IDOR).
    # Cambiar el id en la URL expone pedidos de otros clientes.
    # Correccion: comparar PEDIDOS[id]["cliente_id"] con session["cliente_id"].
    pedido = PEDIDOS.get(id)
    if pedido is None:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify(pedido)


@app.route("/carrito")
def carrito():
    # Los campos ocultos "producto" y "precio" viajan en el navegador del cliente,
    # donde pueden ser editados con las DevTools antes de enviar el formulario.
    return render_template_string(PLANTILLA, vista="carrito")


@app.route("/comprar", methods=["POST"])
def comprar():
    # FALLA INTENCIONAL - INTEGRIDAD: se confia en el precio enviado por el
    # cliente, sin validarlo contra un catalogo del servidor.
    # Correccion: ignorar "precio" del formulario y consultar CATALOGO[producto].
    producto = request.form.get("producto", "Pizza")
    precio = request.form.get("precio", "0")

    nuevo_id = max(PEDIDOS) + 1
    PEDIDOS[nuevo_id] = {
        "id": nuevo_id,
        "cliente_id": session.get("cliente_id", 0),
        "producto": producto,
        "precio": precio,
        "direccion": "Calle Falsa 123",
    }
    return render_template_string(PLANTILLA, vista="comprado", precio=precio)


def fibonacci(n):
    # Recursivo sin memoria: crece exponencialmente (muy lento para n=40)
    return n if n < 2 else fibonacci(n - 1) + fibonacci(n - 2)


@app.route("/reporte/<int:n>")
def reporte(n):
    # FALLA INTENCIONAL - DISPONIBILIDAD: calculo costoso sin limite de n,
    # sin cache ni timeout. Con threaded=False, mientras dura la peticion
    # el servidor no atiende ninguna otra pagina.
    # Correccion: limitar n, usar memoizacion y/o ejecutar en segundo plano.
    return render_template_string(PLANTILLA, vista="reporte", n=n, resultado=fibonacci(n))


if __name__ == "__main__":
    # Solo accesible desde esta computadora (localhost).
    # threaded=False: una sola peticion a la vez, para que /reporte/40 bloquee todo.
    app.run(host="127.0.0.1", port=5000, threaded=False)
