import sqlite3
from flask import Flask, request

app = Flask(__name__)

MODO_SEGURO = True   # False = vulnerable | True = con el control aplicado

# Base de datos en memoria con datos ficticios
db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE usuarios (usuario TEXT, clave TEXT)")
db.execute("INSERT INTO usuarios VALUES ('admin', 'Cl4ve-Larga-2026')")
db.execute("CREATE TABLE clientes (nombre TEXT, correo TEXT)")
db.execute("INSERT INTO clientes VALUES ('Ana Prueba', 'ana@ejemplo.com')")
db.execute("INSERT INTO clientes VALUES ('Luis Prueba', 'luis@ejemplo.com')")

ESTILO = """<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { --carbon:#19120f; --papel:#f3e9dc; --papel-tenue:#c9bba8; --coral:#ff4d2e; --coral-fuerte:#ff6a3d; }
  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body { font-family: -apple-system, "Segoe UI", system-ui, Roboto, Arial, sans-serif;
         background: var(--carbon); color: var(--papel); min-height: 100vh;
         display: flex; flex-direction: column; }
  .franja { padding: 28px 48px; border-bottom: 1px solid rgba(243,233,220,.08); }
  .marca { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; color: var(--papel);
           opacity: 0; animation: subir 200ms ease-out forwards; }
  .marca span { color: var(--coral); }
  main { flex: 1; display: flex; flex-direction: column; justify-content: center;
         padding: 56px 48px 80px; max-width: 420px; }
  h2 { font-size: clamp(30px, 5vw, 44px); font-weight: 700; letter-spacing: -0.03em; line-height: 1.05;
       color: var(--papel); margin: 0 0 32px; opacity: 0; transform: translateY(14px);
       animation: subir 260ms cubic-bezier(.23,1,.32,1) 40ms forwards; }
  form { opacity: 0; transform: translateY(12px); animation: subir 260ms cubic-bezier(.23,1,.32,1) 90ms forwards; }
  label { display: block; font-size: 15px; color: var(--papel-tenue); margin: 0 0 8px; font-weight: 600; }
  input { width: 100%; font-size: 18px; padding: 14px 16px; margin-bottom: 20px;
          border: 1px solid rgba(243,233,220,.2); border-radius: 4px; background: rgba(243,233,220,.05);
          color: var(--papel); transition: border-color 150ms ease-out, background 150ms ease-out; }
  input:focus-visible { outline: none; border-color: var(--coral); background: rgba(243,233,220,.08); }
  button { width: 100%; background: var(--coral); color: var(--carbon); font-size: 18px;
           font-weight: 700; border: 0; cursor: pointer; padding: 16px 30px; border-radius: 4px;
           transition: transform 140ms cubic-bezier(.23,1,.32,1), background 140ms ease-out; }
  button:hover { background: var(--coral-fuerte); }
  button:active { transform: scale(.97); }
  button:focus-visible, input:focus-visible { outline: 2px solid var(--coral); outline-offset: 3px; }
  .error { color: var(--coral-fuerte); font-size: 16px; font-weight: 600; margin-top: 20px; }
  .fila { display: flex; justify-content: space-between; gap: 16px; padding: 16px 0;
          border-bottom: 1px solid rgba(243,233,220,.1); font-size: 18px; color: var(--papel); }
  .fila:last-child { border-bottom: 0; }
  .fila span:last-child { color: var(--papel-tenue); }
  .lista { opacity: 0; transform: translateY(12px); animation: subir 260ms cubic-bezier(.23,1,.32,1) 90ms forwards; }
  @keyframes subir { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; opacity: 1 !important; transform: none !important; transition: none !important; }
  }
</style>"""

FORM = ESTILO + """<div class="franja"><div class="marca">food<span>express</span></div></div>
<main>
<h2>Panel de<br>administracion</h2>
<form method="post">
<label for="u">Usuario</label>
<input id="u" name="u" autocomplete="off">
<label for="p">Clave</label>
<input id="p" name="p" type="password">
<button>Entrar</button>
</form>
</main>"""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return FORM
    u = request.form["u"]
    p = request.form["p"]

    if MODO_SEGURO:
        # CONTROL: consulta parametrizada, la entrada nunca se mezcla con el SQL
        fila = db.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND clave=?", (u, p)
        ).fetchone()
    else:
        # VULNERABILIDAD: la entrada del usuario se pega dentro de la consulta
        consulta = f"SELECT * FROM usuarios WHERE usuario='{u}' AND clave='{p}'"
        fila = db.execute(consulta).fetchone()

    if fila:
        clientes = db.execute("SELECT nombre, correo FROM clientes").fetchall()
        filas = "".join(f'<div class="fila"><span>{n}</span><span>{c}</span></div>' for n, c in clientes)
        return (ESTILO + '<div class="franja"><div class="marca">food<span>express</span></div></div>'
                 '<main><h2>Clientes</h2><div class="lista">' + filas + "</div></main>")
    return FORM.replace("</main>", '<div class="error">Credenciales incorrectas</div></main>')

if __name__ == "__main__":
    app.run(port=5001)
