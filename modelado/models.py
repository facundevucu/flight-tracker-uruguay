# models.py
# Clases de dominio + Analizador sobre objetos
import re
from datetime import datetime
from typing import List, Optional, Tuple


class Aerolinea:
    def __init__(self, nombre: str, codigo_iata: Optional[str] = None, codigo_icao: Optional[str] = None):
        self.nombre = nombre
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao

    def __str__(self) -> str:
        codigo = self.codigo_iata or self.codigo_icao or "N/A"
        return f"{self.nombre} ({codigo})"


class Aeronave:
    def __init__(self, matricula: str, codigo_iata: Optional[str] = None, codigo_icao: Optional[str] = None):
        # si no es válida, guardo literal para que se note en depuración
        self.matricula = matricula if self._matricula_valida(matricula) else "Matrícula inválida"
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao

    def _matricula_valida(self, matricula: Optional[str]) -> bool:
        if not matricula or matricula == "N/A":
            return False
        return bool(re.match(r"^[A-Z]{1,2}-[A-Z0-9]{3,5}$", matricula))

    def es_uruguaya(self) -> bool:
        return bool(re.match(r"^CX-[A-Z]{3}$", self.matricula))

    def __str__(self) -> str:
        bandera = "🇺🇾" if self.es_uruguaya() else ""
        return f"{self.matricula} {bandera}".strip()


class Aeropuerto:
    def __init__(self, nombre: str, codigo_iata: Optional[str], codigo_icao: str, pais: str):
        self.nombre = nombre
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao if self._icao_valido(codigo_icao) else "Código ICAO inválido"
        self.pais = pais

    def _icao_valido(self, codigo: str) -> bool:
        # ^ inicio, 4 letras mayúsculas, $ fin
        return bool(re.match(r"^[A-Z]{4}$", str(codigo)))

    def __str__(self) -> str:
        return f"{self.nombre} ({self.codigo_icao}) - {self.pais}"


class Vuelo:
    """
    Representa un vuelo de alto nivel; 'salida' y 'llegada' pueden ser strings u objetos Aeropuerto,
    y 'aeronave' un objeto Aeronave. 'aerolinea' es un objeto Aerolinea.
    """
    def __init__(
        self,
        numero_vuelo: str,
        aerolinea: Aerolinea,
        aeronave: Aeronave,
        salida,
        llegada,
        estado: str,
        aircraft_icao_code: Optional[str] = None,
        departure_scheduled_iso: Optional[str] = None,
        arrival_scheduled_iso: Optional[str] = None,
    ):
        self.numero_vuelo = numero_vuelo if self._numero_vuelo_valido(numero_vuelo) else "Código inválido"
        self.aerolinea = aerolinea
        self.aeronave = aeronave
        self.salida = salida
        self.llegada = llegada
        self.estado = estado
        # campos extra útiles para el Analizador
        self.aircraft = type("AircraftInfo", (), {})()
        setattr(self.aircraft, "icao_code", aircraft_icao_code or "")
        self.departure = {"scheduled": departure_scheduled_iso} if departure_scheduled_iso else {}
        self.arrival = {"scheduled": arrival_scheduled_iso} if arrival_scheduled_iso else {}

    def _numero_vuelo_valido(self, numero: str) -> bool:
        return bool(re.match(r"^[A-Z0-9]{2,3}\d{1,4}$", str(numero)))

    def mostrar_info(self):
        print(f"✈️ {self.numero_vuelo} - {self.aerolinea}")
        print(f"  Origen: {self.salida}")
        print(f"  Destino: {self.llegada}")
        print(f"  Aeronave: {self.aeronave} (ICAO: {getattr(self.aircraft, 'icao_code', '')})")
        print(f"  Estado: {self.estado}")
        print("-" * 40)

    @staticmethod
    def _parse_iso_z(fecha: Optional[str]) -> Optional[datetime]:
        if not fecha:
            return None
        try:
            # admite '...Z' convirtiendo a offset +00:00
            return datetime.fromisoformat(fecha.replace("Z", "+00:00"))
        except Exception:
            return None


class AnalizadorDeVuelos:
    """
    Opera sobre una lista de objetos Vuelo (no sobre dicts de la API).
    """
    def __init__(self, vuelos: List[Vuelo]):
        self.vuelos = vuelos or []

    def aerolinea_mas_frecuente(self) -> Optional[Tuple[str, int]]:
        """
        Devuelve (nombre_aerolinea, cantidad) de la aerolínea más frecuente,
        o None si no hay datos.
        """
        nombres = [
            getattr(getattr(vuelo, "aerolinea", None), "nombre", None)
            for vuelo in self.vuelos
            if getattr(getattr(vuelo, "aerolinea", None), "nombre", None)
        ]
        if not nombres:
            return None
        from collections import Counter
        aerolinea, cantidad = Counter(nombres).most_common(1)[0]
        return aerolinea, cantidad

    def filtrar_por_estado(self, estado: str) -> List[Vuelo]:
        """
        Filtra vuelos por estado exacto (case-insensitive).
        """
        return [v for v in self.vuelos if getattr(v, "estado", "").lower() == estado.lower()]

    def aeronave_mas_grande(self):
        """
        Devuelve el objeto aeronave 'más grande' según comparación lexicográfica
        del ICAO code del modelo (heurística simple).
        """
        if not self.vuelos:
            return None
        vuelo_top = max(self.vuelos, key=lambda v: getattr(getattr(v, "aircraft", None), "icao_code", ""))
        return getattr(vuelo_top, "aircraft", None)

    def ver_modelos_aeronaves(self) -> List[str]:
        """
        Devuelve una lista con los códigos ICAO únicos de aeronaves presentes.
        """
        return list({
            getattr(getattr(v, "aircraft", None), "icao_code", None) or "Desconocido"
            for v in self.vuelos
        })

    def vuelo_mas_largo(self):
        """
        Devuelve (vuelo, duración_en_horas redondeada a 2 decimales) del vuelo con mayor
        duración programada según campos ISO en v.departure['scheduled'] y v.arrival['scheduled'].
        Si no hay datos suficientes, devuelve (None, 0).
        """
        vuelo_mayor = None
        max_seg = 0

        for v in self.vuelos:
            salida_iso = (v.departure or {}).get("scheduled")
            llegada_iso = (v.arrival or {}).get("scheduled")
            salida = Vuelo._parse_iso_z(salida_iso)
            llegada = Vuelo._parse_iso_z(llegada_iso)
            if salida and llegada:
                dur = (llegada - salida).total_seconds()
                if dur > max_seg:
                    max_seg = dur
                    vuelo_mayor = v

        if vuelo_mayor:
            return vuelo_mayor, round(max_seg / 3600, 2)
        return None, 0.0
