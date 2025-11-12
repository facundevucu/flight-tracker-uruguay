#ejercicio 1.3 de la semana 2

from models import Aerolinea, Aeronave, Aeropuerto, Vuelo
import json

#cargar json real de vuelos
with open("vuelos_prueba.json", "r", encoding="utf-8") as f:
    data = json.load(f)

#tomo los primeros 5 vuelos reales
arrivals = data["arrivals"][:5]  

vuelos_objetos = []

for vuelo_data in arrivals:

    aerolinea = Aerolinea(
        vuelo_data.get("operator"),
        vuelo_data.get("operator_iata"),
        vuelo_data.get("operator_icao")
    )

    aeronave = Aeronave(
        vuelo_data.get("registration"),
        vuelo_data.get("aircraft_type"),
        vuelo_data.get("aircraft_type")
    )

    origen_data = vuelo_data.get("origin", {})
    destino_data = vuelo_data.get("destination", {})

    origen = Aeropuerto(
        origen_data.get("city"),
        origen_data.get("code_iata"),
        origen_data.get("code_icao"),
        origen_data.get("name")
    )

    destino = Aeropuerto(
        destino_data.get("city"),
        destino_data.get("code_iata"),
        destino_data.get("code_icao"),
        destino_data.get("name")
    )

    # determinar número/identificador del vuelo desde campos comunes
    numero_vuelo = (
        (vuelo_data.get("ident") or "")
        or vuelo_data.get("flight_iata")
        or vuelo_data.get("flight_number")
        or vuelo_data.get("callsign")
        or ( (vuelo_data.get("operator_iata") or "") + (vuelo_data.get("flight_number") or "") )
        or "N/A"
    )

    salida = origen          # si preferís usar datos crudos: origen_data
    llegada = destino        # o destino_data
    estado = vuelo_data.get("status", "N/A")

    # pasar numero_vuelo como primer argumento según la firma de Vuelo
    vuelo = Vuelo(numero_vuelo, aerolinea, aeronave, salida, llegada, estado)
    vuelos_objetos.append(vuelo)

print("\n--vuelos de llegada--\n")
for v in vuelos_objetos:
    v.mostrar_info()
