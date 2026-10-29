import secrets
import time
from datetime import datetime
from flask import Flask, request, redirect, make_response

app = Flask(__name__)

# Interruptores de la demo (también se cambian en vivo con la ruta /modo)
PREVENTIVO = False   # límite de intentos y bloqueo temporal
DETECTIVO = False    # registro de auditoría y alerta

MAX_INTENTOS = 5
BLOQUEO_SEG = 60

USUARIOS = {"admin": "Cl4ve-Larga-2026"}   # datos ficticios
SESIONES = {}          # sid -> usuario
FALLOS = {}            # usuario -> cantidad de fallos seguidos
BLOQUEADO_HASTA = {}   # usuario -> instante en que termina el bloqueo

ESTILO = """<style>
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0; min-height: 100vh; display: grid; place-items: center;
  background: #0b0f0c; color: #f2f7f3;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 20px; line-height: 1.5;
}
main {
  width: min(92vw, 520px); padding: 40px;
  background: #141b16; border: 1px solid #2a3a2f; border-radius: 14px;
}
h2 { margin: 0 0 28px; font-size: 28px; color: #3ddc84; }
label { display: block; margin-bottom: 20px; font-weight: 600; }
input {
  display: block; width: 100%; margin-top: 8px; padding: 12px 14px;
  font: inherit; color: #f2f7f3; background: #0b0f0c;
  border: 2px solid #3a4d3f; border-radius: 8px; outline: none;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}
input:hover { border-color: #5f7d67; }
input:focus { border-color: #3ddc84; box-shadow: 0 0 0 3px rgba(61, 220, 132, .35); }
button {
  width: 100%; padding: 12px 16px; font: inherit; font-weight: 700;
  color: #04140a; background: #3ddc84; border: 2px solid #3ddc84;
  border-radius: 8px; cursor: pointer;
  transition: background-color 150ms ease, box-shadow 150ms ease;
}
button:hover { background: #7bf0ae; }
button:focus-visible { outline: none; box-shadow: 0 0 0 3px rgba(61, 220, 132, .5); }
.msg { margin: 24px 0 0; padding: 12px 14px; border-radius: 8px; font-weight: 600; }
.error { color: #ffb4a8; background: #2e1511; border: 1px solid #ff6b57; }
.aviso { color: #ffe08a; background: #2e2610; border: 1px solid #f5c542; }
.ok { color: #04140a; background: #3ddc84; display: inline-block; padding: 8px 16px; border-radius: 8px; font-weight: 700; margin: 0; }
@media (prefers-reduced-motion: reduce) {
  input, button { transition: none; }
}
</style>"""


def pagina(cuerpo):
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>FoodExpress</title>' + ESTILO + '</head><body><main>'
            + cuerpo + '</main></body></html>')


FORM_HTML = """<h2>FoodExpress - Panel de administración</h2>
<form method="post" action="/">
<label>Usuario: <input name="u" autocomplete="off"></label>
<label>Clave: <input name="p" type="password"></label>
<button>Entrar</button></form>"""


def formulario(mensaje="", clase="error"):
    extra = f'<p class="msg {clase}">{mensaje}</p>' if mensaje else ""
    return pagina(FORM_HTML + extra)


def registrar(usuario, ip, accion, resultado):
    # CONTROL DETECTIVO: registro de auditoría (solo si está activado)
    if not DETECTIVO:
        return
    linea = (f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} "
             f"user={usuario} ip={ip} action={accion} result={resultado}")
    print(linea)
    with open("auditoria.log", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def alerta(usuario, ip, n):
    texto = f"ALERTA: {n} intentos fallidos seguidos para user={usuario} desde ip={ip}"
    print(texto)
    with open("auditoria.log", "a", encoding="utf-8") as f:
        f.write(texto + "\n")


@app.route("/modo")
def modo():
    # Solo para la demo: activa o desactiva los controles sin reiniciar
    global PREVENTIVO, DETECTIVO
    PREVENTIVO = request.args.get("preventivo") == "1"
    DETECTIVO = request.args.get("detectivo") == "1"
    FALLOS.clear()
    BLOQUEADO_HASTA.clear()
    return pagina(f'<h2>Modo de la demo</h2><p class="msg aviso">'
                  f'Preventivo: {PREVENTIVO} | Detectivo: {DETECTIVO}</p>')


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return formulario()
    u = request.form.get("u", "")
    p = request.form.get("p", "")
    ip = request.remote_addr
    ahora = time.time()

    # CONTROL PREVENTIVO: si la cuenta está bloqueada, ni se comprueba la clave
    if PREVENTIVO and BLOQUEADO_HASTA.get(u, 0) > ahora:
        registrar(u, ip, "LOGIN", "BLOQUEADO")
        return formulario("Demasiados intentos. Cuenta bloqueada temporalmente.", "aviso")

    if u in USUARIOS and USUARIOS[u] == p:
        FALLOS[u] = 0
        sid = secrets.token_hex(8)
        SESIONES[sid] = u
        registrar(u, ip, "LOGIN", "OK")
        resp = make_response(redirect("/panel"))
        resp.set_cookie("sid", sid)
        return resp

    FALLOS[u] = FALLOS.get(u, 0) + 1
    registrar(u, ip, "LOGIN", "FALLIDO")

    # CONTROL DETECTIVO: alerta al llegar al umbral (avisa, pero NO frena el ataque)
    if DETECTIVO and FALLOS[u] >= MAX_INTENTOS:
        alerta(u, ip, FALLOS[u])

    # CONTROL PREVENTIVO: bloqueo temporal al llegar al umbral
    if PREVENTIVO and FALLOS[u] >= MAX_INTENTOS:
        BLOQUEADO_HASTA[u] = ahora + BLOQUEO_SEG
        FALLOS[u] = 0

    return formulario("Credenciales incorrectas")


@app.route("/panel")
def panel():
    usuario = SESIONES.get(request.cookies.get("sid"))
    if not usuario:
        return formulario("Sesión no válida o revocada. Inicia sesión de nuevo.", "aviso")
    return pagina(f'<h2>Panel de {usuario}</h2><p class="ok">Sesión activa.</p>')


@app.route("/revocar/<usuario>")
def revocar(usuario):
    # CONTROL CORRECTIVO: cierra las sesiones y cambia la credencial.
    # En un sistema real esta acción exigiría un administrador autorizado.
    if usuario not in USUARIOS:
        return "Usuario inexistente", 404
    for sid in [s for s, u in SESIONES.items() if u == usuario]:
        del SESIONES[sid]
    USUARIOS[usuario] = "Nueva-Clave-2026!"
    registrar(usuario, request.remote_addr, "REVOCAR_SESIONES", "OK")
    return pagina(f'<h2>Control correctivo</h2><p class="msg aviso">'
                  f'Sesiones de {usuario} revocadas y credencial cambiada.</p>')


if __name__ == "__main__":
    app.run(port=5003)
