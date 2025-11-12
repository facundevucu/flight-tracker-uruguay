#ejercicio 1.2 de la semana 2
import re

class Aerolinea:
    def __init__(self, nombre, codigo_iata, codigo_icao):
        self.nombre = nombre
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao

    def __str__(self):
        codigo = self.codigo_iata or self.codigo_icao or "N/A"
        return f"{self.nombre} ({codigo})"


class Aeronave:
    def __init__(self, matricula, codigo_iata, codigo_icao):
        self.matricula = matricula if self._matricula_valida(matricula) else "Matrícula inválida"
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao

    def _matricula_valida(self, matricula):
        if not matricula or matricula == "N/A":
            return False
        return bool(re.match(r"^[A-Z]{1,2}-[A-Z0-9]{3,5}$", matricula))

    def es_uruguaya(self):
        return bool(re.match(r"^CX-[A-Z]{3}$", self.matricula))

    def __str__(self):
        bandera = "🇺🇾" if self.es_uruguaya() else ""
        return f"{self.matricula} {bandera}".strip()


class Aeropuerto:
    def __init__(self, nombre, codigo_iata, codigo_icao, pais):
        self.nombre = nombre
        self.codigo_iata = codigo_iata
        self.codigo_icao = codigo_icao if self._icao_valido(codigo_icao) else "Código ICAO inválido"
        self.pais = pais

    def _icao_valido(self, codigo):
        return bool(re.match(r"^[A-Z]{4}$", str(codigo)))
        #regex : ^ al inicio, 4 letras mayusculas y $ al final

    def __str__(self):
        return f"{self.nombre} ({self.codigo_icao}) - {self.pais}"


class Vuelo:
    def __init__(self, numero_vuelo, aerolinea, aeronave, salida, llegada, estado):
        self.numero_vuelo = numero_vuelo if self._numero_vuelo_valido(numero_vuelo) else "Código inválido"
        self.aerolinea = aerolinea
        self.aeronave = aeronave
        self.salida = salida
        self.llegada = llegada
        self.estado = estado

    def _numero_vuelo_valido(self, numero):
        return bool(re.match(r"^[A-Z0-9]{2,3}\d{1,4}$", str(numero)))

    def mostrar_info(self):
        print(f"✈️ {self.numero_vuelo} - {self.aerolinea}")
        print(f"  Origen: {self.salida}")
        print(f"  Destino: {self.llegada}")
        print(f"  Aeronave: {self.aeronave}")
        print(f"  Estado: {self.estado}")
        print("-" * 40)
class VueloBase:
    def __init__(self, datos):
        self.ident = (datos.get("ident") or "").upper()
        self.operador = (datos.get("operator_icao") or "").upper()
        self.tipo = (datos.get("aircraft_type") or "").upper()
        self.iata = datos.get("operator_iata")

    def clasificar(self):
        return "Desconocido"


class VueloMilitar(VueloBase):
    def clasificar(self):
        return "Militar"


class VueloPrivado(VueloBase):
    def __init__(self, datos, pais):
        super().__init__(datos)
        self.pais = pais

    def clasificar(self):
        return f"Privado ({self.pais})"


class VueloComercial(VueloBase):
    def clasificar(self):
        return "Comercial"     



