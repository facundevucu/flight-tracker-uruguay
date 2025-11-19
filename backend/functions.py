import json

def obtener_vuelos_desde(data, codigo_aereopuerto):
    vuelos = []
    for vuelo in data.get("departures", []) or []:
        try:
            origen = (vuelo.get("origin") or {}).get("code", "")
            if origen == codigo_aereopuerto:
                vuelos.append(vuelo)
        except Exception:
            # ignorar vuelo corrupto y continuar
            continue
    return vuelos

def obtener_vuelos_hacia(data, codigo_aereopuerto):
    vuelos = []
    for vuelo in data.get("arrivals", []) or []:
        try:
            destino = (vuelo.get("destination") or {}).get("code", "")
            if destino == codigo_aereopuerto:
                vuelos.append(vuelo)
        except Exception:
            continue
    return vuelos

def buscar_vuelo_por_codigo(data, codigo_vuelo):
    for tipo in ["arrivals", "departures", "scheduled_arrivals"]:
        for vuelo in data.get(tipo, []) or []:
            try:
                if vuelo.get("ident") == codigo_vuelo:
                    return vuelo
            except Exception:
                continue
    return None

def filtrar_vuelos_por_estado(vuelos, estado):
    try:
        filtrados = []
        for v in vuelos or []:
            try:
                status = (v.get("status") or "").lower()
                if estado.lower() in status:
                    filtrados.append(v)
            except Exception:
                continue
        return filtrados
    except Exception:
        return []

def guardar_vuelos_en_json(nombre_archivo, vuelos):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(vuelos, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"Error escribiendo {nombre_archivo}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado guardando JSON: {e}")
        return False

AEROLINEAS_URUGUAY = {
    #LATAM
    "LA": "LATAM Airlines",
    "LXP": "LATAM Express",
    "LAN": "LATAM Chile",

    #aerolíneas argentinas / austral
    "AR": "Aerolíneas Argentinas",
    "AUS": "Austral Líneas Aéreas",

    #copa airlines
    "CM": "Copa Airlines",
    "CMP": "Copa Airlines",

    #avianca
    "AV": "Avianca",
    "AVA": "Avianca Colombia",

    #iberia
    "IB": "Iberia",
    "IBE": "Iberia Líneas Aéreas de España",

    #azul / GOL / TAM Brasil
    "AD": "Azul Linhas Aéreas Brasileiras",
    "AZU": "Azul Linhas Aéreas Brasileiras",
    "G3": "GOL Linhas Aéreas",
    "GLO": "GOL Linhas Aéreas",
    "JJ": "LATAM Brasil",

    #paranair / amaszonas
    "ZP": "Paranair",
    "AZP": "Paranair",
    "Z8": "Amaszonas Uruguay",
    "AZU": "Amaszonas Uruguay",

    #iberia Express / air europa
    "I2": "Iberia Express",
    "UX": "Air Europa",

    #sky airline
    "H2": "Sky Airline",
    "SKU": "Sky Airline",

    #otros
    "UX": "Air Europa",
    "TA": "TACA",
    "TP": "TAP Air Portugal",
    "AF": "Air France",
    "KL": "KLM",
    "LP": "LATAM Airlines Perú",
    "JZ": "JetSmart Perú",
    "2I": "Star Perú",
    "QCL": "Air Class Líneas Aéreas",
    "QT": "Avianca Cargo (Tampa Cargo)",
}

def normalizar_aerolinea(codigo: str) -> str:
    """Devuelve el nombre completo de la aerolínea si se conoce, o el código original."""
    try:
        if not codigo:
            return "Desconocido"
        return AEROLINEAS_URUGUAY.get(str(codigo).upper(), codigo)
    except Exception:
        return "Desconocido"

def clasificar_tipo_vuelo(vuelo):
    """Clasifica el vuelo como 'Comercial', 'Privado (país)', 'Aviación General (país)', 'Militar' o 'Desconocido'."""
    try:
        if not isinstance(vuelo, dict):
            return "Desconocido"

        ident = (vuelo.get("ident") or "").upper()
        operador = (vuelo.get("operator_icao") or "").upper()
        tipo = (vuelo.get("aircraft_type") or "").upper()
        iata = (vuelo.get("operator_iata") or "")

        # --- Detectar vuelos militares ---
        if any(op in operador for op in ["FAU", "FAB", "FACH", "BOL", "ARM"]):
            return "Militar"

        # --- Detectar privados y aviación general por matrícula ---
        if "-" in ident:
            prefijo = ident.split("-")[0]
            paises_privados = {
                "CX": "Uruguay",
                "LV": "Argentina",
                "CC": "Chile",
                "CP": "Bolivia",
                "PP": "Brasil",
                "PT": "Brasil",
                "PR": "Brasil",
                "N":  "EE.UU.",
                "XB": "México",
                "TG": "Guatemala",
                "OB": "Perú",
                "HC": "Ecuador",
                "HP": "Panamá",
                "HK": "Colombia",
            }
            pais = next((p for pref, p in paises_privados.items() if prefijo.startswith(pref)), None)
            if pais:
                # Asegurar que `tipo` sea cadena antes de startswith
                if isinstance(tipo, str) and tipo.startswith(("C1", "C2", "P2", "PA", "BE", "SR", "DA")):
                    return f"Aviación General ({pais})"
                else:
                    return f"Privado ({pais})"
            return "Privado (Desconocido)"

        # --- Detectar privados o aviación general sin matrícula ---
        if isinstance(tipo, str) and tipo.startswith(("C", "P", "B", "S", "D")) and not iata:
            return "Aviación General (Desconocida)"

        # --- Detectar vuelos comerciales ---
        if isinstance(iata, str) and iata.upper() in AEROLINEAS_URUGUAY:
            return "Comercial"

        return "Desconocido"
    except Exception:
        return "Desconocido"