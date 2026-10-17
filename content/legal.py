# -*- coding: utf-8 -*-
"""Textos legales y «Quiénes somos» de Rezo Diario.
Redactados según la normativa española y europea: LSSI-CE (Ley 34/2002), RGPD (Reglamento UE 2016/679),
LOPDGDD (Ley Orgánica 3/2018) y la Guía sobre el uso de cookies de la AEPD (2023).
Los datos del titular se leen de content/ajustes.json → "titular", "nif", "domicilio", "emailContacto".
Revisa estos textos si cambia algo en la web (por ejemplo, al activar Stripe o una herramienta de analítica)."""

ACTUALIZADO = "17 de octubre de 2026"


def legal(AJ):
    t = AJ.get("titular", "").strip()
    nif = AJ.get("nif", "").strip()
    dom = AJ.get("domicilio", "").strip()
    mail = AJ.get("emailContacto", "").strip()
    ident = "".join(f"<li><strong>{a}:</strong> {b}</li>" for a, b in (("Titular", t), ("NIF", nif), ("Domicilio", dom), ("Correo electrónico", f'<a href="mailto:{mail}">{mail}</a>' if mail else ""), ("Sitio web", "rezodiario.com")) if b)

    aviso = f"""
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de los datos del responsable de este sitio web.</p>
<h2>1. Titular</h2><ul>{ident}</ul>
<p>Rezo Diario es un proyecto personal, sin ánimo de lucro, de difusión de la oración católica. No es un servicio oficial de la Iglesia católica ni de ninguna diócesis o congregación.</p>
<h2>2. Objeto</h2>
<p>Rezodiario.com ofrece de forma gratuita contenidos de oración: el Evangelio del día con una reflexión, audios guiados, oraciones, versículos de la Biblia, el Santo Rosario, el Vía Crucis, novenas, santoral y un muro donde dejar intenciones. Puede usarse sin registrarse. La cuenta de usuario es opcional y sirve para guardar el progreso en varios dispositivos.</p>
<h2>3. Condiciones de uso</h2>
<p>Al navegar por la web aceptas usarla de buena fe y conforme a la ley. En particular, te comprometes a no publicar en el muro de intenciones contenidos ofensivos, ilícitos, publicitarios o que identifiquen a terceros (apellidos, teléfonos, direcciones o datos de salud de otras personas). El titular puede retirar sin previo aviso cualquier intención que incumpla estas normas. Las intenciones que reciben varios avisos de otros usuarios se ocultan automáticamente hasta su revisión.</p>
<p>El buscador «¿Qué llevas hoy en el corazón?» funciona en tu propio dispositivo y te propone oraciones de la web. No sustituye el acompañamiento espiritual, médico ni psicológico. Si atraviesas una situación de riesgo, llama al 024 (línea de atención a la conducta suicida) o al 112.</p>
<h2>4. Propiedad intelectual</h2>
<p>El diseño de la web, el logotipo, las reflexiones, las oraciones de nueva redacción, los audios y el resto de contenidos originales pertenecen a su titular. Puedes compartirlos con fines personales y no comerciales citando la fuente y enlazando a rezodiario.com. Para cualquier otro uso, escríbenos.</p>
<p>Las oraciones tradicionales de la Iglesia (Padre nuestro, Avemaría, Credo, Salve, etc.) son patrimonio común de los fieles. Las citas bíblicas siguen la Sagrada Biblia, versión oficial de la Conferencia Episcopal Española, y se reproducen de forma breve con fines de oración y comentario, conforme al derecho de cita (art. 32 de la Ley de Propiedad Intelectual). Las fuentes tipográficas se usan bajo licencia SIL Open Font License.</p>
<h2>5. Voces sintéticas</h2>
<p>Los audios del rezo diario se narran con una voz generada por inteligencia artificial (ElevenLabs) a partir de textos escritos y revisados por Rezo Diario.</p>
<h2>6. Responsabilidad</h2>
<p>Ponemos todo el cuidado en que los contenidos sean correctos y fieles a la liturgia y al Magisterio, pero pueden contener errores. Si encuentras alguno, te agradeceremos que nos lo comuniques. El titular no se hace responsable del uso que terceros hagan de la web ni de los contenidos de páginas externas enlazadas.</p>
<h2>7. Donaciones</h2>
<p>Las aportaciones son voluntarias y se destinan a mantener la web, los audios y los servidores. Los pagos los gestiona una pasarela externa segura; Rezo Diario no conoce ni guarda los datos de tu tarjeta. Las donaciones a una persona física no dan derecho a deducción fiscal.</p>
<h2>8. Legislación aplicable</h2>
<p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales que correspondan conforme a la ley; si actúas como consumidor, los de tu domicilio.</p>
<p class="hint">Última actualización: {ACTUALIZADO}.</p>"""

    priv = f"""
<p>En Rezo Diario cuidamos tu intimidad: pedimos los menos datos posibles y nunca los vendemos ni los usamos para publicidad. Esta política explica qué datos tratamos y por qué, conforme al Reglamento (UE) 2016/679 (RGPD) y a la Ley Orgánica 3/2018 (LOPDGDD).</p>
<h2>1. Responsable del tratamiento</h2><ul>{ident}</ul>
<h2>2. Qué datos tratamos, para qué y con qué base legal</h2>
<div class="tablewrap"><table>
<thead><tr><th>Qué haces</th><th>Datos</th><th>Para qué</th><th>Base legal</th><th>Cuánto tiempo</th></tr></thead>
<tbody>
<tr><td>Usar la web sin cuenta</td><td>Ninguno que te identifique. Tus preferencias, favoritos y racha se guardan solo en tu navegador.</td><td>Que la web recuerde tus elecciones.</td><td>Interés legítimo y tu propia elección (art. 6.1.f RGPD).</td><td>Hasta que borres los datos de tu navegador.</td></tr>
<tr><td>Encender una vela</td><td>El texto de tu intención, tu nombre de pila si lo escribes, la categoría y un identificador anónimo de tu navegador.</td><td>Mostrar tu vela en el muro durante 7 días y evitar abusos.</td><td>Tu consentimiento al publicarla (art. 6.1.a RGPD).</td><td>Visible 7 días; después deja de mostrarse. Puedes pedirnos que la borremos en cualquier momento.</td></tr>
<tr><td>Crear una cuenta</td><td>Correo electrónico o teléfono, o los datos básicos que te pida el proveedor que elijas (Google, Apple, Facebook); tus días rezados, favoritos y novenas.</td><td>Darte acceso y guardar tu progreso en todos tus dispositivos.</td><td>Ejecución del servicio que solicitas (art. 6.1.b RGPD).</td><td>Mientras tengas la cuenta. Puedes borrarla cuando quieras.</td></tr>
<tr><td>Apuntarte al boletín</td><td>Correo electrónico.</td><td>Enviarte el rezo diario y novedades de Rezo Diario.</td><td>Tu consentimiento (art. 6.1.a RGPD).</td><td>Hasta que te des de baja (enlace en cada correo).</td></tr>
<tr><td>Escribirnos</td><td>Tu correo y lo que nos cuentes.</td><td>Responderte.</td><td>Tu consentimiento.</td><td>El tiempo necesario para atenderte.</td></tr>
<tr><td>Donar</td><td>Importe y datos que pide la pasarela de pago.</td><td>Gestionar tu aportación y cumplir obligaciones contables.</td><td>Ejecución de la donación y obligación legal (art. 6.1.b y c RGPD).</td><td>Los plazos que marca la ley fiscal.</td></tr>
</tbody></table></div>
<p>El cuadro «¿Qué llevas hoy en el corazón?» analiza lo que escribes <strong>dentro de tu dispositivo</strong>: ese texto no se envía ni se guarda en ningún servidor. Te pedimos que en el muro de velas no escribas datos de salud, apellidos ni otros datos que identifiquen a otras personas.</p>
<h2>3. Quién más trata los datos (encargados del tratamiento)</h2>
<ul>
<li><strong>Cloudflare, Inc.</strong>: alojamiento y seguridad de la web.</li>
<li><strong>Supabase, Inc.</strong>: base de datos del muro de velas y de las cuentas.</li>
<li><strong>Resend</strong>: envío de correos de acceso y del boletín.</li>
<li><strong>Google, Apple o Meta</strong>, solo si eliges entrar con su cuenta.</li>
<li>La <strong>pasarela de pago</strong> (por ejemplo, Stripe), solo si donas.</li>
</ul>
<p>Algunos de estos proveedores están en Estados Unidos o pueden acceder a datos desde allí. En ese caso, las transferencias se amparan en el Marco de Privacidad de Datos UE-EE. UU. o en las cláusulas contractuales tipo aprobadas por la Comisión Europea (art. 45 y 46 RGPD). No cedemos datos a nadie más, salvo obligación legal.</p>
<h2>4. Menores</h2>
<p>Cualquier persona puede usar la web sin registrarse. Para crear una cuenta o apuntarte al boletín debes tener al menos 14 años (art. 7 LOPDGDD); si eres menor, hazlo con permiso de tus padres o tutores.</p>
<h2>5. Tus derechos</h2>
<p>Puedes pedir en cualquier momento el acceso, la rectificación o la supresión de tus datos, la limitación u oposición a su tratamiento y su portabilidad, así como retirar tu consentimiento. Escribe a <a href="mailto:{mail}">{mail}</a> indicando qué derecho quieres ejercer. Te responderemos en el plazo de un mes. Si crees que no hemos atendido bien tu petición, puedes reclamar ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es" rel="noopener" target="_blank">www.aepd.es</a>).</p>
<h2>6. Seguridad</h2>
<p>La web funciona siempre con conexión cifrada (HTTPS). El acceso a la base de datos está protegido con reglas de seguridad y limitación de envíos, y no guardamos contraseñas: el acceso se hace con enlaces o códigos de un solo uso.</p>
<p class="hint">Última actualización: {ACTUALIZADO}.</p>"""

    cookies = f"""
<p>Esta política explica qué información guarda Rezo Diario en tu dispositivo, conforme al artículo 22.2 de la LSSI-CE y a la Guía sobre el uso de cookies de la Agencia Española de Protección de Datos.</p>
<h2>1. Resumen</h2>
<p><strong>Rezo Diario no usa cookies publicitarias, de analítica ni de redes sociales, ni rastrea tu navegación.</strong> Solo guarda en tu navegador lo imprescindible para que la web funcione y recuerde lo que tú eliges. Por eso no te mostramos un aviso de cookies: según la AEPD, estos elementos están exentos de consentimiento.</p>
<h2>2. Qué guardamos</h2>
<div class="tablewrap"><table>
<thead><tr><th>Nombre</th><th>Tipo</th><th>Para qué</th><th>Duración</th></tr></thead>
<tbody>
<tr><td>rd-tema, rd-theme, rd-lang, rd-langnote-*, rd-musica, rd-voz</td><td>Almacenamiento local · preferencias</td><td>Recordar el modo claro u oscuro, el idioma, la música de fondo y si quieres la voz guía.</td><td>Hasta que lo borres</td></tr>
<tr><td>rd-rezado, rd-favs, rd-nov-*</td><td>Almacenamiento local · funcional</td><td>Tu camino de oración, tus oraciones guardadas y el avance de novenas y retos.</td><td>Hasta que lo borres</td></tr>
<tr><td>rd-uid, rd-mycandles, rd-myflags, rd-myprays, rd-myprays-seen, rd-velas-local, rd-rezos-local</td><td>Almacenamiento local · funcional y de seguridad</td><td>Identificador anónimo para saber qué velas y oraciones son tuyas, evitar avisos repetidos y limitar abusos.</td><td>Hasta que lo borres</td></tr>
<tr><td>rd-auth</td><td>Almacenamiento local · técnico</td><td>Mantener abierta tu sesión si creas una cuenta.</td><td>Hasta que cierres sesión</td></tr>
<tr><td>Caché de la aplicación (service worker)</td><td>Técnico</td><td>Que la web cargue rápido y funcione sin conexión.</td><td>Se renueva sola</td></tr>
<tr><td>rd_oauth</td><td>Cookie técnica</td><td>Solo en el panel de administración, para iniciar sesión de forma segura.</td><td>10 minutos</td></tr>
</tbody></table></div>
<p>Las fuentes tipográficas y el resto de recursos se sirven desde nuestro propio dominio: al visitar la web no se envían datos a Google ni a otros terceros. Cloudflare, que aloja la web, puede usar una cookie técnica de seguridad para protegerla de ataques.</p>
<h2>3. Cómo borrarlas</h2>
<p>Puedes borrar todo lo anterior desde la configuración de tu navegador (opción «Borrar datos de navegación» o «Datos de sitios web»). Perderás tus preferencias y tu camino de oración, salvo que tengas cuenta.</p>
<h2>4. Cambios</h2>
<p>Si algún día añadimos herramientas de analítica o de pago que usen cookies no exentas, te pediremos permiso antes con un aviso claro y actualizaremos esta página.</p>
<p class="hint">Última actualización: {ACTUALIZADO}.</p>"""
    return {"aviso-legal": ("Aviso legal", "Quién está detrás de Rezo Diario y las condiciones de uso de la web.", aviso),
            "privacidad": ("Política de privacidad", "Qué datos tratamos, para qué y cómo ejercer tus derechos.", priv),
            "cookies": ("Política de cookies", "Qué guarda Rezo Diario en tu dispositivo. Sin publicidad ni rastreo.", cookies)}


def quienes(AJ, n_oraciones):
    mail = AJ.get("emailContacto", "").strip()
    return f"""
<div class="prose about">
<p class="about-lead">Rezo Diario nació de una pregunta sencilla: <em>¿cómo hacer que rezar cada día sea tan fácil como mirar el móvil?</em></p>
<p>Muchos queremos rezar más y no sabemos por dónde empezar. Otros rezábamos de pequeños y lo fuimos dejando. Y casi todos vamos con prisa. Rezo Diario quiere ser un rincón tranquilo para esos minutos del día: abrir la web, escuchar el Evangelio, guardar silencio un momento y volver a la vida con algo de paz.</p>

<h2>Qué es Rezo Diario</h2>
<p>Es una web gratuita de oración católica, hecha en España. Cada día preparamos un rezo guiado de unos minutos con el Evangelio de la liturgia, una reflexión breve, unas preguntas para llevarlo a la vida y una oración final. Alrededor de ese rezo hemos reunido lo que nos ayuda a nosotros a rezar: {n_oraciones} oraciones para cada momento, el Santo Rosario cuenta a cuenta, el Vía Crucis, novenas, el santo del día, versículos de la Biblia para cuando más los necesitas y un muro donde encender una vela y rezar unos por otros.</p>
<p>No hace falta registrarse, no hay anuncios y no vendemos datos. Puedes rezar en el autobús, en la cocina o antes de dormir.</p>

<h2>Quién está detrás</h2>
<p>Rezo Diario es un proyecto independiente y sin ánimo de lucro impulsado por <strong>{AJ.get("titular", "Adrián Nogueira")}</strong>, un laico español que quería tener a mano, en un solo sitio, la oración de cada día. No es una web oficial de la Iglesia ni de ninguna diócesis o congregación, pero quiere caminar siempre en comunión con ella: seguimos el calendario litúrgico de la Iglesia católica en España y la Biblia de la Conferencia Episcopal Española.</p>

<h2>Cómo preparamos los contenidos</h2>
<ul>
<li><strong>El Evangelio</strong> es el de la liturgia de cada día. Las citas siguen la traducción oficial de la Conferencia Episcopal Española.</li>
<li><strong>Las reflexiones y las oraciones nuevas</strong> las escribimos nosotros, con lenguaje sencillo y sin sustituir nunca la Palabra de Dios.</li>
<li><strong>Las oraciones tradicionales</strong> se reproducen en su forma habitual en español.</li>
<li><strong>Los audios</strong> se narran con una voz sintética de inteligencia artificial, con música y silencios para rezar. Preferimos decirlo claramente.</li>
<li><strong>«¿Qué llevas hoy en el corazón?»</strong> te propone oraciones de la web según lo que escribes. Lo que escribes se queda en tu dispositivo.</li>
</ul>
<p>Revisamos todo con cariño, pero somos humanos y podemos equivocarnos. Si ves un error, escríbenos y lo corregiremos.</p>

<h2>Lo que nos mueve</h2>
<p>Creemos que un rato de oración cada día cambia la vida, poco a poco y sin ruido. Por eso Rezo Diario quiere ser discreto: sin trofeos ni competiciones, solo un camino que se recorre día a día. Si un día no puedes, no pasa nada. Mañana te volverá a esperar el Evangelio.</p>

<h2>Cómo puedes ayudar</h2>
<ul>
<li><strong>Reza por otros</strong> en el <a href="../muro-de-intenciones.html">muro de velas</a>.</li>
<li><strong>Compártelo</strong> con alguien a quien le pueda hacer bien.</li>
<li><strong>Si eres sacerdote, religioso o catequista</strong> y quieres revisar contenidos o proponer reflexiones, nos encantará hablar contigo.</li>
<li><strong>Si puedes</strong>, <a href="../donar.html">ayúdanos a mantenerlo</a> gratis para todos.</li>
</ul>

<h2>Contacto</h2>
<p>Escríbenos a <a href="mailto:{mail}">{mail}</a>. Leemos todos los mensajes.</p>
</div>"""
