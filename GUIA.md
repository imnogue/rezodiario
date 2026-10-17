# Rezo Diario · Guía de puesta en marcha

Esta carpeta es toda la web. No necesitas instalar nada en tu ordenador: Cloudflare Pages la genera sola cada vez que cambias algo.

## Qué hay en la carpeta

| Carpeta o archivo | Para qué sirve |
|---|---|
| `content/` | Todo el contenido: días (`dias/`), oraciones, santos, novenas y ajustes. Lo editarás desde el panel. |
| `guiones/` | Un guion por día, listo para pegar en ElevenLabs. |
| `static/` | Panel de contenidos (`admin/`), widget para parroquias, imágenes y audios. |
| `assets/` | Diseño (`.css`) y funcionamiento (`site.js`) de la web. |
| `supabase/schema.sql` | La base de datos del muro de velas y de las cuentas. |
| `build.py` | El programa que genera la web. Cloudflare lo ejecuta solo. |
| `functions/api/` | El inicio de sesión del panel con GitHub. |
| `netlify.toml` | Por si algún día prefieres Netlify. |
| `.github/workflows/` | Publica la web cada noche para que «hoy» cambie solo. |

---

## Paso 1 · Subir la carpeta a GitHub (15 min)

1. Crea una cuenta gratis en github.com.
2. Instala **GitHub Desktop** (desktop.github.com). Es más fácil que la web porque la carpeta tiene muchos archivos.
3. En GitHub Desktop: *File → Add local repository* → elige esta carpeta → *Create a repository* → nombre `rezodiario` → *Publish repository*. Puedes dejarlo **privado**.

## Paso 2 · Publicar en Cloudflare Pages (10 min, gratis)

1. Crea una cuenta en **dash.cloudflare.com**.
2. Menú izquierdo: **Workers & Pages → Create → Pages → Connect to Git**. Conecta tu GitHub y elige **rezodiario**.
3. En la configuración:
   - Framework preset: **None**
   - Build command: `python3 build.py`
   - Build output directory: `site`
   - En *Environment variables* añade `PYTHON_VERSION` = `3.11`
4. Pulsa **Save and Deploy**. En 1–2 minutos tendrás la web en `rezodiario.pages.dev` (o un nombre parecido).
5. En el proyecto: **Custom domains → Set up a custom domain** → `rezodiario.com`. Si el dominio no está en Cloudflare, te dirá qué registros DNS poner donde lo compraste (o puedes pasar el dominio a Cloudflare, que es lo más sencillo).

## Paso 3 · Activar el panel de contenidos (10 min)

1. En GitHub: foto de perfil → **Settings → Developer settings → OAuth Apps → New OAuth App**.
   - Application name: `Panel Rezo Diario`
   - Homepage URL: `https://rezodiario.com`
   - Authorization callback URL: `https://rezodiario.com/api/callback`
   - Pulsa *Register*, copia el **Client ID** y pulsa *Generate a new client secret* para copiar el **secret**.
2. En Cloudflare, en tu proyecto: **Settings → Variables and Secrets → Add** (en *Production*):
   - `GITHUB_CLIENT_ID` = el Client ID
   - `GITHUB_CLIENT_SECRET` = el secret (márcalo como *Encrypt*)
3. Vuelve a publicar: **Deployments → … → Retry deployment**.
4. Entra en **rezodiario.com/admin** y pulsa *Login with GitHub*. Cada vez que guardes algo, la web se actualiza en 1–2 minutos.

> Mientras el dominio no esté conectado, puedes probar el panel en la dirección `.pages.dev`: crea una segunda OAuth App igual pero con esa dirección en la *callback URL*, y usa sus datos.

## Paso 4 · Muro de velas y cuentas con Supabase (20 min)

1. Crea una cuenta en supabase.com → *New project*. Elige la región **Frankfurt (EU)** por la protección de datos.
2. *SQL Editor → New query* → pega todo `supabase/schema.sql` → **Run**.
3. *Project Settings → API*: copia la **Project URL** y la clave **anon public**.
4. En el panel de la web: *Ajustes de la web* → pega los dos datos → *Publish*.
5. En Supabase, *Authentication → URL Configuration*:
   - Site URL: `https://rezodiario.com`
   - Redirect URLs: `https://rezodiario.com/**`
6. Para los correos de acceso: *Authentication → SMTP Settings* → conecta un servicio de correo (Brevo o Resend tienen plan gratis). El correo de prueba de Supabase solo deja enviar unos pocos mensajes por hora.

**Moderación:** las velas con 3 avisos se ocultan solas. Para revisarlas: *Table Editor → velas* y ordena por `reportes`.

## Paso 5 · Que «hoy» cambie solo cada día (5 min)

1. En Cloudflare, en tu proyecto: **Settings → Builds → Deploy hooks → Add deploy hook** → nombre «cada día», rama `main` → copia la URL.
2. En GitHub, en tu repositorio: **Settings → Secrets and variables → Actions → New repository secret**.
   - Nombre: `NETLIFY_BUILD_HOOK` (se llama así aunque uses Cloudflare)
   - Valor: la URL del paso anterior.
3. Listo: cada noche, a las 00:01, la web se regenera con el Evangelio y el santo del nuevo día.

---

## Audios automáticos con ElevenLabs

Los audios se generan solos: GitHub pide la voz a ElevenLabs, la monta con silencios y música suave, guarda el MP3 en Supabase y lo enlaza en la web y en el pódcast.

**Preparación (una vez):**
1. En ElevenLabs, contrata el plan **Creator** (incluye licencia comercial).
2. Elige una voz calmada en español en la *Voice Library* → *Add to my voices*. En *My Voices* → los tres puntos → **Copy voice ID**.
3. En ElevenLabs → foto de perfil → **API Keys** → *Create API key* (permiso *Text to Speech*) → cópiala.
4. En Supabase → **Project Settings → API Keys** → copia la **Secret key** (`sb_secret_…`). Es privada: solo va en GitHub.
5. En GitHub → **Settings → Secrets and variables → Actions → New repository secret**, crea tres:
   - `ELEVENLABS_API_KEY`
   - `ELEVENLABS_VOICE_ID`
   - `SUPABASE_SERVICE_KEY`

**Uso:**
- **Automático:** cada domingo por la tarde se generan los audios de los 7 días siguientes.
- **A mano:** GitHub → **Actions → Generar audios con ElevenLabs → Run workflow**. Puedes elegir fechas, volver a generar un día o hacer una **prueba sin gastar créditos**.
- **Tu propia música:** sube un MP3 libre de derechos como `static/musica/fondo.mp3`. Si no hay, se usa un bordón suave generado.
- **Gasto:** unos 1.000 caracteres por día, ~30.000 al mes. El plan Creator incluye 121.000.

Los guiones de `guiones/` siguen ahí por si algún día prefieres grabar a mano.

## Pódcast, WhatsApp y redes

- **Pódcast:** tu feed está en `https://rezodiario.com/podcast.xml`. Dalo de alta en Spotify for Creators (*Add existing podcast*), Apple Podcasts Connect, iVoox y YouTube Music. La portada ya está creada (`static/podcast-portada.jpg`, 3000×3000).
- **Canal de WhatsApp:** créalo desde la app (*Novedades → Canales → Crear canal*), copia el enlace y pégalo en *Ajustes de la web*. Aparecerá un botón verde en la web. Publica cada mañana el enlace del rezo del día.
- **Widget para parroquias:** envía `https://rezodiario.com/widget.html` a parroquias, colegios y blogs. Cada web que lo instala te da un enlace, y eso es lo que más sube en Google.

## Google

1. Entra en **Google Search Console** → añade `rezodiario.com` (tipo «Dominio») → verifica con el registro DNS que te indica.
2. *Sitemaps* → envía `sitemap.xml`.
3. Haz lo mismo en **Bing Webmaster Tools**: importa la web desde Search Console en un clic.

---

## Antes de lanzar · Lista de comprobación

- [ ] Completar `legal/aviso-legal`, `privacidad` y `cookies` con vuestros datos (están en `build.py`, apartado LEGAL) y revisarlos con un profesional.
- [ ] Completar **Quiénes somos** con el equipo y quién revisa los contenidos.
- [ ] Pedir a la Conferencia Episcopal Española la **licencia de los textos bíblicos** si vais a publicar las lecturas completas.
- [ ] Revisar que las **frases del Evangelio** de cada día coinciden con la traducción oficial.
- [ ] Poner el **enlace de pago** real (Stripe Payment Links, PayPal o Bizum) en *Ajustes → Donaciones*.
- [ ] Conectar el **boletín por correo** (Brevo o MailerLite) en el formulario de suscripción.
- [ ] Grabar al menos los primeros **7 audios** antes del lanzamiento.

## Contenido incluido en esta tanda

- Evangelio, reflexión y preguntas de cada día del **12 de octubre al 31 de diciembre de 2026**.
- **47 santos**, **62 oraciones**, **5 novenas** (San Judas, Difuntos, Inmaculada, Guadalupe y Navidad).
- **Adviento 2026**, **Reto de Adviento** (26 gestos) y **Navidad 2026**.

Siguiente tanda: enero a Cuaresma, el resto de santos del año y hasta 150 oraciones.
