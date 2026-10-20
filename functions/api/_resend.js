// Ayudas compartidas para el boletín (Resend). Los archivos que empiezan por _ no son rutas públicas.
export const NOMBRE_SEGMENTO = "Boletín Rezo Diario";
export const rs = (key, path, opt = {}) =>
  fetch("https://api.resend.com" + path, {
    ...opt,
    headers: { authorization: "Bearer " + key, "content-type": "application/json", ...(opt.headers || {}) },
    body: opt.body && typeof opt.body !== "string" ? JSON.stringify(opt.body) : opt.body,
  });
export const espera = (ms) => new Promise((r) => setTimeout(r, ms));
// Devuelve { id, nuevo } del segmento del boletín: el de RESEND_SEGMENT_ID, o uno llamado «Boletín Rezo Diario» (lo crea si no existe)
export async function segmento(key, env) {
  const fijo = String(env.RESEND_SEGMENT_ID || "").trim();
  if (fijo) return { id: fijo, nuevo: false };
  const l = await rs(key, "/segments");
  if (l.ok) {
    const j = await l.json();
    const s = (j.data || []).find((x) => x.name === NOMBRE_SEGMENTO);
    if (s) return { id: s.id, nuevo: false };
  }
  const c = await rs(key, "/segments", { method: "POST", body: { name: NOMBRE_SEGMENTO } });
  const cj = await c.json().catch(() => ({}));
  if (!c.ok || !cj.id) throw new Error("No puedo crear el segmento en Resend: " + (cj.message || c.status));
  return { id: cj.id, nuevo: true };
}
