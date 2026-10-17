# -*- coding: utf-8 -*-
"""Crea las músicas de fondo del reproductor (static/musica/*.mp3).
Todo es sonido sintetizado aquí mismo, así que no hay derechos de autor de terceros.
Cada pista es un bucle perfecto: el final empalma con el principio sin cortes.
Uso: python3 scripts/crear_musica.py   (necesita numpy y ffmpeg)
"""
import os, subprocess, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "musica"); os.makedirs(OUT, exist_ok=True)
SR = 32000; L = 96 * SR  # 96 segundos
t_all = np.arange(L) / SR
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
# Re mayor: D · Bm · G · A, 12 s cada acorde, dos vueltas
CH = [[50, 62, 66, 69], [47, 62, 66, 71], [43, 59, 62, 67], [45, 61, 64, 69]]
CD = 12.0

def add(buf, start, sig):
    """Suma una señal en el bucle; lo que se pasa del final vuelve al principio."""
    i = int(start * SR) % L; n = len(sig)
    while n > 0:
        k = min(n, L - i); buf[i:i + k] += sig[len(sig) - n:len(sig) - n + k]; n -= k; i = 0

def reverb(x, rt=3.0, wet=0.35, bright=4000, seed=1):
    rng = np.random.default_rng(seed); n = int(rt * 1.4 * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 6.9 / rt)
    F = np.fft.rfft(ir, L); f = np.fft.rfftfreq(L, 1 / SR); F *= 1 / (1 + (f / bright) ** 2)
    y = np.fft.irfft(np.fft.rfft(x) * F, L)  # convolución circular: el eco también empalma
    y *= np.sqrt(np.mean(x ** 2) / (np.mean(y ** 2) + 1e-12))
    return (1 - wet) * x + wet * y

def lowpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))

def env(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, na)); e[n - nr:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nr)); return e

def calma():
    b = np.zeros(L); rng = np.random.default_rng(3)
    for v in range(2):
        for ci, notes in enumerate(CH):
            st = (v * 4 + ci) * CD - 3; dur = CD + 6; n = int(dur * SR); tt = np.arange(n) / SR
            for j, m in enumerate(notes):
                f = hz(m); amp = [.5, .3, .26, .2][j]
                s = sum(np.sin(2 * np.pi * f * (1 + d) * tt + rng.uniform(0, 6)) for d in (-0.002, 0, 0.0025)) / 3
                s += .18 * np.sin(2 * np.pi * 2 * f * tt)
                s *= 1 + .15 * np.sin(2 * np.pi * (.07 + .02 * j) * tt)
                add(b, st, amp * s * env(n, 3, 3))
    return reverb(lowpass(b, 1400), 4, .4)

def piano():
    b = np.zeros(L); rng = np.random.default_rng(7)
    def nota(m, vel, dur=6.0):
        f = hz(m); n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for k in range(1, 9):
            fk = f * k * np.sqrt(1 + 0.0004 * k * k)
            if fk > SR / 2.2: break
            s += (1 / k ** 1.6) * np.exp(-tt * (0.55 + 0.45 * k) * (1 + (m - 60) / 40)) * np.sin(2 * np.pi * fk * tt)
        s *= np.minimum(1, tt / 0.006); s *= env(n, .006, 1.0); return vel * s
    for v in range(2):
        for ci, notes in enumerate(CH):
            t0 = (v * 4 + ci) * CD
            add(b, t0, nota(notes[0] - 12 if notes[0] > 45 else notes[0], .5, 9))
            pat = [notes[1], notes[2], notes[3], notes[2] + 12, notes[3], notes[2], notes[1] + 12, notes[3]]
            for i, m in enumerate(pat):
                if rng.random() < .22: continue
                add(b, t0 + 0.6 + i * 1.42 + rng.uniform(-.06, .06), nota(m, rng.uniform(.18, .3)))
    return reverb(b, 3.2, .38, 5000)

def organo():
    b = np.zeros(L); rng = np.random.default_rng(5)
    bars = [(1, 1), (2, .55), (3, .25), (4, .22), (6, .08), (8, .06)]
    for v in range(2):
        for ci, notes in enumerate(CH):
            st = (v * 4 + ci) * CD - 2; dur = CD + 4; n = int(dur * SR); tt = np.arange(n) / SR
            vib = 1 + .0018 * np.sin(2 * np.pi * 5.3 * tt)
            for j, m in enumerate(notes):
                f = hz(m); ph = 2 * np.pi * f * np.cumsum(vib) / SR + rng.uniform(0, 6)
                s = sum(a * np.sin(k * ph) for k, a in bars if f * k < 6000)
                add(b, st, [.45, .28, .24, .2][j] * s * env(n, 2.2, 2.2))
    return reverb(lowpass(b, 2600), 4.5, .5, 3500)

def campanas():
    b = np.zeros(L); rng = np.random.default_rng(11)
    tt = t_all
    b += .12 * np.sin(2 * np.pi * hz(38) * tt) * (1 + .3 * np.sin(2 * np.pi * tt / 24))  # bordón grave muy suave (24 s exactos)
    b += .06 * np.sin(2 * np.pi * hz(45) * tt) * (1 + .3 * np.sin(2 * np.pi * tt / 32 + 1))
    pent = [62, 64, 66, 69, 71, 74, 76, 78]; t0 = 0.5
    while t0 < 96 - 0.5:
        m = pent[rng.integers(len(pent))]; f = hz(m); n = int(9 * SR); x = np.arange(n) / SR; s = np.zeros(n)
        for r, a, d in ((1, 1, 6), (2.0, .45, 3.5), (2.76, .28, 2.2), (5.4, .12, .9), (.5, .25, 7)):
            s += a * np.exp(-x / d) * np.sin(2 * np.pi * f * r * x)
        s *= np.minimum(1, x / 0.004)
        add(b, t0, rng.uniform(.12, .2) * s); t0 += rng.uniform(3.2, 6.5)
    return reverb(b, 5, .45, 4500)

def lluvia():
    rng = np.random.default_rng(13); X = np.fft.rfft(rng.standard_normal(L)); f = np.fft.rfftfreq(L, 1 / SR)
    X *= 1 / np.sqrt(np.maximum(f, 40) / 40) * (1 / (1 + (f / 5000) ** 4)) * (f > 150)
    s = np.fft.irfft(X, L); s /= np.std(s)
    s *= 1 + .25 * np.sin(2 * np.pi * t_all / 16) + .12 * np.sin(2 * np.pi * t_all / 6 + 2)  # oleadas suaves que empalman
    gotas = np.zeros(L)
    for _ in range(1400):
        n = int(.03 * SR); x = np.arange(n) / SR; fq = rng.uniform(1800, 4200)
        add(gotas, rng.uniform(0, 96), rng.uniform(.4, 1.4) * np.exp(-x / .006) * np.sin(2 * np.pi * fq * x))
    s = .85 * s + .7 * lowpass(gotas, 4500)
    s += .35 * np.sin(2 * np.pi * hz(38) * t_all) * (1 + .4 * np.sin(2 * np.pi * t_all / 32))  # fondo cálido
    return reverb(s, 1.2, .25, 3000)

PISTAS = {"calma": (calma, -27), "piano": (piano, -26), "organo": (organo, -27), "campanas": (campanas, -27), "lluvia": (lluvia, -29)}
for nombre, (fn, db) in PISTAS.items():
    x = fn(); x -= x.mean()
    x *= 10 ** (db / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12)
    pk = np.max(np.abs(x))
    if pk > .7: x *= .7 / pk
    raw = (x * 32767).astype("<i2").tobytes()
    path = os.path.join(OUT, nombre + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-b:a", "64k",
                    "-metadata", f"title=Rezo Diario · {nombre}", path], input=raw, check=True)
    print(nombre, os.path.getsize(path) // 1024, "KB")
