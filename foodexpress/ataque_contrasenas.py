import hashlib
import time

def sha256(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

# Diccionario pequeño de contraseñas comunes (solo para la demo)
DICCIONARIO = ["123456", "password", "qwerty", "admin", "letmein",
               "admin123", "iloveyou", "welcome", "abc123", "monkey"]

def ataque_diccionario(hash_objetivo):
    inicio = time.perf_counter()
    for intentos, palabra in enumerate(DICCIONARIO, start=1):
        if sha256(palabra) == hash_objetivo:
            t = time.perf_counter() - inicio
            return f"ENCONTRADA: {palabra} ({intentos} intentos, {t:.6f} s)"
    return "No está en el diccionario"

# En la realidad: guardar contraseñas con bcrypt o Argon2 y sal, no SHA-256 simple
print("Cuenta 1 (clave débil):", ataque_diccionario(sha256("admin123")))
print("Cuenta 2 (clave larga y única):", ataque_diccionario(sha256("Cl4ve-Larga-Unica-2026!")))
