import os
import requests
import json
from typing import Optional, Dict, Any

BASE_URL = "https://aeroapi.flightaware.com/aeroapi"
API_KEY: Optional[str] = None  # se setea desde entorno o desde main al actualizar

class FlightAwareError(Exception):
    pass

def _obtener_api_key(explicita: Optional[str] = None) -> str:
    """Resuelve la API key: primero argumento explícito, luego variable global, luego entorno.
    Lanza FlightAwareError si no existe."""
    if explicita:
        return explicita
    if API_KEY:
        return API_KEY
    env_key = os.getenv("FLIGHTAWARE_API_KEY")
    if env_key:
        return env_key
    raise FlightAwareError("FLIGHTAWARE_API_KEY no encontrada. Definir en .env o pasarla explícita.")

def obtener_vuelos_por_aeropuerto(codigo_aeropuerto: str, limite: int = 10, tipo: str = "arrivals", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Obtiene vuelos para un aeropuerto.
    tipo: arrivals | departures | enroute | scheduled
    limite: cantidad aproximada (API real usa paginado, aquí simplificado)
    """
    key = _obtener_api_key(api_key)
    url = f"{BASE_URL}/airports/{codigo_aeropuerto}/flights"
    headers = {"x-apikey": key}
    params = {
        "type": tipo,
        "max_pages": 1,
        "howMany": max(1, limite)
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code >= 400:
            raise FlightAwareError(f"Error API {resp.status_code}: {resp.text[:200]}")
        return resp.json()
    except FlightAwareError:
        raise
    except Exception as e:
        raise FlightAwareError(f"Fallo de red/API: {e}") from e



if __name__ == "__main__":
    # Uso manual de prueba (requiere FLIGHTAWARE_API_KEY en entorno o editar variable API_KEY)
    aeropuerto = "SUMU"
    try:
        datos = obtener_vuelos_por_aeropuerto(aeropuerto, tipo="arrivals")
        print(json.dumps(datos, ensure_ascii=False, indent=2)[:2000])
    except FlightAwareError as e:
        print("Error:", e)

