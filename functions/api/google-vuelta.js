// Vuelta de Google: código → id_token (Google) → sesión (Supabase) → vuelve a la web con la sesión en el #hash.
import { SB_URL, SB_ANON } from "./_sb.js";
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const cookies = Object.fromEntries((request.headers.get("Cookie") || "").split(/;\s*/).filter(Boolean).map(c => { const i = c.indexOf("="); return [c.slice(0, i), decodeURIComponent(c.slice(i + 1))]; }));
  let back = cookies.rd_gb || "/"; if (!back.startsWith("/") || back.startsWith("//")) back = "/";
  const h = new Headers();
  h.append("Set-Cookie", "rd_g=; Path=/api; Max-Age=0"); h.append("Set-Cookie", "rd_gb=; Path=/api; Max-Age=0");
  const go = hash => { h.set("Location", back.split("#")[0] + "#" + hash); return new Response(null, { status: 302, headers: h }); };
  const fail = m => go("error_description=" + encodeURIComponent(m));
  const code = url.searchParams.get("code"), state = url.searchParams.get("state");
  if (url.searchParams.get("error")) return fail("Has cancelado el acceso con Google.");
  if (!code || !state || state !== cookies.rd_g) return fail("La sesión ha caducado. Vuelve a intentarlo.");
  try {
    const t = await fetch("https://oauth2.googleapis.com/token", { method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ code, client_id: String(env.GOOGLE_CLIENT_ID || "").trim(), client_secret: String(env.GOOGLE_CLIENT_SECRET || "").trim(), redirect_uri: `${url.origin}/api/google-vuelta`, grant_type: "authorization_code" }) });
    const tj = await t.json();
    if (!tj.id_token) return fail("Google no ha devuelto el acceso (" + (tj.error_description || tj.error || t.status) + ").");
    const s = await fetch(SB_URL + "/auth/v1/token?grant_type=id_token", { method: "POST", headers: { apikey: SB_ANON, "content-type": "application/json" }, body: JSON.stringify({ provider: "google", id_token: tj.id_token, access_token: tj.access_token }) });
    const sj = await s.json();
    if (!sj.access_token) return fail("No se ha podido crear la sesión (" + (sj.msg || sj.error_description || sj.message || s.status) + ").");
    return go(new URLSearchParams({ access_token: sj.access_token, refresh_token: sj.refresh_token, expires_in: String(sj.expires_in || 3600), token_type: "bearer" }).toString());
  } catch (e) { return fail("No se ha podido entrar con Google ahora mismo."); }
}
