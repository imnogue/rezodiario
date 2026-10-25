// Entrar con Google mostrando «rezodiario.com» (y no el dominio de Supabase).
// Google vuelve a /api/google-vuelta; allí cambiamos el código por un id_token y se lo damos a Supabase.
// Variables en Cloudflare Pages: GOOGLE_CLIENT_ID (texto) y GOOGLE_CLIENT_SECRET (secreto): las mismas que tiene Supabase en Authentication → Providers → Google.
import { SB_URL } from "./_sb.js";
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const id = String(env.GOOGLE_CLIENT_ID || "").trim();
  if (url.searchParams.has("comprobar")) return new Response(`GOOGLE_CLIENT_ID: ${id ? "puesto (…" + id.slice(-28) + ")" : "FALTA"}\nGOOGLE_CLIENT_SECRET: ${env.GOOGLE_CLIENT_SECRET ? "puesto" : "FALTA"}\nURL de vuelta que hay que autorizar en Google: ${url.origin}/api/google-vuelta`, { headers: { "content-type": "text/plain; charset=utf-8" } });
  let back = url.searchParams.get("volver") || "/";
  if (!back.startsWith("/") || back.startsWith("//")) back = "/";
  // Mientras no estén puestas las variables, seguimos entrando por Supabase como antes
  if (!id || !env.GOOGLE_CLIENT_SECRET) return new Response(null, { status: 302, headers: { Location: `${SB_URL}/auth/v1/authorize?provider=google&redirect_to=${encodeURIComponent(url.origin + back)}` } });
  const state = crypto.randomUUID();
  const g = new URL("https://accounts.google.com/o/oauth2/v2/auth");
  g.searchParams.set("client_id", id);
  g.searchParams.set("redirect_uri", `${url.origin}/api/google-vuelta`);
  g.searchParams.set("response_type", "code");
  g.searchParams.set("scope", "openid email profile");
  g.searchParams.set("state", state);
  g.searchParams.set("prompt", "select_account");
  const ck = (n, v) => `${n}=${encodeURIComponent(v)}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600`;
  const h = new Headers({ Location: g.toString() });
  h.append("Set-Cookie", ck("rd_g", state));
  h.append("Set-Cookie", ck("rd_gb", back));
  return new Response(null, { status: 302, headers: h });
}
