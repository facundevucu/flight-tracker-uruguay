import json
from functions import normalizar_aerolinea, clasificar_tipo_vuelo

# 🔹 Cargar el archivo con los datos de vuelos
with open("vuelos_prueba.json", "r", encoding="utf-8") as f:
    data = json.load(f)

arrivals = data.get("arrivals", [])

print("--- aerolineas normalizadas y tipos de vuelo ---")

# 🔹 Recorremos solo los primeros 15
for vuelo in arrivals[:15]:
    codigo = vuelo.get("operator_iata") or vuelo.get("operator_icao")
    nombre = normalizar_aerolinea(codigo)
    tipo = clasificar_tipo_vuelo(vuelo)
    vuelo_id = vuelo.get("ident", "N/A")
    origen = vuelo.get("origin", {}).get("code_iata", "Desconocido")
    destino = vuelo.get("destination", {}).get("code_iata", "Desconocido")

    print(f"{vuelo_id:10} | {codigo or '---':4} → {nombre:35} | {origen} → {destino} | Tipo: {tipo}")
