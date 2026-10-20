# -*- coding: utf-8 -*-
"""Genera los audios del rezo diario con ElevenLabs, los monta con silencios y música,
los sube a Supabase Storage y los enlaza en content/dias/*.json.

Lo ejecuta GitHub Actions (.github/workflows/generar-audios.yml). También funciona en tu ordenador:
  ELEVENLABS_API_KEY=... ELEVENLABS_VOICE_ID=... SUPABASE_SERVICE_KEY=... \
  python3 scripts/generar_audios.py --desde 2026-10-19 --hasta 2026-10-25

Opciones:
  --desde / --hasta   Fechas (por defecto: de hoy a dentro de 7 días)
  --sobrescribir      Vuelve a generar días que ya tienen audio
  --max N             Máximo de días por ejecución (por defecto 31), para no gastar créditos de más
  --prueba            No llama a ElevenLabs: usa tonos en lugar de voz (para probar el montaje)
  --sin-subir         No sube a Supabase: deja los MP3 en la carpeta audios-generados/
  --solo-historial    Reutiliza las voces ya generadas (historial de ElevenLabs) y no gasta créditos;
                      si a un día le falta alguna voz, lo salta

Cada día se sube dos veces: AAAA-MM-DD.mp3 (voz + música, para el pódcast) y AAAA-MM-DD-voz.mp3
(solo voz, para la web, que pone encima la música que elija cada persona).
Antes de gastar créditos, el programa busca la misma frase en tu historial de ElevenLabs y la descarga gratis.
"""
import argparse, datetime, glob, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "content")
AJ = json.load(open(os.path.join(C, "ajustes.json"), encoding="utf-8"))
ROS = json.load(open(os.path.join(C, "rosario.json"), encoding="utf-8"))
GL = ROS["oraciones"]["GL"]
MUSICA = os.path.join(ROOT, "static", "musica", "fondo.mp3")
SR = 44100

def log(*a): print(*a, flush=True)
def fail(msg): print(f"::error::{msg}", flush=True); sys.exit(1)
def br(s): return f' <break time="{s}s" /> '

SEGS = {0: 0, 1: 1, 2: 2, 3: 3}
def clips(d):
    """Lista de piezas del audio: ('voz', texto, parte) o ('silencio', segundos). Parte: 0 silencio, 1 Evangelio, 2 reflexión, 3 oración final."""
    libro, cap = d["refL"].split(" ")[0], d["refL"].split(" ")[1].rstrip(",")
    out = [("silencio", 2),
           ("voz0", "Busca un lugar tranquilo y ponte cómodo." + br(1.5) + "Respira despacio." + br(2) + "Inspira…" + br(2.5) + "y suelta el aire." + br(2.5) + "Estás en la presencia de Dios." + br(1.5) + "Él te mira con cariño."),
           ("silencio", 4),
           ("voz1", f"Evangelio según san {libro}, capítulo {cap}." + br(1.5) + d["sum"] + br(2) + "Escucha estas palabras del Evangelio:" + br(1.5) + d["ex"]),
           ("silencio", 4),
           ("voz2", d["refl"] + br(2) + "Ahora, en silencio, piensa en estas preguntas."),
           ("silencio", 2)]
    for q in d["qs"]: out += [("voz2", q), ("silencio", 8)]
    out += [("voz3", d["fin"] + br(2) + GL), ("silencio", 4)]
    return out

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: fail("ffmpeg ha fallado:\n" + r.stderr[-1500:])
    return r

HIST = None
class SinHistorial(Exception): pass
def norm(t): return re.sub(r"\s+", " ", t).strip()
def historial():
    """Mapa texto → id del historial de ElevenLabs (lo más reciente gana). Descargarlo no gasta créditos."""
    global HIST
    if HIST is not None: return HIST
    HIST = {}; key, voice = os.environ.get("ELEVENLABS_API_KEY", "").strip(), os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    after = None
    for _ in range(40):
        q = f"https://api.elevenlabs.io/v1/history?page_size=1000&voice_id={voice}" + (f"&start_after_history_item_id={after}" if after else "")
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers={"xi-api-key": key}), timeout=60) as r: j = json.loads(r.read())
        except urllib.error.HTTPError as e:
            log(f"  No puedo leer el historial de ElevenLabs (error {e.code}). Si la clave no tiene permiso de «History», actívalo. {e.read()[:200]!r}"); break
        except Exception as e:
            log(f"  No puedo leer el historial de ElevenLabs: {e}"); break
        for it in j.get("history", []):
            k = norm(it.get("text", ""))
            if k and (k not in HIST or it.get("date_unix", 0) > HIST[k][1]): HIST[k] = (it["history_item_id"], it.get("date_unix", 0))
        if not j.get("has_more"): break
        after = j.get("last_history_item_id")
    log(f"  Historial de ElevenLabs: {len(HIST)} frases ya generadas que puedo reutilizar gratis.")
    return HIST

def tts(text, path, a):
    if a.prueba:  # tono en lugar de voz, con duración parecida a la real
        secs = max(2.0, len(re.sub(r"<[^>]+>", "", text)) / 14 + text.count("<break") * 2)
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=330:sample_rate={SR}", "-t", f"{secs:.2f}", "-af", "volume=0.3", "-ac", "1", path])
        return
    key, voice = os.environ.get("ELEVENLABS_API_KEY", "").strip(), os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    h = historial().get(norm(text))
    if not h:  # los audios antiguos decían «palabras de Jesús»; esa voz sirve igual
        h = historial().get(norm(text.replace("Escucha estas palabras del Evangelio:", "Escucha estas palabras de Jesús:")))
    if h and not a.sin_historial:
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://api.elevenlabs.io/v1/history/{h[0]}/audio", headers={"xi-api-key": key}), timeout=120) as r:
                open(path, "wb").write(r.read()); a.reusados += 1; return
        except Exception as e: log(f"  No he podido descargar una voz del historial ({e}); la genero de nuevo.")
    if a.solo_historial: raise SinHistorial(text[:60])
    a.nuevos += 1
    model = os.environ.get("ELEVENLABS_MODEL", "").strip() or "eleven_multilingual_v2"
    body = json.dumps({"text": text, "model_id": model, "language_code": "es",
                       "voice_settings": {"stability": 0.7, "similarity_boost": 0.75, "style": 0.1, "use_speaker_boost": True, "speed": float(os.environ.get("ELEVENLABS_SPEED", "") or 1.1)}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128", data=body, method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r: open(path, "wb").write(r.read()); return
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")[:400]
            if e.code in (401, 403): fail(f"ElevenLabs no acepta la clave (error {e.code}). Revisa el secreto ELEVENLABS_API_KEY. {msg}")
            if e.code == 404: fail(f"ElevenLabs no encuentra la voz. Revisa el secreto ELEVENLABS_VOICE_ID. {msg}")
            if "quota" in msg.lower() or e.code == 402: fail(f"Te has quedado sin créditos en ElevenLabs. {msg}")
            if e.code == 400 and "language_code" in msg:  # algunos modelos no admiten language_code
                d = json.loads(body); d.pop("language_code", None); body = json.dumps(d).encode(); req.data = body; continue
            log(f"  ElevenLabs respondió {e.code}; reintento en 10 s… {msg}"); time.sleep(10)
        except urllib.error.URLError as e:
            log(f"  Sin conexión con ElevenLabs ({e}); reintento en 10 s…"); time.sleep(10)
    fail("ElevenLabs no ha respondido tras 3 intentos.")

def dur(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path])
    return float(r.stdout.strip())

def frases(t):
    return [x for x in re.split(r"(?<=[.!?»…])\s+", t.strip()) if x]

def marcas_clip(wav, text, offset, seg):
    """Calcula en qué segundo empieza cada frase dentro de un trozo de voz."""
    trozos = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"<break[^>]*>", text)]
    pausas = [float(x) for x in re.findall(r'time="([\d.]+)s"', text)]
    trozos = [x for x in trozos if x]
    D = dur(wav)
    r = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=noise=-38dB:d=0.7", "-f", "null", "-"], capture_output=True, text=True)
    sil = [(float(a), float(b)) for a, b in zip(re.findall(r"silence_start: ([\d.]+)", r.stderr), re.findall(r"silence_end: ([\d.]+)", r.stderr))]
    # tramos con voz entre silencios
    tramos, cur = [], 0.0
    for a_, b_ in sil:
        if a_ - cur > 0.25: tramos.append((cur, a_))
        cur = b_
    if D - cur > 0.25: tramos.append((cur, D))
    if len(tramos) != len(trozos):  # reparto proporcional si no coinciden
        hablado = max(1.0, D - sum(pausas[:len(trozos) - 1]))
        tot = sum(len(x) for x in trozos) or 1; t0 = 0.0; tramos = []
        for k, x in enumerate(trozos):
            l = hablado * len(x) / tot; tramos.append((t0, t0 + l)); t0 += l + (pausas[k] if k < len(pausas) else 0)
    out = []
    for (a_, b_), x in zip(tramos, trozos):
        fs = frases(x); tot = sum(len(f) for f in fs) or 1; t0 = a_
        for f in fs:
            out.append([round(offset + t0, 2), seg, f]); t0 += (b_ - a_) * len(f) / tot
    return out

def montar(d, out_mp3, a):
    marcas = []
    with tempfile.TemporaryDirectory() as tmp:
        partes = []; offset = 0.0
        for i, (kind, val) in enumerate(clips(d)):
            wav = os.path.join(tmp, f"{i:02d}.wav")
            if kind == "silencio":
                run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(val), wav])
            else:
                mp3 = os.path.join(tmp, f"{i:02d}.mp3"); tts(val, mp3, a)
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", str(SR), "-ac", "1", wav])
                marcas += marcas_clip(wav, val, offset, int(kind[-1]))
            partes.append(wav); offset += dur(wav)
        lista = os.path.join(tmp, "lista.txt"); open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
        voz = os.path.join(tmp, "voz.wav"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", voz])
        T = dur(voz)
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", voz, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k",
             "-metadata", f"title={d['title']} · {d['date']} (voz)", "-metadata", "artist=Rezo Diario", out_mp3[:-4] + "-voz.mp3"])
        fondo = os.path.join(tmp, "fondo.wav")
        if os.path.exists(MUSICA):  # tu música (libre de derechos) en static/musica/fondo.mp3
            run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", MUSICA, "-t", f"{T:.2f}", "-ar", str(SR), "-ac", "1",
                 "-af", f"volume=0.12,afade=t=in:d=3,afade=t=out:st={max(0, T - 6):.2f}:d=6", fondo])
        else:  # bordón suave generado (re, la, re), como el de la web
            src = []
            for f, v in ((146.83, .5), (220, .26), (293.66, .2), (440, .06)): src += ["-f", "lavfi", "-i", f"sine=frequency={f}:sample_rate={SR}"]
            mix = "".join(f"[{i}]volume={v}[s{i}];" for i, (f, v) in enumerate(((146.83, .5), (220, .26), (293.66, .2), (440, .06)))) + "".join(f"[s{i}]" for i in range(4)) + \
                  f"amix=inputs=4:normalize=0,tremolo=f=0.12:d=0.3,lowpass=f=900,volume=0.07,afade=t=in:d=4,afade=t=out:st={max(0, T - 7):.2f}:d=7[o]"
            run(["ffmpeg", "-y", "-loglevel", "error", *src, "-filter_complex", mix, "-map", "[o]", "-t", f"{T:.2f}", "-ac", "1", fondo])
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", voz, "-i", fondo, "-filter_complex",
             "[0][1]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k",
             "-metadata", f"title={d['title']} · {d['date']}", "-metadata", "artist=Rezo Diario", "-metadata", "album=Rezo Diario", out_mp3])
    return dur(out_mp3), marcas

def sb_headers(key, extra=None):
    h = {"apikey": key}
    if key.startswith("eyJ"): h["Authorization"] = "Bearer " + key
    h.update(extra or {}); return h

def sb_req(url, key, method="GET", data=None, headers=None, bearer=False):
    h = sb_headers(key, headers)
    if bearer: h["Authorization"] = "Bearer " + key
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return r.status, r.read()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403) and not bearer and "Authorization" not in h: return sb_req(url, key, method, data, headers, True)
        return e.code, e.read()

def subir(path, nombre, a):
    base = (os.environ.get("SUPABASE_URL") or AJ.get("supabaseUrl", "")).strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    if not base: fail("Falta la URL de Supabase en Ajustes de la web.")
    if not key: fail("Falta el secreto SUPABASE_SERVICE_KEY (la clave secreta de Supabase).")
    st, body = sb_req(f"{base}/storage/v1/bucket/audios", key)
    if st != 200:
        st, body = sb_req(f"{base}/storage/v1/bucket", key, "POST", json.dumps({"id": "audios", "name": "audios", "public": True}).encode(), {"Content-Type": "application/json"})
        if st not in (200, 201) and b"already exists" not in body: fail(f"No se ha podido crear la carpeta «audios» en Supabase ({st}): {body[:300]}")
        log("  Creada la carpeta pública «audios» en Supabase Storage.")
    st, body = sb_req(f"{base}/storage/v1/object/audios/{nombre}", key, "POST", open(path, "rb").read(), {"Content-Type": "audio/mpeg", "x-upsert": "true", "Cache-Control": "max-age=31536000"})
    if st not in (200, 201): fail(f"No se ha podido subir {nombre} a Supabase ({st}): {body[:300]}")
    return f"{base}/storage/v1/object/public/audios/{nombre}"

def main():
    p = argparse.ArgumentParser(); p.add_argument("--desde"); p.add_argument("--hasta"); p.add_argument("--sobrescribir", action="store_true")
    p.add_argument("--solo-historial", action="store_true"); p.add_argument("--fechas", default=""); p.add_argument("--sin-historial", action="store_true")
    p.add_argument("--max", type=int, default=31); p.add_argument("--prueba", action="store_true"); p.add_argument("--sin-subir", action="store_true")
    a = p.parse_args(); a.reusados = 0; a.nuevos = 0
    hoy = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date()
    desde = (a.desde or "").strip() or hoy.isoformat(); hasta = (a.hasta or "").strip() or (hoy + datetime.timedelta(days=7)).isoformat()
    if not a.prueba:
        if not os.environ.get("ELEVENLABS_API_KEY", "").strip(): fail("Falta el secreto ELEVENLABS_API_KEY.")
        if not os.environ.get("ELEVENLABS_VOICE_ID", "").strip(): fail("Falta el secreto ELEVENLABS_VOICE_ID (el identificador de la voz elegida).")
    files = sorted(f for f in glob.glob(os.path.join(C, "dias", "*.json")) if desde <= os.path.basename(f)[:10] <= hasta)
    fx = {x.strip() for x in (a.fechas or "").split(",") if x.strip()}
    if fx: files = sorted(f for f in glob.glob(os.path.join(C, "dias", "*.json")) if os.path.basename(f)[:10] in fx)
    todo = []
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        if d.get("audio") and d.get("audioVoz") and not a.sobrescribir: log(f"{d['date']}: ya tiene audio, lo salto."); continue
        todo.append((f, d))
    if not todo: log("No hay días pendientes de audio en ese periodo."); return
    if len(todo) > a.max: log(f"Hay {len(todo)} días pendientes; genero solo los primeros {a.max}."); todo = todo[:a.max]
    chars = sum(len(re.sub(r"<[^>]+>", "", v)) for _, d in todo for k, v in clips(d) if k.startswith("voz"))
    log(f"Voy a generar {len(todo)} audios (unos {chars} caracteres de ElevenLabs).")
    outdir = os.path.join(ROOT, "audios-generados"); os.makedirs(outdir, exist_ok=True)
    for f, d in todo:
        log(f"{d['date']} · {d['title']}")
        mp3 = os.path.join(outdir, f"{d['date']}.mp3")
        try: secs, marcas = montar(d, mp3, a)
        except SinHistorial as e: log(f"  Falta una voz en el historial («{e}…»); salto este día para no gastar créditos."); continue
        dd = f"{int(secs // 60)}:{int(round(secs % 60)):02d}"
        log(f"  Montado: {dd} min, {os.path.getsize(mp3) // 1024} KB, {len(marcas)} frases sincronizadas")
        if a.sin_subir: json.dump(marcas, open(mp3[:-4] + ".json", "w"), ensure_ascii=False)
        if a.sin_subir: continue
        url = subir(mp3, f"{d['date']}.mp3", a); uv = subir(mp3[:-4] + "-voz.mp3", f"{d['date']}-voz.mp3", a)
        v = int(time.time()); d["audio"] = f"{url}?v={v}"; d["audioVoz"] = f"{uv}?v={v}"; d["duracion"] = dd; d["marcas"] = marcas
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        log(f"  Subido y enlazado: {url}")
    log(f"Terminado. Voces reutilizadas del historial: {a.reusados} · generadas nuevas: {a.nuevos}.")

if __name__ == "__main__": main()
