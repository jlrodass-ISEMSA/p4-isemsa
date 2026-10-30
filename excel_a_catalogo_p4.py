# -*- coding: utf-8 -*-
"""
excel_a_catalogo_p4.py
Regenera el diccionario `compatibilidad_fluido_material` de catalogo_fluido_material_p4.py
a partir del Excel de compatibilidad química (hoja Tabelle1) y, si existe, de la hoja
"Correcciones" (que documenta las celdas corregidas el 30/10/2026).

Uso (PowerShell, desde la carpeta que contiene los tres archivos):
    python excel_a_catalogo_p4.py --excel "Material Chemical Compatibility.xlsx" ^
        --base catalogo_fluido_material_p4.py --salida catalogo_fluido_material_p4_NUEVO.py

El script NO sobreescribe nada por su cuenta: escribe solo en --salida.
La parte del módulo posterior al diccionario (funciones, textos) se toma de --base;
solo se actualizan la cabecera y los dos textos "catalogo" (idempotente).

Reglas (las mismas del .py vigente):
  * Escala del Excel: 0 = "Sin dato de laboratorio", 1 = Excelente, 2 = Buena, 3 = Regular, 4 = No compatible.
  * Orden de fluidos = primera aparición en el Excel; si un nombre se repite, gana la última fila.
  * Orden de materiales: EPDM, NBR, H-NBR, C-HPU, MVQ, FPM, POM, PTFE, HPU, UHMWPE, AFLAS, PA.
  * Columnas por nombre de encabezado, no por posición.
"""
import argparse, re, sys
import openpyxl

MATERIALES = ["EPDM", "NBR", "H-NBR", "C-HPU", "MVQ", "FPM", "POM", "PTFE", "HPU", "UHMWPE", "AFLAS", "PA"]
ESCALA = {0: "Sin dato de laboratorio", 1: "Excelente", 2: "Buena", 3: "Regular", 4: "No compatible"}
# Único nombre del Excel que el .py vigente escribe distinto (sin comillas internas).
ALIAS_NOMBRE = {'TEXAMATIC "A" TRANSMISSION-OIL': 'TEXAMATIC A TRANSMISSION-OIL'}
FECHA = "30/10/2026"

CAB_VIEJO_1 = "# Este módulo preserva la tabla del proveedor como FUENTE TÉCNICA PRIMARIA."
CAB_NUEVO_1 = ("# Base: tabla de compatibilidad del proveedor DMH con 24 celdas corregidas el 30/10/2026\n"
               "# con Aero Rubber, ISM y Little Giant (cada celda corregida lleva su comentario en el diccionario).")
CAB_VIEJO_2 = "# 1. NO alterar el contenido del catálogo del proveedor."
CAB_NUEVO_2 = "# 1. Conservar la tabla DMH; solo difieren las 24 celdas corregidas el 30/10/2026 (comentadas)."
CAB_VIEJO_3 = "#   Diccionario compatibilidad_fluido_material provisto por proveedor."
CAB_NUEVO_3 = "#   Tabla DMH (Material Chemical Compatibility.xlsx) y corrección Aero, ISM y Little Giant del 30/10/2026."
CAT_VIEJO = '"catalogo": "Tabla de compatibilidad química del proveedor"'
CAT_NUEVO = '"catalogo": "Tabla proveedor DMH y corrección Aero, ISM y Little Giant"'


def comillas(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def leer_excel(ruta):
    wb = openpyxl.load_workbook(ruta, data_only=True)
    ws = wb["Tabelle1"]
    enc = [c.value for c in ws[1]]
    col = {m: enc.index(m) for m in MATERIALES}
    datos, orden = {}, []
    for r in ws.iter_rows(min_row=3, values_only=True):   # fila 2 = aviso legal de DMH
        nombre = r[0]
        if nombre is None:
            continue
        nombre = ALIAS_NOMBRE.get(nombre, nombre)
        if nombre not in datos:
            orden.append(nombre)
        datos[nombre] = {m: r[col[m]] for m in MATERIALES}
    correcciones = {}
    if "Correcciones" in wb.sheetnames:
        wc = wb["Correcciones"]
        cab = [c.value for c in wc[1]]
        i = {k: cab.index(k) for k in ("Fluido", "Material", "Valor DMH (texto)", "Valor nuevo (texto)", "Fuente 1", "Fuente 2")}
        for r in wc.iter_rows(min_row=2, values_only=True):
            if r[i["Fluido"]] and r[i["Material"]] in MATERIALES:
                correcciones[(ALIAS_NOMBRE.get(r[i["Fluido"]], r[i["Fluido"]]), r[i["Material"]])] = (
                    r[i["Valor DMH (texto)"]], r[i["Valor nuevo (texto)"]], r[i["Fuente 1"]], r[i["Fuente 2"]])
    return datos, orden, correcciones


def construir_diccionario(datos, orden, correcciones):
    usadas = set()
    lineas = ["compatibilidad_fluido_material = {"]
    for nombre in orden:
        lineas.append(f"    {comillas(nombre)}: {{")
        for m in MATERIALES:
            v = datos[nombre][m]
            if v not in ESCALA:
                sys.exit(f"ERROR: valor fuera de escala 0-4 en {nombre} / {m}: {v!r}")
            texto = ESCALA[v]
            linea = f"        {comillas(m)}: {comillas(texto)},"
            if (nombre, m) in correcciones:
                antes, nuevo, f1, f2 = correcciones[(nombre, m)]
                if nuevo != texto:
                    sys.exit(f"ERROR: la hoja Correcciones dice «{nuevo}» pero la celda tiene «{texto}» ({nombre} / {m})")
                linea += f'  # {FECHA}: antes "{antes}" (DMH); {f1} + {f2} = {nuevo}'
                usadas.add((nombre, m))
            lineas.append(linea)
        lineas.append("    },")
    lineas.append("}")
    faltan = set(correcciones) - usadas
    if faltan:
        sys.exit(f"ERROR: filas de Correcciones sin celda en Tabelle1: {sorted(faltan)}")
    return "\n".join(lineas)


def cola_desde_base(ruta_base):
    texto = open(ruta_base, encoding="utf-8", newline="").read()
    if "\r" in texto:
        sys.exit("ERROR: el archivo base tiene CRLF; se esperaba LF")
    lineas = texto.split("\n")
    ini = lineas.index("compatibilidad_fluido_material = {")
    fin = next(k for k in range(ini + 1, len(lineas)) if lineas[k] == "}")
    cola = "\n".join(lineas[fin + 1:])
    for viejo, nuevo in ((CAB_VIEJO_1, CAB_NUEVO_1), (CAB_VIEJO_2, CAB_NUEVO_2), (CAB_VIEJO_3, CAB_NUEVO_3), (CAT_VIEJO, CAT_NUEVO)):
        if viejo in cola:
            cola = cola.replace(viejo, nuevo)
        elif nuevo not in cola:
            sys.exit(f"ERROR: no se encontró el texto esperado en la base: {viejo[:60]}")
    return "\n".join(lineas[:ini]) + ("\n" if ini else ""), cola


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    datos, orden, corr = leer_excel(a.excel)
    antes, cola = cola_desde_base(a.base)
    salida = antes + construir_diccionario(datos, orden, corr) + "\n" + cola
    with open(a.salida, "w", encoding="utf-8", newline="") as f:
        f.write(salida)
    print(f"Fluidos: {len(orden)} | celdas corregidas: {len(corr)} | escrito: {a.salida}")


if __name__ == "__main__":
    main()
