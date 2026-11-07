# -*- coding: utf-8 -*-
"""
Crea la geodatabase (GDB) con dominios y fotos adjuntas a partir de datos.json y la carpeta fotos/.

Uso (ArcGIS Pro 3.x):
  1. Descomprime el ZIP exportado por la app en una carpeta.
  2. Abre ArcGIS Pro > pestana Analisis > Python > Ventana Python, o ejecuta este archivo con
     "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\Scripts\\propy.bat" crear_gdb.py
  3. Resultado: inventario_peatonal.gdb en la misma carpeta.
"""
import os, json
import arcpy

try:
    AQUI = os.path.dirname(os.path.abspath(__file__))
except NameError:               # Ventana Python de Pro: cambia esta ruta a la carpeta del ZIP
    AQUI = os.getcwd()

SR_GDB = 9377                   # sistema de las geometrias en la GDB: 9377, 3115 o 4326
GDB_NOMBRE = "inventario_peatonal.gdb"

SI_NO = ["Sí", "No"]
EST = ["Bueno", "Regular", "Malo"]
DOMINIOS = {
    "zona": ["Ingeniería", "Ciencias", "Administración", "Idiomas", "Artes Integradas"],
    "grupo": ["G1", "G2", "G3", "G4", "G5"],
    "jerarquia": ["Sendero local", "Sendero adaptado", "Acera", "Cruce peatonal"],
    "desnivel": ["Ninguno", "Escalones", "Bordillo", "Rampa"],
    "pavimento": ["Rígido", "Flexible", "Semirrígido", "Natural"],
    "estado": EST,
    "podotactil": ["Sí", "No", "Parcial"],
    "si_no": SI_NO,
    "tipo_mobiliario": ["Banca", "Luminaria", "Papelera", "Fuente de agua", "Árbol"],
    "sombra": ["Sin sombra", "Parcial", "Total"],
    "categoria": ["Fijo", "Temporal"],
    "tipo_obstaculo": ["Poste", "Armario o gabinete", "Paradero", "Vegetación",
                       "Comercio informal", "Vehículos", "Obras"],
}

POS = [("lat", "DOUBLE", None), ("lon", "DOUBLE", None), ("alt", "DOUBLE", None),
       ("e3115", "DOUBLE", None), ("n3115", "DOUBLE", None), ("e9377", "DOUBLE", None),
       ("n9377", "DOUBLE", None), ("solucion", "TEXT", None), ("pdop", "DOUBLE", None),
       ("hdop", "DOUBLE", None), ("hrms", "DOUBLE", None), ("vrms", "DOUBLE", None),
       ("sats", "SHORT", None), ("hora", "TEXT", None)]

CAMPOS = {
    "tramos": [("codigo", "TEXT", None), ("zona", "SHORT", "zona"), ("grupo", "SHORT", "grupo"),
               ("jerarquia", "SHORT", "jerarquia"), ("ancho_total", "DOUBLE", None),
               ("ancho_efectivo", "DOUBLE", None), ("desnivel", "SHORT", "desnivel"),
               ("altura_desnivel", "DOUBLE", None), ("pavimento", "SHORT", "pavimento"),
               ("estado", "SHORT", "estado"), ("podotactil", "SHORT", "podotactil"),
               ("galibo_h", "DOUBLE", None), ("galibo_v", "DOUBLE", None),
               ("observaciones", "TEXT", None), ("longitud_m", "DOUBLE", None),
               ("creado", "TEXT", None)],
    "mobiliario": [("tipo", "SHORT", "tipo_mobiliario"), ("estado", "SHORT", "estado"),
                   ("funciona", "SHORT", "si_no"), ("sombra", "SHORT", "sombra"),
                   ("observaciones", "TEXT", None)] + POS + [("creado", "TEXT", None)],
    "obstaculos": [("categoria", "SHORT", "categoria"), ("tipo", "SHORT", "tipo_obstaculo"),
                   ("ancho_libre", "DOUBLE", None), ("afecta", "SHORT", "si_no"),
                   ("observaciones", "TEXT", None)] + POS + [("creado", "TEXT", None)],
    "tramos_vertices": [("tramo_codigo", "TEXT", None), ("orden", "SHORT", None)] + POS,
}


def codigo(dom, valor):
    """Devuelve el codigo numerico del dominio para una etiqueta (o None)."""
    if valor in (None, ""):
        return None
    lista = DOMINIOS[dom]
    return lista.index(valor) + 1 if valor in lista else None


def xy(p):
    if SR_GDB == 3115:
        return p["x3115"], p["y3115"]
    if SR_GDB == 4326:
        return p["lon"], p["lat"]
    return p["x9377"], p["y9377"]


def pos_vals(p):
    return {"lat": p["lat"], "lon": p["lon"], "alt": p.get("alt"), "e3115": p["x3115"],
            "n3115": p["y3115"], "e9377": p["x9377"], "n9377": p["y9377"],
            "solucion": p.get("solucion"), "pdop": p.get("pdop"), "hdop": p.get("hdop"),
            "hrms": p.get("hrms"), "vrms": p.get("vrms"), "sats": p.get("sats"),
            "hora": p.get("hora")}


def crear_fc(gdb, nombre, tipo, sr, extra_uid=True):
    fc = os.path.join(gdb, nombre)
    arcpy.management.CreateFeatureclass(gdb, nombre, tipo, spatial_reference=sr)
    for nom, t, dom in CAMPOS[nombre]:
        if t == "TEXT":
            arcpy.management.AddField(fc, nom, "TEXT", field_length=500 if nom == "observaciones" else 100)
        else:
            arcpy.management.AddField(fc, nom, t)
        if dom:
            arcpy.management.AssignDomainToField(fc, nom, "dom_" + dom)
    if extra_uid:
        arcpy.management.AddField(fc, "uid", "TEXT", field_length=50)
    return fc


def valores(nombre, r, p=None):
    """Valores de los campos de una capa, en el orden de CAMPOS, para el cursor."""
    base = dict(r)
    if p:
        base.update(pos_vals(p))
    salida = []
    for nom, t, dom in CAMPOS[nombre]:
        v = base.get(nom)
        salida.append(codigo(dom, v) if dom else v)
    return salida


def main():
    with open(os.path.join(AQUI, "datos.json"), encoding="utf-8") as f:
        datos = json.load(f)["capas"]
    sr = arcpy.SpatialReference(SR_GDB)
    gdb = os.path.join(AQUI, GDB_NOMBRE)
    if arcpy.Exists(gdb):
        arcpy.management.Delete(gdb)
    arcpy.management.CreateFileGDB(AQUI, GDB_NOMBRE)

    for dom, etiquetas in DOMINIOS.items():
        nombre = "dom_" + dom
        arcpy.management.CreateDomain(gdb, nombre, dom, "SHORT", "CODED")
        for i, e in enumerate(etiquetas, start=1):
            arcpy.management.AddCodedValueToDomain(gdb, nombre, i, e)

    fotos_por_fc = {}

    # Tramos (linea) y sus vertices (puntos)
    fc_t = crear_fc(gdb, "tramos", "POLYLINE", sr)
    fc_v = crear_fc(gdb, "tramos_vertices", "POINT", sr, extra_uid=False)
    nom_t = [c[0] for c in CAMPOS["tramos"]]
    nom_v = [c[0] for c in CAMPOS["tramos_vertices"]]
    with arcpy.da.InsertCursor(fc_t, ["SHAPE@"] + nom_t + ["uid"]) as ct, \
         arcpy.da.InsertCursor(fc_v, ["SHAPE@"] + nom_v) as cv:
        for r in datos["tramos"]:
            pts = [arcpy.Point(*xy(p)) for p in r["vertices"]]
            ct.insertRow([arcpy.Polyline(arcpy.Array(pts), sr)] + valores("tramos", r) + [r["uid"]])
            fotos_por_fc.setdefault(fc_t, []).extend((r["uid"], x) for x in r["fotos"])
            for i, p in enumerate(r["vertices"], start=1):
                rv = {"tramo_codigo": r["codigo"], "orden": i}
                cv.insertRow([arcpy.PointGeometry(arcpy.Point(*xy(p)), sr)] + valores("tramos_vertices", rv, p))

    # Mobiliario y obstaculos (puntos)
    for capa in ("mobiliario", "obstaculos"):
        fc = crear_fc(gdb, capa, "POINT", sr)
        nombres = [c[0] for c in CAMPOS[capa]]
        with arcpy.da.InsertCursor(fc, ["SHAPE@"] + nombres + ["uid"]) as cur:
            for r in datos[capa]:
                p = r["posicion"]
                cur.insertRow([arcpy.PointGeometry(arcpy.Point(*xy(p)), sr)] + valores(capa, r, p) + [r["uid"]])
                fotos_por_fc.setdefault(fc, []).extend((r["uid"], x) for x in r["fotos"])

    # Fotos como adjuntos (attachments)
    for fc, lista in fotos_por_fc.items():
        if not lista:
            continue
        arcpy.management.EnableAttachments(fc)
        tabla = os.path.join(gdb, "match_" + os.path.basename(fc))
        arcpy.management.CreateTable(gdb, "match_" + os.path.basename(fc))
        arcpy.management.AddField(tabla, "uid", "TEXT", field_length=50)
        arcpy.management.AddField(tabla, "ruta", "TEXT", field_length=255)
        with arcpy.da.InsertCursor(tabla, ["uid", "ruta"]) as cur:
            for uid, archivo in lista:
                cur.insertRow([uid, os.path.join(AQUI, "fotos", archivo)])
        arcpy.management.AddAttachments(fc, "uid", tabla, "uid", "ruta")
        arcpy.management.Delete(tabla)

    print("Listo: " + gdb)


main()
