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
    :root {
      --carbon: #19120f;
      --carbon-alto: #211813;
      --papel: #f3e9dc;
      --papel-tenue: #c9bba8;
      --coral: #ff4d2e;
      --coral-fuerte: #ff6a3d;
    }

    * { box-sizing: border-box; }

    html, body { margin: 0; }

    body {
      font-family: -apple-system, "Segoe UI", system-ui, Roboto, Arial, sans-serif;
      background: var(--carbon);
      color: var(--papel);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .franja {
      padding: 28px 48px;
      border-bottom: 1px solid rgba(243,233,220,.08);
    }

    .marca {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--papel);
      opacity: 0;
      animation: subir 200ms ease-out forwards;
    }

    .marca span { color: var(--coral); }

    main {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 56px 48px 80px;
      max-width: 760px;
    }

    h1 {
      font-size: clamp(34px, 6vw, 56px);
      font-weight: 700;
      line-height: 1.05;
      letter-spacing: -0.03em;
      color: var(--papel);
      margin: 0 0 20px;
      opacity: 0;
      transform: translateY(14px);
      animation: subir 260ms cubic-bezier(.23,1,.32,1) 40ms forwards;
    }

    .cuerpo {
      font-size: 19px;
      line-height: 1.55;
      color: var(--papel-tenue);
      margin: 0 0 36px;
      max-width: 520px;
      opacity: 0;
      transform: translateY(12px);
      animation: subir 260ms cubic-bezier(.23,1,.32,1) 90ms forwards;
    }

    .cuerpo strong { color: var(--papel); font-weight: 700; }

    .cifra {
      font-size: clamp(44px, 9vw, 88px);
      font-weight: 700;
      letter-spacing: -0.04em;
      color: var(--coral);
      line-height: 1;
      margin: 0 0 36px;
      opacity: 0;
      transform: translateY(12px);
      animation: subir 260ms cubic-bezier(.23,1,.32,1) 90ms forwards;
    }

    .acciones {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      opacity: 0;
      transform: translateY(12px);
      animation: subir 260ms cubic-bezier(.23,1,.32,1) 140ms forwards;
    }

    .boton {
      background: var(--coral);
      color: var(--carbon);
      text-decoration: none;
      font-size: 18px;
      font-weight: 700;
      border: 0;
      cursor: pointer;
      padding: 16px 30px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      transition: transform 140ms cubic-bezier(.23,1,.32,1), background 140ms ease-out;
    }

    .boton:hover { background: var(--coral-fuerte); }
    .boton:active { transform: scale(.97); }

    .boton.fantasma {
      background: transparent;
      color: var(--papel);
      box-shadow: inset 0 0 0 1px rgba(243,233,220,.3);
    }

    .boton.fantasma:hover { box-shadow: inset 0 0 0 1px rgba(243,233,220,.6); background: rgba(243,233,220,.04); }

    .boton:focus-visible, a:focus-visible, button:focus-visible, input:focus-visible {
      outline: 2px solid var(--coral);
      outline-offset: 3px;
    }

    form { margin: 0; }

    @keyframes subir {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; opacity: 1 !important; transform: none !important; transition: none !important; }
    }

    @media (max-width: 560px) {
      .franja, main { padding-left: 24px; padding-right: 24px; }
    }
  </style>
</head>
<body>
  <div class="franja"><div class="marca">food<span>express</span></div></div>
  {% if vista == "inicio" %}
    <main>
      <h1>Pide. Paga.<br>Se resuelve al vuelo.</h1>
      <p class="cuerpo">Demo de FoodExpress para el video de seguridad. Tres rutas, tres fallas distintas.</p>
      <div class="acciones">
        <a class="boton" href="/login/1">Entrar como cliente 1</a>
        <a class="boton fantasma" href="/carrito">Carrito</a>
        <a class="boton fantasma" href="/reporte/10">Reporte</a>
      </div>
    </main>
  {% elif vista == "login" %}
    <main>
      <h1>Sesion activa</h1>
      <p class="cuerpo">Identidad establecida como cliente <strong>{{ cliente_id }}</strong>, sin contrasena.</p>
      <div class="acciones"><a class="boton" href="/">Volver al inicio</a></div>
    </main>
  {% elif vista == "carrito" %}
    <main>
      <h1>Tu carrito</h1>
      <p class="cuerpo">Pizza &middot; una unidad.</p>
      <div class="cifra">$12.50</div>
      <form method="post" action="/comprar" class="acciones">
        <input type="hidden" name="producto" value="Pizza">
        <input type="hidden" name="precio" value="12.50">
        <button class="boton" type="submit">Comprar</button>
      </form>
    </main>
  {% elif vista == "comprado" %}
    <main>
      <h1>Pedido registrado</h1>
      <p class="cuerpo">Monto cobrado por el servidor:</p>
      <div class="cifra">${{ precio }}</div>
      <div class="acciones"><a class="boton" href="/">Volver al inicio</a></div>
    </main>
  {% elif vista == "reporte" %}
    <main>
      <h1>Fibonacci({{ n }})</h1>
      <div class="cifra">{{ resultado }}</div>
      <div class="acciones"><a class="boton" href="/">Volver al inicio</a></div>
    </main>
  {% elif vista == "pedido" %}
    <main>
      <h1>Pedido confirmado</h1>
      <p class="cuerpo">Producto registrado: <strong>{{ producto }}</strong>.</p>
      <div class="acciones"><a class="boton" href="/">Volver al inicio</a></div>
    </main>
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
