# run_client.py
import os
from api_client_wrapper import APIClient, schedule_daily_refresh

# --- CONFIG ---
os.environ.setdefault("API_BASE_URL", "https://aeroapi.flightaware.com/aeroapi")
os.environ.setdefault("API_KEY", "kAE2C1JlDyjn6BqhdkuNQpVPbFbMVitU")  # <<-- Coloca tu key real
os.environ.setdefault("RATE_LIMIT_MAX_REQUESTS", "60")
os.environ.setdefault("RATE_LIMIT_WINDOW_SEC", "3600")
os.environ.setdefault("REFRESH_DAILY_AT", "13:00")
# --------------

if __name__ == "__main__":
    client = APIClient()

    # 1) Corrida puntual (prueba)
    raw = client.get_airport_flights(icao="SUMU", tipo="arrivals")
    df  = client.normalize_airport_flights(raw)
    print(client.human_summary(df))
    df.to_csv("vuelos_normalizados.csv", index=False, encoding="utf-8-sig")
    print("CSV guardado en vuelos_normalizados.csv")
    print("Contador:", client.counter.snapshot())

    # 2) (Opcional) Dejar daemon refrescando todos los días
    # schedule_daily_refresh(client, os.getenv("REFRESH_DAILY_AT"), icao="SUMU", tipo="arrivals")
    # import time
    # while True: time.sleep(3600)
