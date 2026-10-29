from flask import Flask, request

app = Flask(__name__)

# Estilo visual: fondo oscuro, acento verde, fuentes del sistema, texto grande,
# animaciones sutiles solo en hover/focus (respeta prefers-reduced-motion).
ESTILO = """<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { --carbon:#14181a; --papel:#f0f4f2; --papel-tenue:#b9c7c1; --verde:#2ecc71; --verde-fuerte:#4ee08a; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body { font-family: -apple-system, "Segoe UI", system-ui, Roboto, Arial, sans-serif;
         background: var(--carbon); color: var(--papel); min-height: 100vh;
         display: flex; flex-direction: column; font-size: 18px; }
  .franja { padding: 28px 48px; border-bottom: 1px solid rgba(240,244,242,.08); }
  .marca { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; color: var(--papel); }
  .marca span { color: var(--verde); }
  main { flex: 1; display: flex; flex-direction: column; justify-content: center;
         padding: 56px 48px 80px; max-width: 460px; }
  h2 { font-size: clamp(26px, 4.5vw, 38px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.15;
       color: var(--papel); margin: 0 0 32px; }
  form { display: block; }
  label { display: block; font-size: 16px; color: var(--papel-tenue); margin: 0 0 8px; font-weight: 600; }
  input { width: 100%; font-size: 18px; padding: 14px 16px; margin-bottom: 20px;
          border: 1px solid rgba(240,244,242,.2); border-radius: 4px; background: rgba(240,244,242,.05);
          color: var(--papel); transition: border-color 150ms ease-out, background 150ms ease-out; }
  input:hover { border-color: rgba(78,224,138,.5); }
  input:focus-visible { outline: none; border-color: var(--verde); background: rgba(240,244,242,.08); }
  button { width: 100%; background: var(--verde); color: var(--carbon); font-size: 18px;
           font-weight: 700; border: 0; cursor: pointer; padding: 16px 30px; border-radius: 4px;
           transition: transform 140ms cubic-bezier(.23,1,.32,1), background 140ms ease-out; }
  button:hover { background: var(--verde-fuerte); }
  button:active { transform: scale(.97); }
  button:focus-visible, input:focus-visible { outline: 2px solid var(--verde); outline-offset: 3px; }
  .ok { color: var(--verde-fuerte); font-size: 18px; font-weight: 700; margin-top: 20px; }
  .error { color: #ff6a6a; font-size: 18px; font-weight: 700; margin-top: 20px; }
  @media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
  }
</style>"""

ENCABEZADO = ESTILO + '<div class="franja"><div class="marca">food<span>express</span></div></div>'

# ---------- DEMO 1: credenciales por HTTP (snooping / sniffing) ----------
PAGINA_LOGIN = ENCABEZADO + """<main>
<h2>FoodExpress - Iniciar sesión (HTTP)</h2>
<form method="post">
<label for="u">Usuario</label>
<input id="u" name="u"><br><br>
<label for="p">Clave</label>
<input id="p" name="p" type="password"><br><br>
<button>Entrar</button></form>
</main>"""

@app.route("/login-http", methods=["GET", "POST"])
def login_http():
    if request.method == "POST":
        # Esto es lo que viaja por la red cuando se usa HTTP: texto legible
        print("Cuerpo tal como viaja por HTTP:", request.get_data(as_text=True))
        return ENCABEZADO + '<main><h2>Sesión iniciada</h2></main>'
    return PAGINA_LOGIN

# ---------- DEMO 2: replay attack ----------
TOKEN = "tok-1042-abc"
aprobaciones = 0
tokens_usados = set()

# VULNERABLE: acepta el mismo token todas las veces que llegue
@app.route("/aprobar/<token>")
def aprobar(token):
    global aprobaciones
    if token != TOKEN:
        return ENCABEZADO + '<main><div class="error">Token inválido</div></main>', 403
    aprobaciones += 1
    return ENCABEZADO + f'<main><p class="ok">Reembolso aprobado (pedido 1042). Aprobaciones con este token: {aprobaciones}</p></main>'

# CONTROL: el token es de un solo uso
@app.route("/aprobar-seguro/<token>")
def aprobar_seguro(token):
    if token != TOKEN:
        return ENCABEZADO + '<main><div class="error">Token inválido</div></main>', 403
    if token in tokens_usados:
        return ENCABEZADO + '<main><div class="error">Token ya usado: solicitud rechazada</div></main>', 409
    tokens_usados.add(token)
    return ENCABEZADO + '<main><p class="ok">Reembolso aprobado (pedido 1042). Token consumido.</p></main>'

if __name__ == "__main__":
    app.run(port=5002)
