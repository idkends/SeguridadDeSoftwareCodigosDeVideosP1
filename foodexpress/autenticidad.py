import hashlib, hmac

original = b"CUPON: 50% de descuento en pizzas"
falso    = b"CUPON: 100% de descuento en todo"

# Solo hash: el atacante publica su propio hash y la verificacion pasa
hash_publicado = hashlib.sha256(falso).hexdigest()
print("Hash coincide (integro):", hashlib.sha256(falso).hexdigest() == hash_publicado)

# HMAC: requiere la clave secreta de FoodExpress
clave = b"clave-secreta-foodexpress"
firma_real = hmac.new(clave, original, hashlib.sha256).hexdigest()

firma_atacante = hmac.new(b"clave-adivinada", falso, hashlib.sha256).hexdigest()
print("Firma del atacante valida:", hmac.compare_digest(firma_real, firma_atacante))
