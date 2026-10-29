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
