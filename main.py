
#Rutas básicas:
#  /                -> Lista simple de llegadas y partidas desde archivo local JSON.
#  /vuelo/<ident>   -> Detalle de un vuelo buscado por código.
#  /actualizar      -> Actualiza datos vía API FlightAware si hay FLIGHTAWARE_API_KEY.



from __future__ import annotations

import os
import json
import argparse
from pathlib import Path
from typing import Any, Dict

from flask import Flask, render_template, abort, request, redirect, url_for, flash

from backend import api_client
from backend.procesador import mapear_vuelos, crear_vuelo_desde_api, buscar_vuelo_por_codigo

APP_ROOT = Path(__file__).parent
DATA_FILE = APP_ROOT / "backend" / "vuelos_prueba.json"

def cargar_datos_local() -> Dict[str, Any]:
    if not DATA_FILE.exists():
        return {}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def guardar_datos_local(data: Dict[str, Any]) -> None:
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"No se pudo guardar JSON local: {e}")

def crear_app() -> Flask:
	app = Flask(__name__)
	app.secret_key = "dev-secret"  # para flash messages

	@app.route("/")
	def index():
		data = cargar_datos_local()
		# PASO 1: Mapear datos crudos JSON a objetos Vuelo modelados
		vuelos_mapeados = mapear_vuelos(data)
		arrivals = vuelos_mapeados["arrivals"]
		departures = vuelos_mapeados["departures"]
		
		# PASO 2: Pasar objetos modelados al template
		return render_template(
			"index.html",
			arrivals=arrivals,
			departures=departures,
			total_arrivals=len(arrivals),
			total_departures=len(departures),
		)

	@app.route("/vuelo/<ident>")
	def vuelo_detalle(ident: str):
		data = cargar_datos_local()
		vuelo_raw = buscar_vuelo_por_codigo(data, ident)
		if not vuelo_raw:
			abort(404, description="Vuelo no encontrado")
		# Convertir a objeto Vuelo modelado
		vuelo = crear_vuelo_desde_api(vuelo_raw)
		return render_template("vuelo.html", vuelo=vuelo)

	@app.route("/actualizar")
	def actualizar():
		aeropuerto = request.args.get("airport", "SUMU")
		api_key = "UlHHqAChlmsEAGUv301gaRGqA72PGGEl"
		api_client.API_KEY = api_key  # type: ignore
		try:
			arrivals = api_client.obtener_vuelos_por_aeropuerto(aeropuerto, tipo="arrivals")
			departures = api_client.obtener_vuelos_por_aeropuerto(aeropuerto, tipo="departures")
			combined = {
				"arrivals": arrivals.get("arrivals") or arrivals.get("flights") or [],
				"departures": departures.get("departures") or departures.get("flights") or [],
			}
			guardar_datos_local(combined)
			flash("Datos actualizados", "success")
		except Exception as e:
			flash(f"Error actualizando: {e}", "danger")
		return redirect(url_for("index"))

	return app

app = crear_app()

if __name__ == "__main__":
	# Permite ejecutar: python main.py --port 5051 --host 127.0.0.1
	parser = argparse.ArgumentParser(description="Servidor Flask para seguimiento de vuelos")
	parser.add_argument("--port", type=int, default=5051, help="Puerto de escucha (default 5051)")
	parser.add_argument("--host", default="0.0.0.0", help="Host de escucha (default 0.0.0.0)")
	parser.add_argument("--no-debug", action="store_true", help="Desactivar modo debug")
	args = parser.parse_args()

	debug = not args.no_debug
	app.run(debug=debug, host=args.host, port=args.port)

