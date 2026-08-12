# Del computador a internet: qué falta para lanzar

Esta guía es la lista de lo que hay que hacer para que la página deje de vivir en tu
computador y esté publicada, medida y lista para compartir con clientes.

No cubre **qué decirles** a los clientes: eso ya está en `GUIA-CLIENTES.md`. Aquí solo
está lo que hay que dejar montado antes de escribir el primer mensaje.

---

## Estado actual

**Lo que ya está listo:**

- La página completa: hero, problema, calculadora de retorno, 9 sectores con 45
  automatizaciones, proceso, beneficios y formulario.
- La base de datos guarda cada solicitud con el sector, el tipo (diagnóstico o MVP) y
  el ahorro que el visitante calculó.
- El aviso por correo, con respuesta directa al cliente.
- El panel de leads protegido con clave, más defensas contra robots.
- El dominio `automat-ia.com.co`, comprado en GoDaddy.
- El favicon, la imagen de vista previa y las etiquetas para compartir el enlace.
- La página de privacidad y la casilla de consentimiento obligatoria.

**Lo que falta:** tres cosas, y solo una cuesta dinero.

| # | Qué falta | Bloquea el lanzamiento | Costo aproximado |
|---|-----------|------------------------|------------------|
| 1 | Verificar el dominio en Resend y activar el correo | Sí | Gratis |
| 2 | Rellenar los datos `[COMPLETAR]` de `privacidad.html` | Sí, es legal | Gratis |
| 3 | Publicar en un hosting | Sí | Gratis o ~7 USD al mes |
| 4 | Medición de visitas | No, pero hazlo | Gratis |

Tiempo total realista: **una tarde**, más la espera de que propaguen los DNS.

---

## Bloque A · Antes de publicar

### A1. Activar el correo

Es el único pendiente grande. Todo el paso a paso está en **`CONECTAR-DOMINIO.md`**:
verificar `automat-ia.com.co` en Resend, sacar la API key y rellenar el `.env`.

**Por qué no se puede saltar:** hasta que el dominio esté verificado, Resend solo te
deja escribirte a ti mismo. Un cliente que llena el formulario y no recibe su
confirmación asume que la página está rota.

### A2. Completar el aviso de privacidad

La página `privacidad.html` ya está escrita y enlazada, y la casilla de autorización ya
es obligatoria en el formulario. Falta un detalle que **no puedes publicar sin
resolver**: dentro del archivo hay cuatro marcas `[COMPLETAR]` con tu nombre o razón
social, cédula o NIT, ciudad y proveedor de hosting.

Publicar la política con esos marcadores a la vista se ve improvisado y la deja sin
valor legal.

> No soy abogado y esto no es asesoría legal. Si vas a trabajar con empresas grandes o
> con datos sensibles (salud, por ejemplo), vale la pena que alguien que sepa del tema
> le dé una mirada. Pero no lanzar nada es peor que lanzar con un aviso razonable.

### A3. Revisión final de la página

- [ ] Ábrela en el **celular** y recórrela completa. Es donde va a llegar la mayoría
      de la gente desde WhatsApp y LinkedIn.
- [ ] Prueba la calculadora con números de un cliente real que tengas en mente.
- [ ] Envía el formulario y confirma que te llega el correo.
- [ ] Lee los textos en voz alta buscando erratas.
- [ ] Verifica que el menú, los botones «Lo quiero» y el enlace de la calculadora
      lleven a donde deben.

---

## Bloque B · Publicar en internet

### B1. Elegir dónde

La página necesita un servidor Node encendido y un lugar donde el archivo
`data/leads.db` no se borre. Eso descarta Vercel y Netlify.

| Servicio | Ventaja | A tener en cuenta |
|----------|---------|-------------------|
| **Render** (recomendado) | Lo más simple, HTTPS automático, disco persistente | El plan gratis "duerme" tras 15 min sin visitas: la primera carga tarda unos segundos |
| **Railway** | Rápido y cómodo de usar | Se paga por consumo, unos pocos dólares al mes |
| **VPS** (Hetzner, DigitalOcean) | Control total y barato | Tienes que configurar todo a mano |

Para arrancar, Render en plan pago básico (unos 7 dólares al mes) evita el "sueño" y
te da el disco persistente. Si quieres probar sin pagar, el plan gratis sirve, pero
recuerda que un cliente que llega y espera 20 segundos se va.

### B2. Subir el proyecto a GitHub

El hosting toma el código desde ahí.

- Crea el repositorio en **privado**. Este código incluye tu estrategia comercial.
- Verifica antes de subir que `.gitignore` esté haciendo su trabajo: **el archivo
  `.env` y `data/leads.db` no se deben subir nunca**. El primero tiene tus claves; el
  segundo, los datos de tus clientes.

Para confirmarlo, antes del primer envío:

```bash
git status
```

Si aparecen `.env` o `data/leads.db` en la lista, **detente** y revisa el `.gitignore`.

### B3. Configurar el servicio

1. Conecta el repositorio de GitHub.
2. Comando de arranque: `npm start`
3. Copia a mano las variables de entorno en el panel del servicio (`RESEND_API_KEY`,
   `MAIL_TO`, `MAIL_FROM`, `ADMIN_KEY`). El archivo `.env` no viaja con el código, por
   eso hay que ponerlas ahí.
4. Monta un **disco persistente** apuntando a la carpeta `data/`. Sin esto pierdes
   todos los contactos en cada actualización que hagas.

### B4. Conectar el dominio

En el panel del hosting agregas tu dominio y te da unos registros DNS para pegar donde
lo compraste. El certificado HTTPS (el candado del navegador) se genera solo y es
obligatorio: sin él, Chrome muestra "No es seguro" justo al lado de tu formulario.

Los DNS pueden tardar entre minutos y unas horas en propagarse.

### B5. Prueba después de publicar

- [ ] `https://automat-ia.com.co` carga con candado.
- [ ] El formulario envía y te llega el correo.
- [ ] El cliente recibe su confirmación (revisa también la carpeta de spam).
- [ ] `https://automat-ia.com.co/api/leads` **sin** clave responde "No autorizado".
- [ ] `https://automat-ia.com.co/api/leads?clave=TU_CLAVE` sí muestra los datos.
- [ ] Pega el enlace en WhatsApp y mira cómo se ve la vista previa.
- [ ] Ábrela en el celular de otra persona.

---

## Bloque C · Medir

Sin medición estás promocionando a ciegas: no sabrás si el problema es que nadie
entra, que entran y se van, o que llegan al formulario y no lo envían.

Instala uno de estos, ambos con una línea en el HTML:

- **Plausible** o **Fathom**: simples, privados, sin banner de cookies. De pago, unos
  9 dólares al mes.
- **Google Analytics 4**: gratis y potente, pero más complejo y obliga a mencionar
  cookies en tu aviso de privacidad.

**Los cuatro números que importan:**

1. Cuántas personas entran.
2. Cuántas llegan a la calculadora y la usan.
3. Cuántas envían el formulario (si de 100 visitas envían 2 o 3, vas bien).
4. Qué sector se pide más, que ya te lo dice `/api/stats`.

Ese último dato es tu validación: **el servicio más solicitado es el que debes
construir primero.**

---

## Bloque D · Dejar listo el terreno para promocionar

Antes del primer mensaje, ten esto en orden:

- [ ] **Una cuenta de correo dedicada al negocio**, separada de la personal. Un Gmail
      solo para esto sirve de sobra al principio, y es lo que ya tienes configurado en
      `MAIL_TO`. Un buzón con tu dominio es mejor, pero puede esperar.
- [ ] **WhatsApp Business** con foto, descripción y un mensaje de bienvenida.
- [ ] **LinkedIn** con el titular, la descripción y el enlace a tu página.
- [ ] **Enlaces con etiqueta de origen**, para saber qué canal funciona:

```text
https://automat-ia.com.co/?utm_source=linkedin
https://automat-ia.com.co/?utm_source=whatsapp
https://automat-ia.com.co/?utm_source=correo
```

Son el mismo enlace; la etiqueta final solo sirve para que tu medición te diga de
dónde llegó cada visita.

- [ ] **Un caso demostrable.** Es lo que más te va a costar y lo que más vende. Sin
      clientes todavía, grábate un video de dos minutos donde una automatización tuya
      procese un archivo de verdad. Ver algo funcionando convence más que cualquier
      texto de la página.

Con eso listo, abre `GUIA-CLIENTES.md` y sigue el plan de los primeros 30 días.

---

## Bloque E · La rutina cuando ya esté en marcha

**Todos los días:** revisar el correo y responder cada solicitud en menos de 24 horas.
La velocidad de respuesta es, con diferencia, lo que más cierra ventas.

**Cada semana:** mirar `/api/stats` para ver qué sector pide más la gente, y revisar
las visitas.

**Cada mes:** descargar una copia de `data/leads.db` como respaldo, y ajustar los
textos de la página según las objeciones que te repitan en las llamadas.

---

## Resumen: el orden

| Paso | Depende de | Tiempo |
|------|-----------|--------|
| 1. Verificar el dominio en Resend | — | 20 min + espera DNS |
| 2. Completar los `[COMPLETAR]` de privacidad | — | 15 min |
| 3. Repositorio privado en GitHub | — | 20 min |
| 4. Publicar en el hosting | Paso 3 | 30 min |
| 5. Conectar dominio y HTTPS | Paso 4 | 15 min + espera DNS |
| 6. Medición | Paso 4 | 15 min |
| 7. WhatsApp Business y LinkedIn | — | 1 hora |

**Costo del primer año:** el dominio, que ya pagaste, más el hosting (0 a 84 USD al año).
Todo lo demás tiene plan gratuito suficiente para empezar.

---

## Lo que NO hay que hacer todavía

Es tan importante como la lista de arriba, porque son las cosas que consumen semanas
sin traer un solo cliente:

- **Pulir la página otra vez.** Ya está lista para vender. Se mejora con lo que te
  digan los clientes reales, no adivinando.
- **Construir las 45 automatizaciones del catálogo.** El catálogo existe justo para
  descubrir cuál construir primero. Construyes cuando alguien pague.
- **Pagar publicidad.** Sin saber cuánto convierte la página, es tirar plata. Primero
  el alcance manual, que además te enseña cómo hablan tus clientes.
- **Añadir un panel de administración bonito.** Mientras sean menos de 50 leads,
  `/api/leads` alcanza.
