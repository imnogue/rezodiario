// Envía el correo del rezo de hoy a todos los apuntados al boletín (Resend Broadcasts).
// Lo llama cada mañana el aviso programado de GitHub (.github/workflows/correo-diario.yml).
// Es seguro llamarlo varias veces: si el correo de hoy ya salió, no hace nada.
// Variables en Cloudflare Pages: RESEND_API_KEY (obligatoria) · RESEND_FROM (opcional, p. ej. "Rezo Diario <rezo@rezodiario.com>")
import { rs, segmento, espera } from "./_resend.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const hoyMadrid = () => new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Madrid", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());

// Mete en el segmento a quien se apuntó antes de que existiera (solo hace falta una vez)
async function sincronizar(key, seg) {
  let after = "", n = 0;
  for (let vuelta = 0; vuelta < 20; vuelta++) {
    const r = await rs(key, "/contacts?limit=100" + (after ? "&after=" + after : ""));
    if (!r.ok) break;
    const j = await r.json();
    for (const c of j.data || []) {
      if (c.unsubscribed) continue;
      await rs(key, `/contacts/${encodeURIComponent(c.email)}/segments/${seg}`, { method: "POST" });
      n++; await espera(550); // Resend permite 2 peticiones por segundo
    }
    if (!j.has_more || !(j.data || []).length) break;
    after = j.data[j.data.length - 1].id;
  }
  return n;
}

export async function onRequest({ request, env }) {
  try {
    const key = String(env.RESEND_API_KEY || "").trim();
    if (!key) return J({ ok: false, error: "Falta RESEND_API_KEY en Cloudflare" }, 503);
    const url = new URL(request.url);
    const fecha = hoyMadrid();
    const nombre = "rezo-" + fecha;
    const seg = await segmento(key, env);
    let sincronizados = 0;
    if (seg.nuevo || url.searchParams.has("sincronizar")) sincronizados = await sincronizar(key, seg.id);

    // ¿Ya salió el de hoy?
    const lb = await rs(key, "/broadcasts?limit=20");
    if (lb.ok) {
      const j = await lb.json();
      if ((j.data || []).some((b) => b.name === nombre)) return J({ ok: true, fecha, enviado: false, motivo: "El correo de hoy ya se había enviado", sincronizados });
    }
    await espera(550);

    const a = await fetch(new URL(`/api/correo/${fecha}.json`, url.origin));
    if (!a.ok) return J({ ok: false, fecha, error: "No hay correo preparado para hoy (falta el rezo de este día)" }, 404);
    const c = await a.json();
    const from = String(env.RESEND_FROM || "").trim() || "Rezo Diario <rezo@rezodiario.com>";
    const b = await rs(key, "/broadcasts", {
      method: "POST",
      body: { segment_id: seg.id, name: nombre, from, reply_to: "contacto@rezodiario.com", subject: c.asunto, html: c.html, send: true },
    });
    const bj = await b.json().catch(() => ({}));
    if (!b.ok) return J({ ok: false, fecha, error: "Resend no ha aceptado el envío", detalle: `${b.status}: ${bj.message || ""}` }, 502);
    return J({ ok: true, fecha, enviado: true, id: bj.id, sincronizados });
  } catch (e) {
    return J({ ok: false, error: String(e).slice(0, 200) }, 500);
  }
}
