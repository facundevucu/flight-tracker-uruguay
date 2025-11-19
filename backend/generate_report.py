import json
from collections import Counter
import html
from functions import normalizar_aerolinea, clasificar_tipo_vuelo

INPUT = "vuelos_prueba.json"
OUTPUT = "report.html"

def safe(s):
    return html.escape(str(s)) if s is not None else "N/A"

def procesar(vuelos):
    filas = []
    cont_aer = Counter()
    cont_tipo = Counter()
    for v in vuelos:
        try:
            codigo = v.get("operator_iata") or v.get("operator_icao") or "---"
            nombre = normalizar_aerolinea(codigo)
            tipo = clasificar_tipo_vuelo(v)
            ident = v.get("ident", "N/A")
            origen = (v.get("origin") or {}).get("code_iata", "Desconocido")
            destino = (v.get("destination") or {}).get("code_iata", "Desconocido")
            filas.append({
                "ident": ident,
                "codigo": codigo,
                "nombre": nombre,
                "origen": origen,
                "destino": destino,
                "tipo": tipo
            })
            cont_aer[nombre] += 1
            cont_tipo[tipo] += 1
        except Exception as e:
            print(f"⚠ Error procesando vuelo: {e}")
            continue
    return filas, cont_aer, cont_tipo

try:
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f" Error: archivo '{INPUT}' no encontrado")
    exit(1)
except json.JSONDecodeError as e:
    print(f" Error: JSON inválido - {e}")
    exit(1)
except Exception as e:
    print(f" Error inesperado al leer archivo: {e}")
    exit(1)

try:
    arrivals = data.get("arrivals", [])
    departures = data.get("departures", [])
    
    if not isinstance(arrivals, list):
        raise TypeError("'arrivals' debe ser una lista")
    if not isinstance(departures, list):
        raise TypeError("'departures' debe ser una lista")
    
    print(f"✓ Cargados {len(arrivals)} arrivals y {len(departures)} departures")
    
    a_rows, a_aer, a_tipo = procesar(arrivals)
    d_rows, d_aer, d_tipo = procesar(departures)
    
    print(f"✓ Procesados {len(a_rows)} arrivals válidos y {len(d_rows)} departures válidos")

except TypeError as e:
    print(f" Error de tipo: {e}")
    exit(1)
except Exception as e:
    print(f" Error procesando datos: {e}")
    exit(1)

def top_html(counter, limit=10):
    items = "".join(f"<li>{safe(k)}: {v}</li>" for k,v in counter.most_common(limit))
    return f"<ul>{items}</ul>"

html_parts = []
css = """
:root {
  --background: oklch(0.9900 0 0);
  --foreground: oklch(0 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0 0 0);
  --popover: oklch(0.9900 0 0);
  --popover-foreground: oklch(0 0 0);
  --primary: oklch(0 0 0);
  --primary-foreground: oklch(1 0 0);
  --secondary: oklch(0.9400 0 0);
  --secondary-foreground: oklch(0 0 0);
  --muted: oklch(0.9700 0 0);
  --muted-foreground: oklch(0.4400 0 0);
  --accent: oklch(0.9400 0 0);
  --accent-foreground: oklch(0 0 0);
  --destructive: oklch(0.6300 0.1900 23.0300);
  --destructive-foreground: oklch(1 0 0);
  --border: oklch(0.9200 0 0);
  --input: oklch(0.9400 0 0);
  --ring: oklch(0 0 0);
  --chart-1: oklch(0.8100 0.1700 75.3500);
  --chart-2: oklch(0.5500 0.2200 264.5300);
  --chart-3: oklch(0.7200 0 0);
  --chart-4: oklch(0.9200 0 0);
  --chart-5: oklch(0.5600 0 0);
  --sidebar: oklch(0.9900 0 0);
  --sidebar-foreground: oklch(0 0 0);
  --sidebar-primary: oklch(0 0 0);
  --sidebar-primary-foreground: oklch(1 0 0);
  --sidebar-accent: oklch(0.9400 0 0);
  --sidebar-accent-foreground: oklch(0 0 0);
  --sidebar-border: oklch(0.9400 0 0);
  --sidebar-ring: oklch(0 0 0);
  --font-sans: Geist, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-serif: Georgia, serif;
  --font-mono: "Geist Mono", monospace;
  --radius: 0.5rem;
  --shadow-2xs: 0px 1px 2px 0px hsl(0 0% 0% / 0.09);
  --shadow-xs: 0px 1px 2px 0px hsl(0 0% 0% / 0.09);
  --shadow-sm: 0px 1px 2px 0px hsl(0 0% 0% / 0.18), 0px 1px 2px -1px hsl(0 0% 0% / 0.18);
  --shadow: 0px 1px 2px 0px hsl(0 0% 0% / 0.18), 0px 1px 2px -1px hsl(0 0% 0% / 0.18);
  --shadow-md: 0px 1px 2px 0px hsl(0 0% 0% / 0.18), 0px 2px 4px -1px hsl(0 0% 0% / 0.18);
  --shadow-lg: 0px 1px 2px 0px hsl(0 0% 0% / 0.18), 0px 4px 6px -1px hsl(0 0% 0% / 0.18);
  --shadow-xl: 0px 1px 2px 0px hsl(0 0% 0% / 0.18), 0px 8px 10px -1px hsl(0 0% 0% / 0.18);
  --shadow-2xl: 0px 1px 2px 0px hsl(0 0% 0% / 0.45);
}

.dark {
  --background: oklch(0 0 0);
  --foreground: oklch(1 0 0);
  --card: oklch(0.1400 0 0);
  --card-foreground: oklch(1 0 0);
  --popover: oklch(0.1800 0 0);
  --popover-foreground: oklch(1 0 0);
  --primary: oklch(1 0 0);
  --primary-foreground: oklch(0 0 0);
  --secondary: oklch(0.2500 0 0);
  --secondary-foreground: oklch(1 0 0);
  --muted: oklch(0.2300 0 0);
  --muted-foreground: oklch(0.7200 0 0);
  --accent: oklch(0.3200 0 0);
  --accent-foreground: oklch(1 0 0);
  --destructive: oklch(0.6900 0.2000 23.9100);
  --destructive-foreground: oklch(0 0 0);
  --border: oklch(0.2600 0 0);
  --input: oklch(0.3200 0 0);
  --ring: oklch(0.7200 0 0);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
body {
  font-family: var(--font-sans);
  background-color: var(--background);
  color: var(--foreground);
  padding: 2rem;
  line-height: 1.6;
}

h1, h2, h3 { margin-top: 1.5rem; margin-bottom: 1rem; font-weight: 600; }
h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; color: var(--primary); }
h3 { font-size: 1.25rem; }

p { margin-bottom: 1rem; color: var(--muted-foreground); }

ul, ol { margin-left: 1.5rem; margin-bottom: 1rem; }
li { margin-bottom: 0.5rem; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  background-color: var(--card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

thead {
  background-color: var(--secondary);
  border-bottom: 2px solid var(--border);
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--foreground);
}

td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  color: var(--card-foreground);
}

tbody tr:hover {
  background-color: var(--muted);
}

tbody tr:last-child td {
  border-bottom: none;
}

ul {
  background-color: var(--card);
  padding: 1rem 1.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  list-style-position: inside;
}

li {
  color: var(--card-foreground);
  padding: 0.5rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}
"""

html_parts.append("<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Reporte Vuelos</title>")
html_parts.append(f"<style>{css}</style></head><body>")
html_parts.append(f"<h1>Reporte simple - {safe(INPUT)}</h1>")
html_parts.append(f"<p>Arrivals: {len(a_rows)} — Departures: {len(d_rows)}</p>")

html_parts.append("<h2>Top aerolíneas (Arrivals)</h2>")
html_parts.append(top_html(a_aer))
html_parts.append("<h2>Top tipos (Arrivals)</h2>")
html_parts.append(top_html(a_tipo))

html_parts.append("<h2>Top aerolíneas (Departures)</h2>")
html_parts.append(top_html(d_aer))
html_parts.append("<h2>Top tipos (Departures)</h2>")
html_parts.append(top_html(d_tipo))

def tabla_html(rows, titulo, limit=15):
    rows = rows[:limit]
    header = "<table><thead><tr><th>Ident</th><th>Op</th><th>Aerolínea</th><th>Origen → Destino</th><th>Tipo</th></tr></thead><tbody>"
    body = ""
    for r in rows:
        body += ("<tr>"
                 f"<td>{safe(r['ident'])}</td>"
                 f"<td>{safe(r['codigo'])}</td>"
                 f"<td>{safe(r['nombre'])}</td>"
                 f"<td>{safe(r['origen'])} → {safe(r['destino'])}</td>"
                 f"<td>{safe(r['tipo'])}</td>"
                 "</tr>")
    footer = "</tbody></table>"
    return f"<h2>{titulo} (primeros {min(limit, len(rows))})</h2>" + header + body + footer

html_parts.append(tabla_html(a_rows, "Arrivals"))
html_parts.append(tabla_html(d_rows, "Departures"))

html_parts.append("</body></html>")

try:
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    print(f" Generado: {OUTPUT}")
except IOError as e:
    print(f" Error escribiendo archivo: {e}")
    exit(1)
except Exception as e:
    print(f" Error inesperado: {e}")
    exit(1)