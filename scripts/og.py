# -*- coding: utf-8 -*-
"""Imágenes para compartir (1200×630) de cada página: título propio sobre el fondo de la marca.
Lee site/og-paginas.json (lo escribe build.py) y guarda static/og/<nombre>.jpg.
Solo crea las que faltan o cuyo texto ha cambiado. Uso: python3 build.py && python3 scripts/og.py
"""
import hashlib, json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "og")
F = os.path.join(ROOT, "static", "fuentes")
GOLD, INK, MUTED = (214, 178, 102), (238, 242, 236), (185, 199, 190)

def base():
    im = Image.open(os.path.join(ROOT, "static", "og-rezodiario.jpg")).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 232, 645, 600), fill=(19, 48, 43))  # fondo liso donde iba el lema
    # la cola de «con» entra en el halo: la tapamos copiando la fila limpia de encima
    fila = im.crop((645, 238, 684, 239))
    for y in range(244, 336): im.paste(fila, (645, y))
    return im

def ajusta(d, txt, font_path, size, width, max_lines):
    lines, lo = [txt], int(size * 0.6)
    while size >= lo:
        f = ImageFont.truetype(font_path, size)
        words, lines, cur = txt.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= width: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= max_lines: return f, lines
        size -= 3
    f = ImageFont.truetype(font_path, size)
    return f, lines[:max_lines - 1] + [" ".join(lines[max_lines - 1:])[:40].rstrip() + "…"]

def pinta(B, eyebrow, title, sub, dest):
    im = B.copy(); d = ImageDraw.Draw(im)
    x, wmax = 90, 600
    fe = ImageFont.truetype(os.path.join(F, "manrope.woff"), 24)
    d.text((x, 250), eyebrow.upper(), font=fe, fill=GOLD, spacing=4)
    ft, lines = ajusta(d, title, os.path.join(F, "marcellus.woff"), 68, wmax, 3)
    y = 292; lh = int(ft.size * 1.14)
    for ln in lines: d.text((x, y), ln, font=ft, fill=INK); y += lh
    if sub:
        fs, sl = ajusta(d, sub, os.path.join(F, "manrope.woff"), 27, wmax, 2)
        y += 16
        for ln in sl: d.text((x, y), ln, font=fs, fill=MUTED); y += int(fs.size * 1.35)
    im.save(dest, "JPEG", quality=80, optimize=True, progressive=True)

def main():
    man = json.load(open(os.path.join(ROOT, "site", "og-paginas.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    idx_p = os.path.join(OUT, "indice.json")
    idx = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
    B = base(); n = 0
    for name, (eyebrow, title, sub) in man.items():
        h = hashlib.md5(f"v3|{eyebrow}|{title}|{sub}".encode()).hexdigest()[:10]
        dest = os.path.join(OUT, name + ".jpg")
        if idx.get(name) == h and os.path.exists(dest): continue
        pinta(B, eyebrow, title, sub, dest); idx[name] = h; n += 1
    json.dump(idx, open(idx_p, "w"), indent=0, sort_keys=True)
    print(f"Imágenes para compartir: {n} nuevas o cambiadas, {len(man)} en total.")

if __name__ == "__main__": main()
