from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Agregar el directorio padre al path para importar desde modelado
sys.path.insert(0, str(Path(__file__).parent.parent))
from modelado.models import Aerolinea, Aeronave, Aeropuerto, Vuelo

# Diccionario de modelos de aeronaves (código ICAO -> nombre completo)
MODELOS_AERONAVES = {
    # Airbus
    "A20N": "Airbus A320neo",
    "A21N": "Airbus A321neo",
    "A319": "Airbus A319",
    "A320": "Airbus A320",
    "A321": "Airbus A321",
    "A332": "Airbus A330-200",
    "A333": "Airbus A330-300",
    "A339": "Airbus A330-900neo",
    "A342": "Airbus A340-200",
    "A343": "Airbus A340-300",
    "A346": "Airbus A340-600",
    "A359": "Airbus A350-900",
    "A35K": "Airbus A350-1000",
    "A388": "Airbus A380",
    
    # Boeing
    "B737": "Boeing 737",
    "B738": "Boeing 737-800",
    "B739": "Boeing 737-900",
    "B37M": "Boeing 737 MAX",
    "B38M": "Boeing 737 MAX 8",
    "B39M": "Boeing 737 MAX 9",
    "B3XM": "Boeing 737 MAX 10",
    "B752": "Boeing 757-200",
    "B753": "Boeing 757-300",
    "B762": "Boeing 767-200",
    "B763": "Boeing 767-300",
    "B764": "Boeing 767-400",
    "B772": "Boeing 777-200",
    "B773": "Boeing 777-300",
    "B77L": "Boeing 777-200LR",
    "B77W": "Boeing 777-300ER",
    "B788": "Boeing 787-8",
    "B789": "Boeing 787-9",
    "B78X": "Boeing 787-10",
    
    # Embraer
    "E190": "Embraer E190",
    "E195": "Embraer E195",
    "E290": "Embraer E190-E2",
    "E295": "Embraer E195-E2",
    "E170": "Embraer E170",
    "E175": "Embraer E175",
    
    # Bombardier/Canadair
    "CRJ2": "Bombardier CRJ-200",
    "CRJ7": "Bombardier CRJ-700",
    "CRJ9": "Bombardier CRJ-900",
    "CRJX": "Bombardier CRJ-1000",
    "DH8A": "Bombardier Dash 8-100",
    "DH8B": "Bombardier Dash 8-200",
    "DH8C": "Bombardier Dash 8-300",
    "DH8D": "Bombardier Dash 8-400",
    
    # ATR
    "AT42": "ATR 42",
    "AT43": "ATR 42-300",
    "AT45": "ATR 42-500",
    "AT72": "ATR 72",
    "AT73": "ATR 72-500",
    "AT75": "ATR 72-600",
    "AT76": "ATR 72-600",
    
    # Aviación general y privada
    "C172": "Cessna 172 Skyhawk",
    "C182": "Cessna 182 Skylane",
    "C208": "Cessna 208 Caravan",
    "C25A": "Cessna Citation CJ2",
    "C25B": "Cessna Citation CJ3",
    "C25C": "Cessna Citation CJ4",
    "C510": "Cessna Citation Mustang",
    "C525": "Cessna Citation",
    "C550": "Cessna Citation II",
    "C560": "Cessna Citation V",
    "C680": "Cessna Citation Sovereign",
    "C750": "Cessna Citation X",
    "BE20": "Beechcraft King Air",
    "BE9L": "Beechcraft King Air 90",
    "BE9T": "Beechcraft King Air 200",
    "BE40": "Beechcraft Beechjet 400",
    "PA28": "Piper Cherokee",
    "PA31": "Piper Navajo",
    "PA34": "Piper Seneca",
    "PA46": "Piper Malibu",
    "SR20": "Cirrus SR20",
    "SR22": "Cirrus SR22",
    "DA40": "Diamond DA40",
    "DA62": "Diamond DA62",
}

# Diccionario de aerolíneas que operan en Uruguay
AEROLINEAS_URUGUAY = {
    # LATAM
    "LA": "LATAM Airlines",
    "LXP": "LATAM Express",
    "LAN": "LATAM Chile",
    
    # Aerolíneas Argentinas / Austral
    "AR": "Aerolíneas Argentinas",
    "AUS": "Austral Líneas Aéreas",
    
    # Copa Airlines
    "CM": "Copa Airlines",
    "CMP": "Copa Airlines",
    
    # Avianca
    "AV": "Avianca",
    "AVA": "Avianca Colombia",
    
    # Iberia
    "IB": "Iberia",
    "IBE": "Iberia Líneas Aéreas de España",
    
    # Azul / GOL / TAM Brasil
    "AD": "Azul Linhas Aéreas Brasileiras",
    "AZU": "Azul Linhas Aéreas Brasileiras",
    "G3": "GOL Linhas Aéreas",
    "GLO": "GOL Linhas Aéreas",
    "JJ": "LATAM Brasil",
    
    # Paranair / Amaszonas
    "ZP": "Paranair",
    "AZP": "Paranair",
    "Z8": "Amaszonas Uruguay",
    
    # Iberia Express / Air Europa
    "I2": "Iberia Express",
    "UX": "Air Europa",
    
    # Sky Airline
    "H2": "Sky Airline",
    "SKU": "Sky Airline",
    
    # Otros
    "TA": "TACA",
    "TP": "TAP Air Portugal",
    "AF": "Air France",
    "KL": "KLM",
    "LP": "LATAM Airlines Perú",
    "JZ": "JetSmart Perú",
    "2I": "Star Perú",
    "QCL": "Air Class Líneas Aéreas",
    "QT": "Avianca Cargo",
}

def normalizar_nombre_aerolinea(codigo: str) -> str:
    """Devuelve el nombre completo de la aerolínea si se conoce, o el código original."""
    if not codigo:
        return "Desconocido"
    return AEROLINEAS_URUGUAY.get(str(codigo).upper(), codigo)

def normalizar_modelo_aeronave(codigo: str) -> str:
    """Devuelve el nombre completo del modelo de aeronave si se conoce, o el código original."""
    if not codigo or codigo == "N/A":
        return "Desconocido"
    return MODELOS_AERONAVES.get(str(codigo).upper(), codigo)

def crear_aerolinea_desde_vuelo(vuelo_data: Dict[str, Any]) -> Aerolinea:
    """Crea un objeto Aerolinea desde los datos crudos del vuelo"""
    # Intentar normalizar el nombre desde los códigos disponibles
    codigo_iata = vuelo_data.get("operator_iata")
    codigo_icao = vuelo_data.get("operator_icao")
    nombre_crudo = vuelo_data.get("operator", "Desconocido")
    
    # Buscar nombre completo en el diccionario (priorizar IATA)
    nombre_normalizado = normalizar_nombre_aerolinea(codigo_iata or codigo_icao or nombre_crudo)
    
    return Aerolinea(
        nombre=nombre_normalizado,
        codigo_iata=codigo_iata,
        codigo_icao=codigo_icao
    )

def crear_aeronave_desde_vuelo(vuelo_data: Dict[str, Any]) -> Aeronave:
    """Crea un objeto Aeronave desde los datos crudos del vuelo"""
    codigo_modelo = vuelo_data.get("aircraft_type")
    modelo_normalizado = normalizar_modelo_aeronave(codigo_modelo) if codigo_modelo else "Desconocido"
    
    return Aeronave(
        matricula=vuelo_data.get("registration", "N/A"),
        codigo_iata=codigo_modelo,
        codigo_icao=codigo_modelo,
        modelo=modelo_normalizado  # Nombre completo (ej: "Airbus A320neo")
    )

def crear_aeropuerto(airport_data: Optional[Dict[str, Any]]) -> Optional[Aeropuerto]:
    """Crea un objeto Aeropuerto desde los datos crudos"""
    if not airport_data:
        return None
    return Aeropuerto(
        nombre=airport_data.get("name", "Desconocido"),
        codigo_iata=airport_data.get("code_iata"),
        codigo_icao=airport_data.get("code_icao"),
        pais=airport_data.get("city", "Desconocido")  # city viene en los datos de FlightAware
    )

def crear_vuelo_desde_api(vuelo_data: Dict[str, Any]) -> Vuelo:
    """Convierte los datos crudos de la API en un objeto Vuelo"""
    aerolinea = crear_aerolinea_desde_vuelo(vuelo_data)
    aeronave = crear_aeronave_desde_vuelo(vuelo_data)
    origen = crear_aeropuerto(vuelo_data.get("origin"))
    destino = crear_aeropuerto(vuelo_data.get("destination"))
    tipo = clasificar_tipo_vuelo(vuelo_data)
    
    return Vuelo(
        numero_vuelo=vuelo_data.get("ident", "N/A"),
        aerolinea=aerolinea,
        aeronave=aeronave,
        salida=origen,
        llegada=destino,
        estado=vuelo_data.get("status", "Desconocido"),
        tipo_vuelo=tipo
    )

def mapear_vuelos(data: Dict[str, Any]) -> Dict[str, List[Vuelo]]:
    """Convierte todos los vuelos crudos en objetos Vuelo
    
    Returns:
        Dict con keys 'arrivals' y 'departures', cada uno con lista de objetos Vuelo
    """
    arrivals_raw = data.get("arrivals", []) or []
    departures_raw = data.get("departures", []) or []
    
    arrivals = []
    for v_data in arrivals_raw:
        try:
            vuelo = crear_vuelo_desde_api(v_data)
            arrivals.append(vuelo)
        except Exception as e:
            print(f"⚠️ Error mapeando arrival {v_data.get('ident')}: {e}")
            continue
    
    departures = []
    for v_data in departures_raw:
        try:
            vuelo = crear_vuelo_desde_api(v_data)
            departures.append(vuelo)
        except Exception as e:
            print(f"⚠️ Error mapeando departure {v_data.get('ident')}: {e}")
            continue
    
    return {
        "arrivals": arrivals,
        "departures": departures
    }

def clasificar_tipo_vuelo(vuelo_data: Dict[str, Any]) -> str:
    """Clasifica el vuelo como 'Comercial', 'Privado', 'Aviación General', 'Militar' o 'Desconocido'."""
    try:
        ident = (vuelo_data.get("ident") or "").upper()
        operador = (vuelo_data.get("operator_icao") or "").upper()
        tipo_aeronave = (vuelo_data.get("aircraft_type") or "").upper()
        iata = (vuelo_data.get("operator_iata") or "")

        # Detectar vuelos militares
        if any(op in operador for op in ["FAU", "FAB", "FACH", "BOL", "ARM"]):
            return "Militar"

        # Detectar privados y aviación general por matrícula
        if "-" in ident:
            prefijo = ident.split("-")[0]
            paises_privados = {
                "CX": "Uruguay", "LV": "Argentina", "CC": "Chile", "CP": "Bolivia",
                "PP": "Brasil", "PT": "Brasil", "PR": "Brasil", "N": "EE.UU.",
                "XB": "México", "TG": "Guatemala", "OB": "Perú", "HC": "Ecuador",
                "HP": "Panamá", "HK": "Colombia",
            }
            pais = next((p for pref, p in paises_privados.items() if prefijo.startswith(pref)), None)
            if pais:
                # Aviación general vs privado por tipo de aeronave
                if tipo_aeronave.startswith(("C1", "C2", "P2", "PA", "BE", "SR", "DA")):
                    return f"Aviación General ({pais})"
                else:
                    return f"Privado ({pais})"
            return "Privado"

        # Detectar aviación general sin matrícula
        if tipo_aeronave.startswith(("C", "P", "B", "S", "D")) and not iata:
            return "Aviación General"

        # Detectar vuelos comerciales
        if iata and iata.upper() in AEROLINEAS_URUGUAY:
            return "Comercial"

        return "Desconocido"
    except Exception:
        return "Desconocido"

def buscar_vuelo_por_codigo(data, codigo_vuelo):
    for tipo in ["arrivals", "departures", "scheduled_arrivals"]:
        for vuelo in data.get(tipo, []) or []:
            try:
                if vuelo.get("ident") == codigo_vuelo:
                    return vuelo
            except Exception:
                continue
    return None