// Donaciones con Stripe Checkout (una vez o cada mes, cualquier cantidad).
// Variable en Cloudflare Pages (Settings → Variables and Secrets), tipo Secret:
//   STRIPE_SECRET_KEY   = sk_test_… para probar · sk_live_… para cobrar de verdad
// Diagnóstico sin datos sensibles: /api/donar?comprobar
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const enc = (obj, pre = "", out = []) => { for (const [k, v] of Object.entries(obj)) { const key = pre ? `${pre}[${k}]` : k; if (v && typeof v === "object") enc(v, key, out); else if (v !== undefined && v !== null) out.push(encodeURIComponent(key) + "=" + encodeURIComponent(String(v))); } return out.join("&"); };
export async function onRequest({ request, env }) {
  try {
    const key = String(env.STRIPE_SECRET_KEY || "").trim();
    const url = new URL(request.url);
    if (request.method === "GET" && url.searchParams.has("comprobar")) {
      if (!key) return J({ clave: "falta STRIPE_SECRET_KEY en Cloudflare (o falta volver a desplegar)" });
      const r = await fetch("https://api.stripe.com/v1/balance", { headers: { authorization: "Bearer " + key } });
      return J({ clave: key.startsWith("sk_live_") ? "real (cobra de verdad)" : key.startsWith("sk_test_") ? "de prueba (no cobra)" : "formato raro", stripe: r.status });
    }
    if (request.method !== "POST") return J({ ok: false, error: "Usa POST" }, 405);
    if (!key) return J({ ok: false, error: "Las donaciones aún no están conectadas." }, 503);
    let b = {}; try { b = await request.json(); } catch (e) {}
    const eur = Math.round(Number(b.amount));
    const monthly = b.freq === "month";
    if (!Number.isFinite(eur) || eur < 1 || eur > 5000) return J({ ok: false, error: "Elige una cantidad entre 1 y 5.000 €." }, 400);
    const origin = url.origin;
    const price = { currency: "eur", unit_amount: eur * 100, product_data: { name: monthly ? "Apoyo mensual a Rezo Diario" : "Donativo a Rezo Diario" } };
    if (monthly) price.recurring = { interval: "month" };
    const params = {
      mode: monthly ? "subscription" : "payment",
      "line_items[0][quantity]": 1,
      success_url: origin + "/donar?gracias=1",
      cancel_url: origin + "/donar#donar",
      locale: "es",
      submit_type: monthly ? undefined : "donate",
      billing_address_collection: "auto",
      "metadata[origen]": "rezodiario.com",
    };
    const body = enc(params) + "&" + enc({ "line_items[0][price_data]": price });
    const r = await fetch("https://api.stripe.com/v1/checkout/sessions", { method: "POST", headers: { authorization: "Bearer " + key, "content-type": "application/x-www-form-urlencoded" }, body });
    const j = await r.json().catch(() => ({}));
    if (r.ok && j.url) return J({ ok: true, url: j.url });
    return J({ ok: false, error: "No se ha podido abrir el pago ahora. Inténtalo en unos minutos.", detalle: (j.error && j.error.message) || ("Stripe " + r.status) }, 502);
  } catch (e) {
    return J({ ok: false, error: "No se ha podido abrir el pago ahora.", detalle: String(e).slice(0, 160) }, 500);
  }
}
