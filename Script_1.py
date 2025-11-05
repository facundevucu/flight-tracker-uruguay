import requests
import re

# 🔑 Nuestra clave de API
API_KEY = "163597d0969fa272817b4955f17b5b50"

# ✈️ Endpoint base
url = "https://api.aviationstack.com/v1/flights"

# 📦 Parámetros (setteamos en 'arrival_icao' a 'SUMU' para filtrar por vuelos que solo llegaran a Carrasco)
params = {
    'access_key': API_KEY,
    'arr_icao': 'SUMU',   # Aeropuerto Internacional de Carrasco
    'limit': 20
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    flights = data.get('data', [])
    print(f"Encontrados {len(flights)} vuelos hacia Carrasco (SUMU):\n")

    # Expresión regular para validar matrículas uruguayas (ejemplo: CX-ABC), todas las matriculas uruguayas comienzan con 'CX-'. 
    # Codigo que usamos tanto como benchmark(para ver si funcionaba la API y todo en orden) como tambien para detectar vuelos uruguayos , y poder 
    # categorizar los vuelos que son nacionales de los internacionales asi como vuelos locales tambien.
    pattern = re.compile(r"^CX-[A-Z]{3}$")

    for flight in flights:
        flight_number = flight.get('flight', {}).get('iata', 'N/A')
        registration = (flight.get('aircraft') or {}).get('registration', 'N/A')
        airline = flight.get('airline', {}).get('name', 'N/A')
        departure = flight.get('departure', {}).get('airport', 'N/A')

        print(f"Vuelo {flight_number} desde {departure} ({airline})")
        print(f"  Matrícula: {registration}")

        if registration != 'N/A' and pattern.match(registration):
            print("  → Avión uruguayo detectado 🇺🇾")
        print("-" * 40)
else:
    print("Error al conectar:", response.status_code, response.text)
