// Inicio de sesión del panel (Decap CMS) con GitHub, sin depender de Netlify.
// Variables necesarias en Cloudflare Pages: GITHUB_CLIENT_ID y GITHUB_CLIENT_SECRET.
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  if (!env.GITHUB_CLIENT_ID) return new Response("Falta GITHUB_CLIENT_ID en las variables de Cloudflare Pages.", { status: 500 });
  const state = crypto.randomUUID();
  const gh = new URL("https://github.com/login/oauth/authorize");
  gh.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  gh.searchParams.set("redirect_uri", `${url.origin}/api/callback`);
  gh.searchParams.set("scope", "repo,user");
  gh.searchParams.set("state", state);
  return new Response(null, { status: 302, headers: { Location: gh.toString(), "Set-Cookie": `rd_oauth=${state}; Path=/api; HttpOnly; Secure; SameSite=Lax; Max-Age=600` } });
}
