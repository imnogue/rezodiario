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
VTOP = JD("versiculos"); VORDER = ["versiculos-para-la-ansiedad", "versiculos-para-cuando-estas-triste", "versiculos-para-dormir", "versiculos-para-el-miedo", "versiculos-para-momentos-dificiles", "versiculos-para-la-fe", "versiculos-sobre-el-amor", "versiculos-para-la-familia", "versiculos-sobre-el-dinero", "versiculos-para-empezar-el-dia", "versiculos-para-dar-gracias", "versiculos-sobre-la-proteccion", "versiculos-para-superar-una-ruptura", "versiculos-para-el-enfado"]
VTOP.sort(key=lambda t: VORDER.index(t["slug"]) if t["slug"] in VORDER else 99); VBY = {t["slug"]: t for t in VTOP}
WDN = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
SETDAY = ["gozosos", "dolorosos", "gloriosos", "luminosos", "dolorosos", "gozosos", "gloriosos"]
LITC = {"green": ["var(--lit-green)", "Verde · Tiempo Ordinario"], "white": ["var(--lit-white)", "Blanco · fiesta o memoria"], "red": ["var(--lit-red)", "Rojo · mártires y apóstoles"],
        "violet": ["var(--lit-violet)", "Morado · Adviento y difuntos"], "rose": ["var(--lit-rose)", "Rosa · domingo de la alegría"], "blue": ["var(--lit-blue)", "Azul · privilegio de España en la Inmaculada"]}
CANDLE_HASH = {"salud": "salud", "familia": "familia", "duelo": "difuntos", "estudios": "estudios", "trabajo": "trabajo", "diaria": "gracias", "paz": "otra", "devociones": "otra"}
for d in DAYS:
    dt = datetime.date.fromisoformat(d["date"]); d["wd"] = WDN[dt.weekday()]; d["n"] = dt.day; d["mes"] = MES[dt.month - 1]; d["set"] = SETDAY[dt.weekday()]
    if d.get("saint") and d["saint"] not in SBY: print("AVISO: santo no encontrado", d["date"], d["saint"]); d["saint"] = ""
    if not d.get("saint") and not re.search(r"Domingo|Solemnidad|Fiesta|Conmemoración|Navidad", d["lit"]):
        _s = next((x for x in SAINTS if x["md"] == d["date"][5:]), None)
        if _s: d["saint"] = _s["slug"]

now = datetime.datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
TODAY = min(max(now, DAYS[0]["date"]), DAYS[-1]["date"])
TW = DBY[TODAY]
ti = DAYS.index(TW)
WLO, WHI = max(0, ti - 7), min(len(DAYS), ti + 9)  # días que van en data.js; el resto, en assets/dias/<fecha>.js
WIN = {w["date"] for w in DAYS[WLO:WHI]}
TOMORROW = DAYS[min(ti + 1, len(DAYS) - 1)]
def nice(d): return f'{d["wd"].lower()} {d["n"]} de {d["mes"]} de {d["date"][:4]}'
def fdate(iso): dt = datetime.date.fromisoformat(iso); return f"{dt.day} de {MES[dt.month-1]}"
pages = []
import time as _t
VER = str(int(_t.time()))  # cambia en cada publicación: el navegador siempre carga los datos nuevos

ICON = {
 "search": '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m20 20-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
 "globe": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z"/></svg>',
 "moon": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
 "menu": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>',
 "user": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>',
 "logo": '<svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true"><path fill="#D9A441" d="M6.1 12.6A10 10 0 0 1 14.8 4.07V12.6Z"/><path fill="#E07A4F" d="M17.2 4.07A10 10 0 0 1 25.9 12.6H17.2Z"/><path fill="#2E8B67" d="M6 15H14.8V28H8a2 2 0 0 1-2-2Z"/><path fill="#3E72B0" d="M17.2 15H26V26a2 2 0 0 1-2 2H17.2Z"/></svg>',
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
NAV = [("index.html", "today", "Hoy"), ("oraciones/index.html", "prayers", "Oraciones"), ("rosario.html", "rosary", "Rosario"), ("evangelio-de-hoy.html", "gospel", "Evangelio"), ("versiculos.html", "verses", "Versículos"), ("santos/index.html", "saints", "Santos"), ("muro-de-intenciones.html", "candles", "Velas")]
# En Cloudflare Pages (variable CF_PAGES=1) las direcciones van sin «.html»: /oraciones/acordaos
CLEAN = os.environ.get("CF_PAGES") == "1" or "--limpias" in sys.argv
def cleanp(path):
    if not CLEAN: return path
    if path.endswith("index.html"): return path[:-10]
    return path[:-5] if path.endswith(".html") else path
def canon(path): return SITE + ("" if path == "index.html" else cleanp(path))
ORG = {"@type": "Organization", "name": "Rezo Diario", "url": SITE, "logo": SITE + "logo-512.png"}

def header(r, active):
    nav = "".join(f'<a href="{r}{h}"{" class=\"on\" aria-current=\"page\"" if k == active else ""} data-i18n="{k}">{t}</a>' for h, k, t in NAV)
    return f'''<header class="top" data-nosnippet>
  <div class="wrap top-in">
    <a class="brand" href="{r}index.html" aria-label="Rezo Diario, inicio">{ICON["logo"]}<span>rezo<b>diario</b></span></a>
    <nav class="nav" aria-label="Principal">{nav}</nav>
    <div class="top-actions">
      <div class="lang notranslate" translate="no"><button class="icon-btn lang-btn" id="btnLang" aria-haspopup="menu" aria-expanded="false" aria-label="Idioma">{ICON["globe"]}<span id="langCode">ES</span></button><div class="lang-menu" id="langMenu" role="menu" hidden></div></div>
      <button class="icon-btn" id="btnTheme" aria-label="Cambiar entre modo claro y oscuro">{ICON["moon"]}</button>
      <button class="icon-btn" id="btnUser" aria-label="Tu cuenta" hidden>{ICON["user"]}</button>
      <a href="{r}donar.html" class="btn btn-gold sm" data-i18n="donate">Donar</a>
      <button class="icon-btn menu-btn" data-drawer aria-label="Abrir menú">{ICON["menu"]}</button>
    </div>
  </div>
</header>'''

def drawer(r):
    groups = [("Rezar", [("index.html", "Rezo de hoy"), ("evangelio-de-hoy.html", "Evangelio de hoy"), ("evangelio-de-manana.html", "Evangelio de mañana"), ("santo-de-hoy.html", "Santo de hoy"), ("rosario.html", "Santo Rosario"), ("via-crucis.html", "Vía Crucis"), ("novenas/index.html", "Novenas"), ("muro-de-intenciones.html", "Muro de velas")]),
              ("Versículos", [("versiculos.html", "Versículo del día")] + [(t["slug"] + ".html", t["t"]) for t in VTOP]),
              ("Tiempos litúrgicos", [("adviento.html", "Adviento 2026"), ("retos/adviento.html", "Reto de Adviento"), ("navidad.html", "Navidad 2026"), ("camino-de-santiago.html", "Camino de Santiago 2027")]),
              ("Oraciones por tema", [(f"oraciones/tema-{k}.html", c["name"]) for k, c in CATS.items()]),
              ("Rezo Diario", [("santos/index.html", "Santoral"), ("evangelio/index.html", "Archivo del Evangelio"), ("widget.html", "Widget para parroquias"), ("perfil.html", "Mi perfil"), ("donar.html", "Donar"), ("sobre-nosotros.html", "Quiénes somos")])]
    out = "".join(f'<h4>{g}</h4>' + "".join(f'<a href="{r}{h}"><i></i>{t}</a>' for h, t in items) for g, items in groups)
    return f'<div class="drawer" id="drawer" data-nosnippet hidden role="dialog" aria-modal="true" aria-label="Menú"><div class="drawer-bg" data-close></div><nav class="drawer-p"><button class="icon-btn" data-close aria-label="Cerrar menú" style="margin-left:auto;display:grid">✕</button>{out}</nav></div>'

def tabbar(r, active):
    items = [("index.html", "today", "Hoy"), ("oraciones/index.html", "prayers", "Oraciones"), ("rosario.html", "rosary", "Rosario"), ("muro-de-intenciones.html", "candles", "Velas")]
    a = "".join(f'<a href="{r}{h}"{" class=\"on\"" if k == active else ""}>{TAB_ICONS[k]}<span data-i18n="{k}">{t}</span></a>' for h, k, t in items)
    return f'<nav class="tabbar" data-nosnippet aria-label="Accesos rápidos">{a}<a href="#" data-drawer>{TAB_ICONS["more"]}<span data-i18n="more">Más</span></a></nav>'

ACCOUNT = '''<div class="drawer" id="account" data-nosnippet hidden role="dialog" aria-modal="true" aria-labelledby="accT"><div class="drawer-bg" data-close></div><div class="drawer-p">
 <button class="icon-btn" data-close aria-label="Cerrar" style="margin-left:auto;display:grid">✕</button>
 <h2 id="accT" style="font-size:30px">Tu cuenta</h2>
 <div id="accOut"><p style="color:var(--muted);margin-top:0">Crea tu cuenta gratis y lleva tu camino de oración contigo, en el móvil y en el ordenador.</p>
  <ul class="acc-ben"><li><b>🔥</b>Tu racha de días rezados y tus estadísticas</li><li><b>♥</b>Tus oraciones guardadas y tu diario del Evangelio</li><li><b>✓</b>Tus novenas y retos, sincronizados</li></ul>
  <button class="btn btn-ghost acc-prov" id="accGoogle" type="button" hidden style="width:100%;margin:0 0 10px;gap:12px"><svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>Continuar con Google</button>
  <button class="btn btn-ghost acc-prov" id="accApple" type="button" hidden style="width:100%;margin:0 0 10px;gap:12px"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.6 2.1-3.8 2.2-3.9-1.2-1.8-3.1-2-3.7-2-1.6-.2-3.1.9-3.9.9-.8 0-2-.9-3.4-.9-1.7 0-3.3 1-4.2 2.6-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.3-.8 1.6 0 2 .8 3.4.8 1.4 0 2.3-1.3 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9 0 0-2.7-1-2.7-4.1zM13.9 5c.7-.9 1.2-2 1-3.2-1 0-2.3.7-3 1.6-.7.8-1.2 2-1.1 3.1 1.2.1 2.3-.6 3.1-1.5z"/></svg>Continuar con Apple</button>
  <button class="btn btn-ghost acc-prov" id="accFacebook" type="button" hidden style="width:100%;margin:0 0 10px;gap:12px"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="#1877F2" d="M24 12a12 12 0 1 0-13.9 11.9v-8.4H7.1V12h3V9.4c0-3 1.8-4.7 4.5-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.4l-.5 3.5h-2.9v8.4A12 12 0 0 0 24 12z"/></svg>Continuar con Facebook</button>
  <button class="btn btn-ghost acc-prov" id="accPhoneBtn" type="button" hidden style="width:100%;margin:0 0 10px;gap:12px"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M10.5 18.5h3"/></svg>Continuar con tu móvil</button>
  <form id="accPhone" class="ask" hidden style="flex-direction:column;margin:0 0 10px"><label class="sr" for="accTel">Tu número de móvil</label><input id="accTel" type="tel" inputmode="tel" placeholder="+34 600 000 000" autocomplete="tel"><button class="btn btn-accent" type="submit">Enviarme un código por SMS</button></form>
  <form id="accCode" class="ask" hidden style="flex-direction:column;margin:0 0 10px"><label class="sr" for="accOtp">Código de 6 cifras</label><input id="accOtp" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="Código de 6 cifras"><button class="btn btn-accent" type="submit">Entrar</button></form>
  <p class="note" id="accOr" style="text-align:center;margin:4px 0 10px" hidden>o con tu correo</p>
  <form id="accForm" class="ask" style="flex-direction:column"><label class="sr" for="accEmail">Correo electrónico</label><input id="accEmail" type="email" placeholder="tu@correo.com" autocomplete="email"><button class="btn btn-accent" type="submit">Enviarme el enlace de acceso</button></form>
  <form id="accECode" class="ask" hidden style="flex-direction:column;margin-top:10px"><label class="sr" for="accEOtp">Código del correo</label><input id="accEOtp" inputmode="numeric" autocomplete="one-time-code" maxlength="10" placeholder="Código del correo"><button class="btn btn-accent" type="submit">Entrar con el código</button></form>
  <p class="note">Te enviaremos un enlace para entrar sin contraseña. No compartimos tu correo con nadie.</p>
  <a class="acc-local" href="/perfil">Ver mis estadísticas en este dispositivo ›</a></div>
 <div id="accIn" hidden><div class="acc-me"><span class="acc-av" id="accAv"></span><div><b id="accWho"></b><small id="accMail"></small></div></div>
  <div class="acc-chips" id="accChips"></div>
  <a class="btn btn-accent" href="/perfil" style="width:100%;margin-top:14px">Ver mi perfil y estadísticas</a>
  <button class="btn btn-ghost sm" id="accLogout" style="margin-top:12px;width:100%">Cerrar sesión</button></div>
 <p class="note" id="accMsg" role="status"></p>
</div></div>'''

def footer(r):
    pop = [("oracion-antes-de-un-examen", "Antes de un examen"), ("oracion-por-un-enfermo", "Por un enfermo"), ("oracion-para-la-ansiedad", "Para la ansiedad"), ("oracion-por-un-difunto", "Por un difunto"), ("oracion-a-san-judas-tadeo", "A san Judas Tadeo"), ("oracion-para-encontrar-trabajo", "Para encontrar trabajo")]
    col = lambda title, items: f'<div><h4>{title}</h4><ul>' + "".join(f'<li><a href="{h if h.startswith("http") else r + h}"{" target=\"_blank\" rel=\"noopener\"" if h.startswith("http") else ""}>{t}</a></li>' for h, t in items) + '</ul></div>'
    social = [(AJ.get(k), n) for k, n in (("whatsappCanal", "Canal de WhatsApp"), ("spotify", "Spotify"), ("applePodcasts", "Apple Podcasts"), ("ivoox", "iVoox"), ("youtube", "YouTube"), ("instagram", "Instagram")) if AJ.get(k)]
    social += [("podcast.xml", "Pódcast (RSS)"), ("widget.html", "Widget para parroquias")]
    return f'''<footer class="foot" data-nosnippet>
  <div class="wrap foot-in">
    <div class="foot-brand">
      <a class="brand" href="{r}index.html">{ICON["logo"]}<span>rezo<b>diario</b></span></a>
      <p>Oración guiada cada día con el Evangelio, el Santo Rosario y más de {len(PRAYERS)} oraciones para todos los momentos de la vida. Gratis y sin registro.</p>
      <p class="verse">«Venid a mí todos los que estáis cansados y agobiados, y yo os aliviaré.» Mt 11, 28</p>
    </div>
    {col("Rezar", [("evangelio-de-hoy.html", "Evangelio de hoy"), ("evangelio-de-manana.html", "Evangelio de mañana"), ("santo-de-hoy.html", "Santo de hoy"), ("rosario.html", "Misterios del Rosario de hoy"), ("via-crucis.html", "Vía Crucis"), ("novenas/index.html", "Novenas"), ("adviento.html", "Adviento 2026"), ("camino-de-santiago.html", "Año Santo 2027"), ("calendario-liturgico.html", "Calendario litúrgico"), ("examen-de-conciencia.html", "Examen de conciencia")])}
    {col("Oraciones", [(f"oraciones/{s}.html", l) for s, l in pop])}
    {col("Versículos", [("versiculos.html", "Versículo del día")] + [(t["slug"] + ".html", t["t"]) for t in VTOP[:6]])}
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

OGM = {}
OG_EYEBROW = {"prayers": "Oración", "saints": "Santoral", "gospel": "Evangelio del día", "verses": "Versículos de la Biblia", "rosary": "Santo Rosario", "candles": "Muro de intenciones", "today": "Rezo Diario"}
def page(path, title, desc, main, active="", lds=(), body_attrs="", og_type="website", mini=False, robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1", js=(), og=None):
    ogn = "inicio" if path == "index.html" else path[:-5].replace("/index", "").replace("/", "--")
    if "noindex" not in robots and path != "404.html":
        t0 = title[:-len(" | Rezo Diario")] if title.endswith(" | Rezo Diario") else title
        OGM[ogn] = list(og) if og else [OG_EYEBROW.get(active, "Rezo Diario"), t0.split(" | ")[0], ""]
    ogimg = f"{SITE}og/{ogn}.jpg" if os.path.exists(os.path.join(ROOT, "static", "og", ogn + ".jpg")) else f"{SITE}og-rezodiario.jpg"
    depth = path.count("/"); r = "../" * depth
    cfg = {"supabaseUrl": AJ.get("supabaseUrl", ""), "supabaseAnonKey": AJ.get("supabaseAnonKey", ""), "today": TODAY}
    if len(title) > 62 and title.endswith(" | Rezo Diario"): title = title[:-len(" | Rezo Diario")]
    head = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
<script>try{{var t=JSON.parse(localStorage.getItem("rd-tema"));if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<script>if(location.hostname.indexOf("www.")===0)location.replace("https://rezodiario.com"+location.pathname+location.search+location.hash)</script>
<link rel="canonical" href="{canon(path)}">
<meta name="theme-color" content="#14302A">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Rezo Diario"><meta property="og:locale" content="es_ES">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon(path)}"><meta property="og:image" content="{ogimg}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{r}favicon.ico?v=4" sizes="48x48"><link rel="icon" href="{r}icon.svg?v=4" type="image/svg+xml"><link rel="icon" href="{r}favicon-96.png?v=4" type="image/png" sizes="96x96"><link rel="icon" href="{r}favicon-48.png?v=4" type="image/png" sizes="48x48"><link rel="icon" href="{r}icon-192.png?v=4" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="{r}apple-touch-icon.png?v=4"><link rel="manifest" href="{r}manifest.webmanifest">
<link rel="preload" href="{r}fuentes/manrope.woff" as="font" type="font/woff" crossorigin><link rel="preload" href="{r}fuentes/marcellus.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="{r}assets/site.css?v={VER}">
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
<script src="{r}assets/data.js?v={VER}"></script>
''' + "".join(f'<script src="{r}assets/{j}?v={VER}"></script>' for j in js) + f'<script src="{r}assets/site.js?v={VER}"></script>'
    pages.append((path, head, body, body_attrs + f' data-root="{r}"' + (" data-clean=\"1\"" if CLEAN else "")))

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
      <div class="p-foot"><button class="tog" id="tSpeed">Velocidad 1×</button><div class="mus"><button class="tog" id="tMusic" aria-haspopup="menu" aria-expanded="false">Música: <span id="tMusicL">Calma</span> ▾</button><div class="mus-menu" id="musMenu" role="menu" hidden></div></div><button class="tog" id="tVoice" aria-pressed="true">Voz guía</button></div>
    </article>'''

def week_section(r, mode="select", title="Esta semana, día a día", sub="Desliza para volver a un rezo que te perdiste o adelantar el de mañana."):
    lo = max(0, ti - 6); hi = min(len(DAYS), ti + 7)
    links = "".join(f'<li><a href="{r}evangelio/{w["date"]}.html">{w["wd"]} {w["n"]} de {w["mes"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in DAYS[lo:hi])
    return f'''<section class="sec" aria-labelledby="hWeek"><div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Sigue rezando</span><h2 id="hWeek">{title}</h2><p>{sub}</p></div>
      <div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><span class="streak" id="streak"></span><a class="btn btn-ghost sm" href="{r}calendario-liturgico.html">Ver el mes</a><div class="arrows"><button class="icon-btn" data-scroll="week" data-dir="-1" aria-label="Días anteriores">‹</button><button class="icon-btn" data-scroll="week" data-dir="1" aria-label="Días siguientes">›</button></div></div></div>
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
    dn = AJ.get("donaciones", {})
    return f'''<div class="give reveal" id="give">
      <div class="seg" role="tablist" aria-label="Frecuencia"><button class="on" data-f="once">Una vez</button><button data-f="month">Apoyar cada mes</button></div>
      <div class="amts" id="amts"></div>
      <div class="other" id="otherBox" hidden><label for="otherAmt">Otra cantidad (€)</label><input class="field" id="otherAmt" type="number" min="1" step="1" inputmode="numeric" placeholder="15"></div>
      <button class="btn btn-gold" id="donBtn">Donar 10 €</button>
      <div class="safe"><span>Pago seguro con Stripe · tarjeta, Apple Pay o Google Pay</span><span>Puedes cancelar el apoyo mensual cuando quieras{f' · <a href="{E(dn["portal"])}" target="_blank" rel="noopener">Gestionar mi apoyo mensual</a>' if dn.get("portal") else ""}</span></div>
      <div class="thanks" id="thanks" hidden></div>
    </div>'''

def donate_section(h="h2"):
    return f'''<section class="sec band" id="donar" aria-labelledby="hDon"><div class="wrap don">
    <div class="reveal"><span class="eyebrow">Apoyo</span><{h} id="hDon" style="font-family:var(--f-display);font-weight:400;font-size:clamp(30px,4.2vw,46px);line-height:1.08;margin:10px 0 0">Ayuda a mantener Rezo Diario</{h}>
      <p style="color:var(--muted);max-width:34em">Tu apoyo nos ayuda a mantener este espacio gratuito y seguir creando nuevos contenidos y audios.</p>
      <p style="color:var(--muted);max-width:34em;font-size:14.5px">Rezo Diario no tiene anuncios ni pide registrarse. Cada aportación, grande o pequeña, sostiene la oración diaria de muchas personas.</p></div>
    {give()}
  </div></section>'''

def news(r=""):
    wa = AJ.get("whatsappCanal")
    extra = f'<a class="btn" href="{E(wa)}" target="_blank" rel="noopener" style="background:#25D366;color:#06301A">Seguir el canal de WhatsApp</a>' if wa else ''
    return f'''<section class="news" aria-labelledby="hNews"><div class="wrap news-in">
    <div><h2 id="hNews">El rezo de cada día, en tu móvil</h2><p>Un mensaje breve a las 7:00 con el audio y el Evangelio. Por correo{" o por WhatsApp" if wa else ""}. Sin publicidad.</p>{f'<p style="margin-top:14px">{extra}</p>' if extra else ''}</div>
    <form id="newsForm" novalidate><label class="sr" for="email">Tu correo electrónico</label><input id="email" type="email" placeholder="tu@correo.com" autocomplete="email"><input type="text" name="web" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px"><button class="btn" type="submit">Apuntarme</button><p class="msg" id="newsMsg" hidden></p><p class="news-legal">Al apuntarte aceptas recibir el rezo diario por correo. Puedes darte de baja en cualquier momento. <a href="{r}legal/privacidad.html">Privacidad</a>.</p></form>
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

def camino(r, compact=False):
    """Tu camino de oración: siete velas (una por día), mensaje que anima y gestos sencillos. Sin puntos ni trofeos."""
    extra = "" if compact else (
        '<div class="camino-int" data-camino-int>'
        '<span class="camino-int-v" data-camino-int-v hidden></span>'
        '<button type="button" class="camino-link" data-camino-int-btn>Añadir por quién rezo esta semana</button>'
        '<form class="camino-int-f" data-camino-int-f hidden><label class="sr" for="caminoInt">Por quién rezas esta semana</label><input id="caminoInt" maxlength="60" placeholder="Por mi madre, por mi amiga Laura…" autocomplete="off"><button class="btn btn-ghost sm" type="submit">Guardar</button></form></div>'
        '<div class="camino-foot"><span data-camino-stats></span><button type="button" class="camino-link" data-camino-ics>Recordármelo cada día</button></div>')
    return (f'<div class="camino{" compact" if compact else ""}" data-camino>'
            '<div class="camino-head"><div class="camino-t"><span class="eyebrow">Tu camino de oración</span>'
            '<p class="camino-n" data-camino-n>Cada día que reces, se enciende una vela.</p><p class="camino-q" data-camino-q></p></div>'
            '<ol class="camino-velas" data-camino-dots aria-label="Tus últimos siete días"></ol></div>'
            '<div class="camino-acts" data-camino-acts>'
            f'<a class="btn btn-accent sm" data-camino-cta href="{r}index.html#player">Rezar hoy · 5 min</a>'
            '<button type="button" class="btn btn-ghost sm" data-camino-done>Ya he rezado hoy</button></div>'
            + extra + '</div>')
def recorrido(r, cand="otra"):
    items = [(f"{r}index.html#momento", "¿Qué llevas hoy en el corazón?", "Cuéntanoslo y te proponemos una oración."),
             (f"{r}muro-de-intenciones.html#{cand}", "Enciende una vela", "Deja tu intención y otras personas rezarán contigo."),
             (f"{r}muro-de-intenciones.html#candles", "Reza por otras personas", "Acompaña las intenciones que otros han dejado hoy."),
             (f"{r}evangelio-de-manana.html", "Vuelve mañana", "El Evangelio y el rezo de mañana ya te esperan.")]
    li = "".join(f'<li><a href="{h}"><b>{t}</b><span>{d}</span></a></li>' for h, t, d in items)
    return f'<nav class="recorrido reveal" aria-label="Sigue rezando"><span class="eyebrow">Sigue rezando</span><ol>{li}</ol>{camino(r, True)}</nav>'
# ================= VERSÍCULOS =================
MOODS = [("Triste", "versiculos-para-cuando-estas-triste"), ("Con ansiedad", "versiculos-para-la-ansiedad"), ("Enamorado", "versiculos-sobre-el-amor"), ("Preocupado por el dinero", "versiculos-sobre-el-dinero"), ("Sin fe", "versiculos-para-la-fe"), ("No puedo dormir", "versiculos-para-dormir"), ("Enfadado", "versiculos-para-el-enfado"), ("Con miedo", "versiculos-para-el-miedo"), ("Agradecido", "versiculos-para-dar-gracias")]
_seen = set(); VALL = []
for _t in VTOP:
    for _v in _t["versos"]:
        if _v["ref"] not in _seen: _seen.add(_v["ref"]); VALL.append((_t, _v))
_ord = datetime.date.fromisoformat(now).toordinal()
VDAY_T, VDAY = VALL[(_ord * 37) % len(VALL)]
def vacts(ref, x, path):
    wa = "https://wa.me/?text=" + E(("«" + x + "» " + ref + " · " + canon(path)).replace(" ", "%20"))
    return f'<div class="vacts"><button class="vbtn gold" data-vimg type="button">Crear imagen</button><a class="vbtn" href="{wa}" target="_blank" rel="noopener">WhatsApp</a><button class="vbtn" data-vcopy type="button">Copiar</button></div>'
def vday_card(r):
    path = VDAY_T["slug"] + ".html"
    return (f'<article class="vday reveal" data-ref="{E(VDAY["ref"])}" data-x="{E(VDAY["x"])}" data-tag="Versículo del día">'
            f'<span class="eyebrow">Versículo del día · {int(now[8:])} de {MES[int(now[5:7]) - 1]}</span>'
            f'<blockquote>«{E(VDAY["x"])}»</blockquote><cite>{E(VDAY["ref"])}</cite><p class="vqs"><b>Qué significa:</b> {E(VDAY["e"])}</p>'
            f'{vacts(VDAY["ref"], VDAY["x"], "versiculos.html")}<a class="vmore" href="{r}{path}">Más {VDAY_T["t"].lower()} →</a></article>')
def mood_picker(r, h="h2"):
    b = "".join(f'<button type="button" class="mood" data-m="{s}">{m}</button>' for m, s in MOODS)
    return (f'<div class="vnow-wrap" id="ahora"><div><span class="eyebrow">¿Cómo te sientes ahora?</span><{h} class="vnow-h">Necesito un versículo <em>ahora</em></{h}>'
            f'<p style="color:var(--muted);margin:8px 0 0">Toca cómo te sientes y te damos un versículo de la Biblia para este momento.</p>'
            f'<div class="moods" role="group" aria-label="Cómo te sientes">{b}</div></div>'
            '<article class="vnow" id="vNow" aria-live="polite" hidden><span class="eyebrow" id="vNowTag"></span><blockquote id="vNowX"></blockquote><cite id="vNowR"></cite><p id="vNowE"></p>'
            '<div class="vacts"><button class="vbtn" id="vNowAgain" type="button">Otro versículo</button><button class="vbtn gold" data-vimg type="button">Crear imagen</button><a class="vbtn" id="vNowWa" target="_blank" rel="noopener">WhatsApp</a></div>'
            '<a class="vmore" id="vNowMore" href="#">Ver los 20 versículos →</a></article></div>')
def vtiles(r, skip=""):
    return '<div class="vtiles">' + "".join(f'<a class="vtile reveal" href="{r}{t["slug"]}.html"><i></i><b>{t["t"]}</b><small>{len(t["versos"])} versículos</small></a>' for t in VTOP if t["slug"] != skip) + '</div>'
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
      <a class="momento" id="momento" href="oraciones/oracion-de-la-manana.html" hidden><i aria-hidden="true"></i><span><b></b><small></small></span><em aria-hidden="true">›</em></a>
      <a class="momento momento-ev" href="evangelio-de-hoy.html#lectio"><i aria-hidden="true"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6.5C10 5 7 4.5 4 5v13c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V5c-3-.5-6 0-8 1.5z"/><path d="M12 6.5V19"/></svg></i><span><b>Profundiza en el Evangelio de hoy</b><small>«{E(TW["title"])}» · Lectio Divina, propósito y tu diario</small></span><em aria-hidden="true">›</em></a>
      <div class="facts"><div><small>Evangelio</small><span id="fRef">{TW["ref"]}</span></div><div><small>Rosario de hoy</small><span id="fSet">Misterios {setname(TW)}</span></div><div><small>Duración</small><span id="fDur">5 min</span></div></div>
    </div>
    {player()}
  </div>
</section>
{week_section(r)}
<section class="sec"><div class="wrap"><div class="vhub">{vday_card(r)}{mood_picker(r)}</div></div></section>
<section class="sec band" id="momento" aria-labelledby="hMom"><div class="wrap assist chatwrap">
  <div class="reveal chat-intro"><span class="eyebrow">Para este momento</span><h2 id="hMom">¿Qué llevas hoy en el corazón?</h2>
    <p style="color:var(--muted);margin:10px 0 0">Cuéntalo con tus palabras, como se lo contarías a un amigo, y te acompañamos con una oración para este momento.</p>
    <ol class="chat-steps"><li><b>Cuéntalo</b><span>Lo que te preocupa, lo que agradeces o lo que pides.</span></li><li><b>Recibe una oración</b><span>Elegida entre las {len(PRAYERS)} de Rezo Diario, con audio y un versículo si encaja.</span></li><li><b>No reces solo</b><span>Enciende una vela y otras personas rezarán contigo.</span></li></ol>
    <p class="note">Lo que escribes no se guarda ni se envía a ningún sitio: se queda en tu dispositivo. No sustituye el acompañamiento espiritual, médico o psicológico. Si estás pasando por un momento muy difícil, llama al <strong>024</strong> (atención a la conducta suicida, España) o al <strong>112</strong> si es una emergencia.</p></div>
  <div class="chat reveal" role="region" aria-label="Acompañante de oración">
    <div class="chat-top"><span class="chat-av" aria-hidden="true">{ICON["logo"]}</span><div><b>Acompañante de oración</b><small><i></i>Privado · se queda en tu dispositivo</small></div></div>
    <div class="chat-log" id="answers" aria-live="polite"></div>
    <div class="chat-sug"><div class="feel" id="feel"></div></div>
    <form class="chat-in" id="askForm"><label class="sr" for="askIn">Lo que llevas hoy en el corazón</label><textarea id="askIn" rows="1" maxlength="400" placeholder="Cuéntame qué llevas dentro…"></textarea><button class="chat-send" type="submit" aria-label="Enviar"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button></form>
  </div>
</div></section>
{sec(camino(r) + head2("Oraciones por tema", "Un rezo para cada momento", f"{len(PRAYERS)} oraciones para estudiar, por un enfermo, por tu familia, para la ansiedad o por un ser querido difunto.", '<a class="btn btn-ghost sm" href="oraciones/index.html">Ver todas</a>') + tiles(r))}
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
 home_main, "today", [{"@context": "https://schema.org", "@type": "WebSite", "url": SITE, "name": "Rezo Diario", "alternateName": ["RezoDiario", "rezodiario.com"], "inLanguage": "es", "publisher": ORG, "potentialAction": {"@type": "SearchAction", "target": SITE + "oraciones/index.html?q={search_term_string}", "query-input": "required name=search_term_string"}},
 {"@context": "https://schema.org", **ORG}, faq_ld(home_faq)], mini=True, js=("versos.js",))

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
    top = [PBY[x] for x in c.get("top", []) if x in PBY]
    top_html = sec(head2(c.get("topK", "Las más rezadas"), c.get("topT", f"Las {len(top)} oraciones más rezadas")) + '<ol class="top-or">' + "".join(f'<li><a href="{q["slug"]}.html"><b>{E(q["t"])}</b><span>{E(re.split(r"(?<=[.!?])[ \n]", q["x"].replace(chr(10), " "))[0][:140])}</span></a></li>' for q in top) + '</ol>') if top else ""
    m = phero(r, cr, f'{len(ps)} oraciones', c["h1"], c["intro"]) + top_html + sec(f'<div class="grid">{"".join(card(p, r) for p in ps)}</div>') + (sec('<div class="prose" style="max-width:760px">' + "".join(f"<p>{E(x)}</p>" for x in c["texto"].split(chr(10)+chr(10))) + '</div>') if c.get("texto") else "") + sec(head2("Preguntas frecuentes", "Dudas sobre estas oraciones") + faq_html(FAQ_CAT[k]), "sec band") + sec(head2("Otros temas", "Sigue explorando") + tiles(r))
    page(path, f'{c.get("seoT") or c["h1"]} | Rezo Diario', c.get("seoD") or c["intro"][:158], m, "prayers", [crumbs_ld(cr), faq_ld(FAQ_CAT[k]), {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["h1"], "url": canon(path), "inLanguage": "es"}])

def pplayer(p, r):
    """Reproductor de una oración con audio: anterior · play/pausa · siguiente, barra y tiempo."""
    if not p.get("audio"): return ""
    lst = [q for q in PRAYERS if q.get("audio")]; i = lst.index(p)
    pv, nx = lst[i - 1], lst[(i + 1) % len(lst)]
    ic = lambda d: f'<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{d}"/></svg>'
    return (f'<div class="pplayer" id="pplayer" data-src="{E(p["audio"])}" data-dur="{p.get("duracion", 0)}">'
            f'<a class="pp-skip" href="{q_href(pv)}" data-next="{pv["slug"]}" aria-label="Oración anterior: {E(pv["t"])}" title="{E(pv["t"])}">{ic("M6 5h2v14H6zM20 5v14L9 12z")}</a>'
            '<button class="pp-play" id="ppPlay" type="button" aria-label="Escuchar la oración">' + ic("M7 4.5v15l12.5-7.5z") + '</button>'
            f'<a class="pp-skip" href="{q_href(nx)}" data-next="{nx["slug"]}" aria-label="Oración siguiente: {E(nx["t"])}" title="{E(nx["t"])}">{ic("M16 5h2v14h-2zM4 5v14l11-7z")}</a>'
            '<div class="pp-bar"><input type="range" id="ppSeek" min="0" max="1000" value="0" step="1" aria-label="Avanzar o retroceder en la oración">'
            f'<div class="pp-time"><span id="ppCur">0:00</span><span id="ppDur">{int(p.get("duracion", 0)) // 60}:{int(p.get("duracion", 0)) % 60:02d}</span></div></div></div>')
def q_href(q): return f'{q["slug"]}.html'
def desc_for(p):
    first = re.split(r"(?<=[.!?])\s", p["x"].replace("\n", " "))[0]
    if len(first) < 30 or re.match(r"^\d", first):
        intro1 = re.split(r"(?<=[.!?])\s", (p.get("intro") or "").replace("\n", " "))[0]
        d = f'{intro1} Texto completo para rezar y escuchar.' if intro1 else f'{p["t"]}: «{first}» Texto completo para rezar y escuchar.'
    else: d = f'{p["t"]}: «{first}» Texto completo para rezar y escuchar.'
    if len(d) < 120: d += " Con audio, cuándo rezarla y cómo."
    if len(d) <= 160: return d
    c = d[:154].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return c + ("»" if c.count("«") > c.count("»") else "")
EXAM_RX = re.compile(r"perd[oó]n|perdona|pecad|convi[eé]rt|conversi|misericordia|arrepent|pródigo|publicano", re.I)
EXAM_SLUGS = {"oracion-de-la-noche": ("Antes de dormir, mira tu día", "El examen de conciencia te ayuda a repasar el día con calma y a pedir perdón sin miedo."),
              "examen-del-dia": ("¿Quieres ir un paso más allá?", "Si hace tiempo que no te confiesas, el examen de conciencia te ayuda a prepararlo con sencillez."),
              "oracion-para-perdonar": ("El perdón también se recibe", "En la confesión Dios te perdona a ti. Prepárala con un examen de conciencia sencillo."),
              "oracion-para-perdonarme-a-mi-mismo": ("Deja tu carga en manos de Dios", "La confesión es el lugar donde Dios te dice: «Estás perdonado». Prepárala sin miedo."),
              "acto-de-contricion": ("Prepara tu confesión", "Antes del acto de contrición viene el examen: preguntas sencillas y los pasos para confesarte.")}
def dato_box(d):
    """Respuesta directa arriba de la página (la pregunta exacta que busca la gente)."""
    if not d: return ""
    return f'<div class="dato reveal"><small>{E(d["k"])}</small><b>{E(d["t"])}</b>{"<span>" + E(d["x"]) + "</span>" if d.get("x") else ""}</div>'
def mas_html(p):
    """Otras oraciones cortas para la misma necesidad, en la misma página (más contenido útil para quien busca)."""
    if not p.get("mas"): return ""
    return f'<h2>{E(p.get("masT", "Más oraciones"))}</h2>' + "".join(f'<div class="mas-or"><h3>{E(o["t"])}</h3>' + "".join(f"<p>{E(x)}</p>" for x in o["x"].split(chr(10)+chr(10))) + '</div>' for o in p["mas"])
def extra_faq(o): return [(f["q"], f["a"]) for f in o.get("faq", [])]
def exam_box(r, t, d): return f'<a class="exam-cta reveal" href="{r}examen-de-conciencia.html"><small>Examen de conciencia</small><b>{E(t)}</b><span>{E(d)}</span><em>Prepararme ›</em></a>'
for p in PRAYERS:
    c = CATS[p["cat"]]; path = f'oraciones/{p["slug"]}.html'
    cr = [("Inicio", "index.html"), ("Oraciones", "oraciones/index.html"), (c["name"], f'oraciones/tema-{p["cat"]}.html'), (p["t"], path)]
    rel = [q for q in PRAYERS if q["cat"] == p["cat"] and q["slug"] != p["slug"]][:5]
    wa = "https://wa.me/?text=" + html.escape((p["t"] + " " + canon(path)).replace(" ", "%20"))
    faq = [(f'¿Cuándo rezar la {p["t"][0].lower() + p["t"][1:]}?' if p["t"].startswith("Oración") else f'¿Cuándo rezar «{p["t"]}»?', p["when"])] + FAQ_CAT[p["cat"]]
    faq = extra_faq(p) + faq
    m = phero(r, cr, f'<span style="display:inline-flex;align-items:center;gap:8px"><i class="dot" style="background:{c["color"]}"></i>{c["name"]} · {p["min"]} min</span>', E(p["t"]), E(p["when"])) + f'''
<section class="sec"><div class="wrap art">
  <div style="min-width:0">
    <article class="pray reveal"><p class="pray-text" id="prayText">{E(p["x"])}</p>
      {pplayer(p, r)}<div class="pray-acts">{"" if p.get("audio") else '<button class="btn btn-accent sm" id="btnSpeak">Escuchar</button>'}<button class="btn btn-ghost sm" id="btnCopy">Copiar oración</button><button class="btn btn-ghost sm" id="btnFav" aria-pressed="false">Guardar</button><button class="btn btn-ghost sm" id="btnAmen" type="button">Amén</button><a class="btn btn-ghost sm" href="{wa}" target="_blank" rel="noopener">Compartir por WhatsApp</a></div>
    </article>
    <div class="prose">
      {dato_box(p.get("dato"))}
      {"<h2>Sobre esta oración</h2>" + "".join(f"<p>{E(x)}</p>" for x in p["intro"].split(chr(10)+chr(10))) if p.get("intro") else ""}
      {mas_html(p)}
      <h2>Cuándo rezarla</h2><p>{E(p["when"])}</p>
      <h2>Cómo rezarla</h2><p>Busca un momento de calma, respira despacio y lee la oración sin prisa, en voz baja o en silencio. Si una frase te toca, quédate en ella. Puedes pulsar «Escuchar» para que la web la lea por ti, o guardarla en favoritos para tenerla a mano.</p>
      <p>Si rezas por otra persona, díselo: saber que alguien reza por nosotros es un gran consuelo. También puedes <a href="{r}muro-de-intenciones.html#{CANDLE_HASH[p["cat"]]}">encender una vela por esta intención</a> para que otros recen contigo.</p>
      <h2>Preguntas frecuentes</h2>{faq_html(faq)}
    </div>
    {recorrido(r, CANDLE_HASH[p["cat"]])}
  </div>
  <aside class="side">
    {exam_box(r, *EXAM_SLUGS[p["slug"]]) if p["slug"] in EXAM_SLUGS else ""}
    <div class="box candle-cta"><h3>Enciende una vela</h3><p>Deja esta intención en el muro y otras personas rezarán por ella durante siete días.</p><a class="btn btn-flame sm" href="{r}muro-de-intenciones.html#{CANDLE_HASH[p["cat"]]}">Encender una vela</a></div>
    <div class="box"><h3>Más oraciones de {c["name"].lower()}</h3><ul class="links">{"".join(f'<li><a href="{q["slug"]}.html">{E(q["t"])}<small>{q["min"]} min</small></a></li>' for q in rel)}</ul></div>
    <div class="box"><h3>Rezo de hoy</h3><p style="margin:0 0 12px;color:var(--muted);font-size:14.5px">{E(TW["title"])} · {TW["ref"]}</p><a class="btn btn-accent sm" href="{r}evangelio-de-hoy.html">Escuchar el rezo</a></div>
  </aside>
</div></section>'''
    page(path, f'{p.get("seoT") or p["t"]} | Rezo Diario', p.get("seoD") or desc_for(p), m, "prayers",
     [crumbs_ld(cr), faq_ld(faq), {"@context": "https://schema.org", "@type": "Article", "headline": p["t"], "description": p.get("seoD") or desc_for(p), "inLanguage": "es", "articleSection": c["name"], "author": ORG, "publisher": ORG, "datePublished": "2026-10-17", "dateModified": TODAY, "mainEntityOfPage": canon(path), "keywords": p["k"]}],
     body_attrs=f' data-slug="{p["slug"]}"', og_type="article", og=(f'Oración · {c["name"]}', p["t"], f'Texto completo y audio · {p["min"]} min'))

# ================= EVANGELIO =================
def cita_corta(t):
    """«Lectura de la primera carta del apóstol san Pablo a los Corintios 1, 3-9» → «1 Corintios 1, 3-9»."""
    n = "1 " if re.search(r"\bprimera carta\b", t) else "2 " if re.search(r"\bsegunda carta\b", t) else "3 " if re.search(r"\btercera carta\b", t) else ""
    if re.search(r"libro primero", t): n = "1 "
    if re.search(r"libro segundo", t): n = "2 "
    c = re.sub(r"^Lectura (del santo evangelio según san |de la (primera |segunda |tercera )?carta (del apóstol san Pablo |del apóstol |de san |de |)(a los |a )?|del libro (primero |segundo )?(de los |del |de la |de )?|de la profecía de |de los |del |de la |de )", "", t).strip()
    if c.startswith("Hebreos") is False and "a los Hebreos" in t: c = "Hebreos " + c
    c = re.sub(r"^(Salmo \d+).*", r"\1", c)
    return n + c[:1].upper() + c[1:]
def lecturas_html(r, w):
    ls = w.get("lecturas")
    if not ls: return ""
    li = "".join(f'<li{" class=is-ev" if x["tipo"] == "Evangelio" else ""}><small>{E(x["tipo"])}</small><span title="{E(x["titulo"])}">{E(cita_corta(x["titulo"]))}</span>{"<em>aquí abajo</em>" if x["tipo"] == "Evangelio" else ""}</li>' for x in ls)
    url = w.get("lecturasUrl") or "https://www.dominicos.org/predicacion/evangelio-del-dia/hoy/"
    return f'<div class="lecturas reveal"><div class="lec-h"><b>Lecturas de la misa</b><a href="{E(url)}" target="_blank" rel="noopener">Leerlas completas ›</a></div><ol>{li}</ol></div>'
def gospel_main(r, w, kind):
    s = SBY.get(w["saint"])
    title = {"hoy": "Evangelio de hoy", "manana": "Evangelio de mañana"}.get(kind, f'Evangelio del {w["wd"].lower()} {w["n"]} de {w["mes"]}')
    cr = [("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")] + ([("Hoy", "evangelio-de-hoy.html")] if kind == "hoy" else [("Mañana", "evangelio-de-manana.html")] if kind == "manana" else [(f'{w["n"]} de {w["mes"]}', f'evangelio/{w["date"]}.html')])
    ex = EXTRA.get(w["date"])
    lit_t = E(ex["t"] if ex else w["lit"]); lit_x = E(ex["x"] if ex else "")
    santo = (f'<div class="gs-box gs-saint"><span class="eyebrow">Santo del día</span><h3>{E(s["name"])}</h3><p>{E(s["short"])}</p><a href="{r}santos/{s["slug"]}.html">Su vida y su oración ›</a></div>') if s else ""
    i0 = DAYS.index(w); near = [x for x in DAYS[max(0, i0 - 2):i0 + 4] if x is not w][:5]
    semana = '<div class="gs-box"><span class="eyebrow">Otros días</span><ul class="gs-days">' + "".join(f'<li><a href="{r}evangelio/{x["date"]}.html"><i class="dot" style="background:{LITC[x["color"]][0]}"></i><span><b>{x["wd"][:3]} {x["n"]} {x["mes"][:3]}</b><small>{E(x["title"])}</small></span></a></li>' for x in near) + f'</ul><a class="gs-more" href="{r}calendario-liturgico.html">Ver el calendario ›</a></div>'
    share_url = canon(f'evangelio/{w["date"]}.html'); wa = "https://wa.me/?text=" + html.escape((f'Evangelio del {w["n"]} de {w["mes"]}: «{w["ex"]}» ' + share_url).replace(" ", "%20"))
    box = f'''<aside class="gos-side">
   <div class="gs-box gs-listen"><span class="eyebrow">Reza este Evangelio</span><h3>{E(w["title"])}</h3><p>Evangelio, reflexión y silencio guiado{(" · " + w["duracion"] + " min") if w.get("duracion") else ""}</p>
    <a class="btn btn-gold sm" href="#player" data-gs-play>{ICON["play"]}<span>Escuchar ahora</span></a></div>
   <div class="gs-box gs-lit" style="--lc:{LITC[w["color"]][0]}"><span class="eyebrow">Liturgia del día</span><h3>{lit_t}</h3><p class="gs-color"><i class="dot"></i>{E(LITC[w["color"]][1])}</p>{f"<p>{lit_x}</p>" if lit_x else ""}</div>
   {santo}
   {semana}
   <div class="gs-box gs-share"><span class="eyebrow">Compártelo</span><p>Envía el Evangelio de hoy a alguien que lo necesite.</p><div class="gs-acts"><a class="btn btn-ghost sm" href="{wa}" target="_blank" rel="noopener">WhatsApp</a><button class="btn btn-ghost sm" type="button" data-copy="{E(share_url)}">Copiar enlace</button></div></div>
  </aside>'''
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
  <article class="panel reveal">{lecturas_html(r, w)}<span class="eyebrow">{E(w["refL"])}</span><p class="quote">{E(w["ex"])}</p><p>{E(w["sum"])}</p>
   {ctx_html(w)}
   <h3>Reflexión</h3><p>{E(w["refl"])}</p><h3>Preguntas para tu oración</h3><ol class="qs">{"".join(f"<li>{E(q)}</li>" for q in w["qs"])}</ol>
   <h3>Oración final</h3><p style="font-family:var(--f-read);font-style:italic">{E(w["fin"])}</p>
   {prop_html(w)}
   {fam_html(w)}
   <div class="ev-share" data-ref="{E(w["refL"])}" data-x="{E(w["ex"])}" data-tag="Evangelio del {w["n"]} de {w["mes"]}"><button class="btn btn-gold sm" type="button" data-vimg>Crear imagen para compartir</button><span>Para WhatsApp o tus estados</span></div>
   {exam_box(r, "Un buen día para volver a Dios", "El Evangelio de hoy invita a la conversión. Mira tu vida con calma y prepara una confesión.") if EXAM_RX.search(w["ex"] + " " + w["sum"] + " " + w["refl"]) else ""}
   <div class="hero-cta" style="margin-top:22px"><a class="btn btn-ghost sm" href="{E(w.get("lecturasUrl") or "https://www.vaticannews.va/es/evangelio-de-hoy.html")}" target="_blank" rel="noopener">Lecturas completas del día</a><a class="btn btn-ghost sm" href="{r}rosario.html">Rezar el Rosario</a></div>{pn}</article>
  {box}
</div></section>
{lectio_html(r, w)}
{week_section(r, "link", "Evangelios de estos días", "Vuelve a cualquier día o adelanta los próximos.")}'''
    return m, cr
def ctx_html(w):
    c = w.get("ctx")
    if not c: return ""
    return (f'<div class="ev-ctx"><span class="eyebrow">Para entenderlo</span><dl>'
            f'<div><dt>Dónde</dt><dd>{E(c["donde"])}</dd></div><div><dt>A quién habla</dt><dd>{E(c["quien"])}</dd></div>'
            f'<div class="ev-kw"><dt>Palabra clave</dt><dd><b>{E(c["palabra"])}</b> {E(c["significa"])}</dd></div></dl></div>')
def prop_html(w):
    if not w.get("proposito"): return ""
    return (f'<div class="ev-prop" data-prop="{w["date"]}"><span class="eyebrow">El propósito de hoy</span><p>{E(w["proposito"])}</p>'
            f'<button class="btn btn-accent sm" type="button" data-prop-btn>Me lo propongo</button><span class="ev-prop-ok" hidden>✓ Te lo has propuesto. Esta noche, en el examen del día, mira cómo te ha ido.</span></div>')
def fam_html(w):
    f = w.get("familia")
    if not f: return ""
    return f'<div class="ev-fam"><span class="eyebrow">En familia</span><p>{E(f["x"])}</p><p class="ev-q"><b>Para hablar en la mesa:</b> {E(f["q"])}</p></div>'
def lectio_html(r, w):
    qs = "".join(f"<li>{E(q)}</li>" for q in w["qs"])
    return f'''<section class="sec band" id="lectio" aria-labelledby="hLec"><div class="wrap lec-wrap">
  <div class="lec-intro"><span class="eyebrow">Lectio Divina</span><h2 id="hLec">Reza este Evangelio en cuatro pasos</h2>
   <p>La forma más antigua de rezar con la Biblia. Unos diez minutos: lees, meditas, le hablas a Dios y te quedas en silencio con él.</p>
   <div class="diario" id="diario"><span class="eyebrow">Mi diario del Evangelio</span><ul id="diarioList"></ul><p class="diario-empty" id="diarioEmpty">Lo que escribas en el paso «Orar» se guardará aquí, junto a su Evangelio. Solo lo ves tú.</p></div></div>
  <div class="lec" id="lec" data-day="{w["date"]}" data-title="{E(w["title"])}" data-ref="{E(w["refL"])}">
   <ol class="lec-tabs" role="tablist"><li><button role="tab" data-i="0" aria-selected="true"><b>1</b>Leer</button></li><li><button role="tab" data-i="1"><b>2</b>Meditar</button></li><li><button role="tab" data-i="2"><b>3</b>Orar</button></li><li><button role="tab" data-i="3"><b>4</b>Contemplar</button></li></ol>
   <div class="lec-p" data-p="0"><h3>Lee despacio</h3><p class="lec-help">Léelo dos veces, sin prisa. Fíjate en la palabra o la frase que más te llame la atención.</p><blockquote>«{E(w["ex"])}»<cite>{E(w["refL"])}</cite></blockquote><p>{E(w["sum"])}</p></div>
   <div class="lec-p" data-p="1" hidden><h3>Medita</h3><p class="lec-help">¿Qué te dice a ti este Evangelio hoy? Deja que estas preguntas te acompañen.</p><ol class="qs">{qs}</ol><div class="lec-timer" data-secs="120"><button class="btn btn-ghost sm" type="button" data-timer>Dos minutos de silencio</button><span class="lec-t" aria-live="polite"></span></div></div>
   <div class="lec-p" data-p="2" hidden><h3>Ora</h3><p class="lec-help">Háblale a Dios con tus palabras. Da gracias, pide, cuéntale lo que has descubierto.</p><label class="sr" for="lecNote">Lo que le dices a Dios</label><textarea id="lecNote" rows="4" placeholder="Señor, hoy…"></textarea><p class="lec-saved" id="lecSaved" aria-live="polite"></p></div>
   <div class="lec-p" data-p="3" hidden><h3>Contempla</h3><p class="lec-help">Quédate un minuto en silencio, sin decir nada. Solo estar con Dios, que te mira con cariño.</p><div class="lec-breath" aria-hidden="true"><i></i></div><div class="lec-timer" data-secs="60"><button class="btn btn-accent sm" type="button" data-timer>Empezar el minuto de silencio</button><span class="lec-t" aria-live="polite"></span></div></div>
   <div class="lec-nav"><button class="btn btn-ghost sm" type="button" data-lprev disabled>Anterior</button><button class="btn btn-accent sm" type="button" data-lnext>Siguiente paso</button></div>
  </div></div></section>'''
def gld(w, path): return {"@context": "https://schema.org", "@type": "PodcastEpisode", "name": f'{w["title"]} · Rezo del {w["n"]} de {w["mes"]} de {w["date"][:4]}', "datePublished": w["date"], "inLanguage": "es", "description": w["sum"], "url": canon(path), "partOfSeries": {"@type": "PodcastSeries", "name": "Rezo Diario", "url": SITE}, **({"associatedMedia": {"@type": "MediaObject", "contentUrl": w["audio"] if w["audio"].startswith("http") else SITE + w["audio"].lstrip("/")}} if w.get("audio") else {})}
for w in DAYS:
    m, cr = gospel_main("../", w, "dia"); path = f'evangelio/{w["date"]}.html'
    page(path, f'Evangelio del {w["n"]} de {w["mes"]} de {w["date"][:4]} ({w["ref"]}) y reflexión', f'Evangelio del {nice(w)}, {w["refL"]}: «{w["ex"]}» Reflexión y audio para rezar.'[:160], m, "gospel", [crumbs_ld(cr), gld(w, path)], body_attrs=f' data-day="{w["date"]}"', mini=True, og_type="article", js=() if w["date"] in WIN else (f'dias/{w["date"]}.js',), og=(f'Evangelio del {w["n"]} de {w["mes"]}', w["title"], f'{w["refL"]} · reflexión y audio para rezar'))
m, cr = gospel_main("", TW, "hoy")
page("evangelio-de-hoy.html", f'Evangelio de hoy, {nice(TW)} ({TW["ref"]}) | Rezo Diario', f'Evangelio de hoy {TW["n"]} de {TW["mes"]}, {TW["refL"]}: «{TW["ex"]}» Comentario, preguntas y audio para rezar.'[:160], m, "gospel", [crumbs_ld(cr), gld(TW, "evangelio-de-hoy.html")], body_attrs=f' data-day="{TODAY}"', mini=True)
m, cr = gospel_main("", TOMORROW, "manana")
page("evangelio-de-manana.html", f'Evangelio de mañana, {nice(TOMORROW)} ({TOMORROW["ref"]}) | Rezo Diario', f'Evangelio de mañana {TOMORROW["n"]} de {TOMORROW["mes"]}, {TOMORROW["refL"]}: «{TOMORROW["ex"]}» Prepara tu oración.'[:160], m, "gospel", [crumbs_ld(cr)], body_attrs=f' data-day="{TOMORROW["date"]}"', mini=True)
months = {}
for w in DAYS: months.setdefault(w["date"][:7], []).append(w)
arch = "".join(f'<h2 style="margin-top:34px">{MES[int(k[5:]) - 1].capitalize()} de {k[:4]}</h2><ul class="links" style="columns:2 300px;column-gap:40px;display:block">' + "".join(f'<li style="break-inside:avoid"><a href="{w["date"]}.html">{w["wd"]} {w["n"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in v) + '</ul>' for k, v in months.items())
page("evangelio/index.html", "Archivo del Evangelio del día | Rezo Diario", "Archivo del Evangelio del día: todos los Evangelios con su comentario, preguntas para rezar y audio guiado, ordenados por meses y días.",
 phero("../", [("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")], "Archivo", "El Evangelio de cada día", "Vuelve a cualquier día: cada Evangelio con su comentario, sus preguntas y su audio.") + sec(f'<div class="prose" style="max-width:none">{arch}</div>'), "gospel", [crumbs_ld([("Inicio", "index.html"), ("Evangelio", "evangelio/index.html")])])
# ================= CALENDARIO LITÚRGICO =================
def es_fiesta(w): return bool(re.search(r"Solemnidad|Fiesta|Domingo|Natividad|Navidad|Todos los Santos|Inmaculada|Cristo, Rey", w["lit"]))
def cal_mes(k, ws):
    y, mo = int(k[:4]), int(k[5:])
    first = datetime.date(y, mo, 1); pad = first.weekday()
    nd = (datetime.date(y + (mo == 12), mo % 12 + 1, 1) - first).days
    by = {w["n"]: w for w in ws}
    cells = ['<li class="cal-pad" aria-hidden="true"></li>'] * pad
    for d in range(1, nd + 1):
        w = by.get(d)
        if not w:
            cells.append(f'<li class="cal-off"><span class="cal-n">{d}</span></li>'); continue
        s = SBY.get(w["saint"]) if w.get("saint") else None
        sn = f"<em>{E(s['name'])}</em>" if s and not any(len(x) > 3 and x.lower() in w["lit"].lower() for x in s["name"].split(" ")[1:3]) else ""
        cls = "cal-d" + (" is-fiesta" if es_fiesta(w) else "") + (" is-today" if w["date"] == TODAY else "")
        cells.append(f'<li class="{cls}"><a href="evangelio/{w["date"]}.html"><span class="cal-n">{d}<i class="dot" style="background:{LITC[w["color"]][0]}" title="{E(LITC[w["color"]][1])}"></i><small class="cal-wd">{w["wd"][:3]}</small></span>'
                     f'<b>{E(w["lit"])}</b>{sn}<span class="cal-ref">{E(w["ref"])}</span></a></li>')
    head = "".join(f"<li>{x[:3]}</li>" for x in WDN)
    return f'<div class="cal-m" id="mes-{k}"><h2>{MES[mo - 1].capitalize()} de {y}</h2><ol class="cal-h" aria-hidden="true">{head}</ol><ol class="cal-g">{"".join(cells)}</ol></div>'
cal_html = "".join(cal_mes(k, v) for k, v in months.items())
leyenda = '<ul class="cal-ley">' + "".join(f'<li><i class="dot" style="background:{v[0]}"></i>{E(v[1])}</li>' for k, v in LITC.items() if any(w["color"] == k for w in DAYS)) + '</ul>'
adv1 = next((f"{w['n']} de {w['mes']}" for w in DAYS if "Adviento" in w["lit"] and w["wd"] == "Domingo"), "primer domingo de Adviento")
cal_faq = [("¿Qué es el calendario litúrgico?", "Es el orden con el que la Iglesia católica celebra el año: los tiempos de Adviento, Navidad, Cuaresma, Pascua y Tiempo Ordinario, con sus domingos, solemnidades, fiestas y memorias de los santos. Cada día tiene sus lecturas y su color."),
           ("¿Qué significan los colores litúrgicos?", "El verde se usa en el Tiempo Ordinario y habla de esperanza; el morado, en Adviento, Cuaresma y en la misa de difuntos, e invita a la conversión; el blanco, en las fiestas del Señor, de la Virgen y de los santos que no son mártires; el rojo, en las fiestas de los mártires, de los apóstoles y en Pentecostés."),
           ("¿Cuándo empieza el año litúrgico?", f"El año litúrgico empieza el primer domingo de Adviento. En {TODAY[:4]} es el {adv1}, cuatro domingos antes de Navidad."),
           ("¿Qué diferencia hay entre solemnidad, fiesta y memoria?", "La solemnidad es la celebración más importante (como Navidad o Todos los Santos); la fiesta es un grado menor (como la de un apóstol); y la memoria recuerda a un santo dentro de la misa del día, unas veces de forma obligatoria y otras libre.")]
page("calendario-liturgico.html", f"Calendario litúrgico {TODAY[:4]}: fiestas, santos y colores de cada día | Rezo Diario", f"Calendario litúrgico católico día a día: tiempo litúrgico, color, fiestas, santos y Evangelio de cada día de {MES[int(TODAY[5:7]) - 1]} a diciembre de {TODAY[:4]}.",
 phero("", [("Inicio", "index.html"), ("Calendario litúrgico", "calendario-liturgico.html")], "Calendario litúrgico", "Fiestas, santos y colores de cada día",
       "Mira qué celebra la Iglesia cada día, de qué color se viste el altar y qué santo recordamos. Toca un día para rezar con su Evangelio.", leyenda)
 + sec(f'<div class="cal">{cal_html}</div>') + sec(head2("Preguntas frecuentes", "Sobre el calendario litúrgico") + faq_html(cal_faq), "sec band"),
 "gospel", [crumbs_ld([("Inicio", "index.html"), ("Calendario litúrgico", "calendario-liturgico.html")]), faq_ld(cal_faq)])
# ================= EXAMEN DE CONCIENCIA Y CONFESIÓN =================
EXG = PBY["examen-de-conciencia-guiado"]; ACT = PBY["acto-de-contricion"]
_grupos, _g = [], None
for par in [x.strip() for x in EXG["x"].split("\n\n") if x.strip()]:
    if par.endswith(".") and len(par) < 25 and not par.startswith("¿"): _g = [par.rstrip("."), []]; _grupos.append(_g)
    elif par.startswith("¿") and _g: _g[1].append(par)
ex_cards = '<div class="ex-g">' + "".join(f'<div class="panel ex-c reveal"><span class="eyebrow">{i + 1} de {len(_grupos)}</span><h3>{E(t)}</h3><ul>' + "".join(f"<li>{E(q)}</li>" for q in qs) + '</ul></div>' for i, (t, qs) in enumerate(_grupos)) + '</div>'
pasos = [("Prepárate antes", "Haz el examen con calma, arrepiéntete de corazón y propón cambiar. No hace falta que lo sientas todo con fuerza: basta con querer volver a Dios."),
         ("Saluda al sacerdote", "En España es costumbre empezar con «Ave María Purísima», y el sacerdote responde «Sin pecado concebida». Después haz la señal de la cruz."),
         ("Di cuándo fue tu última confesión", "Por ejemplo: «Hace dos meses» o «Hace muchos años». Si te cuesta o estás nervioso, díselo: el sacerdote te ayudará."),
         ("Confiesa tus pecados", "Con sencillez y sin rodeos, empezando por lo que más te pesa. No hace falta dar detalles innecesarios ni justificarse."),
         ("Escucha el consejo y la penitencia", "El sacerdote te dirá unas palabras y te pondrá una penitencia: una oración o un gesto concreto para reparar y empezar de nuevo."),
         ("Reza el acto de contrición", "Expresa tu arrepentimiento con el «Señor mío Jesucristo» o con tus propias palabras."),
         ("Recibe la absolución", "El sacerdote te da la absolución en nombre de Dios. Responde «Amén». Tus pecados quedan perdonados."),
         ("Cumple la penitencia", "Hazla cuanto antes y da gracias. Sales con el corazón en paz: no tienes que volver a cargar con lo que ya has confesado.")]
pasos_html = '<ol class="ex-pasos">' + "".join(f'<li class="reveal"><b>{E(t)}</b><p>{E(d)}</p></li>' for t, d in pasos) + '</ol>'
ex_faq = [("¿Cada cuánto hay que confesarse?", "La Iglesia pide confesarse al menos una vez al año y siempre antes de comulgar si se tiene conciencia de un pecado grave. Pero se recomienda hacerlo con frecuencia, por ejemplo una vez al mes, porque ayuda a crecer y a vivir con más paz."),
          ("¿Qué pasa si se me olvida un pecado?", "Si lo olvidas sin querer, queda perdonado con los demás. Si después lo recuerdas y es grave, basta con decirlo en la siguiente confesión."),
          ("Hace muchos años que no me confieso, ¿puedo hacerlo?", "Sí, y es una gran alegría. Díselo al sacerdote al empezar: él te ayudará a hacer memoria con calma. No importa el tiempo que haya pasado."),
          ("¿Qué es un pecado mortal o grave?", "Es una falta en materia grave, cometida sabiendo que lo es y queriéndolo de verdad. Los pecados leves o veniales también se pueden confesar y es bueno hacerlo."),
          ("¿El sacerdote puede contar lo que le digo?", "No. El secreto de confesión es absoluto: el sacerdote no puede revelar nunca lo que ha escuchado, a nadie y bajo ninguna circunstancia."),
          ("¿Puedo confesarme por internet o por teléfono?", "No. La confesión necesita la presencia del penitente y del sacerdote. Esta página te ayuda a prepararla; para confesarte, acércate a tu parroquia o a cualquier iglesia en horario de confesiones.")]
ex_main = phero("", [("Inicio", "index.html"), ("Oraciones", "oraciones/index.html"), ("Examen de conciencia", "examen-de-conciencia.html")], "Confesión",
    "Examen de conciencia para confesarse",
    "Un repaso sencillo y sin miedo de tu relación con Dios, con los demás y contigo mismo, y una guía paso a paso para confesarte bien, aunque haga años que no lo haces.",
    pplayer(EXG, "") if EXG.get("audio") else "") \
 + sec(head2("Examen", "Preguntas para mirar tu vida", "Léelas despacio. Quédate en las que te remuevan por dentro y apunta, si te ayuda, lo que quieras decir.") + ex_cards) \
 + sec('<div id="confesion"></div>' + head2("Confesión", "Cómo confesarse paso a paso", "Si estás nervioso, no te preocupes: el sacerdote está para ayudarte.") + pasos_html, "sec band") \
 + sec(f'''<div class="gos"><article class="panel reveal"><span class="eyebrow">Oración</span><h2 style="margin-top:6px">Acto de contrición</h2>{"".join(f'<p style="font-family:var(--f-read);font-size:19px;line-height:1.6">{E(x)}</p>' for x in ACT["x"].split(chr(10) + chr(10)))}
 <div class="hero-cta" style="margin-top:18px"><a class="btn btn-ghost sm" href="oraciones/acto-de-contricion.html">Escucharla y copiarla</a><a class="btn btn-ghost sm" href="oraciones/examen-del-dia.html">Examen del día (antes de dormir)</a></div></article>
 <aside class="panel saint reveal"><span class="eyebrow">Si no la recuerdas</span><h3>Basta con decirlo de corazón</h3><p style="opacity:.85">«Jesús, Hijo de Dios, ten compasión de mí, que soy un pecador.» Dios mira tu corazón, no tu memoria.</p></aside></div>''') \
 + sec(head2("Preguntas frecuentes", "Sobre la confesión") + faq_html(ex_faq))
page("examen-de-conciencia.html", "Examen de conciencia para confesarse y cómo confesarse paso a paso | Rezo Diario",
     "Examen de conciencia sencillo para preparar la confesión, con audio guiado, cómo confesarse paso a paso y el acto de contrición «Señor mío Jesucristo».",
     ex_main, "prayers", [crumbs_ld([("Inicio", "index.html"), ("Oraciones", "oraciones/index.html"), ("Examen de conciencia", "examen-de-conciencia.html")]), faq_ld(ex_faq),
     {"@context": "https://schema.org", "@type": "HowTo", "name": "Cómo confesarse paso a paso", "inLanguage": "es", "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": d} for i, (t, d) in enumerate(pasos)]}],
     body_attrs=f' data-slug="{EXG["slug"]}"')

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
def santo_color(x):
    t = (x["name"] + " " + x["short"]).lower()
    if "inmaculada" in t: return "blue"
    return "red" if re.search(r"mártir|apóstol", t) else "white"
_ty, _tm = int(TODAY[:4]), int(TODAY[5:7])
def santoral_mes(mo, v):
    y = _ty if mo >= _tm else _ty + 1
    first = datetime.date(y, mo, 1); pad = first.weekday()
    nd = (datetime.date(y + (mo == 12), mo % 12 + 1, 1) - first).days
    by = {}
    for x in v: by.setdefault(int(x["md"][3:]), []).append(x)
    cells = ['<li class="cal-pad" aria-hidden="true"></li>'] * pad
    for d in range(1, nd + 1):
        xs = by.get(d)
        if not xs: cells.append(f'<li class="cal-off"><span class="cal-n">{d}</span></li>'); continue
        x = xs[0]; iso = f"{y}-{mo:02d}-{d:02d}"
        otros = "".join(f'<em>{E(o["name"])}</em>' for o in xs[1:])
        cls = "cal-d is-santo" + (" is-today" if iso == TODAY else "")
        cells.append(f'<li class="{cls}"><a href="{r}santos/{x["slug"]}.html"><span class="cal-n">{d}<i class="dot" style="background:{LITC[DBY[iso]["color"] if iso in DBY and DBY[iso].get("saint") == x["slug"] and DBY[iso]["color"] != "green" else santo_color(x)][0]}"></i><small class="cal-wd">{WDN[datetime.date(y, mo, d).weekday()][:3]}</small></span>'
                     f'<b>{E(x["name"])}</b><span class="cal-sh">{E(x["short"])}</span>{otros}</a></li>')
    head = "".join(f"<li>{w[:3]}</li>" for w in WDN)
    lit = f'<a class="cal-link" href="{r}calendario-liturgico.html#mes-{y}-{mo:02d}">Ver este mes en el calendario litúrgico ›</a>' if f"{y}-{mo:02d}" in months else ""
    return f'<div class="cal-m" id="mes-{mo:02d}"><div class="cal-mh"><h2>{MES[mo - 1].capitalize()} de {y}</h2>{lit}</div><ol class="cal-h" aria-hidden="true">{head}</ol><ol class="cal-g">{"".join(cells)}</ol></div>'
_orden = sorted(bym, key=lambda m: (m < _tm, m))
_grandes = [m for m in _orden if len(bym[m]) >= 3]; _sueltos = [m for m in _orden if len(bym[m]) < 3]
cal = '<div class="cal">' + "".join(santoral_mes(m, bym[m]) for m in _grandes) + '</div>'
if _sueltos:
    cal += f'<div class="cal-m"><div class="cal-mh"><h2>Otros santos del año</h2></div><div class="pagegrid">' + "".join(saint_link(r, x) for m in _sueltos for x in bym[m]) + '</div></div>'
page("santos/index.html", "Santoral católico: vida y oración de cada santo | Rezo Diario", "Santoral con la vida breve y la oración de cada santo: san Judas Tadeo, santa Rita, san Expedito, la Inmaculada, la Virgen de Guadalupe y el santo de cada día.",
 phero(r, [("Inicio", "index.html"), ("Santos", "santos/index.html")], "Santoral", "Santoral: la vida y la oración de cada santo", "Empieza por el <a href=\"../santo-de-hoy.html\" style=\"color:var(--gold)\">santo de hoy</a> o busca por meses. Toca un día para leer la vida del santo y rezar su oración.") + sec(cal), "saints", [crumbs_ld([("Inicio", "index.html"), ("Santos", "santos/index.html")])])
def saint_desc(x):
    sh = x["short"][0].lower() + x["short"][1:]
    nm = x["name"] if sh.split(" ")[0] in x["name"].lower() else f'{x["name"]}, {sh}'
    d = f'{nm} ({x["date"]}): su vida, por qué es patrón de {x["patron"]}, qué nos enseña hoy y una oración para pedir su intercesión.'
    if len(d) > 160: d = f'{nm} ({x["date"]}): su vida y su oración. Patrón de {x["patron"]}.'
    if len(d) > 160: d = f'{nm} ({x["date"]}): su vida, qué nos enseña hoy y una oración para pedir su intercesión.'
    if len(d) > 160: d = d[:157].rsplit(" ", 1)[0] + "…"
    return d
for x in SAINTS:
    path = f'santos/{x["slug"]}.html'; cr = [("Inicio", "index.html"), ("Santos", "santos/index.html"), (x["name"], path)]; pr = PBY.get(x["prayer"])
    faq = [(f'¿Cuándo se celebra {x["name"]}?', f'Su fiesta o memoria es el {x["date"]}.'), (f'¿De qué es patrón {x["name"]}?', f'Se le invoca como patrón de {x["patron"]}.')]
    m = phero(r, cr, f'{x["date"]} · {E(x["short"])}', E(x["name"]), E(x["bio"][0])) + f'''<section class="sec"><div class="wrap art"><div style="min-width:0">
  <article class="pray reveal"><span class="eyebrow">Oración</span><p class="pray-text" id="prayText" style="margin-top:12px">{E(x["oracion"])}</p><div class="pray-acts"><button class="btn btn-ghost sm" id="btnCopy">Copiar oración</button></div></article>
  <div class="prose"><h2>Su vida</h2>{"".join(f"<p>{E(b)}</p>" for b in x["bio"] + x.get("mas", []))}{f'<h2>Qué nos enseña hoy</h2><p>{E(x["ensena"])}</p>' if x.get("ensena") else ""}<h2>Patrón de</h2><p>{E(x["patron"][0].upper() + x["patron"][1:])}.</p><h2>Preguntas frecuentes</h2>{faq_html(faq)}</div></div>
  <aside class="side">{f'<div class="box"><h3>Oración relacionada</h3><ul class="links"><li><a href="../oraciones/{pr["slug"]}.html">{E(pr["t"])}<small>{pr["min"]} min</small></a></li></ul></div>' if pr else ""}
   <div class="box candle-cta"><h3>Enciende una vela</h3><p>Pide su intercesión y deja tu intención en el muro.</p><a class="btn btn-flame sm" href="../muro-de-intenciones.html">Encender una vela</a></div>
   <div class="box"><h3>Otros santos</h3><ul class="links">{"".join([f'<li><a href="{o["slug"]}.html">{E(o["name"])}<small>{o["date"]}</small></a></li>' for o in SAINTS if o is not x and o["md"] > x["md"]][:6])}</ul></div></aside></div></section>'''
    page(path, f'{x["name"]}: vida y oración ({x["date"]}) | Rezo Diario', saint_desc(x), m, "saints",
     [crumbs_ld(cr), faq_ld(faq), {"@context": "https://schema.org", "@type": "Article", "headline": f'{x["name"]}: vida y oración', "inLanguage": "es", "author": ORG, "publisher": ORG, "datePublished": "2026-10-17", "dateModified": TODAY, "mainEntityOfPage": canon(path), "about": {"@type": "Person", "name": x["name"]}}], og_type="article", og=(f'Santoral · {x["date"]}', x["name"], x["short"]))

# ================= ROSARIO =================
r = ""
ros_faq = [("¿Qué misterios se rezan hoy?", f'Hoy, {TW["wd"].lower()}, se rezan los misterios {setname(TW)}. Lunes y sábado: gozosos; martes y viernes: dolorosos; miércoles y domingo: gloriosos; jueves: luminosos.'),
 ("¿Cuánto se tarda en rezar el Rosario?", "Unos 20 minutos rezado con calma. Un solo misterio (un denario) se reza en unos 4 minutos."),
 ("¿Cómo se reza el Rosario paso a paso?", "Se empieza con la señal de la cruz y el Credo, un Padre Nuestro, tres Avemarías y un Gloria. Después, en cada uno de los cinco misterios, se anuncia el misterio y se reza un Padre Nuestro, diez Avemarías y un Gloria. Se termina con la Salve."),
 ("¿Quién añadió los misterios luminosos?", "San Juan Pablo II, en la carta Rosarium Virginis Mariae, en el año 2002.")]
rows = "".join(f'<tr><th scope="row">{S["name"]}</th><td>{S["days"]}</td><td>{"<br>".join(E(m[0]) for m in S["list"])}</td></tr>' for S in SETS.values())
SET_STYLE = {"gozosos": ("#A8812D", "Alegría"), "dolorosos": ("#7A4E8C", "Pasión"), "gloriosos": ("#C08A1E", "Gloria"), "luminosos": ("#4F86B5", "Luz")}
mis_cards = '<div class="mis-g">' + "".join(
    f'<article class="mis-c reveal{" is-hoy" if k == TW["set"] else ""}" style="--mc:{SET_STYLE.get(k, ("#2C5D47", ""))[0]}">'
    f'<header><span class="mis-days">{E(S["days"])}</span>{"<span class=mis-hoy>Hoy</span>" if k == TW["set"] else ""}<h3>Misterios {E(S["name"].lower())}</h3></header>'
    '<ol>' + "".join(f'<li><b>{E(m[0])}</b><small>{E(m[1])} · Fruto: {E(m[2][0].lower() + m[2][1:])}</small></li>' for m in S["list"]) + '</ol>'
    f'<a class="btn {"btn-accent" if k == TW["set"] else "btn-ghost"} sm mis-go" href="#rosario" data-set="{k}">Rezar los misterios {E(S["name"].lower())}</a></article>'
    for k, S in SETS.items()) + '</div>'
ros = f'''<section class="phero"><div class="wrap">{crumbs_html(r, [("Inicio", "index.html"), ("Santo Rosario", "rosario.html")])}<div class="eyebrow" style="margin-top:22px">Santo Rosario guiado</div><h1>Misterios del Rosario de hoy: {setname(TW)}</h1><p class="lead">Reza el Rosario cuenta a cuenta. Cada misterio con su cita del Evangelio y su fruto. Pulsa una cuenta, desliza la tarjeta o usa las flechas del teclado.</p></div></section>
<section class="sec band" id="rosario"><div class="wrap"><div class="ros ros2">
  <aside class="ros-side">
    <div class="ros-ring"><svg class="ros-svg" id="beads" viewBox="0 0 320 470" role="img" aria-label="Rosario con la cuenta actual resaltada"></svg>
      <div class="ros-center" aria-hidden="true"><b id="rcN">✝</b><small id="rcL">Inicio</small></div></div>
    <ol class="ros-chap" id="rChap" aria-label="Partes del Rosario"></ol>
  </aside>
  <div style="min-width:0"><div class="sets" id="sets"></div>
    <div class="step" id="step" tabindex="0" aria-live="polite"><span class="eyebrow" id="stK">Inicio</span><h2 class="step-t" id="stT">Señal de la cruz y Credo</h2><div class="step-meta" id="stM"></div><p class="step-x" id="stX">{E(O["SENAL"])}</p><div class="tens" id="tens" aria-hidden="true"></div></div>
    <div class="rplayer" role="group" aria-label="Controles del Rosario">
      <button class="rp-play" id="rVoice" aria-pressed="false" aria-label="Rezar en voz alta"><svg class="i-play" width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg><svg class="i-pause" width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg></button>
      <div class="rp-mid"><div class="rp-top"><b id="rpNow">Señal de la cruz y Credo</b><span class="hint" id="rCount"></span></div>
        <div class="rp-bar" id="rpBar" role="slider" tabindex="0" aria-label="Avanzar por el Rosario" aria-valuemin="1"><i id="rBar"></i><span class="rp-ticks" id="rpTicks"></span></div>
        <div class="rp-sub"><span id="rpVoz">Pulsa ▶ para rezarlo con voz, o avanza a tu ritmo</span></div></div>
      <div class="rp-ctl"><button class="rp-ic" id="rPrev" aria-label="Paso anterior"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6 5h2v14H6zM20 5v14L9 12z"/></svg></button><button class="rp-ic rp-next" id="rNext" aria-label="Paso siguiente"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 5h2v14h-2zM4 5v14l11-7z"/></svg></button><button class="rp-ic" id="rReset" aria-label="Empezar de nuevo" title="Empezar de nuevo"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></svg></button></div>
    </div>
    <div class="rp-opts"><button class="tog rp-opt" id="rSpeed" aria-label="Velocidad de la voz" title="Velocidad de la voz">1×</button><div class="mus" id="rMusWrap"><button class="tog rp-opt" id="rMusic" aria-haspopup="menu" aria-expanded="false" aria-label="Música de fondo">♪ <span id="rMusicL">Calma</span></button><div class="mus-menu" id="rMusMenu" role="menu" hidden></div></div><span class="hint rp-optx">Velocidad y música de fondo mientras rezas con voz</span></div>
  </div></div></div></section>
{sec(head2("Cada día de la semana", "Qué misterios se rezan cada día", "Cuatro grupos de cinco misterios que recorren la vida de Jesús y de María. Toca uno para rezarlo ahora.") + mis_cards)}
{sec(head2("Guía", "Cómo rezar el Rosario paso a paso") + f"""<div class="art"><div class="prose">
 <p>El Rosario es una oración sencilla que recorre la vida de Jesús de la mano de María. Se reza con un rosario de 59 cuentas, aunque basta con los dedos.</p>
 <ol class="qs"><li>Haz la señal de la cruz y reza el Credo con el crucifijo.</li><li>En la primera cuenta grande, reza un Padre Nuestro.</li><li>En las tres cuentas pequeñas, tres Avemarías: por la fe, la esperanza y la caridad. Después, un Gloria.</li><li>Anuncia el primer misterio y reza un Padre Nuestro en la cuenta grande.</li><li>Reza diez Avemarías mientras contemplas el misterio, y termina con el Gloria y el «Oh Jesús mío».</li><li>Repite con los cinco misterios y termina con la Salve.</li></ol>
 <h2>Preguntas frecuentes</h2>{faq_html(ros_faq)}</div>
 <aside class="side"><div class="box"><h3>Oraciones a la Virgen</h3><ul class="links"><li><a href="oraciones/acordaos.html">Acordaos<small>1 min</small></a></li><li><a href="oraciones/bajo-tu-amparo.html">Bajo tu amparo<small>1 min</small></a></li><li><a href="oraciones/el-angelus.html">El Ángelus<small>3 min</small></a></li></ul></div>
 <div class="box candle-cta"><h3>Ofrece tu Rosario</h3><p>Enciende una vela por la intención por la que rezas hoy.</p><a class="btn btn-flame sm" href="muro-de-intenciones.html">Encender una vela</a></div><div class="box don-cta"><span class="don-ic" aria-hidden="true">♥</span><h3>¿Te ayuda rezar aquí?</h3><p>Rezo Diario es gratis y sin anuncios. Con un pequeño donativo mantienes las voces, la música y los audios nuevos de cada día.</p><a class="btn btn-gold sm" href="donar.html">Hacer un donativo</a><span class="hint don-nota">Pago seguro con Stripe</span></div></aside></div>""")}'''
page("rosario.html", f'Misterios del Rosario de hoy ({setname(TW)}) y cómo rezarlo | Rezo Diario', f'Hoy se rezan los misterios {setname(TW)}. Reza el Santo Rosario guiado cuenta a cuenta, con la cita bíblica y el fruto de cada misterio.', ros, "rosary",
 [crumbs_ld([("Inicio", "index.html"), ("Santo Rosario", "rosario.html")]), faq_ld(ros_faq), {"@context": "https://schema.org", "@type": "HowTo", "name": "Cómo rezar el Santo Rosario", "inLanguage": "es", "totalTime": "PT20M", "step": [{"@type": "HowToStep", "text": t} for t in ["Señal de la cruz y Credo", "Padre Nuestro", "Tres Avemarías y Gloria", "Anunciar el misterio y rezar el Padre Nuestro", "Diez Avemarías, Gloria y Oh Jesús mío", "Repetir con los cinco misterios y terminar con la Salve"]]}])

# ================= VÍA CRUCIS =================
VIA = [(e["t"], e["x"]) for e in VIAJ["estaciones"]]
via_faq = [("¿Cuándo se reza el Vía Crucis?", "Sobre todo los viernes de Cuaresma y el Viernes Santo, aunque se puede rezar cualquier día, especialmente los viernes."), ("¿Cuántas estaciones tiene el Vía Crucis?", "Catorce estaciones, desde la condena de Jesús hasta su sepultura. Muchas parroquias añaden una decimoquinta: la Resurrección.")]
vc = phero(r, [("Inicio", "index.html"), ("Vía Crucis", "via-crucis.html")], "14 estaciones", "Vía Crucis guiado", "Acompaña a Jesús en el camino de la cruz. Desliza la tarjeta o toca una estación para avanzar.") + f'''
<section class="sec"><div class="wrap" style="max-width:900px">
  <div class="vc-path" id="vcPath" aria-label="Estaciones"></div>
  <article class="vc-card" id="vc" tabindex="0" aria-live="polite"><div class="vc-num" id="vcNum">I</div><h2 id="vcT">{E(VIA[0][0])}</h2><p class="vc-ant">{E(VIAJ["antifona"])}</p><p class="pray-text" id="vcX" style="margin-top:16px">{E(VIA[0][1])}</p><p class="vc-ant">Padre Nuestro, Ave María y Gloria.</p>
   <div class="ros-nav"><button class="btn btn-ghost sm" id="vcPrev">Anterior</button><button class="btn btn-accent sm" id="vcNext" style="margin-left:auto">Siguiente estación</button></div></article>
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
    faq = extra_faq(n) + faq
    m = phero(r, cr, f'Fiesta: {n["feast"]}', E(n["t"]), E(n["intro"])) + f'''<section class="sec"><div class="wrap art"><div style="min-width:0" id="novena" data-slug="{n["slug"]}">{dato_box(n.get("dato"))}
  <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap"><svg class="ring" id="novRing" viewBox="0 0 84 84" aria-hidden="true"></svg><div><b style="font-size:17px" id="novStatus"></b><p class="hint" style="margin:4px 0 0">Tu progreso se guarda en este dispositivo y en tu cuenta.</p></div></div>
  <div class="nov-days" id="novDays"></div>
  <article class="pray"><span class="eyebrow">Oración inicial</span><p class="pray-text" style="margin:10px 0 22px;font-size:18px">{E(n["open"])}</p>
   <span class="eyebrow" id="novK">Día 1</span><h2 id="novT" style="margin:6px 0 10px">{E(n["days"][0]["t"])}</h2><p class="pray-text" id="novX">{E(n["days"][0]["x"])}</p>
   <span class="eyebrow" style="display:block;margin-top:22px">Oración final</span><p class="pray-text" style="margin-top:10px;font-size:18px">{E(n["close"])}</p>
   <div class="pray-acts"><button class="btn btn-accent sm" id="novDone" aria-pressed="false">Marcar este día como rezado</button></div></article>
  <div class="prose"><h2>Los nueve días</h2><ol class="qs">{"".join(f"<li><strong>{E(d['t'])}.</strong> {E(d['x'])}</li>" for d in n["days"])}</ol><h2>Preguntas frecuentes</h2>{faq_html(faq)}</div></div>
  <aside class="side"><div class="box candle-cta"><h3>Enciende una vela</h3><p>Acompaña tu novena con una vela en el muro de intenciones.</p><a class="btn btn-flame sm" href="../muro-de-intenciones.html{"#difuntos" if "difuntos" in n["slug"] else ""}">Encender una vela</a></div>
   <div class="box"><h3>Otras novenas</h3><ul class="links">{"".join(f'<li><a href="{o["slug"]}.html">{E(o["t"])}<small>{fdate(o["start"])}</small></a></li>' for o in NOVENAS if o is not n)}</ul></div></aside></div></section>'''
    page(path, f'{n.get("seoT") or n["t"] + ": los 9 días para rezar"} | Rezo Diario', n.get("seoD") or f'{n["t"]} completa: oración inicial, meditación de cada día y oración final. {n["intro"]}'[:160], m, "novenas", [crumbs_ld(cr), faq_ld(faq)])

# ================= ADVIENTO, RETO Y NAVIDAD =================
r = ""
adv_days = [w for w in DAYS if "2026-11-29" <= w["date"] <= "2026-12-24"]
adv_faq = [("¿Cuándo empieza el Adviento en 2026?", "El domingo 29 de noviembre de 2026. Dura cuatro semanas, hasta la Nochebuena del 24 de diciembre."),
 ("¿Cuándo empieza la corona de Adviento en 2026?", "La corona de Adviento se empieza a encender el domingo 29 de noviembre de 2026, primer domingo de Adviento. Ese día se bendice y se enciende la primera vela."),
 ("¿Cuándo se bendice la corona de Adviento en 2026?", "El domingo 29 de noviembre de 2026, o la tarde del sábado 28. Se bendice en la misa de ese domingo o en casa, en familia, antes de encender la primera vela."),
 ("¿Qué día se enciende cada vela en 2026?", "Primera vela: domingo 29 de noviembre. Segunda: domingo 6 de diciembre. Tercera (la rosa): domingo 13 de diciembre. Cuarta: domingo 20 de diciembre."),
 ("¿Qué significan las velas de la corona de Adviento?", "Cada domingo se enciende una vela más. Tradicionalmente representan la esperanza, la paz, la alegría (la vela rosa del tercer domingo) y el amor."),
 ("¿Qué color se usa en Adviento?", "El morado, color de la espera y la conversión. El tercer domingo, llamado Gaudete, puede usarse el rosa."),
 ("¿Cuándo es la Inmaculada?", "El 8 de diciembre. En España es fiesta de precepto y patrona del país.")]
sundays = [w for w in adv_days if w["wd"] == "Domingo"]
adv = phero(r, [("Inicio", "index.html"), ("Adviento 2026", "adviento.html")], "Del 29 de noviembre al 24 de diciembre", "Adviento 2026: prepara tu corazón para la Navidad", "Cuatro semanas para esperar a Jesús que viene: la corona y sus velas, el Evangelio de cada día, un reto diario y las novenas de la Inmaculada, Guadalupe y Navidad.") + \
 sec('<div class="dato reveal" style="margin:0"><small>Corona de Adviento 2026</small><b>Se bendice y se enciende la primera vela el domingo 29 de noviembre de 2026.</b><span>2.ª vela: 6 de diciembre · 3.ª vela (rosa): 13 de diciembre · 4.ª vela: 20 de diciembre. <a href="oraciones/bendicion-corona-de-adviento.html">Bendición de la corona</a> · <a href="oraciones/oracion-de-las-velas-de-adviento.html">Oración de las velas</a></span></div>') + \
 sec(head2("Los cuatro domingos", "La corona de Adviento, semana a semana") + '<div class="pagegrid">' + "".join(f'<a class="saintcard reveal" href="evangelio/{w["date"]}.html"><small>{w["n"]} de {w["mes"]} · vela {i + 1}</small><b>{E(w["lit"])}</b><span>{w["ref"]}: {E(w["title"])}</span></a>' for i, w in enumerate(sundays)) + '</div>') + \
 sec(head2("Para rezar", "Oraciones y devociones de Adviento") + '<div class="duo">' + f'<a class="feature reveal" href="retos/adviento.html" style="background:linear-gradient(150deg,#5B3D7A,#24163A)"><small>26 días</small><b>Reto de Adviento</b><p>Un gesto pequeño cada día para preparar la Navidad.</p></a><a class="feature reveal" href="novenas/novena-a-la-inmaculada.html" style="background:linear-gradient(150deg,#3C6FA8,#16304F)"><small>29 nov – 7 dic</small><b>Novena a la Inmaculada</b><p>Nueve días con María antes de su fiesta.</p></a><a class="feature reveal" href="novenas/novena-de-navidad.html" style="background:linear-gradient(150deg,#A8812D,#4A3510)"><small>16 – 24 dic</small><b>Novena de Navidad</b><p>Nueve días en familia antes de Nochebuena.</p></a><a class="feature reveal" href="examen-de-conciencia.html" style="background:linear-gradient(150deg,#2C5D47,#10261D)"><small>Antes del 24 dic</small><b>Confesarse por Navidad</b><p>Examen de conciencia y cómo confesarse paso a paso.</p></a></div>' +
  '<ul class="links" style="margin-top:22px">' + "".join(f'<li><a href="oraciones/{s}.html">{E(PBY[s]["t"])}<small>{PBY[s]["min"]} min</small></a></li>' for s in ["bendicion-corona-de-adviento", "oracion-de-las-velas-de-adviento", "oracion-de-adviento", "oracion-a-la-inmaculada", "oracion-a-la-virgen-de-guadalupe", "bendicion-del-belen"]) + '</ul>', "sec band") + \
 sec(head2("Día a día", "El Evangelio de cada día de Adviento") + '<ul class="links" style="columns:2 300px;column-gap:40px;display:block">' + "".join(f'<li style="break-inside:avoid"><a href="evangelio/{w["date"]}.html">{w["wd"]} {w["n"]} de {w["mes"]}: {E(w["title"])}<small>{w["ref"]}</small></a></li>' for w in adv_days) + '</ul>') + sec(head2("Preguntas frecuentes", "Sobre el Adviento") + faq_html(adv_faq), "sec band")
page("adviento.html", "Adviento 2026: cuándo empieza, corona y oraciones | Rezo Diario", "El Adviento y la corona de Adviento 2026 empiezan el domingo 29 de noviembre. Fechas de cada vela, bendición de la corona, oraciones, Evangelio diario y reto.", adv, "", [crumbs_ld([("Inicio", "index.html"), ("Adviento 2026", "adviento.html")]), faq_ld(adv_faq)])

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

r = ""
hub_faq = [("¿Qué versículo leer hoy?", "Cada día proponemos un versículo del día. Si buscas algo concreto, toca cómo te sientes en «Necesito un versículo ahora»."),
 ("¿Qué traducción de la Biblia usáis?", "Citamos los versículos en español siguiendo la Biblia de la Conferencia Episcopal Española. Te recomendamos leer siempre el pasaje completo en tu Biblia."),
 ("¿Puedo compartir los versículos?", "Sí. Pulsa «Crear imagen» y te preparamos una imagen vertical para WhatsApp, Instagram Stories, TikTok o Pinterest.")]
hub = phero(r, [("Inicio", "index.html"), ("Versículos", "versiculos.html")], f"{len(VALL)} versículos para cada momento", "Versículos de la Biblia para cada momento",
 "El versículo del día y versículos para la ansiedad, para dormir, para cuando estás triste, sobre el amor o para dar gracias. Léelos, escúchalos y compártelos.") + \
 sec(f'<div class="vhub">{vday_card(r)}{mood_picker(r)}</div>') + sec(head2("Por situación", "Versículos para lo que estás viviendo") + vtiles(r), "sec band") + sec(head2("Preguntas frecuentes", "Sobre los versículos") + faq_html(hub_faq))
page("versiculos.html", "Versículo del día y versículos de la Biblia para cada momento | Rezo Diario", "Versículo del día y versículos de la Biblia para la ansiedad, para dormir, para cuando estás triste, sobre el amor, la familia o el dinero. Escúchalos y compártelos.",
 hub, "verses", [crumbs_ld([("Inicio", "index.html"), ("Versículos", "versiculos.html")]), faq_ld(hub_faq), {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Versículos de la Biblia para cada momento", "url": canon("versiculos.html"), "inLanguage": "es"}], js=("versos.js",))
for t in VTOP:
    path = t["slug"] + ".html"; cr = [("Inicio", "index.html"), ("Versículos", "versiculos.html"), (t["t"], path)]
    pr = PBY.get(t["prayer"]); faq = [(f["q"], f["a"]) for f in t["faq"]]
    cards = "".join(f'<article class="vcard reveal" id="v{i + 1}" data-ref="{E(v["ref"])}" data-x="{E(v["x"])}" data-tag="{E(t["t"])}"><span class="vnum">{i + 1}</span>'
                    f'<blockquote>«{E(v["x"])}»</blockquote><cite>{E(v["ref"])}</cite><p class="vqs"><b>Qué significa:</b> {E(v["e"])}</p>{vacts(v["ref"], v["x"], path + "#v" + str(i + 1))}</article>' for i, v in enumerate(t["versos"]))
    rel = [VBY[x] for x in t["rel"] if x in VBY]
    prbtn = f'<a class="btn btn-accent sm" href="oraciones/{pr["slug"]}.html">Rezar: {E(pr["t"])}</a> ' if pr else ""
    rel_html = "".join(f'<li><a href="{x["slug"]}.html">{E(x["t"])}<small>{len(x["versos"])}</small></a></li>' for x in rel)
    _ip = t["intro"].split("\n\n")
    m = phero(r, cr, f'{len(t["versos"])} versículos', t["h1"], E(_ip[0]),
      '<div class="hero-cta" style="margin-top:18px"><a class="btn btn-gold" href="versiculos.html#ahora">Necesito un versículo ahora</a></div>') + \
      ('<section class="sec"><div class="wrap art"><div style="min-width:0">'
       + "".join(f'<p class="vintro">{E(x)}</p>' for x in _ip[1:]) +
       f'<div class="vlist">{cards}</div>'
       f'<div class="box vpray reveal"><span class="eyebrow">Oración</span><h2>Reza con estos versículos</h2><p class="pray-text">{E(t["oracion"])}</p><div class="hero-cta">{prbtn}<a class="btn btn-ghost sm" href="muro-de-intenciones.html">Encender una vela</a></div></div>'
       f'<div class="prose" style="margin-top:34px"><h2>Preguntas frecuentes</h2>{faq_html(faq)}</div>{recorrido(r)}</div>'
       f'<aside class="side"><div class="box"><h3>Versículos relacionados</h3><ul class="links">{rel_html}</ul></div>'
       '<div class="box candle-cta"><h3>¿Rezamos contigo?</h3><p>Deja tu intención en el muro y otras personas rezarán por ti durante siete días.</p><a class="btn btn-flame sm" href="muro-de-intenciones.html">Encender una vela</a></div>'
       f'<div class="box"><h3>Rezo de hoy</h3><p style="margin:0 0 12px;color:var(--muted);font-size:14.5px">{E(TW["title"])} · {TW["ref"]}</p><a class="btn btn-accent sm" href="evangelio-de-hoy.html">Escuchar el rezo</a></div></aside>'
       '</div></section>') + sec(head2("Más versículos", "Para otros momentos") + vtiles(r, t["slug"]), "sec band")
    d = f'{len(t["versos"])} {t["t"].lower()}: {t["versos"][0]["ref"]}, {t["versos"][1]["ref"]} y más, con explicación, oración y audio para escuchar y compartir.'
    page(path, f'{t["h1"]} ({len(t["versos"])} citas) | Rezo Diario', d[:160], m, "verses",
     [crumbs_ld(cr), faq_ld(faq), {"@context": "https://schema.org", "@type": "Article", "headline": t["h1"], "description": d[:160], "inLanguage": "es", "author": ORG, "publisher": ORG, "datePublished": "2026-10-17", "dateModified": TODAY, "mainEntityOfPage": canon(path), "image": SITE + "og-rezodiario.jpg"},
      {"@context": "https://schema.org", "@type": "ItemList", "name": t["h1"], "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": v["ref"], "url": canon(path) + f"#v{i + 1}"} for i, v in enumerate(t["versos"])]}],
     body_attrs=f' data-vtopic="{t["slug"]}"', og_type="article")

# ================= CAMINO DE SANTIAGO Y AÑO SANTO 2027 =================
CAM_PR = ["bendicion-del-peregrino", "oracion-del-peregrino", "oracion-al-llegar-a-santiago", "oracion-al-apostol-santiago"]
def cam_count(r): return f'<div class="cam-cd reveal" data-countdown="2026-12-31T17:00:00+01:00"><div class="cam-shell" aria-hidden="true">{CONCHA}</div><div><small>Apertura de la Puerta Santa · 31 de diciembre de 2026</small><b data-cd-txt>Faltan pocos días</b><span data-cd-sub>Comienza el Año Santo Compostelano 2027</span></div><div class="cam-cdn" data-cd-n aria-hidden="true"></div></div>'
CONCHA = '<svg viewBox="0 0 64 64" width="44" height="44" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M32 56 8 26c4-10 13-16 24-16s20 6 24 16Z"/><path d="M32 56 20 13M32 56l-4-45M32 56l4-45M32 56l12-43M32 56 12 19M32 56l20-37"/><path d="M26 56h12"/></svg>'
r = ""
cam_faq = [("¿Cuándo es el próximo Año Santo Xacobeo?", "En 2027. Hay Año Santo Compostelano cada vez que el 25 de julio, fiesta de Santiago Apóstol, cae en domingo. Empieza con la apertura de la Puerta Santa el 31 de diciembre de 2026 y dura todo 2027."),
 ("¿Cuándo se abre la Puerta Santa de Santiago?", "El 31 de diciembre de 2026, por la tarde, en una celebración solemne en la Catedral de Santiago. La hora exacta la confirma la Catedral; se ha anunciado a las 17:00."),
 ("¿Hay que hacer el Camino para ganar el Jubileo?", "No. Para ganar el Jubileo basta con visitar la Catedral de Santiago durante el Año Santo, rezar, confesarse y comulgar. Hacer el Camino a pie no es obligatorio, aunque es la forma tradicional de peregrinar."),
 ("¿Cuántos kilómetros hay que hacer para la Compostela?", "Al menos los últimos 100 km a pie o a caballo, o 200 km en bicicleta, con dos sellos al día en la credencial durante ese tramo. La Compostela se recoge en la Oficina del Peregrino, en Santiago."),
 ("¿Y si no puedo peregrinar?", "Puedes acompañar el Año Santo desde casa: reza cada día por los peregrinos, ofrece tus oraciones por alguien que haga el Camino y reza al apóstol Santiago. Pronto podrás hacer en Rezo Diario un Camino virtual que avanza con cada día que rezas.")]
fechas = [("31 dic 2026", "Apertura de la Puerta Santa", "Comienza el Año Santo"), ("21–28 mar 2027", "Semana Santa", "En pleno Año Santo"), ("15–18 jul 2027", "Peregrinación Europea de Jóvenes", "Miles de jóvenes en Santiago"), ("25 jul 2027", "Santiago Apóstol", "La gran fiesta del Año Santo"), ("31 dic 2027", "Cierre de la Puerta Santa", "Termina el Año Santo")]
fechas_html = '<ol class="cam-dates">' + "".join(f'<li class="reveal"><small>{d}</small><b>{E(t)}</b><span>{E(x)}</span></li>' for d, t, x in fechas) + '</ol>'
cam_or = '<div class="grid">' + "".join(card(PBY[s], r) for s in CAM_PR if s in PBY) + '</div>'
cam = phero(r, [("Inicio", "index.html"), ("Camino de Santiago", "camino-de-santiago.html")], "Xacobeo · Año Santo Compostelano 2027", "Camino de Santiago y Año Santo 2027", "Reza el Camino: el Jubileo explicado paso a paso, las oraciones del peregrino y todo lo que necesitas para vivir el Año Santo con fe, peregrines a Compostela o lo acompañes desde casa.", cam_count(r)) + \
 sec(head2("Año Santo 2027", "Un año de gracia en Compostela", "Cuando el 25 de julio cae en domingo, la Iglesia celebra en Santiago un Año Santo: un año jubilar en el que todo el que visita la tumba del Apóstol puede ganar el Jubileo.") +
  '<div class="duo">' + f'<a class="feature reveal" href="camino-de-santiago/ano-santo-2027.html" style="background:linear-gradient(150deg,#A8812D,#4A3510)"><small>Paso a paso</small><b>Cómo ganar el Jubileo</b><p>Qué es la indulgencia plenaria del Año Santo y qué hace falta: visita, oración, confesión y comunión.</p></a><a class="feature reveal" href="santos/santiago-apostol.html" style="background:linear-gradient(150deg,#2E5C8A,#132A42)"><small>25 de julio</small><b>Santiago Apóstol</b><p>Quién fue el «hijo del trueno», por qué sus restos están en Compostela y por qué es patrón de España.</p></a></div>') + \
 sec(head2("Fechas clave", "El Año Santo en el calendario") + fechas_html, "sec band") + \
 sec(head2("Para rezar", "Oraciones del peregrino", "Para antes de salir, para cada etapa y para el momento de llegar ante el Apóstol.") + cam_or) + \
 sec('<div class="cam-soon reveal"><div class="cam-shell" aria-hidden="true">' + CONCHA + '</div><div><span class="eyebrow">Muy pronto</span><h2>Tu Camino virtual a Santiago</h2><p>Cada día que reces avanzarás kilómetros en el Camino desde Sarria. Llega a Santiago rezando, desbloquea cada etapa y consigue tu recuerdo de peregrinación. Perfecto si este año no puedes caminar.</p><a class="btn btn-gold sm" href="perfil.html">Ver mi perfil</a></div></div>', "sec band") + \
 sec(head2("Preguntas frecuentes", "Sobre el Año Santo y el Camino") + faq_html(cam_faq) + '<p class="hint" style="margin-top:22px">Información práctica oficial: <a href="https://catedraldesantiago.es/" rel="noopener" target="_blank">Catedral de Santiago</a> · Oficina del Peregrino (rúa Carretas, 33, Santiago).</p>')
page("camino-de-santiago.html", "Camino de Santiago y Año Santo 2027: Jubileo y oraciones | Rezo Diario", "Año Santo Xacobeo 2027: la Puerta Santa se abre el 31 de diciembre de 2026. Cómo ganar el Jubileo, fechas clave y oraciones del peregrino del Camino de Santiago.", cam, "", [crumbs_ld([("Inicio", "index.html"), ("Camino de Santiago", "camino-de-santiago.html")]), faq_ld(cam_faq)], og=("Año Santo 2027", "Camino de Santiago y Año Santo", "Jubileo · oraciones del peregrino"))

r = "../"
jub_faq = [("¿Qué es el Jubileo del Año Santo Compostelano?", "Es la gracia de la indulgencia plenaria que la Iglesia concede durante el Año Santo a quienes visitan la tumba del apóstol Santiago con las debidas disposiciones. La indulgencia perdona la pena que queda por los pecados ya perdonados en la confesión."),
 ("¿Qué hay que hacer para ganar el Jubileo en 2027?", "Visitar la Catedral de Santiago durante el Año Santo; rezar allí, por ejemplo el Credo y el Padre Nuestro, y pedir por las intenciones del Papa; confesarse y comulgar. La confesión y la comunión pueden hacerse unos días antes o después de la visita: habitualmente se indican hasta 15 días."),
 ("¿Es obligatorio pasar por la Puerta Santa?", "No es imprescindible, aunque es un gesto muy significativo y lo hacen casi todos los peregrinos. Lo necesario es la visita a la Catedral con oración, confesión y comunión."),
 ("¿Hay que llegar caminando?", "No. El Jubileo puede ganarse visitando la Catedral aunque se llegue en coche, en tren o en avión. Caminar es la forma tradicional de peregrinar y la que da derecho a la Compostela, pero no es una condición del Jubileo."),
 ("¿Puedo ganar el Jubileo por un difunto?", "Sí. La Iglesia permite ofrecer la indulgencia plenaria por un difunto. Muchas personas peregrinan a Santiago ofreciendo el Jubileo por un ser querido que ha fallecido."),
 ("¿Cuántas veces se puede ganar?", "La indulgencia plenaria se puede ganar una vez al día, cumpliendo cada vez las condiciones. Una misma confesión puede servir para varias indulgencias en esos días."),
 ("¿Qué diferencia hay entre el Jubileo y la Compostela?", "El Jubileo es una gracia espiritual que se recibe con la visita, la oración y los sacramentos. La Compostela es el documento que entrega la Oficina del Peregrino a quien ha hecho al menos los últimos 100 km a pie (o 200 km en bicicleta) por motivos religiosos o espirituales.")]
pasos = [("1", "Visita la Catedral", "Durante el Año Santo, del 31 de diciembre de 2026 al 31 de diciembre de 2027. Es tradición entrar por la Puerta Santa, abrazar la imagen del Apóstol y rezar ante su sepulcro."),
 ("2", "Reza", "Allí, reza con calma: el Credo, el Padre Nuestro y una oración por las intenciones del Papa. Si puedes, participa en la Misa del Peregrino."),
 ("3", "Confiésate", "Unos días antes o después de la visita. Si hace tiempo que no te confiesas, prepárate con un examen de conciencia sencillo."),
 ("4", "Comulga", "En la misa, el mismo día de la visita o en los días cercanos, con el deseo sincero de cambiar de vida.")]
pasos_html = '<ol class="cam-steps">' + "".join(f'<li class="reveal"><span>{n}</span><div><b>{E(t)}</b><p>{E(x)}</p></div></li>' for n, t, x in pasos) + '</ol>'
jub = phero(r, [("Inicio", "index.html"), ("Camino de Santiago", "camino-de-santiago.html"), ("Año Santo 2027", "camino-de-santiago/ano-santo-2027.html")], "31 de diciembre de 2026 – 31 de diciembre de 2027", "Año Santo 2027: cómo ganar el Jubileo paso a paso", "Qué es el Año Santo Compostelano, cuándo empieza y qué hace falta para ganar la indulgencia plenaria al visitar la tumba del apóstol Santiago.", cam_count(r)) + \
 f'''<section class="sec"><div class="wrap art"><div style="min-width:0"><div class="prose">
  <div class="dato reveal"><small>Lo esencial</small><b>Para ganar el Jubileo: visita la Catedral de Santiago en 2027, reza por las intenciones del Papa, confiésate y comulga.</b><span>No es obligatorio llegar caminando ni pasar por la Puerta Santa, aunque son gestos tradicionales del peregrino.</span></div>
  <h2>Los cuatro pasos del Jubileo</h2>{pasos_html}
  <h2>¿Qué es el Año Santo Compostelano?</h2>
  <p>Es un año de gracia que la Iglesia celebra en Santiago de Compostela cada vez que el 25 de julio, fiesta del apóstol Santiago, cae en domingo. Eso ocurre con un ritmo de 6, 5, 6 y 11 años; el de 2027 es el primero desde el Año Santo 2021-2022, que se alargó dos años por la pandemia.</p>
  <p>La tradición sitúa su origen en el siglo XII, cuando los papas concedieron a la Iglesia de Compostela el privilegio del jubileo, equiparando la peregrinación a Santiago con las de Roma y Jerusalén. Desde entonces, millones de peregrinos han llegado a la tumba del Apóstol buscando perdón, sentido y un nuevo comienzo.</p>
  <h2>La Puerta Santa</h2>
  <p>La Puerta Santa de la Catedral, en la plaza de la Quintana, solo se abre en los Años Santos. El arzobispo la abre el 31 de diciembre anterior, la tarde del último día del año, y se cierra el 31 de diciembre siguiente. Pasar por ella simboliza dejar atrás el pecado y entrar en la misericordia de Dios a través de Cristo, que dijo: «Yo soy la puerta».</p>
  <h2>Si no puedes ir a Santiago</h2>
  <p>El Jubileo compostelano está unido a la visita a la Catedral. Pero el Año Santo también se vive desde casa: rezando por los peregrinos, ofreciendo tus oraciones por alguien que haga el Camino o preparándote para ir más adelante. Lo importante es el corazón que se pone en camino.</p>
  <h2>Preguntas frecuentes</h2>{faq_html(jub_faq)}
  <p class="hint">Las condiciones concretas y los horarios los publica la Archidiócesis de Santiago al comenzar el Año Santo. Información oficial: <a href="https://catedraldesantiago.es/" rel="noopener" target="_blank">Catedral de Santiago</a> · Oficina del Peregrino (rúa Carretas, 33, Santiago).</p>
 </div></div>
 <aside class="side">
  {exam_box(r, "Prepara tu confesión", "El Jubileo pide confesarse. Prepárala con un examen de conciencia sencillo y sin miedo.")}
  <div class="box"><h3>Oraciones del peregrino</h3><ul class="links">{"".join(f'<li><a href="../oraciones/{s}.html">{E(PBY[s]["t"])}<small>{PBY[s]["min"]} min</small></a></li>' for s in CAM_PR if s in PBY)}</ul></div>
  <div class="box"><h3>Camino de Santiago</h3><p style="margin:0 0 12px;color:var(--muted);font-size:14.5px">Fechas clave del Año Santo, oraciones y tu Camino virtual.</p><a class="btn btn-accent sm" href="../camino-de-santiago.html">Ver todo</a></div>
 </aside></div></section>'''
page("camino-de-santiago/ano-santo-2027.html", "Año Santo 2027: cómo ganar el Jubileo paso a paso | Rezo Diario", "Año Santo Compostelano 2027: qué es, cuándo se abre la Puerta Santa (31 de diciembre de 2026) y cómo ganar el Jubileo: visita, oración, confesión y comunión.", jub, "", [crumbs_ld([("Inicio", "index.html"), ("Camino de Santiago", "camino-de-santiago.html"), ("Año Santo 2027", "camino-de-santiago/ano-santo-2027.html")]), faq_ld(jub_faq), {"@context": "https://schema.org", "@type": "Article", "headline": "Año Santo 2027: cómo ganar el Jubileo paso a paso", "inLanguage": "es", "author": ORG, "publisher": ORG, "datePublished": "2026-10-25", "dateModified": TODAY, "mainEntityOfPage": canon("camino-de-santiago/ano-santo-2027.html")}], og_type="article", og=("Año Santo 2027", "Cómo ganar el Jubileo", "Paso a paso"))

# ================= MURO DE VELAS =================
r = ""
muro_faq = [("¿Cuánto tiempo arde una vela?", "Siete días. Cada día la vela se consume un poco, hasta apagarse."), ("¿Quién puede ver mi intención?", "Si es pública, cualquiera que visite el muro. Si marcas «privada», solo se ve la vela encendida, nunca el texto."), ("¿Puedo encender una vela por un difunto?", "Sí. Elige «Difuntos» y escribe su nombre de pila. Muchas personas rezarán por su descanso."), ("¿Qué pasa si veo una intención ofensiva?", "Pulsa «Avisar». Cuando una vela recibe varios avisos se oculta automáticamente y se revisa.")]
page("muro-de-intenciones.html", "Muro de intenciones: enciende una vela virtual | Rezo Diario", "Enciende una vela virtual por tu intención: por un enfermo, por un difunto, por tu familia o por un examen. Arde siete días y otras personas rezan por ti.",
 f'<div class="chapel" style="padding-top:20px"><div class="wrap">{crumbs_html(r, [("Inicio", "index.html"), ("Muro de intenciones", "muro-de-intenciones.html")])}</div></div>' + chapel(r, True) + sec(head2("Preguntas frecuentes", "Sobre el muro de velas") + faq_html(muro_faq)), "candles", [crumbs_ld([("Inicio", "index.html"), ("Muro de intenciones", "muro-de-intenciones.html")]), faq_ld(muro_faq)])

# ================= WIDGET =================
wcode = f'<div id="rezodiario-evangelio"><a href="{canon("evangelio-de-hoy.html")}">Evangelio de hoy en Rezo Diario</a></div>\n<script src="{SITE}widget/evangelio.js" async></script>'
wid = phero(r, [("Inicio", "index.html"), ("Widget para parroquias", "widget.html")], "Gratis para parroquias, colegios y blogs", "Pon el Evangelio del día en tu web", "Un recuadro que se actualiza solo cada día con el Evangelio, una frase y un enlace al audio. Copia el código y pégalo en tu web: no necesitas saber programar.") + \
 sec(f'''<div class="art"><div style="min-width:0"><h2>Así se verá</h2><div id="wPreview" style="margin:16px 0 28px"></div>
 <h2>Código para copiar</h2><p style="color:var(--muted)">Pégalo en tu página donde quieras que aparezca (en WordPress, en un bloque «HTML personalizado»).</p>
 <pre class="tablewrap" style="padding:16px;white-space:pre-wrap;word-break:break-all;font-size:13px" id="wCode">{E(wcode)}</pre>
 <div class="hero-cta"><button class="btn btn-accent sm" id="wCopy">Copiar código</button><button class="btn btn-ghost sm" id="wDark" aria-pressed="false">Versión oscura</button></div></div>
 <aside class="side"><div class="box"><h3>Qué incluye</h3><ul class="links"><li><a>Evangelio y frase del día</a></li><li><a>Color litúrgico</a></li><li><a>Enlace al audio y la reflexión</a></li><li><a>Se adapta al ancho de tu web</a></li></ul></div></aside></div>''')
page("widget.html", "Widget del Evangelio del día para tu web o parroquia | Rezo Diario", "Pon gratis el Evangelio del día en la web de tu parroquia, colegio o blog. Se actualiza solo cada día. Copia y pega el código.", wid, "", [crumbs_ld([("Inicio", "index.html"), ("Widget para parroquias", "widget.html")])])

# ================= PERFIL Y ESTADÍSTICAS =================
r = ""
pf = f'''<section class="pf-hero"><div class="wrap"><div class="pf-top" id="perfil">
  <span class="pf-av" id="pfAv"><i>✝</i></span>
  <div class="pf-id"><span class="eyebrow" id="pfEye">Tu camino de oración</span><h1 id="pfName">Mi perfil</h1><p id="pfSub">Tus estadísticas se guardan en este dispositivo.</p><button class="pf-share" id="pfShare" type="button"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7"/><path d="M16 6l-4-4-4 4"/><path d="M12 2v13"/></svg>Compartir mi racha</button></div>
  <div class="pf-cta" id="pfCta"><button class="btn btn-gold" id="pfJoin" type="button">Crear cuenta gratis</button><small>Para no perder tu racha y verla en todos tus dispositivos</small></div>
 </div>
 <div class="pf-tiles" id="pfTiles"></div></div></section>
<section class="sec pf"><div class="wrap">
 <div class="pf-grid">
  <div class="pf-card pf-wide"><div class="pf-h"><h2>Tu año de oración</h2><span class="hint" id="pfHeatN"></span></div><div class="pf-heat" id="pfHeat"></div><div class="pf-leg"><span>Menos</span><i></i><i class="l1"></i><i class="l2"></i><span>Más</span></div></div>
  <div class="pf-card"><div class="pf-h"><h2>Meta semanal</h2><span class="hint" id="pfMetaN"></span></div><div class="pf-meta" id="pfMeta"></div></div>
  <div class="pf-card" id="pfMesCard"><div class="pf-h"><h2 id="pfMesT">Tu mes</h2></div><div id="pfMes"></div></div>
  <div class="pf-card pf-wide" id="pfInt"><div class="pf-h"><h2>Mis intenciones</h2><span class="hint" id="pfIntN"></span></div>
   <p class="pf-empty" style="margin-top:-6px">Apunta por qué o por quién rezas. Cuando sientas que Dios te ha respondido, márcala como respondida y quedará guardada con su fecha.</p>
   <form class="pf-intf" id="pfIntF"><input id="pfIntIn" maxlength="140" placeholder="Por ejemplo: por la salud de mi madre" autocomplete="off"><button class="btn btn-accent sm" type="submit">Añadir</button></form>
   <div class="pf-tabs" role="tablist"><button type="button" class="on" data-int="abiertas">Rezando por ellas</button><button type="button" data-int="respondidas">Respondidas</button></div>
   <ul class="pf-ints" id="pfInts"></ul></div>
  <div class="pf-card"><div class="pf-h"><h2>Cuándo rezas</h2></div><div class="pf-wd" id="pfWd"></div></div>
  <div class="pf-card"><div class="pf-h"><h2>Cómo rezas</h2></div><div class="pf-act" id="pfAct"></div></div>
  <div class="pf-card pf-wide"><div class="pf-h"><h2>Logros</h2><span class="hint" id="pfBadgeN"></span></div><div class="pf-badges" id="pfBadges"></div></div>
  <div class="pf-card"><div class="pf-h"><h2>Tus novenas</h2></div><div id="pfNov"></div></div>
  <div class="pf-card"><div class="pf-h"><h2>Oraciones guardadas</h2></div><div id="pfFavs"></div></div>
  <div class="pf-card pf-wide"><div class="pf-h"><h2>Tu diario del Evangelio</h2><a class="hint" href="evangelio-de-hoy.html">Escribir hoy ›</a></div><div id="pfDiario"></div></div>
  <div class="pf-card pf-wide" id="pfSet"><div class="pf-h"><h2>Ajustes</h2></div>
   <div class="pf-rows">
    <label class="pf-row"><span><b>¿Cómo quieres que te llamemos?</b><small>Solo se muestra en tu perfil</small></span><input id="pfNameIn" maxlength="40" placeholder="Tu nombre" autocomplete="given-name"></label>
    <div class="pf-row" id="pfMailRow"><span><b>El Evangelio cada mañana en tu correo</b><small id="pfMailTxt">Gratis. Puedes darte de baja cuando quieras.</small></span><button class="btn btn-ghost sm" id="pfMail" type="button">Apuntarme</button></div>
    <div class="pf-row"><span><b>Tema de la web</b><small>Oscuro o claro</small></span><button class="btn btn-ghost sm" id="pfTheme" type="button">Cambiar</button></div>
    <div class="pf-row" id="pfOutRow" hidden><span><b>Sesión</b><small id="pfMailMe"></small></span><button class="btn btn-ghost sm" id="pfOut" type="button">Cerrar sesión</button></div>
   </div></div>
 </div></div></section>'''
page("perfil.html", "Mi perfil y estadísticas de oración | Rezo Diario", "Tu racha de oración, tus días rezados, logros, novenas, oraciones guardadas y tu diario del Evangelio.", pf, "", robots="noindex, follow")

# ================= DONAR, SOBRE, LEGAL =================
don_faq = [("¿Es seguro donar?", "Sí. El pago se hace en la página segura de Stripe, una de las pasarelas más usadas del mundo. Rezo Diario nunca ve ni guarda los datos de tu tarjeta."), ("¿Puedo cancelar el apoyo mensual?", "Sí, cuando quieras y sin dar explicaciones. Desde el enlace del correo de Stripe o escribiéndonos."), ("¿Mi donativo desgrava?", "No. Rezo Diario es un proyecto personal, no una entidad acogida a la Ley 49/2002, así que las aportaciones no dan derecho a deducción fiscal."), ("¿A qué se destina el dinero?", "A mantener la web, los servidores, los audios del rezo diario y a preparar nuevos contenidos.")]
page("donar.html", "Donar a Rezo Diario | Rezo Diario", "Ayuda a mantener Rezo Diario gratis y sin anuncios: con tu donativo publicamos audios nuevos cada día y traducimos las oraciones a otros idiomas.",
 phero(r, [("Inicio", "index.html"), ("Donar", "donar.html")], "Donaciones", "Gracias por sostener Rezo Diario", "Rezo Diario es gratis para todos. Tu aportación paga los audios, la música y los servidores.") + donate_section("h2") + sec(head2("Preguntas", "Sobre las donaciones") + faq_html(don_faq)), "", [crumbs_ld([("Inicio", "index.html"), ("Donar", "donar.html")]), faq_ld(don_faq)])
sys.path.insert(0, C); import legal as LEG
page("sobre-nosotros.html", "Quiénes somos | Rezo Diario", "Rezo Diario es una web gratuita de oración católica hecha en España: el Evangelio de cada día, el Rosario, oraciones y un muro de velas. Esta es nuestra historia.",
 phero(r, [("Inicio", "index.html"), ("Quiénes somos", "sobre-nosotros.html")], "Quiénes somos", "Un rincón tranquilo para rezar cada día", "Rezo Diario es una web gratuita de oración católica, hecha en España con mucho cariño, para que nadie tenga que rezar solo.") +
 sec(LEG.quienes(AJ, len(PRAYERS))), "", [crumbs_ld([("Inicio", "index.html"), ("Quiénes somos", "sobre-nosotros.html")]), {"@context": "https://schema.org", "@type": "AboutPage", "name": "Quiénes somos", "url": canon("sobre-nosotros.html"), "inLanguage": "es", "publisher": ORG}])
r = "../"
for k, (t, lead, x) in LEG.legal(AJ).items():
    page(f"legal/{k}.html", f"{t} | Rezo Diario", f"{t} de Rezo Diario: {lead}", phero(r, [("Inicio", "index.html"), (t, f"legal/{k}.html")], "Información legal", t, lead) + sec(f'<div class="prose legal">{x}</div>'), "", robots="noindex, follow")
for _f in ("titular", "nif", "domicilio"):
    pass
page("404.html", "Página no encontrada | Rezo Diario", "La página que buscas no existe.", phero("", [("Inicio", "index.html")], "Error 404", "No hemos encontrado esta página", "Puede que haya cambiado de dirección. Prueba con el rezo de hoy o busca una oración.", '<div class="hero-cta" style="margin-top:18px"><a class="btn btn-gold" href="/">Ir al rezo de hoy</a><a class="btn btn-ghost" href="/oraciones/index.html">Buscar una oración</a></div>'), "", robots="noindex")

# ================= SALIDA =================
if os.path.exists(OUT): shutil.rmtree(OUT)
shutil.copytree(os.path.join(ROOT, "static"), OUT)
os.makedirs(OUT + "/assets", exist_ok=True)
css = open(ROOT + "/assets/base.css", encoding="utf-8").read() + open(ROOT + "/assets/extra.css", encoding="utf-8").read()
def solo_raton(css):
    """En móvil, los efectos :hover se quedan «pegados» al deslizar el dedo. Los envolvemos en @media (hover:hover)
    para que solo existan con ratón; en el móvil un botón solo cambia al pulsarlo."""
    out, i, depth, start = [], 0, 0, 0
    while i < len(css):
        ch = css[i]
        if ch == "{":
            if depth == 0: sel_start = start
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                block = css[start:i + 1]; sel = block.split("{", 1)[0]
                if ":hover" in sel and not sel.strip().startswith("@"):
                    parts = [x for x in sel.split(",")]; hov = [x for x in parts if ":hover" in x]; rest = [x for x in parts if ":hover" not in x]
                    body = block.split("{", 1)[1]
                    block = (",".join(rest) + "{" + body if rest else "") + "@media (hover:hover){" + ",".join(hov) + "{" + body + "}"
                out.append(block); start = i + 1
        elif depth == 0 and ch == ";" :
            out.append(css[start:i + 1]); start = i + 1
        i += 1
    out.append(css[start:])
    return "".join(out)
css = solo_raton(css) + "\n*{-webkit-tap-highlight-color:transparent}\n"
open(OUT + "/assets/site.css", "w", encoding="utf-8").write(css)
shutil.copy(ROOT + "/assets/site.js", OUT + "/assets/site.js")
def dia_js(w): return {k: w[k] for k in ("date", "wd", "n", "mes", "color", "lit", "ref", "refL", "title", "set", "ex", "sum", "refl", "qs", "fin", "audio", "duracion")} | ({"marcas": w["marcas"]} if w.get("marcas") else {}) | ({"audioVoz": w["audioVoz"]} if w.get("audioVoz") else {})
os.makedirs(OUT + "/assets/dias", exist_ok=True)
for w in DAYS:
    open(f'{OUT}/assets/dias/{w["date"]}.js', "w", encoding="utf-8").write("(function(D){var W=(window.RD=window.RD||{}).week=window.RD.week||[];if(!W.some(function(x){return x.date===D.date})){W.push(D);W.sort(function(a,b){return a.date<b.date?-1:1})}})(" + json.dumps(dia_js(w), ensure_ascii=False) + ");")
data = {"week": [dia_js(w) for w in DAYS[WLO:WHI]], "LITC": LITC, "SETS": SETS, **O, "via": VIA, "VIA_ANT": VIAJ["antifona"],
        "prayers": [{"slug": p["slug"], "t": p["t"], "cat": p["cat"], "min": p["min"], **({"a": p["audio"]} if p.get("audio") else {})} for p in PRAYERS], "VOZROS": (json.load(open(os.path.join(C, "voces-rosario.json"), encoding="utf-8")) if os.path.exists(os.path.join(C, "voces-rosario.json")) else {}), "CATS": {k: {"name": c["name"], "color": c["color"]} for k, c in CATS.items()},
        "novenas": [{"slug": n["slug"], "t": n["t"], "start": n["start"], "end": n["end"], "open": n["open"], "close": n["close"], "days": [[d["t"], d["x"]] for d in n["days"]]} for n in NOVENAS]}
open(OUT + "/assets/oraciones.js", "w", encoding="utf-8").write("window.RDO=" + json.dumps({p["slug"]: p["x"] for p in PRAYERS}, ensure_ascii=False) + ";")
open(OUT + "/assets/versos.js", "w", encoding="utf-8").write("window.RDV=" + json.dumps({t["slug"]: {"t": t["t"], "v": [[v["ref"], v["x"], v["e"]] for v in t["versos"]]} for t in VTOP}, ensure_ascii=False) + ";")
open(OUT + "/assets/data.js", "w", encoding="utf-8").write("window.RD=" + json.dumps(data, ensure_ascii=False) + ";")
for path, head, body, battrs in pages:
    full = f'<!doctype html>\n<html lang="es" data-theme="dark">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body{battrs}>\n{body}\n</body>\n</html>\n'
    if CLEAN:
        full = re.sub(r'href="([^"#:?]*?)index\.html', lambda m: f'href="{m.group(1) or "./"}', full)
        full = re.sub(r'href="([^"#:?]+?)\.html', r'href="\1', full)
        full = full.replace('"evangelio/"+d.date+".html"', '"evangelio/"+d.date')
    os.makedirs(os.path.dirname(OUT + "/" + path) or OUT, exist_ok=True); open(OUT + "/" + path, "w", encoding="utf-8").write(full)
    if path == "index.html": open(ROOT + "/.preview-index.html", "w", encoding="utf-8").write(head.replace(E("Rezo Diario · Oración diaria, Evangelio de hoy, Rosario y velas"), "Rezo Diario", 1) + "\n" + body)
# API del widget: un JSON por día
os.makedirs(OUT + "/api/evangelio", exist_ok=True)
for w in DAYS:
    json.dump({"fecha": w["date"], "dia": f'{w["wd"]} {w["n"]} de {w["mes"]}', "liturgia": w["lit"], "color": w["color"], "cita": w["refL"], "titulo": w["title"], "frase": w["ex"], "url": canon(f'evangelio/{w["date"]}.html')}, open(f'{OUT}/api/evangelio/{w["date"]}.json', "w", encoding="utf-8"), ensure_ascii=False)
# Correo diario (boletín): un HTML por día que envía /api/enviar-diario
def correo_html(w):
    st = SBY.get(w["saint"]) if w.get("saint") else None
    url = canon(f'evangelio/{w["date"]}.html') + "?utm_source=boletin&utm_medium=email"
    qs = "".join(f'<li style="margin:0 0 6px">{E(q)}</li>' for q in w["qs"])
    santo = ""
    if st:
        santo = (f'<tr><td style="padding:6px 32px 22px"><div style="border-top:1px solid #DCE3DA;padding-top:18px;font-size:13px;letter-spacing:1.5px;text-transform:uppercase;color:#7B8A80">Santo del día</div>'
                 f'<p style="margin:6px 0 0;font-size:16px;line-height:1.55;color:#17211C"><a href="{canon("santos/" + st["slug"] + ".html")}" style="color:#1F5A47;font-weight:bold;text-decoration:none">{E(st["name"])}</a> · {E(st["short"])}</p></td></tr>')
    dur = f' · {w["duracion"]}' if w.get("duracion") else ""
    fecha = f'{w["wd"][:1].upper()}{w["wd"][1:]} {w["n"]} de {w["mes"]}'
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light only"><title>{E(w["title"])}</title></head>
<body style="margin:0;padding:0;background:#ECEFEA;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;color:#17211C">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">«{E(w["ex"])}»</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ECEFEA;padding:28px 12px"><tr><td align="center">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#FAFBF8;border-radius:22px;overflow:hidden;border:1px solid #CDD6CB">
<tr><td style="background:#14302A;padding:20px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
<td><img src="https://rezodiario.com/logo-512.png" width="34" height="34" alt="" style="display:inline-block;vertical-align:middle;border:0;border-radius:9px"> <span style="vertical-align:middle;font-size:20px;letter-spacing:-.5px;color:#EEF2EC"><b style="font-weight:800">rezo</b><span style="color:#D6B266">diario</span></span></td>
<td align="right" style="font-size:13px;color:#B9C7BE">{E(fecha)}</td></tr></table></td></tr>
<tr><td style="padding:30px 32px 6px"><div style="font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#7B8A80">{E(w["lit"])}</div>
<h1 style="margin:8px 0 14px;font-family:Georgia,'Times New Roman',serif;font-weight:normal;font-size:28px;line-height:1.2;color:#17211C">{E(w["title"])}</h1>
<p style="margin:0 0 18px;font-family:Georgia,'Times New Roman',serif;font-size:19px;line-height:1.5;color:#1F5A47;font-style:italic">«{E(w["ex"])}»<br><span style="font-size:14px;font-style:normal;color:#7B8A80">{E(w["refL"])}</span></p>
<p style="margin:0 0 14px;font-size:16px;line-height:1.65;color:#3E4C43">{E(w["sum"])}</p>
<p style="margin:0 0 22px;font-size:16px;line-height:1.65;color:#3E4C43">{E(w["refl"])}</p>
<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="background:#1F5A47;border-radius:999px"><a href="{url}" style="display:inline-block;padding:14px 26px;font-size:16px;font-weight:bold;color:#FFFFFF;text-decoration:none">&#9654; Escuchar el rezo de hoy{dur}</a></td></tr></table>
</td></tr>
<tr><td style="padding:24px 32px 10px"><div style="background:#EEF2EC;border-radius:16px;padding:18px 20px"><div style="font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#7B8A80;margin-bottom:8px">Para tu oración</div>
<ol style="margin:0;padding-left:20px;font-size:16px;line-height:1.55;color:#17211C">{qs}</ol>
<p style="margin:12px 0 0;font-family:Georgia,'Times New Roman',serif;font-size:16px;line-height:1.55;color:#3E4C43;font-style:italic">{E(w["fin"])}</p></div></td></tr>
{santo}
<tr><td style="padding:4px 32px 28px;font-size:14px;line-height:1.6;color:#56645B">También hoy: <a href="https://rezodiario.com/rosario?utm_source=boletin" style="color:#1F5A47">rezar el Rosario</a> · <a href="https://rezodiario.com/muro-de-intenciones?utm_source=boletin#candles" style="color:#1F5A47">encender una vela por alguien</a></td></tr>
</table>
<p style="max-width:520px;margin:18px auto 0;font-size:12px;line-height:1.6;color:#7B8A80;text-align:center">Recibes este correo porque te apuntaste al rezo diario en rezodiario.com.<br><a href="{{{{{{RESEND_UNSUBSCRIBE_URL}}}}}}" style="color:#56645B">Darme de baja</a></p>
</td></tr></table></body></html>'''
os.makedirs(OUT + "/api/correo", exist_ok=True)
for w in DAYS:
    json.dump({"fecha": w["date"], "asunto": f'{w["title"]} · Evangelio del {w["n"]} de {w["mes"]}', "html": correo_html(w)}, open(f'{OUT}/api/correo/{w["date"]}.json', "w", encoding="utf-8"), ensure_ascii=False)
# Pódcast
items = "".join(f'''<item><title>{E(w["title"])} · {w["n"]} de {w["mes"]}</title><description>{E(w["refL"] + ". " + w["sum"])}</description><link>{canon("evangelio/" + w["date"] + ".html")}</link><guid isPermaLink="false">rezodiario-{w["date"]}</guid><pubDate>{datetime.datetime.fromisoformat(w["date"] + "T06:00:00+01:00").strftime("%a, %d %b %Y %H:%M:%S +0100")}</pubDate><enclosure url="{E(w["audio"] if w["audio"].startswith("http") else SITE + w["audio"].lstrip("/"))}" type="audio/mpeg" length="0"/>{f'<itunes:duration>{w["duracion"]}</itunes:duration>' if w.get("duracion") else ""}</item>\n''' for w in reversed(DAYS) if w.get("audio") and w["date"] <= TODAY)
pc = AJ["podcast"]
open(OUT + "/podcast.xml", "w", encoding="utf-8").write(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"><channel>
<title>{E(pc["titulo"])}</title><link>{SITE}</link><language>es</language><description>{E(pc["descripcion"])}</description>
<itunes:author>{E(pc["autor"])}</itunes:author><itunes:owner><itunes:name>{E(pc["autor"])}</itunes:name><itunes:email>{E(pc["email"])}</itunes:email></itunes:owner>
<itunes:image href="{E(pc["imagen"])}"/><itunes:category text="Religion &amp; Spirituality"><itunes:category text="Christianity"/></itunes:category><itunes:explicit>false</itunes:explicit>
{items}</channel></rss>''')
icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#14302A"/><g transform="translate(8 8) scale(1.5)"><path fill="#D9A441" d="M6.1 12.6A10 10 0 0 1 14.8 4.07V12.6Z"/><path fill="#E07A4F" d="M17.2 4.07A10 10 0 0 1 25.9 12.6H17.2Z"/><path fill="#2E8B67" d="M6 15H14.8V28H8a2 2 0 0 1-2-2Z"/><path fill="#3E72B0" d="M17.2 15H26V26a2 2 0 0 1-2 2H17.2Z"/></g></svg>'
open(OUT + "/icon.svg", "w").write(icon)
open(OUT + "/manifest.webmanifest", "w").write(json.dumps({"name": "Rezo Diario", "short_name": "Rezo Diario", "lang": "es", "start_url": "/", "display": "standalone", "background_color": "#14302A", "theme_color": "#14302A", "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"}, {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/logo-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))
open(OUT + "/sw.js", "w").write("const C='rd-v2';const PRE=['/','/assets/site.css','/assets/site.js','/assets/data.js','/rosario.html','/oraciones/index.html'];\nself.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(PRE))));\nself.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))));\nself.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request)))});\n")
json.dump(OGM, open(OUT + "/og-paginas.json", "w", encoding="utf-8"), ensure_ascii=False)
open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE}sitemap.xml\n")
daily = ("index.html", "evangelio-de-hoy.html", "evangelio-de-manana.html", "santo-de-hoy.html", "rosario.html", "muro-de-intenciones.html", "versiculos.html")
idx = [p for p, h, _, _ in pages if "noindex" not in h]
open(OUT + "/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f'  <url><loc>{canon(p)}</loc>{f"<lastmod>{TODAY}</lastmod>" if p in daily else ""}<changefreq>{"daily" if p in daily else "monthly"}</changefreq><priority>{"1.0" if p == "index.html" else "0.9" if p in daily else "0.7"}</priority></url>\n' for p in idx) + '</urlset>\n')

# ================= GUIONES ELEVENLABS =================
def guion(w):
    def br(s): return f' <break time="{s}s" /> '
    seg1 = "Busca un lugar tranquilo y ponte cómodo." + br(1.5) + "Respira despacio." + br(2) + "Inspira…" + br(2.5) + "y suelta el aire." + br(2.5) + "Estás en la presencia de Dios." + br(1.5) + "Él te mira con cariño."
    seg2 = f'Evangelio según san {w["refL"].split(" ")[0].replace("Lucas", "Lucas").replace("Mateo", "Mateo")}, capítulo {w["refL"].split(" ")[1].rstrip(",")}.' + br(1.5) + w["sum"] + br(2) + "Escucha estas palabras del Evangelio:" + br(1.5) + w["ex"]
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
