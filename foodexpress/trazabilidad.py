from datetime import datetime


def ahora():
    # Marca de tiempo en formato ISO, para responder "cuando"
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


# ---------- PARTE 1: TRAZABILIDAD ----------
# Un log sin contexto no sirve; uno util responde las preguntas clave.
print("=== LOG MALO ===")
print("ERROR LOGIN")

print("\n=== LOG UTIL ===")
print(f"{ahora()} user=cliente17 ip=192.168.10.25 action=LOGIN result=FAILED reason=INVALID_CREDENTIALS")
print("-> Responde: cuando, quien, desde donde, que paso y con que resultado")

# ---------- PARTE 2: RESPONSABILIDAD ----------
# Con una cuenta compartida no se puede atribuir la accion a una persona.
print("\n=== CUENTA COMPARTIDA ===")
conocen_la_clave = ["maria", "luis", "pedro"]
print(f"{ahora()} user=admin ip=192.168.1.20 action=REEMBOLSO pedido=1042 monto=200 result=OK")
print("Quien fue? Lo pudo hacer cualquiera de:", conocen_la_clave)

# Con cuentas individuales, cada accion apunta a una sola persona.
print("\n=== CUENTAS INDIVIDUALES ===")
print(f"{ahora()} user=maria.gerente ip=192.168.1.20 action=REEMBOLSO pedido=1042 monto=200 result=OK")
print("Quien fue? -> maria.gerente (una persona identificable)")
