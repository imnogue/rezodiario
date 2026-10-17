// Vuelta de GitHub: cambia el código por un token y se lo pasa al panel.
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code"), state = url.searchParams.get("state");
  const cookie = (request.headers.get("Cookie") || "").match(/rd_oauth=([^;]+)/);
  const page = (status, content) => new Response(`<!doctype html><html><body><p>${status === "success" ? "Conectado. Puedes cerrar esta ventana." : "No se ha podido entrar."}</p><script>
(function(){var msg='authorization:github:${status}:'+${JSON.stringify(JSON.stringify(content))};
function recv(e){window.opener.postMessage(msg,e.origin);window.removeEventListener('message',recv,false)}
window.addEventListener('message',recv,false);window.opener.postMessage('authorizing:github','*');})();
</script></body></html>`, { headers: { "Content-Type": "text/html; charset=utf-8", "Set-Cookie": "rd_oauth=; Path=/api; Max-Age=0" } });
  if (!code || !cookie || cookie[1] !== state) return page("error", { message: "La sesión ha caducado. Vuelve a intentarlo." });
  const r = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json", "User-Agent": "rezodiario-cms" },
    body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code, redirect_uri: `${url.origin}/api/callback` })
  });
  const j = await r.json();
  if (!j.access_token) return page("error", { message: j.error_description || "GitHub no ha devuelto el acceso." });
  return page("success", { token: j.access_token, provider: "github" });
}
