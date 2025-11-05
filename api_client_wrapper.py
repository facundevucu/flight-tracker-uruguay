# api_client_wrapper.py
import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List

import requests
import pandas as pd

# =========================
# CONFIGURACIÓN (AeroAPI)
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "https://aeroapi.flightaware.com/aeroapi")
API_KEY      = os.getenv("API_KEY", "kAE2C1JlDyjn6BqhdkuNQpVPbFbMVitU")  # <<-- Coloca tu key real

# Auth correcta para AeroAPI v4: x-apikey
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "x-apikey": API_KEY,
}

# Rate limit conservador (evitar quemar cuota)
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))   # p.ej. 60 por hora
RATE_LIMIT_WINDOW_SEC   = int(os.getenv("RATE_LIMIT_WINDOW_SEC",   str(3600)))

# Contador persistido
COUNTER_PATH = Path(os.getenv("REQUEST_COUNTER_PATH", "request_counter.json"))

# Programación del refresco (hora local, formato HH:MM)
REFRESH_DAILY_AT = os.getenv("REFRESH_DAILY_AT", "13:00")


# =========================
# RATE LIMITER (ventana deslizante)
# =========================
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.timestamps: List[datetime] = []

    def acquire(self) -> float:
        now = datetime.now()
        self.timestamps = [t for t in self.timestamps if now - t < self.window]
        if len(self.timestamps) < self.max_requests:
            self.timestamps.append(now)
            return 0.0
        oldest = min(self.timestamps)
        return max((self.window - (now - oldest)).total_seconds(), 0.01)


# =========================
# CONTADOR DE REQUESTS
# =========================
class RequestCounter:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"total": 0, "por_dia": {}}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                pass

    def _save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def inc(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        self.data["total"] = self.data.get("total", 0) + 1
        self.data.setdefault("por_dia", {})
        self.data["por_dia"][hoy] = self.data["por_dia"].get(hoy, 0) + 1
        self._save()

    def snapshot(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        return {
            "total": self.data.get("total", 0),
            "hoy": self.data.get("por_dia", {}).get(hoy, 0),
            "por_dia": self.data.get("por_dia", {}),
        }


# =========================
# CLIENTE API + NORMALIZADOR
# =========================
class APIClient:
    def __init__(self,
                 base_url: str = API_BASE_URL,
                 headers: Optional[Dict[str, str]] = None,
                 limiter: Optional[RateLimiter] = None,
                 counter: Optional[RequestCounter] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or DEFAULT_HEADERS
        self.limiter = limiter or RateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SEC)
        self.counter = counter or RequestCounter(COUNTER_PATH)

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        wait = self.limiter.acquire()
        if wait > 0:
            time.sleep(wait)

        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
        self.counter.inc()

        if not resp.ok:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")
        try:
            return resp.json()
        except Exception:
            return {"raw_text": resp.text}

    # -------- Endpoints AeroAPI (aeropuertos) --------
    def get_airport_flights(self, icao: str,
                            tipo: str = "arrivals",
                            **query) -> Dict[str, Any]:
        """
        tipo: 'arrivals' | 'departures' | 'scheduled_arrivals' | 'scheduled_departures'
        Más info: /airports/{id}/flights/*   (OpenAPI)
        """
        valid = {"arrivals", "departures", "scheduled_arrivals", "scheduled_departures"}
        if tipo not in valid:
            raise ValueError(f"tipo inválido: {tipo}. Opciones: {sorted(valid)}")
        path = f"/airports/{icao}/flights/{tipo}"
        return self._request("GET", path, params=query or {})

    def get_airport_all(self, icao: str, **query) -> Dict[str, Any]:
        """Devuelve el agregado /airports/{id}/flights (recent+upcoming)."""
        path = f"/airports/{icao}/flights"
        return self._request("GET", path, params=query or {})

    # ---------- Normalizador ----------
    @staticmethod
    def _to_iso(ts):
        if ts is None:
            return None
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        if isinstance(ts, str):
            return ts
        return str(ts)

    @staticmethod
    def normalize_airport_flights(payload: Dict[str, Any]) -> pd.DataFrame:
        """
        Normaliza cualquiera de los 4 listados por aeropuerto (arrivals, departures, scheduled_*)
        y también /airports/{id}/flights si viene el agregado.
        Campos mapeados según OpenAPI AeroAPI.
        """
        # Ubicar listas posibles en la respuesta
        lists_keys = ["arrivals", "departures", "scheduled_arrivals", "scheduled_departures"]
        rows = []
        for list_name in lists_keys:
            for x in (payload.get(list_name) or []):
                origin = x.get("origin") or {}
                dest   = x.get("destination") or {}
                rows.append({
                    "lista": list_name,
                    "ident": x.get("ident"),
                    "operator": x.get("operator"),
                    "operator_iata": x.get("operator_iata"),
                    "flight_number": x.get("flight_number"),
                    "registration": x.get("registration"),
                    "status": x.get("status"),
                    "aircraft_type": x.get("aircraft_type"),
                    "origin_code": origin.get("code"),
                    "origin_city": origin.get("city"),
                    "destination_code": dest.get("code"),
                    "destination_city": dest.get("city"),
                    "scheduled_out": APIClient._to_iso(x.get("scheduled_out")),
                    "estimated_out": APIClient._to_iso(x.get("estimated_out")),
                    "actual_out":    APIClient._to_iso(x.get("actual_out")),
                    "scheduled_off": APIClient._to_iso(x.get("scheduled_off")),
                    "estimated_off": APIClient._to_iso(x.get("estimated_off")),
                    "actual_off":    APIClient._to_iso(x.get("actual_off")),
                    "scheduled_on":  APIClient._to_iso(x.get("scheduled_on")),
                    "estimated_on":  APIClient._to_iso(x.get("estimated_on")),
                    "actual_on":     APIClient._to_iso(x.get("actual_on")),
                    "scheduled_in":  APIClient._to_iso(x.get("scheduled_in")),
                    "estimated_in":  APIClient._to_iso(x.get("estimated_in")),
                    "actual_in":     APIClient._to_iso(x.get("actual_in")),
                    "terminal_origin": x.get("terminal_origin"),
                    "gate_origin":     x.get("gate_origin"),
                    "terminal_destination": x.get("terminal_destination"),
                    "gate_destination":     x.get("gate_destination"),
                    "route_distance_nm": x.get("route_distance"),
                    "progress_percent": x.get("progress_percent"),
                    "baggage_claim": x.get("baggage_claim"),
                })

        # Si vino el agregado /airports/{id}/flights trae además scheduled_* en el mismo payload
        for agg_key in lists_keys:
            # ya los tomamos arriba; este bloque es por si el payload viene plano sin keys
            pass

        df = pd.DataFrame(rows)
        ordered = [
            "lista","ident","operator","operator_iata","flight_number","registration",
            "status","aircraft_type",
            "origin_code","origin_city","destination_code","destination_city",
            "scheduled_out","estimated_out","actual_out",
            "scheduled_off","estimated_off","actual_off",
            "scheduled_on","estimated_on","actual_on",
            "scheduled_in","estimated_in","actual_in",
            "terminal_origin","gate_origin","terminal_destination","gate_destination",
            "route_distance_nm","progress_percent","baggage_claim"
        ]
        df = df[[c for c in ordered if c in df.columns]]
        return df

    @staticmethod
    def human_summary(df: pd.DataFrame) -> str:
        if df.empty:
            return "No hay vuelos."
        tot = len(df)
        por_lista = df.groupby("lista")["ident"].count().to_dict() if "lista" in df.columns else {}
        estados = df["status"].value_counts(dropna=False).to_dict() if "status" in df.columns else {}
        return f"Vuelos total: {tot}\nPor lista: {por_lista}\nEstados: {estados}"


# =========================
# REFRESCO DIARIO
# =========================
def schedule_daily_refresh(client: APIClient, at_hhmm: str,
                           icao: str,
                           tipo: str = "arrivals",
                           query: Optional[Dict[str, Any]] = None,
                           out_csv: Optional[str] = "vuelos_normalizados.csv"):
    """
    Programa un hilo que, todos los días a HH:MM (hora local), llama al endpoint, normaliza y guarda CSV.
    """
    hh, mm = map(int, at_hhmm.split(":"))

    def worker():
        while True:
            now = datetime.now()
            run_at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if run_at <= now:
                run_at += timedelta(days=1)
            time.sleep((run_at - now).total_seconds())
            try:
                raw = client.get_airport_flights(icao=icao, tipo=tipo, **(query or {}))
                df = client.normalize_airport_flights(raw)
                if out_csv:
                    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
                print(f"[{datetime.now():%Y-%m-%d %H:%M}] Refresco OK. Guardado: {out_csv}.")
            except Exception as e:
                print(f"[{datetime.now():%Y-%m-%d %H:%M}] Error refrescando: {e}")

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t


# =========================
# EJEMPLO DE USO DIRECTO
# =========================
if __name__ == "__main__":
    client = APIClient()
    try:
        # Ejemplo: llegadas a SUMU (Montevideo)
        raw = client.get_airport_flights(icao="SUMU", tipo="arrivals")
        df  = client.normalize_airport_flights(raw)
        print(client.human_summary(df))
        df.to_csv("vuelos_normalizados.csv", index=False, encoding="utf-8-sig")
        print("CSV guardado en vuelos_normalizados.csv")
        print("Contador:", client.counter.snapshot())
    except Exception as e:
        print("Error:", e)

    # Programar refresco diario (descomenta para usar)
    # schedule_daily_refresh(client, REFRESH_DAILY_AT, icao="SUMU", tipo="arrivals")
    # import time
    # while True:
    #     time.sleep(3600)
