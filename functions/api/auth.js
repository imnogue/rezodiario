// Inicio de sesión del panel (Decap CMS) con GitHub, sin depender de Netlify.
// Variables necesarias en Cloudflare Pages: GITHUB_CLIENT_ID y GITHUB_CLIENT_SECRET.
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const id = String(env.GITHUB_CLIENT_ID || "").replace(/[\s"']/g, "");
  if (url.searchParams.has("comprobar")) {
    const sec = String(env.GITHUB_CLIENT_SECRET || "").replace(/[\s"']/g, "");
    return new Response(`Client ID: ${id ? id.slice(0, 6) + "…" + id.slice(-3) + " (" + id.length + " caracteres)" : "NO CONFIGURADO"}\nSecret: ${sec ? "configurado (" + sec.length + " caracteres)" : "NO CONFIGURADO"}\nCallback: ${url.origin}/api/callback`, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }
  if (!id) return new Response("Falta GITHUB_CLIENT_ID en las variables de Cloudflare Pages.", { status: 500 });
  const state = crypto.randomUUID();
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.searchParams.set("client_id", id);
  gh.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  gh.searchParams.set("scope", "repo,user");
  gh.searchParams.set("state", state);
  return new Response(null, { status: 302, headers: { Location: gh.toString(), "Set-Cookie": `rd_oauth=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600` } });
}
