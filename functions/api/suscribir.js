// Alta en el boletín de Rezo Diario: guarda el correo como contacto en Resend.
// Variables en Cloudflare Pages (Settings → Variables and Secrets):
//   RESEND_API_KEY     (obligatoria, tipo Secret)
//   RESEND_SEGMENT_ID  (opcional: el segmento «Boletín» donde guardar los contactos)
import { segmento } from "./_resend.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
export async function onRequest({ request, env }) {
  try {
    if (request.method === "GET" && new URL(request.url).searchParams.has("comprobar")) {
      // Diagnóstico sin datos personales: ¿hay clave? ¿la acepta Resend? ¿puede crear contactos?
      const key = String(env.RESEND_API_KEY || "").trim();
      if (!key) return J({ clave: "falta RESEND_API_KEY en Cloudflare (o falta volver a desplegar)" });
      const d = await fetch("https://api.resend.com/domains", { headers: { authorization: "Bearer " + key } });
      const c = await fetch("https://api.resend.com/contacts?limit=1", { headers: { authorization: "Bearer " + key } });
      let cm = ""; try { cm = (await c.json()).message || ""; } catch (e) {}
      return J({ clave: "puesta (" + key.slice(0, 3) + "…)", dominios: d.status, contactos: c.status, mensaje: cm });
    }
    if (request.method !== "POST") return J({ ok: false, error: "Usa POST" }, 405);
    let body = {};
    try { body = await request.json(); } catch (e) { return J({ ok: false, error: "Petición no válida" }, 400); }
    if (body.web) return J({ ok: true }); // trampa para robots
    const email = String(body.email || "").trim().toLowerCase();
    if (!/^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,}$/.test(email)) return J({ ok: false, error: "Revisa el correo: no parece válido." }, 400);
    const key = String(env.RESEND_API_KEY || "").trim();
    if (!key) return J({ ok: false, error: "El boletín aún no está conectado." }, 503);
    const payload = { email, unsubscribed: false };
    try { const sg = await segmento(key, env); payload.segments = [{ id: sg.id }]; } catch (e) {}
    const r = await fetch("https://api.resend.com/contacts", { method: "POST", headers: { authorization: "Bearer " + key, "content-type": "application/json" }, body: JSON.stringify(payload) });
    const t = await r.text();
    if (r.ok) return J({ ok: true });
    if (r.status === 409 || /already exist/i.test(t)) {
      // ya estaba: lo reactivamos y lo metemos en el boletín
      await fetch(`https://api.resend.com/contacts/${encodeURIComponent(email)}`, { method: "PATCH", headers: { authorization: "Bearer " + key, "content-type": "application/json" }, body: JSON.stringify({ unsubscribed: false }) });
      if (payload.segments) await fetch(`https://api.resend.com/contacts/${encodeURIComponent(email)}/segments/${payload.segments[0].id}`, { method: "POST", headers: { authorization: "Bearer " + key } });
      return J({ ok: true });
    }
    let msg = ""; try { msg = JSON.parse(t).message || ""; } catch (e) { msg = t.slice(0, 160); }
    return J({ ok: false, error: "No se ha podido apuntar ahora. Inténtalo más tarde.", detalle: `Resend ${r.status}: ${msg}` }, 502);
  } catch (e) {
    return J({ ok: false, error: "No se ha podido apuntar ahora. Inténtalo más tarde.", detalle: String(e).slice(0, 160) }, 500);
  }
}
