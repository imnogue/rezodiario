# -*- coding: utf-8 -*-
"""Citas de las lecturas de la misa de cada día (solo las citas, no el texto: el texto tiene derechos).
Fuente: dominicos.org (sigue el calendario litúrgico de España).
Guarda en content/dias/<fecha>.json → "lecturas": [{"tipo": "Primera lectura", "titulo": "Lectura de la carta…, 2, 12-22"}, …]
Uso: python3 scripts/lecturas.py [--todas] [--fechas AAAA-MM-DD,…]
"""
import argparse, glob, html, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def limpia(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()

def lecturas(fecha):
    y, m, d = fecha.split("-")
    url = f"https://www.dominicos.org/predicacion/evangelio-del-dia/{d}-{m}-{y}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (RezoDiario; +https://rezodiario.com)"})
    with urllib.request.urlopen(req, timeout=60) as r: s = r.read().decode("utf-8", "ignore")
    m = re.search(r'"@type":\s*"Book".{0,200}?"description":\s*\[(.*?)\]', s, re.S)
    if not m: return None, url
    items = [limpia(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
    lec, sal, ev = [], None, None
    for t in items:
        t = re.split(r"\s*R/\.?", t)[0].strip()  # sin la respuesta del salmo (es texto litúrgico)
        if not t: continue
        if t.lower().startswith("salmo") or t.lower().startswith("sal "): sal = sal or t
        elif "evangelio" in t.lower(): ev = ev or t
        else: lec.append(t)
    out = []
    if lec: out.append({"tipo": "Primera lectura", "titulo": lec[0]})
    if sal: out.append({"tipo": "Salmo", "titulo": sal})
    if len(lec) > 1: out.append({"tipo": "Segunda lectura", "titulo": lec[1]})
    if ev: out.append({"tipo": "Evangelio", "titulo": ev})
    return out, url

def main():
    p = argparse.ArgumentParser(); p.add_argument("--todas", action="store_true"); p.add_argument("--fechas", default="")
    a = p.parse_args()
    fs = sorted(glob.glob(os.path.join(ROOT, "content/dias/*.json")))
    want = {x.strip() for x in a.fechas.split(",") if x.strip()}
    n = 0
    for f in fs:
        j = json.load(open(f, encoding="utf-8")); fecha = j["date"]
        if want and fecha not in want: continue
        if j.get("lecturas") and not a.todas and not want: continue
        try: ls, url = lecturas(fecha)
        except Exception as e: print(f"{fecha}: no he podido leerlo ({e})"); continue
        if not ls or not any(x["tipo"] == "Evangelio" for x in ls): print(f"{fecha}: sin lecturas todavía"); continue
        ev = next(x["titulo"] for x in ls if x["tipo"] == "Evangelio")
        if j.get("refL") and j["refL"].split(",")[0].split(" ")[-1] not in ev: print(f"  Aviso: el Evangelio de la web ({j['refL']}) no coincide con «{ev}»")
        j["lecturas"] = ls; j["lecturasUrl"] = url
        json.dump(j, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        n += 1; print(f"{fecha}: " + " · ".join(x["titulo"] for x in ls)); time.sleep(1.2)
    print(f"Terminado: {n} días actualizados.")

if __name__ == "__main__": main()
