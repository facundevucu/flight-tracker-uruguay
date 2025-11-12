# test_models.py
# ejercicio 1.3 de la semana 2
import json
from models import Aerolinea, Aeronave, Aeropuerto, Vuelo, AnalizadorDeVuelos

# ------------------------
# Utilidades para distancia de la API (en NM)
# ------------------------

def _to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def _nm_from_km(km):
    v = _to_float(km)
    return v * 0.539957 if v is not None else None

def _nm_from_mi(mi):
    v = _to_float(mi)
    return v * 0.868976 if v is not None else None

def extract_distance_nm(flight: dict):
    """
    Extrae la distancia en millas náuticas (NM) desde diferentes convenciones que puede traer la API.
    Orden de preferencia:
      1) 'distance_nm' directo
      2) 'distance' como dict con claves 'nm' | 'nmi' | 'mi' | 'km'
      3) 'great_circle_distance' como dict con 'nm' | 'nmi' | 'mi' | 'km'
      4) 'distance' como número con acompañamiento de 'distance_units' o 'units'
    Devuelve float o None si no se puede determinar.
    """
    if not isinstance(flight, dict):
        return None

    # 1) Campo directo
    if "distance_nm" in flight:
        v = _to_float(flight.get("distance_nm"))
        if v is not None:
            return v

    # 2) distance como dict
    dist = flight.get("distance")
    if isinstance(dist, dict):
        # prioridad a nm/nmi
        for key in ("nm", "nmi", "nautical_miles"):
            if key in dist:
                v = _to_float(dist[key])
                if v is not None:
                    return v
        # millas -> nm
        for key in ("mi", "miles"):
            if key in dist:
                v = _nm_from_mi(dist[key])
                if v is not None:
                    return v
        # km -> nm
        for key in ("km", "kilometers", "kilometres"):
            if key in dist:
                v = _nm_from_km(dist[key])
                if v is not None:
                    return v

    # 3) great_circle_distance como dict
    gcd = flight.get("great_circle_distance")
    if isinstance(gcd, dict):
        for key in ("nm", "nmi", "nautical_miles"):
            if key in gcd:
                v = _to_float(gcd[key])
                if v is not None:
                    return v
        for key in ("mi", "miles"):
            if key in gcd:
                v = _nm_from_mi(gcd[key])
                if v is not None:
                    return v
        for key in ("km", "kilometers", "kilometres"):
            if key in gcd:
                v = _nm_from_km(gcd[key])
                if v is not None:
                    return v

    # 4) distance como número + unidades aparte
    if isinstance(dist, (int, float, str)):
        val = _to_float(dist)
        if val is not None:
            units = (
                flight.get("distance_units")
                or (isinstance(flight.get("distance"), dict) and flight["distance"].get("units"))
                or flight.get("units")
            )
            units = (units or "").lower()
            if units in ("nm", "nmi", "nautical_miles"):
                return val
            if units in ("mi", "mile", "miles"):
                return _nm_from_mi(val)
            if units in ("km", "kilometer", "kilometre", "kilometers", "kilometres"):
                return _nm_from_km(val)

    return None

# ------------------------
# Carga de datos y objetos
# ------------------------

with open("vuelos_prueba.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# tomo los primeros 5 vuelos reales (llegadas)
arrivals = data.get("arrivals", [])[:5]

vuelos_objetos = []

for vuelo_data in arrivals:
    # Aerolínea
    aerolinea = Aerolinea(
        nombre=vuelo_data.get("operator"),
        codigo_iata=vuelo_data.get("operator_iata"),
        codigo_icao=vuelo_data.get("operator_icao"),
    )

    # Aeronave
    aeronave = Aeronave(
        matricula=vuelo_data.get("registration"),
        codigo_iata=vuelo_data.get("aircraft_iata"),
        codigo_icao=vuelo_data.get("aircraft_type"),
    )

    # Origen/Destino
    origen_data = vuelo_data.get("origin", {}) or {}
    destino_data = vuelo_data.get("destination", {}) or {}

    origen = Aeropuerto(
        nombre=origen_data.get("city") or origen_data.get("name"),
        codigo_iata=origen_data.get("code_iata") or origen_data.get("code"),
        codigo_icao=origen_data.get("code_icao"),
        pais=origen_data.get("name") or "N/A",
    )

    destino = Aeropuerto(
        nombre=destino_data.get("city") or destino_data.get("name"),
        codigo_iata=destino_data.get("code_iata") or destino_data.get("code"),
        codigo_icao=destino_data.get("code_icao"),
        pais=destino_data.get("name") or "N/A",
    )

    # Campos extra opcionales para el analizador
    vuelo = Vuelo(
        numero_vuelo=vuelo_data.get("ident"),
        aerolinea=aerolinea,
        aeronave=aeronave,
        salida=origen,
        llegada=destino,
        estado=vuelo_data.get("status") or "desconocido",
        aircraft_icao_code=vuelo_data.get("aircraft_type"),
        departure_scheduled_iso=(vuelo_data.get("departure", {}) or {}).get("scheduled"),
        arrival_scheduled_iso=(vuelo_data.get("arrival", {}) or {}).get("scheduled"),
    )

    vuelos_objetos.append(vuelo)

print("\n-- Vuelos de llegada (objetos) --\n")
for v in vuelos_objetos:
    v.mostrar_info()

# ------------------------
# Analizador clásico (opcional)
# ------------------------
analizador = AnalizadorDeVuelos(vuelos_objetos)

print("\n-- Analizador --")
top = analizador.aerolinea_mas_frecuente()
print(f"Aerolínea más frecuente: {top}" if top else "Sin datos de aerolíneas")

modelos = analizador.ver_modelos_aeronaves()
print(f"Modelos ICAO presentes: {modelos}")

activos = analizador.filtrar_por_estado("active")
print(f"Vuelos en estado 'active': {len(activos)}")

# ---------------------------------------------------------
# Vuelo "más largo" por DISTANCIA (usando distancia NM de la API)
# ---------------------------------------------------------
dist_max_nm = -1.0
ident_mas_largo = None

for vuelo_data in arrivals:
    nm = extract_distance_nm(vuelo_data)
    if nm is None:
        continue
    if nm > dist_max_nm:
        dist_max_nm = nm
        ident_mas_largo = vuelo_data.get("ident") or "SIN_IDENT"

if ident_mas_largo is not None and dist_max_nm >= 0:
    print(f"Vuelo más largo por distancia (API): {ident_mas_largo} ({round(dist_max_nm, 1)} NM)")
else:
    print("No hay distancia en NM disponible en el JSON para calcular el vuelo más largo.")
