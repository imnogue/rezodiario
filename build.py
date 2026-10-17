# -*- coding: utf-8 -*-
"""Generador de rezodiario.com. Lee content/*.json y escribe la web en site/.
Uso:  python3 build.py            (genera la web)
      python3 build.py --guiones  (además genera los guiones de ElevenLabs en guiones/)
"""
import json, os, re, sys, shutil, html, glob, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "site")
E = lambda s: html.escape(str(s), quote=True)
def J(p): return json.load(open(os.path.join(C, p), encoding="utf-8"))
def JD(d): return [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(C, d, "*.json")))]

AJ = J("ajustes.json"); SITE = AJ.get("sitio", "https://rezodiario.com/").rstrip("/") + "/"
TEMAS = J("temas.json"); CATS = {t["key"]: t for t in TEMAS["temas"]}; FAQ_CAT = {k: [(x["q"], x["a"]) for x in v] for k, v in TEMAS["faq"].items()}
ROS = J("rosario.json"); SETS = ROS["sets"]; O = ROS["oraciones"]
VIAJ = J("via-crucis.json"); RETO = J("reto-adviento.json"); EXTRA = J("liturgia-extra.json")
DAYS = sorted(JD("dias"), key=lambda d: d["date"]); DBY = {d["date"]: d for d in DAYS}
PRAYERS = JD("oraciones"); PBY = {p["slug"]: p for p in PRAYERS}
SAINTS = sorted(JD("santos"), key=lambda s: s["md"]); SBY = {s["slug"]: s for s in SAINTS}
NOVENAS = sorted(JD("novenas"), key=lambda n: n["start"])
WDN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
SETDAY = ["gozosos", "dolorosos", "gloriosos", "luminosos", "dolorosos", "gozosos", "gloriosos"]
LITC = {"green": ["var(--lit-green)", "Verde · Tiempo Ordinario"], "white": ["var(--lit-white)", "Blanco · fiesta o memoria"], "red": ["var(--lit-red)", "Rojo · mártires y apóstoles"],
        "violet": ["var(--lit-violet)", "Morado · Adviento y difuntos"], "rose": ["var(--lit-rose)", "Rosa · domingo de la alegría"], "blue": ["var(--lit-blue)", "Azul · privilegio de España en la Inmaculada"]}
CANDLE_HASH = {"salud": "salud", "familia": "familia", "duelo": "difuntos", "estudios": "estudios", "trabajo": "trabajo", "diaria": "gracias", "paz": "otra", "devociones": "otra"}
for d in DAYS:
    dt = datetime.date.fromisoformat(d["date"]); d["wd"] = WDN[dt.weekday()]; d["n"] = dt.day; d["mes"] = MES[dt.month - 1]; d["set"] = SETDAY[dt.weekday()]
    if d.get("saint") and d["saint"] not in SBY: print("AVISO: santo no encontrado", d["date"], d["saint"]); d["saint"] = ""

now = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
TODAY = min(max(now, DAYS[0]["date"]), DAYS[-1]["date"])
TW = DBY[TODAY]
ti = DAYS.index(TW)
TOMORROW = DAYS[min(ti + 1, len(DAYS) - 1)]
def nice(d): return f'{d["wd"].lower()} {d["n"]} de {d["mes"]} de {d["date"][:4]}'
def fdate(iso): dt = datetime.date.fromisoformat(iso); return f"{dt.day} de {MES[dt.month-1]}"
pages = []

ICON = {
 "search": '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "globe": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z"/></svg>',
 "moon": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
 "menu": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
 "user": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>',
 "logo": '<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14.6" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="16" cy="16" r="10" fill="none" stroke="currentColor" stroke-width=".8" stroke-dasharray="1.6 2.2"/><path d="M16 7.5v17M11 13h10" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
 "arrow": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 "play": '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg>',
}
TAB_ICONS = {
 "today": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
 "prayers": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5zM4 5.5v16M12 7v6M9.5 9.5h5"/></svg>',
 "rosary": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="9" r="6.5" stroke-dasharray="1.5 2.4" stroke-linecap="round"/><path d="M12 15.5v6M9.5 19h5"/></svg>',
 "candles": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3c1.8 2 2.5 3.4 2.5 4.6A2.5 2.5 0 0 1 12 10a2.5 2.5 0 0 1-2.5-2.4C9.5 6.4 10.2 5 12 3zM8.5 12h7v9h-7z"/></svg>',
 "more": '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>',
}
NAV = [("index.html", "today", "Hoy"), ("oraciones/index.html", "prayers", "Oraciones"), ("rosario.html", "rosary", "Rosario"), ("evangelio-de-hoy.html", "gospel", "Evangelio"), ("santos/index.html", "saints", "Santos"), ("novenas/index.html", "novenas", "Novenas"), ("muro-de-intenciones.html", "candles", "Velas")]
def canon(path): return SITE + ("" if path == "index.html" else path)
ORG = {"@type": "Organization", "name": "Rezo Diario", "url": SITE, "logo": SITE + "icon.svg"}

def header(r, active):
    nav = "".join(f'<a href="{r}{h}"{" class=\"on\" aria-current=\"page\"" if k == active else ""} data-i18n="{k}">{t}</a>' for h, k, t in NAV)
    return f'''<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="{r}index.html" aria-label="Rezo Diario, inicio">{ICON["logo"]}<span>Rezo<b>Diario</b></span></a>
    <nav class="nav" aria-label="Principal">{nav}</nav>
    <div class="top-actions">
      <button class="icon-btn" id="btnSearch" aria-label="Buscar una oración">{ICON["search"]}</button>
      <div class="lang"><button class="icon-btn lang-btn" id="btnLang" aria-haspopup="menu" aria-expanded="false" aria-label="Idioma">{ICON["globe"]}<span id="langCode">ES</span></button><div class="lang-menu" id="langMenu" role="menu" hidden></div></div>
      <button class="icon-btn" id="btnTheme" aria-label="Cambiar entre modo claro y oscuro">{ICON["moon"]}</button>
      <button class="icon-btn" id="btnUser" aria-label="Tu cuenta" hidden>{ICON["user"]}</button>
      <a href="{r}donar.html" class="btn btn-gold sm" data-i18n="donate">Donar</a>
      <button class="icon-btn menu-btn" data-drawer aria-label="Abrir menú">{ICON["menu"]}</button>
    </div>
  </div>
</header>'''

def drawer(r):
    groups = [("Rezar", [("index.html", "Rezo de hoy"), ("evangelio-de-hoy.html", "Evangelio de hoy"), ("evangelio-de-manana.html", "Evangelio de mañana"), ("santo-de-hoy.html", "Santo de hoy"), ("rosario.html", "Santo Rosario"), ("via-crucis.html", "Vía Crucis"), ("novenas/index.html", "Novenas"), ("muro-de-intenciones.html", "Muro de velas")]),
              ("Tiempos litúrgicos", [("adviento.html", "Adviento 2026"), ("retos/adviento.html", "Reto de Adviento"), ("navidad.html", "Navidad 2026")]),
              ("Oraciones por tema", [(f"oraciones/tema-{k}.html", c["name"]) for k, c in CATS.items()]),
              ("Rezo Diario", [("santos/index.html", "Santoral"), ("evangelio/index.html", "Archivo del Evangelio"), ("widget.html", "Widget para parroquias"), ("donar.html", "Donar"), ("sobre-nosotros.html", "Quiénes somos")])]
    out = "".join(f'<h4>{g}</h4>' + "".join(f'<a href="{r}{h}"><i></i>{t}</a>' for h, t in items) for g, items in groups)
    return f'<div class="drawer" id="drawer" hidden role="dialog" aria-modal="true" aria-label="Menú"><div class="drawer-bg" data-close></div><nav class="drawer-p"><button class="icon-btn" data-close aria-label="Cerrar menú" style="margin-left:auto;display:grid">✕</button>{out}</nav></div>'

def tabbar(r, active):
    items = [("index.html", "today", "Hoy"), ("oraciones/index.html", "prayers", "Oraciones"), ("rosario.html", "rosary", "Rosario"), ("muro-de-intenciones.html", "candles", "Velas")]
    a = "".join(f'<a href="{r}{h}"{" class=\"on\"" if k == active else ""}>{TAB_ICONS[k]}<span data-i18n="{k}">{t}</span></a>' for h, k, t in items)
    return f'<nav class="tabbar" aria-label="Accesos rápidos">{a}<a href="#" data-drawer>{TAB_ICONS["more"]}<span data-i18n="more">Más</span></a></nav>'

ACCOUNT = '''<div class="drawer" id="account" hidden role="dialog" aria-modal="true" aria-labelledby="accT"><div class="drawer-bg" data-close></div><div class="drawer-p">
 <button class="icon-btn" data-close aria-label="Cerrar" style="margin-left:auto;display:grid">✕</button>
 <h2 id="accT" style="font-size:30px">Tu cuenta</h2>
 <div id="accOut"><p style="color:var(--muted)">Crea tu cuenta gratis para guardar tu racha, tus oraciones favoritas, tus novenas y tus velas en todos tus dispositivos.</p>
  <form id="accForm" class="ask" style="flex-direction:column"><label class="sr" for="accEmail">Correo electrónico</label><input id="accEmail" type="email" placeholder="tu@correo.com" autocomplete="email"><button class="btn btn-accent" type="submit">Enviarme el enlace de acceso</button></form>
  <p class="note">Te enviaremos un enlace para entrar sin contraseña. No compartimos tu correo con nadie.</p></div>
 <div id="accIn" hidden><p>Has entrado como <strong id="accWho"></strong>.</p><ul class="links" id="accStats"></ul><button class="btn btn-ghost sm" id="accLogout" style="margin-top:16px">Cerrar sesión</button></div>
 <p class="note" id="accMsg" role="status"></p>
</div></div>'''

def footer(r):
    pop = [("oracion-antes-de-un-examen", "Antes de un examen"), ("oracion-por-un-enfermo", "Por un enfermo"), ("oracion-para-la-ansiedad", "Para la ansiedad"), ("oracion-por-un-difunto", "Por un difunto"), ("oracion-a-san-judas-tadeo", "A san Judas Tadeo"), ("oracion-para-encontrar-trabajo", "Para encontrar trabajo")]
    col = lambda title, items: f'<div><h4>{title}</h4><ul>' + "".join(f'<li><a href="{h if h.startswith("http") else r + h}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}>{t}</a></li>' for h, t in items) + '</ul></div>'
    social = [(AJ.get(k), n) for k, n in (("whatsappCanal", "Canal de WhatsApp"), ("spotify", "Spotify"), ("applePodcasts", "Apple Podcasts"), ("ivoox", "iVoox"), ("youtube", "YouTube"), ("instagram", "Instagram")) if AJ.get(k)]
    social += [("podcast.xml", "Pódcast (RSS)"), ("widget.html", "Widget para parroquias")]
    return f'''<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand">
      <a class="brand" href="{r}index.html">{ICON["logo"]}<span>Rezo<b>Diario</b></span></a>
      <p>Oración guiada cada día con el Evangelio, el Santo Rosario y más de {len(PRAYERS)} oraciones para todos los momentos de la vida. Gratis y sin registro.</p>
      <p class="verse">«Venid a mí todos los que estáis cansados y agobiados, y yo os aliviaré.» Mt 11, 28</p>
    </div>
    {col("Rezar", [("evangelio-de-hoy.html", "Evangelio de hoy"), ("evangelio-de-manana.html", "Evangelio de mañana"), ("santo-de-hoy.html", "Santo de hoy"), ("rosario.html", "Misterios del Rosario de hoy"), ("via-crucis.html", "Vía Crucis"), ("novenas/index.html", "Novenas"), ("adviento.html", "Adviento 2026")])}
    {col("Oraciones", [(f"oraciones/{s}.html", l) for s, l in pop])}
    {col("Síguenos", social)}
  </div>
  <div class="wrap foot-bot">
    <span>© {TODAY[:4]} Rezo Diario · rezodiario.com</span>
    <span><a href="{r}sobre-nosotros.html">Quiénes somos</a> · <a href="{r}legal/aviso-legal.html">Aviso legal</a> · <a href="{r}legal/privacidad.html">Privacidad</a> · <a href="{r}legal/cookies.html">Cookies</a> · <a href="{r}donar.html">Donar</a></span>
  </div>
</footer>'''

def ld(obj): return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
def crumbs_ld(items): return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": canon(p)} for i, (n, p) in enumerate(items)]}
def crumbs_html(r, items):
    li = "".join(f'<li><a href="{r}{p}">{E(n)}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{E(n)}</li>' for i, (n, p) in enumerate(items))
    return f'<ol class="crumbs">{li}</ol>'
def faq_ld(qs): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qs]}
def faq_html(qs): return '<div class="faq">' + "".join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(qs)) + '</div>'

def page(path, title, desc, main, active="", lds=(), body_attrs="", og_type="website", mini=False, robots="index, follow, max-image-preview:large"):
    depth = path.count("/"); r = "../" * depth
    cfg = {"supabaseUrl": AJ.get("supabaseUrl", ""), "supabaseAnonKey": AJ.get("supabaseAnonKey", ""), "today": TODAY}
    head = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon(path)}">
<meta name="theme-color" content="#14302A">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Rezo Diario"><meta property="og:locale" content="es_ES">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon(path)}"><meta property="og:image" content="{SITE}og-rezodiario.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}icon.svg" type="image/svg+xml"><link rel="manifest" href="{r}manifest.webmanifest"><link rel="alternate" type="application/rss+xml" title="Rezo Diario (pódcast)" href="{SITE}podcast.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Manrope:wght@400;500;600;700;800&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;1,7..72,400&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
<script>window.RD_CONFIG={json.dumps(cfg)}</script>
''' + "\n".join(ld(x) for x in lds)
    minihtml = '<div class="mini" id="mini" hidden><button id="miniBtn" aria-label="Pausar"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg></button><div><strong id="miniT"></strong><span id="miniS"></span></div></div>' if mini else ""
    body = f'''{header(r, active)}
<main id="main">
{main}
</main>
{footer(r)}
{tabbar(r, active)}
{drawer(r)}
{ACCOUNT}
{minihtml}
<div id="toastHost"></div>
<script src="{r}assets/data.js"></script>
<script src="{r}assets/site.js"></script>'''
    pages.append((path, head, body, body_attrs + f' data-root="{r}"'))

# ---------- componentes ----------
def player():
    return f'''<article class="player" id="player" aria-label="Reproductor del rezo del día">
      <div class="p-head"><span class="eyebrow">Rezo del día</span><span class="p-time" id="pTime"></span></div>
      <h2 class="p-title" id="pTitle"></h2>
      <div class="orb" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="p-seg" id="pSeg">Entrar en silencio</div>
      <p class="p-text" id="pText" aria-live="polite">Pulsa el botón y respira. Te acompañamos.</p>
      <div class="pills" id="pills"></div>
      <div class="controls">
        <button class="ctl" id="pPrev" aria-label="Parte anterior"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h2v14H6zM20 5v14L9 12z"/></svg></button>
        <button class="play" id="pPlay" aria-label="Reproducir">{ICON["play"]}</button>
        <button class="ctl" id="pNext" aria-label="Parte siguiente"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16 5h2v14h-2zM4 5v14l11-7z"/></svg></button>
      </div>
      <div class="p-foot"><button class="tog" id="tSpeed">Velocidad 1×</button><button class="tog" id="tMusic" aria-pressed="true">Música de fondo</button><button class="tog" id="tVoice" aria-pressed="true">Voz guía</button></div>
    </article>'''

def week_section(r, mode="select", title="Esta semana, día a día", sub="Desliza para volver a un rezo que te perdiste o adelantar el de mañana."):
    lo = max(0, ti - 6); hi = min(len(DAYS), ti + 7)
    links = "".join(f'<li><a href="{r}evangelio/{w["date"]}.html">{w["wd"]} {w["n"]} de {w["mes"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in DAYS[lo:hi])
    return f'''<section class="sec" aria-labelledby="hWeek"><div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Sigue rezando</span><h2 id="hWeek">{title}</h2><p>{sub}</p></div>
      <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><span class="streak" id="streak"></span><div class="arrows"><button class="icon-btn" data-scroll="week" data-dir="-1" aria-label="Días anteriores">‹</button><button class="icon-btn" data-scroll="week" data-dir="1" aria-label="Días siguientes">›</button></div></div></div>
    <div class="rail" id="week" role="list" data-mode="{mode}"></div>
    <noscript><ul class="links">{links}</ul></noscript>
  </div></section>'''

def chapel(r, full=False):
    feed = '<ul class="feed" id="vFeed" aria-label="Intenciones de esta semana"></ul>' if full else f'<p style="margin-top:22px"><a class="btn btn-wax sm" href="{r}muro-de-intenciones.html">Ver todas las intenciones</a></p>'
    h = "h1" if full else "h2"
    return f'''<section class="chapel" id="chapel" data-limit="{120 if full else 30}" data-full="{1 if full else 0}" aria-labelledby="hChapel"><div class="wrap sec">
  <span class="eyebrow">Muro de intenciones</span>
  <{h} id="hChapel" style="font-family:var(--f-display);font-weight:400;font-size:clamp(32px,4.6vw,54px);line-height:1.05;margin:10px 0 0">Enciende una vela por tu intención</{h}>
  <p class="sub">Deja tu petición y enciende una vela. Arderá durante siete días y se irá consumiendo poco a poco. Quien la vea podrá rezar por ti.</p>
  <div class="chapel-stats"><div><b id="vStat1">0</b><span>velas esta semana</span></div><div><b id="vStat2">0</b><span>oraciones por otros</span></div></div>
  <div class="altar">
    <div style="min-width:0"><div class="rack"><div class="candles" id="candles" aria-label="Velas encendidas"></div><div class="shelf"></div></div>{feed}</div>
    <div style="min-width:0">
      <div class="reader" id="vReader" aria-live="polite"></div>
      <form class="light-form" id="vForm">
        <label for="vText">Tu intención</label>
        <textarea id="vText" maxlength="160" placeholder="Por mi madre, que mañana entra en quirófano"></textarea>
        <div class="count" id="vCount">0/160</div>
        <label for="vName">Tu nombre de pila (opcional)</label>
        <input type="text" id="vName" maxlength="30" placeholder="Ana" autocomplete="given-name">
        <span class="sr" id="vCatL">Tipo de intención</span><div class="cc" id="vCats" role="radiogroup" aria-labelledby="vCatL"></div>
        <label class="chk"><input type="checkbox" id="vPriv"> Intención privada: solo se ve la vela, no el texto</label>
        <button class="btn btn-flame" id="vSubmit" type="submit">Encender mi vela</button>
        <p class="note" id="vMode" style="margin:0"></p>
        <p class="note" style="margin:0">No escribas apellidos, teléfonos ni direcciones. Las intenciones que reciben varios avisos se ocultan y se revisan.</p>
      </form>
    </div>
  </div>
</div></section>'''

def card(p, r):
    c = CATS[p["cat"]]; ex = p["x"].replace("\n", " ")
    return f'<a class="card" href="{r}oraciones/{p["slug"]}.html" data-cat="{p["cat"]}" data-k="{E(p["t"] + " " + p["k"] + " " + c["name"] + " " + ex)}"><span class="cat"><i style="background:{c["color"]}"></i>{c["name"]}</span><h3>{E(p["t"])}</h3><p>{E(ex)}</p><span class="meta"><span>{p["min"]} min</span><span class="go">{ICON["arrow"]}</span></span></a>'

def tiles(r): return '<div class="tiles">' + "".join(f'<a class="tile reveal" href="{r}oraciones/tema-{k}.html" style="--tc:{c["color"]}"><i></i><b>{c["name"]}</b><span>{sum(1 for p in PRAYERS if p["cat"] == k)} oraciones</span></a>' for k, c in CATS.items()) + '</div>'

def give():
    dn = AJ.get("donaciones", {}); goal = dn.get("objetivoMensual") or 0; have = dn.get("donantesMes") or 0
    meter = f'<div style="margin-bottom:16px"><div style="display:flex;justify-content:space-between;font-size:14px;font-weight:700"><span>Donantes este mes</span><span style="font-variant-numeric:tabular-nums">{have} de {goal}</span></div><div class="split" style="margin:8px 0 0;background:var(--surface-2)"><i style="width:{min(100, round(have / goal * 100)) if goal else 0}%;background:var(--gold)"></i></div></div>' if goal else ""
    return f'''<div class="give reveal" id="give" data-pay="{E(dn.get("enlacePago", ""))}">{meter}
      <div class="seg" role="tablist" aria-label="Frecuencia"><button class="on" data-f="once">Una vez</button><button data-f="month">Cada mes</button></div>
      <div class="amts" id="amts"></div>
      <div class="other"><label for="otherAmt">Otra cantidad (€)</label><input class="field" id="otherAmt" type="number" min="1" step="1" inputmode="numeric" placeholder="15"></div>
      <p class="impact" id="impact"></p>
      <button class="btn btn-gold" id="donBtn">Donar 10 €</button>
      <div class="safe"><span>Pago seguro</span><span>Tarjeta · Bizum · PayPal</span></div>
      <div class="thanks" id="thanks" hidden></div>
    </div>'''

def donate_section(h="h2"):
    return f'''<section class="sec band" id="donar" aria-labelledby="hDon"><div class="wrap don">
    <div class="reveal"><span class="eyebrow">Donaciones</span><{h} id="hDon" style="font-family:var(--f-display);font-weight:400;font-size:clamp(30px,4.2vw,48px);line-height:1.08;margin:10px 0 0">Ayúdanos a que nadie rece solo</{h}>
      <p style="color:var(--muted);max-width:34em">Rezo Diario es gratis y sin anuncios porque muchas personas aportan lo que pueden. Con tu donativo publicamos audios nuevos cada día y llevamos la oración a más idiomas.</p>
      <div class="split" aria-hidden="true"><i style="width:45%;background:var(--accent)"></i><i style="width:25%;background:var(--gold)"></i><i style="width:20%;background:var(--c-study)"></i><i style="width:10%;background:var(--c-grief)"></i></div>
      <div class="legend"><span><i style="background:var(--accent)"></i>Audios y música<b>45%</b></span><span><i style="background:var(--gold)"></i>Servidores y web<b>25%</b></span><span><i style="background:var(--c-study)"></i>Traducciones<b>20%</b></span><span><i style="background:var(--c-grief)"></i>Gestión<b>10%</b></span></div>
      <p class="hint" style="margin-top:12px">Ejemplo de reparto: sustitúyelo por vuestras cuentas reales.</p></div>
    {give()}
  </div></section>'''

def news():
    wa = AJ.get("whatsappCanal")
    extra = f'<a class="btn" href="{E(wa)}" target="_blank" rel="noopener" style="background:#25D366;color:#06301A">Seguir el canal de WhatsApp</a>' if wa else ''
    return f'''<section class="news" aria-labelledby="hNews"><div class="wrap news-in">
    <div><h2 id="hNews">El rezo de cada día, en tu móvil</h2><p>Un mensaje breve a las 7:00 con el audio y el Evangelio. Por correo{" o por WhatsApp" if wa else ""}. Sin publicidad.</p>{f'<p style="margin-top:14px">{extra}</p>' if extra else ''}</div>
    <form id="newsForm" novalidate><label class="sr" for="email">Tu correo electrónico</label><input id="email" type="email" placeholder="tu@correo.com" autocomplete="email"><button class="btn" type="submit">Apuntarme</button><p class="msg" id="newsMsg" hidden></p></form>
  </div></section>'''

def phero(r, crumbs, eyebrow, h1, lead, extra=""): return f'<section class="phero"><div class="wrap">{crumbs_html(r, crumbs)}<div class="eyebrow" style="margin-top:22px">{eyebrow}</div><h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div></section>'
def sec(inner, cls="sec"): return f'<section class="{cls}"><div class="wrap">{inner}</div></section>'
def head2(eyebrow, h, p="", right=""): return f'<div class="sec-head"><div><span class="eyebrow">{eyebrow}</span><h2>{h}</h2>{f"<p>{p}</p>" if p else ""}</div>{right}</div>'
def saint_link(r, s): return f'<a class="saintcard reveal" href="{r}santos/{s["slug"]}.html"><small>{s["date"]}</small><b>{E(s["name"])}</b><span>{E(s["short"])}</span></a>'
def setname(d): return SETS[d["set"]]["name"].lower()

def season_feature(r):
    if TODAY < "2026-11-29":
        return (f"{r}adviento.html", "linear-gradient(150deg,#5B3D7A,#24163A)", f"Empieza el 29 de noviembre", "Adviento 2026", "Corona, reto diario, novena a la Inmaculada y la espera de la Navidad.")
    if TODAY <= "2026-12-24":
        return (f"{r}retos/adviento.html", "linear-gradient(150deg,#5B3D7A,#24163A)", "Un gesto cada día", "Reto de Adviento", "26 gestos pequeños para preparar la Navidad.")
    return (f"{r}navidad.html", "linear-gradient(150deg,#A8812D,#4A3510)", "Tiempo de Navidad", "Navidad 2026", "Oraciones para Nochebuena, Navidad y fin de año.")
def novena_now():
    for n in NOVENAS:
        if n["start"] <= TODAY <= n["end"]: return n, f'Hoy toca el día {(datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(n["start"])).days + 1}'
    up = [n for n in NOVENAS if n["start"] > TODAY]
    if up: return up[0], f'Empieza el {fdate(up[0]["start"])}'
    return NOVENAS[0], "Para rezar en cualquier momento"

# ================= PORTADA =================
r = ""
home_faq = [("¿Rezo Diario es gratis?", "Sí. Todos los rezos, audios, el Rosario y el muro de velas son gratuitos y no necesitas registrarte. El proyecto se sostiene con donaciones voluntarias."),
 ("¿Qué misterios del Rosario se rezan cada día?", "Lunes y sábado, misterios gozosos; martes y viernes, dolorosos; miércoles y domingo, gloriosos; jueves, luminosos."),
 ("¿Cuánto dura el rezo diario?", "Unos minutos: música para entrar en silencio, el Evangelio del día, unas preguntas para la reflexión con tiempo de silencio y una oración final."),
 ("¿Cómo funciona el muro de velas?", "Escribes tu intención, eliges si es pública o privada y enciendes una vela. Arde siete días y otras personas pueden pulsar «He rezado por ti»."),
 ("¿Rezo Diario es católico?", "Sí. Sigue el calendario litúrgico de la Iglesia católica y el Evangelio de cada día, y está abierto a cualquier persona que quiera rezar.")]
popular = ["oracion-antes-de-un-examen", "oracion-por-un-enfermo", "oracion-para-la-ansiedad", "oracion-a-san-judas-tadeo", "oracion-por-un-difunto", "oracion-para-dormir", "oracion-por-la-familia", "oracion-para-encontrar-trabajo", "acordaos", "oracion-antes-de-una-operacion"]
ts = SBY.get(TW["saint"]); sf = season_feature(r); nv, nvs = novena_now()
home_main = f'''<section class="hero" aria-labelledby="h1">
  <canvas id="rose" aria-hidden="true"></canvas>
  <div class="wrap hero-in">
    <div class="stag">
      <div class="eyebrow" id="hDate">{TW["wd"]}, {TW["n"]} de {TW["mes"]} de {TODAY[:4]}</div>
      <div class="lit" id="hLit"><i class="dot" style="background:{LITC[TW["color"]][0]}"></i><span>{E(TW["lit"])}</span></div>
      <h1 id="h1">Un momento con Dios, <em>cada día.</em></h1>
      <p class="lead">Escucha el Evangelio de hoy con música y silencio, reza el Rosario cuenta a cuenta, enciende una vela por tu intención y encuentra una oración para cada momento.</p>
      <div class="hero-cta"><button class="btn btn-gold" id="ctaPlay">{ICON["play"]}<span data-i18n="listen">Escuchar el rezo de hoy</span></button><a class="btn btn-ghost" href="muro-de-intenciones.html" data-i18n="light">Enciende una vela</a></div>
      <div class="facts"><div><small>Evangelio</small><span id="fRef">{TW["ref"]}</span></div><div><small>Rosario de hoy</small><span id="fSet">Misterios {setname(TW)}</span></div><div><small>Duración</small><span id="fDur">5 min</span></div></div>
    </div>
    {player()}
  </div>
</section>
{week_section(r)}
<section class="sec band" id="momento" aria-labelledby="hMom"><div class="wrap assist">
  <div class="reveal"><span class="eyebrow">Para este momento</span><h2 id="hMom">¿Qué llevas hoy en el corazón?</h2>
    <p style="color:var(--muted);margin:10px 0 0">Cuéntanos con tus palabras o toca una opción. Te proponemos las oraciones que mejor encajan.</p>
    <div class="feel" id="feel"></div>
    <form class="ask" id="askForm"><label class="sr" for="askIn">Describe cómo te sientes</label><input id="askIn" placeholder="Ej.: mañana tengo un examen y estoy nervioso" autocomplete="off"><button class="btn btn-accent" type="submit">Buscar</button></form>
    <p class="note">Este buscador no sustituye el acompañamiento espiritual, médico o psicológico. Si estás pasando por un momento muy difícil, llama al <strong>024</strong> (atención a la conducta suicida, España) o al <strong>112</strong> si es una emergencia.</p></div>
  <div class="answers" id="answers" aria-live="polite"></div>
</div></section>
{sec(head2("Oraciones por tema", "Un rezo para cada momento", f"{len(PRAYERS)} oraciones para estudiar, por un enfermo, por tu familia, para la ansiedad o por un ser querido difunto.", '<a class="btn btn-ghost sm" href="oraciones/index.html">Ver todas</a>') + tiles(r))}
{chapel(r)}
{sec(head2("Devociones", "Reza a tu ritmo") + f"""<div class="duo">
  <a class="feature reveal" href="{sf[0]}" style="background:{sf[1]}"><small>{sf[2]}</small><b>{sf[3]}</b><p>{sf[4]}</p></a>
  <a class="feature reveal" href="novenas/{nv["slug"]}.html" style="background:linear-gradient(150deg,#6E64A8,#2A2350)"><small>{nvs}</small><b>{E(nv["t"])}</b><p>Nueve días de oración con recordatorio de qué día toca.</p></a>
  <a class="feature reveal" href="rosario.html" style="background:linear-gradient(150deg,#2C5D47,#14302A)"><small>Hoy · Misterios {setname(TW)}</small><b>Santo Rosario guiado</b><p>Cuenta a cuenta, con la cita del Evangelio y el fruto de cada misterio.</p></a>
</div>""")}
{sec(f"""<div class="gos">
  <article class="panel reveal"><span class="eyebrow">Evangelio de hoy · <span id="gRefL">{TW["refL"]}</span></span><h2 id="gTitle" style="margin-top:8px">{E(TW["title"])}</h2><p class="quote" id="gQuote">{E(TW["ex"])}</p>
    <div class="hero-cta" style="margin-top:6px"><a class="btn btn-accent sm" id="gLink" href="evangelio/{TODAY}.html">Leer el Evangelio y la reflexión</a><a class="btn btn-ghost sm" href="evangelio-de-manana.html">Evangelio de mañana</a></div></article>
  <aside class="panel saint reveal"><span class="eyebrow">Santo de hoy</span><h3>{E(ts["name"]) if ts else "Feria"}</h3><p style="opacity:.85">{E(ts["bio"][0]) if ts else "Hoy no hay ninguna memoria en el calendario general."}</p><a class="btn btn-ghost sm" href="santo-de-hoy.html" style="margin-top:10px">Vida y oración</a></aside>
</div>""", "sec band")}
{sec(head2("Las más rezadas", "Oraciones populares") + '<ul class="links" style="columns:2 280px;column-gap:40px;display:block">' + "".join(f'<li style="break-inside:avoid"><a href="oraciones/{s}.html">{E(PBY[s]["t"])}<small>{PBY[s]["min"]} min</small></a></li>' for s in popular) + '</ul>')}
{news()}
{sec(head2("Preguntas frecuentes", "Lo que suelen preguntarnos") + faq_html(home_faq))}
{donate_section()}'''
page("index.html", "Rezo Diario · Oración diaria, Evangelio de hoy, Rosario y velas",
 f"Reza cada día con Rezo Diario: audio con el Evangelio de hoy, Santo Rosario guiado, muro de velas por tus intenciones y {len(PRAYERS)} oraciones para estudios, salud, familia y trabajo.",
 home_main, "today", [{"@context": "https://schema.org", "@type": "WebSite", "url": SITE, "name": "Rezo Diario", "inLanguage": "es", "publisher": ORG, "potentialAction": {"@type": "SearchAction", "target": SITE + "oraciones/index.html?q={search_term_string}", "query-input": "required name=search_term_string"}},
 {"@context": "https://schema.org", **ORG}, faq_ld(home_faq)], mini=True)

# ================= BIBLIOTECA =================
r = "../"
chips = '<div class="chips" id="chips" role="tablist" aria-label="Temas"><button class="chip on" data-c="todos">Todas</button>' + "".join(f'<button class="chip" data-c="{k}">{c["name"]}</button>' for k, c in CATS.items()) + '</div>'
lib = phero(r, [("Inicio", "index.html"), ("Oraciones", "oraciones/index.html")], "Biblioteca de oraciones", "Oraciones católicas para cada momento",
 f"{len(PRAYERS)} oraciones para leer, escuchar y copiar: antes de un examen, por un enfermo, para la ansiedad, por la familia, por los difuntos, de Adviento y Navidad y las oraciones tradicionales de siempre.") + \
 sec(f'''<div class="tools" id="buscar">{chips}<div class="find">{ICON["search"]}<label class="sr" for="q">Buscar oración</label><input id="q" type="search" placeholder="Buscar: examen, enfermo, noche…"></div></div>
 <p class="hint" id="libCount" style="margin:-8px 0 14px"></p>
 <div class="box" id="favList" hidden style="margin-bottom:18px"><h3>Tus oraciones guardadas</h3><ul class="links"></ul></div>
 <div class="grid" id="libGrid">{"".join(card(p, r) for p in PRAYERS)}</div><div class="empty" id="libEmpty" hidden></div>''') + sec(head2("Por tema", "Explora por temas") + tiles(r), "sec band")
page("oraciones/index.html", "Oraciones católicas para cada momento | Rezo Diario", f"{len(PRAYERS)} oraciones católicas para leer y escuchar: antes de un examen, por un enfermo, para la ansiedad, por la familia, por los difuntos, de Adviento y tradicionales.",
 lib, "prayers", [crumbs_ld([("Inicio", "index.html"), ("Oraciones", "oraciones/index.html")]), {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Oraciones católicas para cada momento", "url": canon("oraciones/index.html"), "inLanguage": "es"}])

for k, c in CATS.items():
    ps = [p for p in PRAYERS if p["cat"] == k]; path = f"oraciones/tema-{k}.html"
    cr = [("Inicio", "index.html"), ("Oraciones", "oraciones/index.html"), (c["name"], path)]
    m = phero(r, cr, f'{len(ps)} oraciones', c["h1"], c["intro"]) + sec(f'<div class="grid">{"".join(card(p, r) for p in ps)}</div>') + sec(head2("Preguntas frecuentes", "Dudas sobre estas oraciones") + faq_html(FAQ_CAT[k]), "sec band") + sec(head2("Otros temas", "Sigue explorando") + tiles(r))
    page(path, f'{c["h1"]} | Rezo Diario', c["intro"][:158], m, "prayers", [crumbs_ld(cr), faq_ld(FAQ_CAT[k]), {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["h1"], "url": canon(path), "inLanguage": "es"}])

def desc_for(p):
    first = re.split(r"(?<=[.!?])\s", p["x"].replace("\n", " "))[0]
    d = f'{p["t"]}: «{first}» Texto completo para rezar y escuchar.'
    return d if len(d) <= 160 else (d[:150].rsplit(" ", 1)[0] + "…»")
for p in PRAYERS:
    c = CATS[p["cat"]]; path = f'oraciones/{p["slug"]}.html'
    cr = [("Inicio", "index.html"), ("Oraciones", "oraciones/index.html"), (c["name"], f'oraciones/tema-{p["cat"]}.html'), (p["t"], path)]
    rel = [q for q in PRAYERS if q["cat"] == p["cat"] and q["slug"] != p["slug"]][:5]
    wa = "https://wa.me/?text=" + html.escape((p["t"] + " " + canon(path)).replace(" ", "%20"))
    faq = [(f'¿Cuándo rezar la {p["t"][0].lower() + p["t"][1:]}?' if p["t"].startswith("Oración") else f'¿Cuándo rezar «{p["t"]}»?', p["when"])] + FAQ_CAT[p["cat"]]
    m = phero(r, cr, f'<span style="display:inline-flex;align-items:center;gap:8px"><i class="dot" style="background:{c["color"]}"></i>{c["name"]} · {p["min"]} min</span>', E(p["t"]), E(p["when"])) + f'''
<section class="sec"><div class="wrap art">
  <div style="min-width:0">
    <article class="pray reveal"><p class="pray-text" id="prayText">{E(p["x"])}</p>
      <div class="pray-acts"><button class="btn btn-accent sm" id="btnSpeak">Escuchar</button><button class="btn btn-ghost sm" id="btnCopy">Copiar oración</button><button class="btn btn-ghost sm" id="btnFav" aria-pressed="false">☆ Guardar</button><a class="btn btn-ghost sm" href="{wa}" target="_blank" rel="noopener">Compartir por WhatsApp</a></div>
    </article>
    <div class="prose">
      <h2>Cuándo rezarla</h2><p>{E(p["when"])}</p>
      <h2>Cómo rezarla</h2><p>Busca un momento de calma, respira despacio y lee la oración sin prisa, en voz baja o en silencio. Si una frase te toca, quédate en ella. Puedes pulsar «Escuchar» para que la web la lea por ti, o guardarla en favoritos para tenerla a mano.</p>
      <p>Si rezas por otra persona, díselo: saber que alguien reza por nosotros es un gran consuelo. También puedes <a href="{r}muro-de-intenciones.html#{CANDLE_HASH[p["cat"]]}">encender una vela por esta intención</a> para que otros recen contigo.</p>
      <h2>Preguntas frecuentes</h2>{faq_html(faq)}
    </div>
  </div>
  <aside class="side">
    <div class="box candle-cta"><h3>Enciende una vela</h3><p>Deja esta intención en el muro y otras personas rezarán por ella durante siete días.</p><a class="btn btn-flame sm" href="{r}muro-de-intenciones.html#{CANDLE_HASH[p["cat"]]}">Encender una vela</a></div>
    <div class="box"><h3>Más oraciones de {c["name"].lower()}</h3><ul class="links">{"".join(f'<li><a href="{q["slug"]}.html">{E(q["t"])}<small>{q["min"]} min</small></a></li>' for q in rel)}</ul></div>
    <div class="box"><h3>Rezo de hoy</h3><p style="margin:0 0 12px;color:var(--muted);font-size:14.5px">{E(TW["title"])} · {TW["ref"]}</p><a class="btn btn-accent sm" href="{r}evangelio-de-hoy.html">Escuchar el rezo</a></div>
  </aside>
</div></section>'''
    page(path, f'{p["t"]} | Rezo Diario', desc_for(p), m, "prayers",
     [crumbs_ld(cr), faq_ld(faq), {"@context": "https://schema.org", "@type": "Article", "headline": p["t"], "description": desc_for(p), "inLanguage": "es", "articleSection": c["name"], "author": ORG, "publisher": ORG, "datePublished": "2026-10-17", "dateModified": TODAY, "mainEntityOfPage": canon(path), "keywords": p["k"]}],
     body_attrs=f' data-slug="{p["slug"]}"', og_type="article")

# ================= EVANGELIO =================
def gospel_main(r, w, kind):
    s = SBY.get(w["saint"])
    title = {"hoy": "Evangelio de hoy", "manana": "Evangelio de mañana"}.get(kind, f'Evangelio del {w["wd"].lower()} {w["n"]} de {w["mes"]}')
    cr = [("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")] + ([("Hoy", "evangelio-de-hoy.html")] if kind == "hoy" else [("Mañana", "evangelio-de-manana.html")] if kind == "manana" else [(f'{w["n"]} de {w["mes"]}', f'evangelio/{w["date"]}.html')])
    ex = EXTRA.get(w["date"])
    box = f'<aside class="panel saint reveal"><span class="eyebrow">Santo del día</span><h3>{E(s["name"])}</h3><p style="opacity:.85">{E(s["bio"][0])}</p><a class="btn btn-ghost sm" href="{r}santos/{s["slug"]}.html">Vida y oración</a></aside>' if s else f'<aside class="panel saint reveal"><span class="eyebrow">Liturgia</span><h3>{E(ex["t"] if ex else w["lit"])}</h3><p style="opacity:.85">{E(ex["x"] if ex else "Rezo Diario sigue el calendario litúrgico de la Iglesia católica.")}</p></aside>'
    i = DAYS.index(w); prv = DAYS[i - 1] if i else None; nxt = DAYS[i + 1] if i < len(DAYS) - 1 else None
    pn = f'<div class="hero-cta" style="margin-top:18px">' + (f'<a class="btn btn-ghost sm" href="{r}evangelio/{prv["date"]}.html">‹ {prv["n"]} de {prv["mes"]}</a>' if prv else "") + (f'<a class="btn btn-ghost sm" href="{r}evangelio/{nxt["date"]}.html">{nxt["n"]} de {nxt["mes"]} ›</a>' if nxt else "") + '</div>'
    m = f'''<section class="hero" aria-labelledby="h1"><canvas id="rose" aria-hidden="true"></canvas><div class="wrap hero-in">
  <div class="stag">{crumbs_html(r, cr)}<div class="eyebrow" style="margin-top:22px" id="hDate">{w["wd"]}, {w["n"]} de {w["mes"]} de {w["date"][:4]}</div>
   <div class="lit" id="hLit"><i class="dot" style="background:{LITC[w["color"]][0]}"></i><span>{E(w["lit"])}</span></div>
   <h1 id="h1" style="font-size:clamp(36px,5vw,62px)">{title}: <em>{E(w["title"])}</em></h1>
   <p class="lead">{E(w["refL"])}. {E(w["sum"])}</p>
   <div class="facts"><div><small>Evangelio</small><span id="fRef">{w["ref"]}</span></div><div><small>Color litúrgico</small><span>{LITC[w["color"]][1].split(" · ")[0]}</span></div><div><small>Rosario</small><span id="fSet">Misterios {setname(w)}</span></div></div></div>
  {player()}</div></section>
<section class="sec"><div class="wrap gos">
  <article class="panel reveal"><span class="eyebrow">{E(w["refL"])}</span><p class="quote">{E(w["ex"])}</p><p>{E(w["sum"])}</p>
   <h3>Reflexión</h3><p>{E(w["refl"])}</p><h3>Preguntas para tu oración</h3><ol class="qs">{"".join(f"<li>{E(q)}</li>" for q in w["qs"])}</ol>
   <h3>Oración final</h3><p style="font-family:var(--f-read);font-style:italic">{E(w["fin"])}</p>
   <div class="hero-cta" style="margin-top:22px"><a class="btn btn-ghost sm" href="https://www.vaticannews.va/es/evangelio-de-hoy.html" target="_blank" rel="noopener">Lecturas completas del día</a><a class="btn btn-ghost sm" href="{r}rosario.html">Rezar el Rosario</a></div>{pn}</article>
  {box}
</div></section>
{week_section(r, "link", "Evangelios de estos días", "Vuelve a cualquier día o adelanta los próximos.")}'''
    return m, cr
def gld(w, path): return {"@context": "https://schema.org", "@type": "PodcastEpisode", "name": f'{w["title"]} · Rezo del {w["n"]} de {w["mes"]} de {w["date"][:4]}', "datePublished": w["date"], "inLanguage": "es", "description": w["sum"], "url": canon(path), "partOfSeries": {"@type": "PodcastSeries", "name": "Rezo Diario", "url": SITE}, **({"associatedMedia": {"@type": "MediaObject", "contentUrl": SITE + w["audio"].lstrip("/")}} if w.get("audio") else {})}
for w in DAYS:
    m, cr = gospel_main("../", w, "dia"); path = f'evangelio/{w["date"]}.html'
    page(path, f'Evangelio del {w["n"]} de {w["mes"]} de {w["date"][:4]} ({w["ref"]}): {w["title"]} | Rezo Diario', f'Evangelio del {nice(w)}, {w["refL"]}: «{w["ex"]}» Reflexión y audio para rezar.'[:160], m, "gospel", [crumbs_ld(cr), gld(w, path)], body_attrs=f' data-day="{w["date"]}"', mini=True, og_type="article")
m, cr = gospel_main("", TW, "hoy")
page("evangelio-de-hoy.html", f'Evangelio de hoy, {nice(TW)} ({TW["ref"]}) | Rezo Diario', f'Evangelio de hoy {TW["n"]} de {TW["mes"]}, {TW["refL"]}: «{TW["ex"]}» Comentario, preguntas y audio para rezar.'[:160], m, "gospel", [crumbs_ld(cr), gld(TW, "evangelio-de-hoy.html")], body_attrs=f' data-day="{TODAY}"', mini=True)
m, cr = gospel_main("", TOMORROW, "manana")
page("evangelio-de-manana.html", f'Evangelio de mañana, {nice(TOMORROW)} ({TOMORROW["ref"]}) | Rezo Diario', f'Evangelio de mañana {TOMORROW["n"]} de {TOMORROW["mes"]}, {TOMORROW["refL"]}: «{TOMORROW["ex"]}» Prepara tu oración.'[:160], m, "gospel", [crumbs_ld(cr)], body_attrs=f' data-day="{TOMORROW["date"]}"', mini=True)
months = {}
for w in DAYS: months.setdefault(w["date"][:7], []).append(w)
arch = "".join(f'<h2 style="margin-top:34px">{MES[int(k[5:]) - 1].capitalize()} de {k[:4]}</h2><ul class="links" style="columns:2 300px;column-gap:40px;display:block">' + "".join(f'<li style="break-inside:avoid"><a href="{w["date"]}.html">{w["wd"]} {w["n"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in v) + '</ul>' for k, v in months.items())
page("evangelio/index.html", "Archivo del Evangelio del día | Rezo Diario", "Todos los Evangelios del día con su comentario, preguntas para rezar y audio, ordenados por meses.",
 phero("../", [("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")], "Archivo", "El Evangelio de cada día", "Vuelve a cualquier día: cada Evangelio con su comentario, sus preguntas y su audio.") + sec(f'<div class="prose" style="max-width:none">{arch}</div>'), "gospel", [crumbs_ld([("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")])])

# ================= SANTOS =================
r = ""
s = SBY.get(TW["saint"]) or next((x for x in SAINTS if x["md"] == TODAY[5:]), None)
upcoming = [w for w in DAYS[ti:ti + 10] if w["saint"]]
if s:
    st_main = phero(r, [("Inicio", "index.html"), ("Santo de hoy", "santo-de-hoy.html")], f'Santo de hoy · {TW["wd"]} {TW["n"]} de {TW["mes"]}', E(s["name"]), E(s["short"]) + ". " + E(s["bio"][0])) + \
     sec(f'<div class="art"><div class="prose">{"".join(f"<p>{E(b)}</p>" for b in s["bio"][1:])}<h2>Oración</h2><p style="font-family:var(--f-read);font-style:italic;font-size:19px">{E(s["oracion"])}</p><p><a class="btn btn-accent sm" href="santos/{s["slug"]}.html">Ver la página completa</a></p></div><aside class="side"><div class="box"><h3>Próximos santos</h3><ul class="links">{"".join(f"<li><a href=\"santos/{w['saint']}.html\">{E(SBY[w['saint']]['name'])}<small>{w['n']} {w['mes'][:3]}</small></a></li>" for w in upcoming)}</ul></div></aside></div>')
    stitle = f'Santo de hoy, {TW["n"]} de {TW["mes"]}: {s["name"]} | Rezo Diario'; sdesc = f'Santo de hoy {TW["n"]} de {TW["mes"]}: {s["name"]}. {s["short"]}. Su vida en breve y una oración para pedir su intercesión.'[:160]
else:
    ex = EXTRA.get(TODAY, {"t": "Hoy es día de feria", "x": "Hoy no hay ninguna memoria en el calendario general de la Iglesia."})
    st_main = phero(r, [("Inicio", "index.html"), ("Santo de hoy", "santo-de-hoy.html")], f'Santo de hoy · {TW["wd"]} {TW["n"]} de {TW["mes"]}', E(ex["t"]), E(ex["x"])) + sec(head2("Próximos días", "Santos de los próximos días") + '<div class="pagegrid">' + "".join(saint_link(r, SBY[w["saint"]]) for w in upcoming) + '</div>')
    stitle = f'Santo de hoy, {TW["n"]} de {TW["mes"]} | Rezo Diario'; sdesc = f'Santo de hoy {TW["n"]} de {TW["mes"]}: {ex["t"]}. Santos de los próximos días con su vida y su oración.'
st_main += sec(head2("Santos populares", "Santos a los que más se reza") + '<div class="pagegrid">' + "".join(saint_link(r, SBY[x]) for x in ["san-judas-tadeo", "santa-rita-de-casia", "san-expedito", "san-antonio-de-padua", "san-jose", "virgen-de-guadalupe"]) + '</div>', "sec band")
page("santo-de-hoy.html", stitle, sdesc, st_main, "saints", [crumbs_ld([("Inicio", "index.html"), ("Santo de hoy", "santo-de-hoy.html")])])
r = "../"
bym = {}
for x in sorted(SAINTS, key=lambda x: x["md"]): bym.setdefault(int(x["md"][:2]), []).append(x)
cal = "".join(f'<h2 style="margin-top:34px">{MES[m - 1].capitalize()}</h2><div class="pagegrid">' + "".join(saint_link(r, x) for x in v) + '</div>' for m, v in bym.items())
page("santos/index.html", "Santoral católico: vida y oración de cada santo | Rezo Diario", "Santoral con la vida breve y la oración de cada santo: san Judas Tadeo, santa Rita, san Expedito, la Inmaculada, la Virgen de Guadalupe y el santo de cada día.",
 phero(r, [("Inicio", "index.html"), ("Santos", "santos/index.html")], "Santoral", "Santoral: la vida y la oración de cada santo", "Empieza por el <a href=\"../santo-de-hoy.html\" style=\"color:var(--gold)\">santo de hoy</a> o busca por meses.") + sec(cal), "saints", [crumbs_ld([("Inicio", "index.html"), ("Santos", "santos/index.html")])])
for x in SAINTS:
    path = f'santos/{x["slug"]}.html'; cr = [("Inicio", "index.html"), ("Santos", "santos/index.html"), (x["name"], path)]; pr = PBY.get(x["prayer"])
    faq = [(f'¿Cuándo se celebra {x["name"]}?', f'Su fiesta o memoria es el {x["date"]}.'), (f'¿De qué es patrón {x["name"]}?', f'Se le invoca como patrón de {x["patron"]}.')]
    m = phero(r, cr, f'{x["date"]} · {E(x["short"])}', E(x["name"]), E(x["bio"][0])) + f'''<section class="sec"><div class="wrap art"><div style="min-width:0">
  <article class="pray reveal"><span class="eyebrow">Oración</span><p class="pray-text" id="prayText" style="margin-top:12px">{E(x["oracion"])}</p><div class="pray-acts"><button class="btn btn-accent sm" id="btnSpeak">Escuchar</button><button class="btn btn-ghost sm" id="btnCopy">Copiar oración</button></div></article>
  <div class="prose"><h2>Su vida</h2>{"".join(f"<p>{E(b)}</p>" for b in x["bio"])}<h2>Patrón de</h2><p>{E(x["patron"][0].upper() + x["patron"][1:])}.</p><h2>Preguntas frecuentes</h2>{faq_html(faq)}</div></div>
  <aside class="side">{f'<div class="box"><h3>Oración relacionada</h3><ul class="links"><li><a href="../oraciones/{pr["slug"]}.html">{E(pr["t"])}<small>{pr["min"]} min</small></a></li></ul></div>' if pr else ""}
   <div class="box candle-cta"><h3>Enciende una vela</h3><p>Pide su intercesión y deja tu intención en el muro.</p><a class="btn btn-flame sm" href="../muro-de-intenciones.html">Encender una vela</a></div>
   <div class="box"><h3>Otros santos</h3><ul class="links">{"".join([f'<li><a href="{o["slug"]}.html">{E(o["name"])}<small>{o["date"]}</small></a></li>' for o in SAINTS if o is not x and o["md"] > x["md"]][:6])}</ul></div></aside></div></section>'''
    page(path, f'{x["name"]}: vida y oración ({x["date"]}) | Rezo Diario', f'{x["name"]}, {x["short"][0].lower() + x["short"][1:]}. Se celebra el {x["date"]}. Su vida en breve y una oración para pedir su intercesión.'[:160], m, "saints",
     [crumbs_ld(cr), faq_ld(faq), {"@context": "https://schema.org", "@type": "Article", "headline": f'{x["name"]}: vida y oración', "inLanguage": "es", "author": ORG, "publisher": ORG, "datePublished": "2026-10-17", "dateModified": TODAY, "mainEntityOfPage": canon(path), "about": {"@type": "Person", "name": x["name"]}}], og_type="article")

# ================= ROSARIO =================
r = ""
ros_faq = [("¿Qué misterios se rezan hoy?", f'Hoy, {TW["wd"].lower()}, se rezan los misterios {setname(TW)}. Lunes y sábado: gozosos; martes y viernes: dolorosos; miércoles y domingo: gloriosos; jueves: luminosos.'),
 ("¿Cuánto se tarda en rezar el Rosario?", "Unos 20 minutos rezado con calma. Un solo misterio (un denario) se reza en unos 4 minutos."),
 ("¿Cómo se reza el Rosario paso a paso?", "Se empieza con la señal de la cruz y el Credo, un Padre Nuestro, tres Avemarías y un Gloria. Después, en cada uno de los cinco misterios, se anuncia el misterio y se reza un Padre Nuestro, diez Avemarías y un Gloria. Se termina con la Salve."),
 ("¿Quién añadió los misterios luminosos?", "San Juan Pablo II, en la carta Rosarium Virginis Mariae, en el año 2002.")]
rows = "".join(f'<tr><th scope="row">{S["name"]}</th><td>{S["days"]}</td><td>{"<br>".join(E(m[0]) for m in S["list"])}</td></tr>' for S in SETS.values())
ros = f'''<section class="phero"><div class="wrap">{crumbs_html(r, [("Inicio", "index.html"), ("Santo Rosario", "rosario.html")])}<div class="eyebrow" style="margin-top:22px">Santo Rosario guiado</div><h1>Misterios del Rosario de hoy: {setname(TW)}</h1><p class="lead">Reza el Rosario cuenta a cuenta. Cada misterio con su cita del Evangelio y su fruto. Pulsa una cuenta, desliza la tarjeta o usa las flechas del teclado.</p></div></section>
<section class="sec band" id="rosario"><div class="wrap"><div class="ros">
  <svg class="ros-svg" id="beads" viewBox="0 0 320 470" role="img" aria-label="Rosario con la cuenta actual resaltada"></svg>
  <div style="min-width:0"><div class="sets" id="sets"></div>
    <div class="step" id="step" tabindex="0" aria-live="polite"><span class="eyebrow" id="stK">Inicio</span><h2 class="step-t" id="stT">Señal de la cruz y Credo</h2><div class="step-meta" id="stM"></div><p class="step-x" id="stX">{E(O["SENAL"])}</p><div class="tens" id="tens" aria-hidden="true"></div></div>
    <div class="ros-nav"><button class="btn btn-ghost sm" id="rPrev">Anterior</button><div class="bar" aria-hidden="true"><i id="rBar"></i></div><button class="btn btn-accent sm" id="rNext">Siguiente</button></div>
    <div class="ros-nav" style="margin-top:10px"><button class="tog" id="rVoice" aria-pressed="false" style="color:var(--ink);border-color:var(--line)">Rezar en voz alta</button><button class="tog" id="rReset" style="color:var(--ink);border-color:var(--line)">Empezar de nuevo</button><span class="hint" id="rCount"></span></div>
  </div></div></div></section>
{sec(head2("Guía", "Cómo rezar el Rosario paso a paso") + f"""<div class="art"><div class="prose">
 <p>El Rosario es una oración sencilla que recorre la vida de Jesús de la mano de María. Se reza con un rosario de 59 cuentas, aunque basta con los dedos.</p>
 <ol class="qs"><li>Haz la señal de la cruz y reza el Credo con el crucifijo.</li><li>En la primera cuenta grande, reza un Padre Nuestro.</li><li>En las tres cuentas pequeñas, tres Avemarías: por la fe, la esperanza y la caridad. Después, un Gloria.</li><li>Anuncia el primer misterio y reza un Padre Nuestro en la cuenta grande.</li><li>Reza diez Avemarías mientras contemplas el misterio, y termina con el Gloria y el «Oh Jesús mío».</li><li>Repite con los cinco misterios y termina con la Salve.</li></ol>
 <h2>Qué misterios se rezan cada día</h2><div class="tablewrap"><table class="mt"><thead><tr><th>Misterios</th><th>Días</th><th>Los cinco misterios</th></tr></thead><tbody>{rows}</tbody></table></div>
 <h2>Preguntas frecuentes</h2>{faq_html(ros_faq)}</div>
 <aside class="side"><div class="box"><h3>Oraciones a la Virgen</h3><ul class="links"><li><a href="oraciones/acordaos.html">Acordaos<small>1 min</small></a></li><li><a href="oraciones/bajo-tu-amparo.html">Bajo tu amparo<small>1 min</small></a></li><li><a href="oraciones/el-angelus.html">El Ángelus<small>3 min</small></a></li></ul></div>
 <div class="box candle-cta"><h3>Ofrece tu Rosario</h3><p>Enciende una vela por la intención por la que rezas hoy.</p><a class="btn btn-flame sm" href="muro-de-intenciones.html">Encender una vela</a></div></aside></div>""")}'''
page("rosario.html", f'Misterios del Rosario de hoy ({setname(TW)}) y cómo rezarlo | Rezo Diario', f'Hoy se rezan los misterios {setname(TW)}. Reza el Santo Rosario guiado cuenta a cuenta, con la cita bíblica y el fruto de cada misterio.', ros, "rosary",
 [crumbs_ld([("Inicio", "index.html"), ("Santo Rosario", "rosario.html")]), faq_ld(ros_faq), {"@context": "https://schema.org", "@type": "HowTo", "name": "Cómo rezar el Santo Rosario", "inLanguage": "es", "totalTime": "PT20M", "step": [{"@type": "HowToStep", "text": t} for t in ["Señal de la cruz y Credo", "Padre Nuestro", "Tres Avemarías y Gloria", "Anunciar el misterio y rezar el Padre Nuestro", "Diez Avemarías, Gloria y Oh Jesús mío", "Repetir con los cinco misterios y terminar con la Salve"]]}])

# ================= VÍA CRUCIS =================
VIA = [(e["t"], e["x"]) for e in VIAJ["estaciones"]]
via_faq = [("¿Cuándo se reza el Vía Crucis?", "Sobre todo los viernes de Cuaresma y el Viernes Santo, aunque se puede rezar cualquier día, especialmente los viernes."), ("¿Cuántas estaciones tiene el Vía Crucis?", "Catorce estaciones, desde la condena de Jesús hasta su sepultura. Muchas parroquias añaden una decimoquinta: la Resurrección.")]
vc = phero(r, [("Inicio", "index.html"), ("Vía Crucis", "via-crucis.html")], "14 estaciones", "Vía Crucis guiado", "Acompaña a Jesús en el camino de la cruz. Desliza la tarjeta o toca una estación para avanzar.") + f'''
<section class="sec"><div class="wrap" style="max-width:900px">
  <div class="vc-path" id="vcPath" aria-label="Estaciones"></div>
  <article class="vc-card" id="vc" tabindex="0" aria-live="polite"><div class="vc-num" id="vcNum">I</div><h2 id="vcT">{E(VIA[0][0])}</h2><p class="vc-ant">{E(VIAJ["antifona"])}</p><p class="pray-text" id="vcX" style="margin-top:16px">{E(VIA[0][1])}</p><p class="vc-ant">Padre Nuestro, Ave María y Gloria.</p>
   <div class="ros-nav"><button class="btn btn-ghost sm" id="vcPrev">Anterior</button><button class="btn btn-ghost sm" id="vcSpeak">Escuchar</button><button class="btn btn-accent sm" id="vcNext" style="margin-left:auto">Siguiente estación</button></div></article>
  <div class="prose" style="margin-top:40px"><h2>Las catorce estaciones</h2><ol class="qs">{"".join(f"<li>{E(v[0])}</li>" for v in VIA)}</ol><h2>Preguntas frecuentes</h2>{faq_html(via_faq)}</div>
</div></section>'''
page("via-crucis.html", "Vía Crucis: las 14 estaciones para rezar | Rezo Diario", "Reza el Vía Crucis guiado con las 14 estaciones, una breve meditación en cada una y audio. Para los viernes de Cuaresma, Viernes Santo o cualquier día.", vc, "", [crumbs_ld([("Inicio", "index.html"), ("Vía Crucis", "via-crucis.html")]), faq_ld(via_faq)])

# ================= NOVENAS =================
r = "../"
GR = ["linear-gradient(150deg,#6E64A8,#2A2350)", "linear-gradient(150deg,#4A4F5C,#16181D)", "linear-gradient(150deg,#3C6FA8,#16304F)", "linear-gradient(150deg,#2F8C84,#123F3B)", "linear-gradient(150deg,#A8812D,#4A3510)"]
page("novenas/index.html", "Novenas católicas para rezar día a día | Rezo Diario", "Novenas para rezar durante nueve días con recordatorio de qué día toca: San Judas Tadeo, difuntos, Inmaculada, Virgen de Guadalupe y Navidad.",
 phero(r, [("Inicio", "index.html"), ("Novenas", "novenas/index.html")], "Nueve días de oración", "Novenas para rezar día a día", "Una novena es una oración que se reza durante nueve días seguidos para pedir una gracia o preparar una fiesta. Te decimos qué día toca y guardamos tu progreso.") +
 sec('<div class="duo">' + "".join(f'<a class="feature reveal" href="{n["slug"]}.html" style="background:{GR[i % len(GR)]}"><small>Del {fdate(n["start"])} al {fdate(n["end"])}</small><b>{E(n["t"])}</b><p>{E(n["intro"])}</p></a>' for i, n in enumerate(NOVENAS)) + '</div>'), "novenas", [crumbs_ld([("Inicio", "index.html"), ("Novenas", "novenas/index.html")])])
for n in NOVENAS:
    path = f'novenas/{n["slug"]}.html'; cr = [("Inicio", "index.html"), ("Novenas", "novenas/index.html"), (n["t"], path)]
    faq = [(f'¿Cuándo empieza la {n["t"][0].lower() + n["t"][1:]}?', n["intro"]), ("¿Qué pasa si me salto un día?", "No pasa nada. Retómala donde la dejaste. Lo importante es la constancia y la confianza, no la perfección.")]
    m = phero(r, cr, f'Fiesta: {n["feast"]}', E(n["t"]), E(n["intro"])) + f'''<section class="sec"><div class="wrap art"><div style="min-width:0" id="novena" data-slug="{n["slug"]}">
  <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap"><svg class="ring" id="novRing" viewBox="0 0 84 84" aria-hidden="true"></svg><div><b style="font-size:17px" id="novStatus"></b><p class="hint" style="margin:4px 0 0">Tu progreso se guarda en este dispositivo y en tu cuenta.</p></div></div>
  <div class="nov-days" id="novDays"></div>
  <article class="pray"><span class="eyebrow">Oración inicial</span><p class="pray-text" style="margin:10px 0 22px;font-size:18px">{E(n["open"])}</p>
   <span class="eyebrow" id="novK">Día 1</span><h2 id="novT" style="margin:6px 0 10px">{E(n["days"][0]["t"])}</h2><p class="pray-text" id="novX">{E(n["days"][0]["x"])}</p>
   <span class="eyebrow" style="display:block;margin-top:22px">Oración final</span><p class="pray-text" style="margin-top:10px;font-size:18px">{E(n["close"])}</p>
   <div class="pray-acts"><button class="btn btn-accent sm" id="novDone" aria-pressed="false">Marcar este día como rezado</button><button class="btn btn-ghost sm" id="novSpeak">Escuchar</button></div></article>
  <div class="prose"><h2>Los nueve días</h2><ol class="qs">{"".join(f"<li><strong>{E(d['t'])}.</strong> {E(d['x'])}</li>" for d in n["days"])}</ol><h2>Preguntas frecuentes</h2>{faq_html(faq)}</div></div>
  <aside class="side"><div class="box candle-cta"><h3>Enciende una vela</h3><p>Acompaña tu novena con una vela en el muro de intenciones.</p><a class="btn btn-flame sm" href="../muro-de-intenciones.html{"#difuntos" if "difuntos" in n["slug"] else ""}">Encender una vela</a></div>
   <div class="box"><h3>Otras novenas</h3><ul class="links">{"".join(f'<li><a href="{o["slug"]}.html">{E(o["t"])}<small>{fdate(o["start"])}</small></a></li>' for o in NOVENAS if o is not n)}</ul></div></aside></div></section>'''
    page(path, f'{n["t"]}: los 9 días para rezar | Rezo Diario', f'{n["t"]} completa: oración inicial, meditación de cada día y oración final. {n["intro"]}'[:160], m, "novenas", [crumbs_ld(cr), faq_ld(faq)])

# ================= ADVIENTO, RETO Y NAVIDAD =================
r = ""
adv_days = [w for w in DAYS if "2026-11-29" <= w["date"] <= "2026-12-24"]
adv_faq = [("¿Cuándo empieza el Adviento en 2026?", "El domingo 29 de noviembre de 2026. Dura cuatro semanas, hasta la Nochebuena del 24 de diciembre."),
 ("¿Qué significan las velas de la corona de Adviento?", "Cada domingo se enciende una vela más. Tradicionalmente representan la esperanza, la paz, la alegría (la vela rosa del tercer domingo) y el amor."),
 ("¿Qué color se usa en Adviento?", "El morado, color de la espera y la conversión. El tercer domingo, llamado Gaudete, puede usarse el rosa."),
 ("¿Cuándo es la Inmaculada?", "El 8 de diciembre. En España es fiesta de precepto y patrona del país.")]
sundays = [w for w in adv_days if w["wd"] == "Domingo"]
adv = phero(r, [("Inicio", "index.html"), ("Adviento 2026", "adviento.html")], "Del 29 de noviembre al 24 de diciembre", "Adviento 2026: prepara tu corazón para la Navidad", "Cuatro semanas para esperar a Jesús que viene: la corona y sus velas, el Evangelio de cada día, un reto diario y las novenas de la Inmaculada, Guadalupe y Navidad.") + \
 sec(head2("Los cuatro domingos", "La corona de Adviento, semana a semana") + '<div class="pagegrid">' + "".join(f'<a class="saintcard reveal" href="evangelio/{w["date"]}.html"><small>{w["n"]} de {w["mes"]} · vela {i + 1}</small><b>{E(w["lit"])}</b><span>{w["ref"]}: {E(w["title"])}</span></a>' for i, w in enumerate(sundays)) + '</div>') + \
 sec(head2("Para rezar", "Oraciones y devociones de Adviento") + '<div class="duo">' + f'<a class="feature reveal" href="retos/adviento.html" style="background:linear-gradient(150deg,#5B3D7A,#24163A)"><small>26 días</small><b>Reto de Adviento</b><p>Un gesto pequeño cada día para preparar la Navidad.</p></a><a class="feature reveal" href="novenas/novena-a-la-inmaculada.html" style="background:linear-gradient(150deg,#3C6FA8,#16304F)"><small>29 nov – 7 dic</small><b>Novena a la Inmaculada</b><p>Nueve días con María antes de su fiesta.</p></a><a class="feature reveal" href="novenas/novena-de-navidad.html" style="background:linear-gradient(150deg,#A8812D,#4A3510)"><small>16 – 24 dic</small><b>Novena de Navidad</b><p>Nueve días en familia antes de Nochebuena.</p></a></div>' +
  '<ul class="links" style="margin-top:22px">' + "".join(f'<li><a href="oraciones/{s}.html">{E(PBY[s]["t"])}<small>{PBY[s]["min"]} min</small></a></li>' for s in ["bendicion-corona-de-adviento", "oracion-de-las-velas-de-adviento", "oracion-de-adviento", "oracion-a-la-inmaculada", "oracion-a-la-virgen-de-guadalupe", "bendicion-del-belen"]) + '</ul>', "sec band") + \
 sec(head2("Día a día", "El Evangelio de cada día de Adviento") + '<ul class="links" style="columns:2 300px;column-gap:40px;display:block">' + "".join(f'<li style="break-inside:avoid"><a href="evangelio/{w["date"]}.html">{w["wd"]} {w["n"]} de {w["mes"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in adv_days) + '</ul>') + sec(head2("Preguntas frecuentes", "Sobre el Adviento") + faq_html(adv_faq), "sec band")
page("adviento.html", "Adviento 2026: fechas, corona, oraciones y reto diario | Rezo Diario", "El Adviento 2026 empieza el 29 de noviembre. Corona de Adviento y sus velas, Evangelio de cada día, reto diario, novena a la Inmaculada y novena de Navidad.", adv, "", [crumbs_ld([("Inicio", "index.html"), ("Adviento 2026", "adviento.html")]), faq_ld(adv_faq)])

nav_faq = [("¿Cuándo termina el tiempo de Navidad?", "Con la fiesta del Bautismo del Señor, el domingo siguiente a la Epifanía (6 de enero)."), ("¿Qué se celebra el 28 de diciembre?", "Los Santos Inocentes, los niños de Belén que Herodes mandó matar para acabar con Jesús."), ("¿Qué se celebra el 1 de enero?", "La solemnidad de Santa María, Madre de Dios, y la Jornada Mundial de la Paz.")]
xmas = [w for w in DAYS if w["date"] >= "2026-12-24"]
nav = phero(r, [("Inicio", "index.html"), ("Navidad 2026", "navidad.html")], "Nochebuena, Navidad y fin de año", "Navidad 2026: oraciones para rezar en familia", "Oraciones para bendecir el belén y la cena de Nochebuena, el Evangelio de cada día de la octava y una oración para despedir el año.") + \
 sec('<ul class="links">' + "".join(f'<li><a href="oraciones/{s}.html">{E(PBY[s]["t"])}<small>{PBY[s]["min"]} min</small></a></li>' for s in ["bendicion-del-belen", "oracion-de-nochebuena", "oracion-de-navidad", "oracion-de-fin-de-ano", "oracion-de-ano-nuevo"]) + '</ul>') + \
 sec(head2("Día a día", "El Evangelio de Navidad") + '<div class="pagegrid">' + "".join(f'<a class="saintcard reveal" href="evangelio/{w["date"]}.html"><small>{w["n"]} de {w["mes"]}</small><b>{E(w["title"])}</b><span>{E(w["lit"])}</span></a>' for w in xmas) + '</div>', "sec band") + sec(head2("Preguntas frecuentes", "Sobre la Navidad") + faq_html(nav_faq))
page("navidad.html", "Navidad 2026: oraciones de Nochebuena, Navidad y fin de año | Rezo Diario", "Oraciones para la Navidad 2026: bendición del belén, oración para la cena de Nochebuena, oración de Navidad, de fin de año y de Año Nuevo, y el Evangelio de cada día.", nav, "", [crumbs_ld([("Inicio", "index.html"), ("Navidad 2026", "navidad.html")]), faq_ld(nav_faq)])

r = "../"
start = datetime.date.fromisoformat(RETO["inicio"])
reto_items = "".join(f'<li class="reto-d" data-k="{i}" data-date="{(start + datetime.timedelta(days=i)).isoformat()}"><label><input type="checkbox" data-k="{i}"><span><small>{fdate((start + datetime.timedelta(days=i)).isoformat())}</small>{E(g)}</span></label><a href="../evangelio/{(start + datetime.timedelta(days=i)).isoformat()}.html">Evangelio</a></li>' for i, g in enumerate(RETO["gestos"]))
reto = phero(r, [("Inicio", "index.html"), ("Adviento", "adviento.html"), ("Reto de Adviento", "retos/adviento.html")], "26 días · 29 nov – 24 dic", "Reto de Adviento: un gesto cada día", "Pequeños gestos para preparar la Navidad. Marca cada día cuando lo hagas: tu progreso se guarda.",
 '<div style="display:flex;align-items:center;gap:16px;margin-top:22px"><svg class="ring" id="retoRing" viewBox="0 0 84 84" aria-hidden="true"></svg><b id="retoStatus" style="font-size:17px"></b></div>') + sec(f'<ol class="reto" id="reto" data-key="rd-reto-adviento">{reto_items}</ol>')
page("retos/adviento.html", "Reto de Adviento 2026: un gesto cada día | Rezo Diario", "Reto de Adviento 2026: 26 gestos sencillos, uno para cada día del 29 de noviembre al 24 de diciembre, con el Evangelio del día. Guarda tu progreso.", reto, "", [crumbs_ld([("Inicio", "index.html"), ("Adviento", "adviento.html"), ("Reto de Adviento", "retos/adviento.html")])])

# ================= MURO DE VELAS =================
r = ""
muro_faq = [("¿Cuánto tiempo arde una vela?", "Siete días. Cada día la vela se consume un poco, hasta apagarse."), ("¿Quién puede ver mi intención?", "Si es pública, cualquiera que visite el muro. Si marcas «privada», solo se ve la vela encendida, nunca el texto."), ("¿Puedo encender una vela por un difunto?", "Sí. Elige «Difuntos» y escribe su nombre de pila. Muchas personas rezarán por su descanso."), ("¿Qué pasa si veo una intención ofensiva?", "Pulsa «Avisar». Cuando una vela recibe varios avisos se oculta automáticamente y se revisa.")]
page("muro-de-intenciones.html", "Muro de intenciones: enciende una vela virtual | Rezo Diario", "Enciende una vela virtual por tu intención: por un enfermo, por un difunto, por tu familia o por un examen. Arde siete días y otras personas rezan por ti.",
 f'<div class="chapel" style="padding-top:20px"><div class="wrap">{crumbs_html(r, [("Inicio", "index.html"), ("Muro de intenciones", "muro-de-intenciones.html")])}</div></div>' + chapel(r, True) + sec(head2("Preguntas frecuentes", "Sobre el muro de velas") + faq_html(muro_faq)), "candles", [crumbs_ld([("Inicio", "index.html"), ("Muro de intenciones", "muro-de-intenciones.html")]), faq_ld(muro_faq)])

# ================= WIDGET =================
wcode = f'<div id="rezodiario-evangelio"><a href="{SITE}evangelio-de-hoy.html">Evangelio de hoy en Rezo Diario</a></div>\n<script src="{SITE}widget/evangelio.js" async></script>'
wid = phero(r, [("Inicio", "index.html"), ("Widget para parroquias", "widget.html")], "Gratis para parroquias, colegios y blogs", "Pon el Evangelio del día en tu web", "Un recuadro que se actualiza solo cada día con el Evangelio, una frase y un enlace al audio. Copia el código y pégalo en tu web: no necesitas saber programar.") + \
 sec(f'''<div class="art"><div style="min-width:0"><h2>Así se verá</h2><div id="wPreview" style="margin:16px 0 28px"></div>
 <h2>Código para copiar</h2><p style="color:var(--muted)">Pégalo en tu página donde quieras que aparezca (en WordPress, en un bloque «HTML personalizado»).</p>
 <pre class="tablewrap" style="padding:16px;white-space:pre-wrap;word-break:break-all;font-size:13px" id="wCode">{E(wcode)}</pre>
 <div class="hero-cta"><button class="btn btn-accent sm" id="wCopy">Copiar código</button><button class="btn btn-ghost sm" id="wDark" aria-pressed="false">Versión oscura</button></div></div>
 <aside class="side"><div class="box"><h3>Qué incluye</h3><ul class="links"><li><a>Evangelio y frase del día</a></li><li><a>Color litúrgico</a></li><li><a>Enlace al audio y la reflexión</a></li><li><a>Se adapta al ancho de tu web</a></li></ul></div></aside></div>''')
page("widget.html", "Widget del Evangelio del día para tu web o parroquia | Rezo Diario", "Pon gratis el Evangelio del día en la web de tu parroquia, colegio o blog. Se actualiza solo cada día. Copia y pega el código.", wid, "", [crumbs_ld([("Inicio", "index.html"), ("Widget para parroquias", "widget.html")])])

# ================= DONAR, SOBRE, LEGAL =================
don_faq = [("¿Mi donativo desgrava?", "Las donaciones a entidades acogidas a la Ley 49/2002 desgravan en la renta. Confirma la situación fiscal de vuestra entidad antes de anunciarlo."), ("¿Puedo cancelar la donación mensual?", "Sí, en cualquier momento y sin preguntas.")]
page("donar.html", "Donar a Rezo Diario | Rezo Diario", "Ayuda a mantener Rezo Diario gratis y sin anuncios: con tu donativo publicamos audios nuevos cada día y traducimos las oraciones a otros idiomas.",
 phero(r, [("Inicio", "index.html"), ("Donar", "donar.html")], "Donaciones", "Gracias por sostener Rezo Diario", "Rezo Diario es gratis para todos. Tu aportación paga los audios, la música y los servidores.") + donate_section("h2") + sec(head2("Preguntas", "Sobre las donaciones") + faq_html(don_faq)), "", [crumbs_ld([("Inicio", "index.html"), ("Donar", "donar.html")]), faq_ld(don_faq)])
page("sobre-nosotros.html", "Quiénes somos | Rezo Diario", "Rezo Diario es un proyecto para ayudar a rezar cada día con el Evangelio, el Rosario y oraciones para todos los momentos de la vida.",
 phero(r, [("Inicio", "index.html"), ("Quiénes somos", "sobre-nosotros.html")], "El proyecto", "Quiénes somos", "Rezo Diario nace para que rezar cada día sea fácil, bonito y esté al alcance de cualquiera, en cualquier lugar.") +
 sec(f'''<div class="prose"><h2>Qué hacemos</h2><p>Cada día preparamos un rezo guiado con el Evangelio de la liturgia, una reflexión breve y unas preguntas para llevarlo a la vida. Además, reunimos oraciones para cada necesidad, el Santo Rosario, el Vía Crucis, novenas y un muro de velas donde rezar unos por otros.</p>
 <h2>Cómo elaboramos los contenidos</h2><p>Seguimos el calendario litúrgico de la Iglesia católica. Las reflexiones y oraciones nuevas son originales; las oraciones tradicionales se reproducen en su forma habitual en español. Para las lecturas completas enlazamos a fuentes oficiales. Los audios se narran con una voz sintética y se revisan antes de publicarse.</p>
 <h2>Equipo y revisión</h2><p class="hint" style="font-size:15px">Pendiente de completar: nombres del equipo, sacerdote o institución que revisa los contenidos y datos legales de la entidad.</p>
 <h2>Contacto</h2><p>{E(AJ.get("emailContacto", ""))}</p></div>'''), "", [crumbs_ld([("Inicio", "index.html"), ("Quiénes somos", "sobre-nosotros.html")])])
LEGAL = {"aviso-legal": ("Aviso legal", "Titular del sitio: [nombre de la persona o entidad]. NIF: [número]. Domicilio: [dirección]. Correo: " + AJ.get("emailContacto", "") + ".\n\nEl contenido original de Rezo Diario (reflexiones, oraciones nuevas, diseño) es propiedad de su titular. Las oraciones tradicionales son de dominio público. Las citas bíblicas breves se usan con fines de comentario.\n\nEste texto es una plantilla: revísalo con un profesional antes de publicar."),
         "privacidad": ("Política de privacidad", "Responsable: [nombre]. Datos que tratamos: el correo electrónico si te suscribes al boletín o creas una cuenta; el texto y el nombre de pila que escribas al encender una vela; y un identificador anónimo de tu navegador para evitar abusos en el muro.\n\nFinalidad: enviarte el rezo diario, guardar tu progreso y mostrar tu vela durante siete días. Base legal: tu consentimiento. Encargados: Supabase (base de datos), Netlify (alojamiento) y el proveedor de correo que elijáis.\n\nPuedes pedir acceso, rectificación o borrado escribiendo a " + AJ.get("emailContacto", "") + ".\n\nEste texto es una plantilla: revísalo con un profesional antes de publicar."),
         "cookies": ("Política de cookies", "Rezo Diario no usa cookies publicitarias. Guardamos en tu navegador (almacenamiento local) tus preferencias: tema claro u oscuro, idioma, favoritos, racha y progreso de novenas. Si añadís herramientas de analítica, actualizad este texto y mostrad un aviso de consentimiento.\n\nEste texto es una plantilla: revísalo con un profesional antes de publicar.")}
r = "../"
for k, (t, x) in LEGAL.items():
    page(f"legal/{k}.html", f"{t} | Rezo Diario", f"{t} de Rezo Diario.", phero(r, [("Inicio", "index.html"), (t, f"legal/{k}.html")], "Información legal", t, "") + sec(f'<div class="prose"><p style="white-space:pre-line">{E(x)}</p></div>'), "", robots="noindex, follow")
page("404.html", "Página no encontrada | Rezo Diario", "La página que buscas no existe.", phero("", [("Inicio", "index.html")], "Error 404", "No hemos encontrado esta página", "Puede que haya cambiado de dirección. Prueba con el rezo de hoy o busca una oración.", '<div class="hero-cta" style="margin-top:18px"><a class="btn btn-gold" href="/">Ir al rezo de hoy</a><a class="btn btn-ghost" href="/oraciones/index.html">Buscar una oración</a></div>'), "", robots="noindex")

# ================= SALIDA =================
if os.path.exists(OUT): shutil.rmtree(OUT)
shutil.copytree(os.path.join(ROOT, "static"), OUT)
os.makedirs(OUT + "/assets", exist_ok=True)
css = open(ROOT + "/assets/base.css", encoding="utf-8").read() + open(ROOT + "/assets/extra.css", encoding="utf-8").read()
open(OUT + "/assets/site.css", "w", encoding="utf-8").write(css)
shutil.copy(ROOT + "/assets/site.js", OUT + "/assets/site.js")
data = {"week": [{k: w[k] for k in ("date", "wd", "n", "mes", "color", "lit", "ref", "refL", "title", "set", "ex", "sum", "refl", "qs", "fin", "audio", "duracion")} for w in DAYS], "LITC": LITC, "SETS": SETS, **O, "via": VIA, "VIA_ANT": VIAJ["antifona"],
        "prayers": [{"slug": p["slug"], "t": p["t"], "cat": p["cat"], "min": p["min"]} for p in PRAYERS], "CATS": {k: {"name": c["name"], "color": c["color"]} for k, c in CATS.items()},
        "novenas": [{"slug": n["slug"], "t": n["t"], "start": n["start"], "end": n["end"], "open": n["open"], "close": n["close"], "days": [[d["t"], d["x"]] for d in n["days"]]} for n in NOVENAS]}
open(OUT + "/assets/data.js", "w", encoding="utf-8").write("window.RD=" + json.dumps(data, ensure_ascii=False) + ";")
for path, head, body, battrs in pages:
    full = f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body{battrs}>\n{body}\n</body>\n</html>\n'
    os.makedirs(os.path.dirname(OUT + "/" + path) or OUT, exist_ok=True); open(OUT + "/" + path, "w", encoding="utf-8").write(full)
    if path == "index.html": open(ROOT + "/.preview-index.html", "w", encoding="utf-8").write(head.replace(E("Rezo Diario · Oración diaria, Evangelio de hoy, Rosario y velas"), "Rezo Diario", 1) + "\n" + body)
# API del widget: un JSON por día
os.makedirs(OUT + "/api/evangelio", exist_ok=True)
for w in DAYS:
    json.dump({"fecha": w["date"], "dia": f'{w["wd"]} {w["n"]} de {w["mes"]}', "liturgia": w["lit"], "color": w["color"], "cita": w["refL"], "titulo": w["title"], "frase": w["ex"], "url": f'{SITE}evangelio/{w["date"]}.html'}, open(f'{OUT}/api/evangelio/{w["date"]}.json', "w", encoding="utf-8"), ensure_ascii=False)
# Pódcast
items = "".join(f'''<item><title>{E(w["title"])} · {w["n"]} de {w["mes"]}</title><description>{E(w["refL"] + ". " + w["sum"])}</description><link>{SITE}evangelio/{w["date"]}.html</link><guid isPermaLink="false">rezodiario-{w["date"]}</guid><pubDate>{datetime.datetime.fromisoformat(w["date"] + "T06:00:00+01:00").strftime("%a, %d %b %Y %H:%M:%S +0100")}</pubDate><enclosure url="{SITE}{w["audio"].lstrip("/")}" type="audio/mpeg" length="0"/>{f'<itunes:duration>{w["duracion"]}</itunes:duration>' if w.get("duracion") else ""}</item>\n''' for w in reversed(DAYS) if w.get("audio") and w["date"] <= TODAY)
pc = AJ["podcast"]
open(OUT + "/podcast.xml", "w", encoding="utf-8").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"><channel>
<title>{E(pc["titulo"])}</title><link>{SITE}</link><language>es</language><description>{E(pc["descripcion"])}</description>
<itunes:author>{E(pc["autor"])}</itunes:author><itunes:owner><itunes:name>{E(pc["autor"])}</itunes:name><itunes:email>{E(pc["email"])}</itunes:email></itunes:owner>
<itunes:image href="{E(pc["imagen"])}"/><itunes:category text="Religion &amp; Spirituality"><itunes:category text="Christianity"/></itunes:category><itunes:explicit>false</itunes:explicit>
{items}</channel></rss>''')
icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#14302A"/><circle cx="32" cy="32" r="22" fill="none" stroke="#D6B266" stroke-width="2.4"/><path d="M32 16v32M23 27h18" stroke="#D6B266" stroke-width="4.4" stroke-linecap="round"/></svg>'
open(OUT + "/icon.svg", "w").write(icon)
open(OUT + "/manifest.webmanifest", "w").write(json.dumps({"name": "Rezo Diario", "short_name": "Rezo Diario", "lang": "es", "start_url": "/", "display": "standalone", "background_color": "#14302A", "theme_color": "#14302A", "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]}, ensure_ascii=False))
open(OUT + "/sw.js", "w").write("const C='rd-v2';const PRE=['/','/assets/site.css','/assets/site.js','/assets/data.js','/rosario.html','/oraciones/index.html'];\nself.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(PRE))));\nself.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))));\nself.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request)))});\n")
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE}sitemap.xml\n")
daily = ("index.html", "evangelio-de-hoy.html", "evangelio-de-manana.html", "santo-de-hoy.html", "rosario.html", "muro-de-intenciones.html")
idx = [p for p, h, _, _ in pages if "noindex" not in h]
open(OUT + "/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f'  <url><loc>{canon(p)}</loc><lastmod>{TODAY}</lastmod><changefreq>{"daily" if p in daily else "monthly"}</changefreq><priority>{"1.0" if p == "index.html" else "0.9" if p in daily else "0.7"}</priority></url>\n' for p in idx) + '</urlset>\n')

# ================= GUIONES ELEVENLABS =================
def guion(w):
    def br(s): return f' <break time="{s}s" /> '
    seg1 = "Busca un lugar tranquilo y ponte cómodo." + br(1.5) + "Respira despacio." + br(2) + "Inspira…" + br(2.5) + "y suelta el aire." + br(2.5) + "Estás en la presencia de Dios." + br(1.5) + "Él te mira con cariño."
    seg2 = f'Evangelio según san {w["refL"].split(" ")[0].replace("Lucas", "Lucas").replace("Mateo", "Mateo")}, capítulo {w["refL"].split(" ")[1].rstrip(",")}.' + br(1.5) + w["sum"] + br(2) + "Escucha estas palabras de Jesús:" + br(1.5) + w["ex"]
    seg2 = seg2.replace("san Juan", "san Juan").replace("según san Marcos", "según san Marcos")
    qs = (br(3)).join(w["qs"])
    seg3 = w["refl"] + br(2.5) + "Ahora, en silencio, piensa en estas preguntas." + br(1.5) + qs
    seg4 = w["fin"] + br(2) + O["GL"]
    blocks = [("1 · Entrar en silencio", seg1, "Deja 10 segundos solo de música."), ("2 · Evangelio", seg2, "Deja 15 segundos de silencio con música suave."),
              ("3 · Reflexión", seg3, "Deja 25 segundos de silencio después de cada pregunta (puedes partir el bloque en las pausas largas)."), ("4 · Oración final", seg4, "Termina con 8 segundos de música que se apaga.")]
    out = [f'GUION PARA ELEVENLABS · {w["wd"]} {w["n"]} de {w["mes"]} de {w["date"][:4]}', f'{w["title"]} ({w["refL"]})', "",
           "Ajustes recomendados: voz calmada en español de España, estabilidad alta (60-75 %), estilo bajo (0-15 %), velocidad 0,9.",
           "Pega cada bloque por separado en ElevenLabs. Las etiquetas <break> crean pausas cortas (máximo 3 segundos).", "Los silencios largos añádelos al montar el audio con la música.", ""]
    for t, b, note in blocks: out += ["=" * 60, f"BLOQUE {t}", "=" * 60, re.sub(r"\s+", " ", b).strip(), "", f"[MONTAJE] {note}", ""]
    out += ["Cuando tengas el audio final: súbelo al panel (Días → este día → Audio) y escribe la duración, por ejemplo 9:30."]
    return "\n".join(out)
if "--guiones" in sys.argv:
    os.makedirs(ROOT + "/guiones", exist_ok=True)
    for w in DAYS: open(f'{ROOT}/guiones/{w["date"]}.txt', "w", encoding="utf-8").write(guion(w))
print(f"{len(pages)} páginas · hoy={TODAY} · {len(DAYS)} días · {len(PRAYERS)} oraciones · {len(SAINTS)} santos · {len(NOVENAS)} novenas")
