# Rezo Diario · Guía de puesta en marcha

Esta carpeta es toda la web. No necesitas instalar nada en tu ordenador: Netlify la genera sola cada vez que cambias algo.

## Qué hay en la carpeta

| Carpeta o archivo | Para qué sirve |
|---|---|
| `content/` | Todo el contenido: días (`dias/`), oraciones, santos, novenas y ajustes. Lo editarás desde el panel. |
| `guiones/` | Un guion por día, listo para pegar en ElevenLabs. |
| `static/` | Panel de contenidos (`admin/`), widget para parroquias, imágenes y audios. |
| `assets/` | Diseño (`.css`) y funcionamiento (`site.js`) de la web. |
| `supabase/schema.sql` | La base de datos del muro de velas y de las cuentas. |
| `build.py` | El programa que genera la web. Netlify lo ejecuta solo. |
| `netlify.toml` | Instrucciones para Netlify. |
| `.github/workflows/` | Publica la web cada noche para que «hoy» cambie solo. |

---

## Paso 1 · Subir la carpeta a GitHub (15 min)

1. Crea una cuenta gratis en github.com.
2. Instala **GitHub Desktop** (desktop.github.com). Es más fácil que la web porque la carpeta tiene muchos archivos.
3. En GitHub Desktop: *File → Add local repository* → elige esta carpeta → *Create a repository* → nombre `rezodiario` → *Publish repository*. Puedes dejarlo **privado**.

## Paso 2 · Publicar en Netlify (10 min)

1. Crea una cuenta en netlify.com entrando con tu cuenta de GitHub.
2. *Add new site → Import an existing project → GitHub* → elige `rezodiario`.
3. Netlify lee `netlify.toml` y ya sabe qué hacer. Pulsa **Deploy**.
4. En *Domain management* añade **rezodiario.com** y sigue las instrucciones para cambiar los DNS en la empresa donde compraste el dominio. El certificado HTTPS se activa solo.

## Paso 3 · Activar el panel de contenidos (15 min)

1. El panel ya está configurado para tu repositorio `imnogue/rezodiario`.
2. En GitHub: *Settings → Developer settings → OAuth Apps → New OAuth App*.
   - Homepage URL: `https://rezodiario.com`
   - Authorization callback URL: `https://api.netlify.com/auth/done`
   - Copia el **Client ID** y genera un **Client secret**.
3. En Netlify: *Site configuration → Access & security → OAuth → Install provider → GitHub* y pega los dos datos.
4. Entra en **rezodiario.com/admin** y pulsa *Login with GitHub*. Ya puedes editar días, oraciones, santos, novenas y ajustes. Cada vez que guardas, la web se actualiza en 1–2 minutos.

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

1. En Netlify: *Site configuration → Build & deploy → Build hooks → Add build hook* → nombre «cada día» → copia la URL.
2. En GitHub, en tu repositorio: *Settings → Secrets and variables → Actions → New repository secret*.
   - Nombre: `NETLIFY_BUILD_HOOK`
   - Valor: la URL del paso anterior.
3. Listo: cada noche, a las 00:01, la web se regenera con el Evangelio y el santo del nuevo día.

---

## Cada día · Cómo crear el audio con ElevenLabs

1. Abre `guiones/AAAA-MM-DD.txt` del día que quieras grabar.
2. Pega **cada bloque por separado** en ElevenLabs (Text to Speech) con una voz calmada en español de España. Ajustes que funcionan bien: estabilidad 60–75 %, estilo 0–15 %, velocidad 0,9.
3. Descarga los 4 MP3.
4. Móntalos con **música suave libre de derechos** en Audacity o CapCut (gratis). Respeta los silencios que indica el guion: son la parte más importante de la oración.
   - Música libre: Pixabay Music o la Biblioteca de audio de YouTube.
5. Exporta en **MP3, 128 kbps, mono**.
6. En el panel: *Rezo de cada día* → el día → **Audio** → sube el MP3 → escribe la duración (por ejemplo `9:30`) → *Publish*.

Cuando un día tiene audio, la web lo reproduce en lugar de la voz del navegador y lo añade al pódcast automáticamente.

> Comprueba que tu plan de ElevenLabs permite **uso comercial** y en pódcast. Los planes gratuitos suelen tener límites.

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
