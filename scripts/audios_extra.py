# -*- coding: utf-8 -*-
"""Audios de las oraciones y del Santo Rosario con ElevenLabs.
Uso (lo lanza la acción «Audios de oraciones y Rosario» de GitHub):
  python3 scripts/audios_extra.py [--solo oraciones|rosario] [--sobrescribir] [--max N] [--prueba] [--sin-subir]

- Oraciones: un MP3 por oración (título + texto) en Supabase audios/oraciones/<slug>.mp3.
  Se guarda en content/oraciones/<slug>.json → "audio" y "duracion".
- Rosario: cada texto se graba UNA sola vez (Padre nuestro, Ave María, Gloria, Credo, Salve, anuncio de cada misterio…)
  y la web los encadena: el Ave María se graba una vez y suena 53 veces. Enlaces en content/voces-rosario.json.
Antes de gastar créditos busca la misma frase en el historial de ElevenLabs y la descarga gratis.
"""
import argparse, glob, json, os, re, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_audios as G

ROOT, C = G.ROOT, G.C
br = G.br

def texto_voz(t):
    """Saltos de línea → pausas suaves para que la voz respire."""
    t = re.sub(r"\n\s*\n", br(1.2), t.strip())
    return re.sub(r"\n", br(0.6), t)

def trozos(t, n=2400):
    """ElevenLabs acepta textos de tamaño limitado: partimos por párrafos."""
    if len(t) <= n: return [t]
    out, cur = [], ""
    for p in re.split(r"(?<=\.)\s+", t):
        if len(cur) + len(p) + 1 > n and cur: out.append(cur); cur = p
        else: cur = (cur + " " + p).strip()
    if cur: out.append(cur)
    return out

def grabar(texto, out_mp3, a, cola=1.2):
    """Texto → MP3 mono normalizado, con un pequeño silencio al principio y al final."""
    with tempfile.TemporaryDirectory() as tmp:
        partes = []
        sil = os.path.join(tmp, "sil.wav"); G.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={G.SR}:cl=mono", "-t", "0.6", sil])
        partes.append(sil)
        for i, tz in enumerate(trozos(texto)):
            mp3 = os.path.join(tmp, f"{i}.mp3"); G.tts(tz, mp3, a)
            wav = os.path.join(tmp, f"{i}.wav"); G.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(G.SR), "-ac", "1", wav]); partes.append(wav)
        fin = os.path.join(tmp, "fin.wav"); G.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={G.SR}:cl=mono", "-t", str(cola), fin]); partes.append(fin)
        lista = os.path.join(tmp, "l.txt"); open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
        voz = os.path.join(tmp, "v.wav"); G.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", voz])
        G.run(["ffmpeg", "-y", "-loglevel", "error", "-i", voz, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(G.SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k",
               "-metadata", "artist=Rezo Diario", out_mp3])
    return G.dur(out_mp3)

def oraciones(a, outdir):
    hechos = 0
    for f in sorted(glob.glob(os.path.join(C, "oraciones", "*.json"))):
        p = json.load(open(f, encoding="utf-8"))
        if p.get("audio") and not a.sobrescribir: continue
        if hechos >= a.max: G.log(f"Límite de {a.max} oraciones en esta tanda."); break
        G.log(f"Oración · {p['t']}")
        mp3 = os.path.join(outdir, f"{p['slug']}.mp3")
        secs = grabar(p["t"] + "." + br(1.2) + texto_voz(p["x"]), mp3, a)
        hechos += 1
        if a.sin_subir: continue
        url = G.subir(mp3, f"oraciones/{p['slug']}.mp3", a)
        p["audio"] = f"{url}?v={int(time.time())}"; p["duracion"] = round(secs, 1)
        json.dump(p, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        G.log(f"  {secs:.0f} s · subido")

def rosario_textos():
    """Las piezas que suenan en el Rosario. Las claves coinciden con las que usa la web (assets/site.js)."""
    R = json.load(open(os.path.join(C, "rosario.json"), encoding="utf-8")); O = R["oraciones"]
    ORD = ["Primer", "Segundo", "Tercer", "Cuarto", "Quinto"]
    T = {k: O[k] for k in ("SENAL", "CREDO", "PN", "AM", "GL", "OJ", "SALVE")}
    T["CONTEMPLA"] = "Contempla en silencio este misterio."
    for i, v in enumerate(["Por la fe.", "Por la esperanza.", "Por la caridad."]): T[f"INT{i}"] = v
    for k, s in R["sets"].items():
        for m, my in enumerate(s["list"]):
            T[f"M-{k}-{m}"] = f"{ORD[m]} misterio {s['adj']}: {my[0]}. Fruto del misterio: {my[2].lower()}."
    return T

def rosario(a, outdir):
    path = os.path.join(C, "voces-rosario.json")
    voces = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for k, t in rosario_textos().items():
        if voces.get(k) and not a.sobrescribir: continue
        G.log(f"Rosario · {k}")
        mp3 = os.path.join(outdir, f"rosario-{k}.mp3")
        grabar(texto_voz(t), mp3, a, cola=0.4)
        if a.sin_subir: continue
        url = G.subir(mp3, f"rosario/{k}.mp3", a)
        voces[k] = f"{url}?v={int(time.time())}"
        json.dump(voces, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def main():
    p = argparse.ArgumentParser(); p.add_argument("--solo", choices=["oraciones", "rosario"]); p.add_argument("--sobrescribir", action="store_true")
    p.add_argument("--max", type=int, default=200); p.add_argument("--prueba", action="store_true"); p.add_argument("--sin-subir", action="store_true")
    a = p.parse_args(); a.reusados = 0; a.nuevos = 0; a.solo_historial = False; a.sin_historial = False
    outdir = os.path.join(ROOT, "audios-generados"); os.makedirs(outdir, exist_ok=True)
    if a.solo != "oraciones": rosario(a, outdir)
    if a.solo != "rosario": oraciones(a, outdir)
    G.log(f"Terminado. Voces reutilizadas del historial: {a.reusados} · generadas nuevas: {a.nuevos}.")

if __name__ == "__main__": main()
