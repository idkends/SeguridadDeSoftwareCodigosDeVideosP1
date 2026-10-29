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

1. Abre la app en http://127.0.0.1:5000 y haz un pedido: todo funciona bien.
2. Visita http://127.0.0.1:5000/static/respaldo_clientes.csv: el archivo se descarga con datos de clientes (el problema de seguridad).
3. Mueve `static/respaldo_clientes.csv` a la carpeta `privado/`.
4. Recarga la URL del paso 2: ahora devuelve error 404.
