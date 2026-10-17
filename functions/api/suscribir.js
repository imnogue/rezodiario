// Alta en el boletín de Rezo Diario: guarda el correo como contacto en Resend.
// Variables en Cloudflare Pages (Settings → Variables and Secrets):
//   RESEND_API_KEY     (obligatoria, tipo Secret)
//   RESEND_SEGMENT_ID  (opcional: el segmento «Boletín» donde guardar los contactos)
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
export async function onRequestPost({ request, env }) {
  let body = {};
  try { body = await request.json(); } catch (e) { return J({ ok: false, error: "Petición no válida" }, 400); }
  if (body.web) return J({ ok: true }); // trampa para robots: campo oculto relleno
  const email = String(body.email || "").trim().toLowerCase();
  if (!/^[^\s@]{1,64}@[^\s@]{1,190}\.[a-z]{2,}$/.test(email)) return J({ ok: false, error: "Correo no válido" }, 400);
  const key = (env.RESEND_API_KEY || "").trim();
  if (!key) return J({ ok: false, error: "El boletín aún no está conectado" }, 503);
  const payload = { email, unsubscribed: false, properties: { origen: "web", alta: new Date().toISOString().slice(0, 10) } };
  const seg = (env.RESEND_SEGMENT_ID || "").trim(); if (seg) payload.segments = [seg];
  const r = await fetch("https://api.resend.com/contacts", { method: "POST", headers: { authorization: "Bearer " + key, "content-type": "application/json" }, body: JSON.stringify(payload) });
  if (r.ok || r.status === 409) return J({ ok: true });
  const t = await r.text();
  if (/already exists/i.test(t)) return J({ ok: true });
  return J({ ok: false, error: "No se ha podido guardar ahora. Inténtalo más tarde." }, 502);
}
export const onRequest = ({ request }) => request.method === "POST" ? null : J({ ok: false, error: "Usa POST" }, 405);
