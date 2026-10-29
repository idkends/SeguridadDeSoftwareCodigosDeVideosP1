# FoodExpress (demo de seguridad)

App ficticia de pedidos de comida, solo para un video de Seguridad de Software.
Corre unicamente en localhost y todos los datos son inventados.

## Como ejecutarla

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000

## Demo del video

Cada ruta tiene a proposito una falla de seguridad (solo para demostracion).

### Confidencialidad (control de acceso roto)

1. Abre http://127.0.0.1:5000/login/1 (sesion como cliente 1).
2. Abre http://127.0.0.1:5000/api/pedidos/1: devuelve tu pedido.
3. Cambia el 1 por 2 en la URL: el servidor entrega el pedido de otro cliente.

### Integridad (precio manipulable)

1. Abre http://127.0.0.1:5000/carrito (Pizza, $12.50).
2. Clic derecho > Inspeccionar (DevTools) y edita `value="12.50"` del campo oculto `precio` a `0.01`.
3. Pulsa "Comprar": la app muestra "Pedido registrado por $0.01".

### Disponibilidad (denegacion de servicio)

1. Abre http://127.0.0.1:5000/reporte/40 (tarda mucho: Fibonacci recursivo).
2. Mientras carga, abre http://127.0.0.1:5000/ en otra pestana: no responde hasta que termina el calculo (`threaded=False`).

### Autenticidad (HMAC)

```powershell
python autenticidad.py
```

Muestra que un hash solo no prueba el origen (`True`), pero una firma HMAC sin la clave secreta no es valida (`False`).

### Exposicion de archivos (demo anterior)

1. Abre la app en http://127.0.0.1:5000 y haz un pedido: todo funciona bien.
2. Visita http://127.0.0.1:5000/static/respaldo_clientes.csv: el archivo se descarga con datos de clientes (el problema de seguridad).
3. Mueve `static/respaldo_clientes.csv` a la carpeta `privado/`.
4. Recarga la URL del paso 2: ahora devuelve error 404.

## Video 3: trazabilidad y no repudio

Ejecuta `python trazabilidad.py` para ver logs malos vs. utiles y cuentas compartidas vs. individuales.
Los comandos de firma digital (OpenSSL) estan en `comandos_firma.txt`.

## Video 4: amenaza, vulnerabilidad, riesgo y ataque

Demo independiente en `demo_riesgo.py` (puerto 5001): un panel de administracion de
FoodExpress con inyeccion SQL en el login.

1. Ejecuta:

   ```powershell
   python demo_riesgo.py
   ```

   Abre http://127.0.0.1:5001

2. Prueba una clave incorrecta: usuario `admin`, clave `clave-equivocada`.
   El panel responde "Credenciales incorrectas".

3. Prueba el ataque: usuario `admin' --`, clave (cualquier valor).
   La comilla cierra la cadena SQL y `--` comenta el resto de la consulta, de modo
   que la condicion de la clave nunca se evalua. El panel entra sin conocer la
   clave real y muestra los clientes.

4. Abre `demo_riesgo.py` y cambia `MODO_SEGURO = False` por `MODO_SEGURO = True`
   (es la unica linea que se edita a mano).

5. Reinicia la app (`Ctrl+C` y `python demo_riesgo.py` de nuevo) y repite el
   paso 3 con el mismo usuario `admin' --`: ahora responde "Credenciales
   incorrectas", porque la consulta parametrizada (`?`) nunca mezcla la entrada
   con el SQL. El usuario `admin` con la clave real `Cl4ve-Larga-2026` sigue
   entrando con normalidad.

## Video 5: ataques más comunes

Demo independiente en `demo_ataques.py` (puerto 5002): credenciales que viajan
por HTTP y un ataque de repetición (replay attack) sobre un enlace de
aprobación de reembolso.

1. Ejecuta:

   ```powershell
   python demo_ataques.py
   ```

   Abre http://127.0.0.1:5002

2. **Snooping/sniffing de credenciales (HTTP sin cifrar).** Abre
   http://127.0.0.1:5002/login-http, llena usuario y clave, y pulsa "Entrar".
   En la terminal donde corre `demo_ataques.py` aparece la línea
   `Cuerpo tal como viaja por HTTP: u=...&p=...`: así viaja el formulario por
   la red cuando no hay HTTPS, en texto legible para cualquiera que esté
   escuchando el tráfico.

3. **Replay attack (vulnerable).** Abre
   http://127.0.0.1:5002/aprobar/tok-1042-abc y recarga la página varias
   veces: el contador de "Aprobaciones con este token" sube (1, 2, 3...). El
   mismo enlace, capturado una sola vez, se puede reutilizar para aprobar el
   reembolso tantas veces como se quiera.

4. **Control: token de un solo uso.** Abre
   http://127.0.0.1:5002/aprobar-seguro/tok-1042-abc: la primera vez aprueba
   el reembolso. Recarga la misma URL: ahora responde 409 "Token ya usado:
   solicitud rechazada", porque el token ya se marcó como consumido.

5. **Reiniciar el contador de aprobaciones.** El contador y la lista de
   tokens usados viven en memoria. Para reiniciarlos, detén el servidor con
   `Ctrl + C` en la terminal y vuelve a ejecutar `python demo_ataques.py`.

6. **Ataque por diccionario a contraseñas.** Ejecuta:

   ```powershell
   python ataque_contrasenas.py
   ```

   Muestra que la clave débil `admin123` se encuentra en el diccionario
   (`ENCONTRADA: admin123 ...`), mientras que la clave larga y única
   `Cl4ve-Larga-Unica-2026!` no aparece (`No está en el diccionario`). En la
   práctica, las contraseñas se guardan con bcrypt o Argon2 y sal, nunca con
   SHA-256 simple.

## Video 6: tipos de controles

Demo de controles preventivo, detectivo y correctivo sobre un login ficticio
(`demo_controles.py`, puerto 5003, solo localhost).

1. **Ejecutar la demo.**

   ```powershell
   python demo_controles.py
   ```

   Abre http://127.0.0.1:5003/ (usuario `admin`, clave correcta
   `Cl4ve-Larga-2026`).

2. **Sin controles.** Abre
   http://127.0.0.1:5003/modo?preventivo=0&detectivo=0 e intenta 6 veces con
   una clave incorrecta: siempre "Credenciales incorrectas", sin líneas en la
   terminal y sin `auditoria.log`.

3. **Control detectivo.** Abre
   http://127.0.0.1:5003/modo?preventivo=0&detectivo=1 y repite 6 intentos
   fallidos: la terminal imprime cada intento y, desde el quinto, una línea
   `ALERTA`. El ataque no se frena: el sexto intento sigue respondiendo
   "Credenciales incorrectas".

4. **Control preventivo.** Abre
   http://127.0.0.1:5003/modo?preventivo=1&detectivo=1, falla 5 veces y luego
   entra con la clave correcta: responde "Demasiados intentos. Cuenta
   bloqueada temporalmente." (60 s) y el log registra `result=BLOQUEADO`.

5. **Control correctivo.** Abre
   http://127.0.0.1:5003/modo?preventivo=0&detectivo=0, inicia sesión con la
   clave correcta y comprueba que `/panel` muestra "Sesión activa". En otra
   pestaña abre http://127.0.0.1:5003/revocar/admin; al recargar `/panel`
   sale "Sesión no válida o revocada". `Cl4ve-Larga-2026` ya no entra y
   `Nueva-Clave-2026!` sí.

6. **Ver el registro de auditoría.** Con el modo detectivo activo se crea
   `auditoria.log` junto al script:

   ```powershell
   Get-Content auditoria.log
   Get-Content auditoria.log -Wait   # seguirlo en vivo
   ```

7. **Reiniciar el estado.** Las sesiones, los fallos, los bloqueos y el cambio
   de clave viven en memoria. Detén el servidor con `Ctrl + C`, borra
   `auditoria.log` (`Remove-Item auditoria.log`) y vuelve a ejecutar
   `python demo_controles.py`.
