# Conectar el dominio automat-ia.com.co

Esta guía responde dos cosas: **para qué sirve el dominio que compraste** y **qué tienes
que hacer ahora**, en orden y sin rodeos.

---

## 1. Para qué sirve el dominio

Un dominio hace tres trabajos independientes. Compraste uno, pero eso no significa que
los tres estén funcionando: cada uno se activa por separado.

| Trabajo | Qué significa | Estado |
|---------|---------------|--------|
| **Enviar** | Que los correos de la página salgan desde `hola@automat-ia.com.co` y no caigan en spam | Es lo que vas a hacer ahora |
| **Mostrar** | Que la página web cargue al escribir `automat-ia.com.co` | Más adelante, cuando publiques |
| **Recibir** | Tener un buzón real en `hola@automat-ia.com.co` para leer y escribir | Opcional, cuesta dinero, no lo necesitas todavía |

Lo importante: **enviar y recibir son cosas distintas.** Puedes enviar desde tu dominio
sin tener un buzón en tu dominio. Es exactamente lo que vas a hacer.

---

## 2. Tu situación hoy

Decidiste no pagar un buzón profesional y usar Gmail. Es una decisión válida y no rompe
nada. Así queda el flujo:

```
Cliente llena el formulario
        │
        ├──> Te llega el aviso a tu Gmail                    ← lo lees ahí
        │
        └──> Al cliente le llega su confirmación
             enviada desde  hola@automat-ia.com.co           ← se ve profesional
             y si responde, su respuesta cae en tu Gmail     ← no se pierde nada
```

Esto ya está configurado en el código. El correo de confirmación lleva un `reply-to`
apuntando a tu Gmail, así que cuando el cliente pulse «Responder», su mensaje te llega.

**Lo único que sacrificas** es que el cliente ve tu dirección de Gmail al responder. Nada
más. El día que quieras arreglarlo, se resuelve con un buzón (ver el punto 6).

**Y por qué necesitas el dominio de todas formas:** Resend no te deja escribirle a otras
personas hasta que verifiques un dominio propio. Con la dirección de pruebas
`onboarding@resend.dev` solo puedes escribirte a ti mismo. Sin dominio verificado, tus
clientes **nunca reciben** su confirmación.

---

## 3. Lo único que tienes que hacer ahora: verificar el dominio

Ya tienes la cuenta de Resend creada, así que empieza aquí.

### 3.1 Agregar el dominio

1. Entra a [resend.com/domains](https://resend.com/domains) y pulsa **Add Domain**.
2. Escribe `automat-ia.com.co`.
3. En la región, elige **us-east-1** (Norteamérica). Es la más cercana a Colombia.
4. Guarda. Resend te muestra una pantalla con tres registros DNS pendientes.

### 3.2 Crear los registros (elige un camino)

**Camino A — automático (recomendado, 2 minutos)**

Resend detecta que tu dominio está en GoDaddy y muestra un botón **Auto Configure**.
Púlsalo, inicia sesión en GoDaddy cuando te lo pida y autoriza el cambio. Los tres
registros quedan creados solos, sin que escribas nada.

Si aparece ese botón, usa esto y salta al punto 3.3.

**Camino B — manual (si no aparece el botón, 15 minutos)**

En GoDaddy: **Mis productos → automat-ia.com.co → DNS → Agregar nuevo registro**. Crea
los tres, copiando los valores de la pantalla de Resend:

| Tipo | Nombre | Valor | Prioridad |
|------|--------|-------|-----------|
| MX | `send` | El que muestre Resend, tipo `feedback-smtp.us-east-1.amazonses.com` | 10 |
| TXT | `send` | `v=spf1 include:amazonses.com ~all` | — |
| TXT | `resend._domainkey` | La clave larga que empieza por `p=MIIBIjANBgkq...` | — |

Dos advertencias, y son las dos únicas formas en que esto suele fallar:

> **1. GoDaddy completa el dominio por ti.** En el campo *Nombre* escribe solo `send`,
> nunca `send.automat-ia.com.co`. Si escribes el nombre completo, GoDaddy lo guarda como
> `send.automat-ia.com.co.automat-ia.com.co` y el registro queda en un sitio que no
> existe. En el campo *Valor* sí va el texto exacto que da Resend, sin tocar nada.
>
> **2. El MX va en `send`, jamás en `@`.** Los registros MX de la raíz son los que
> reciben correo en tu dominio. Como no usas buzón propio no hay nada que romper hoy,
> pero si algún día lo contratas, sus MX van en `@` y conviven sin problema con el de
> `send`. Son sitios distintos.

Del DKIM (el tercero): es un texto larguísimo. Cópialo completo de una sola vez. Cortarlo
a la mitad es el error más común después del anterior.

### 3.3 Verificar

Vuelve a Resend y pulsa **Verify DNS Records**. Suele confirmarse en unos 15 minutos,
aunque puede tardar hasta unas horas. Cuando esté listo el dominio aparece como
**Verified** en verde.

Mientras esperas puedes comprobarlo tú mismo desde la terminal:

```bash
nslookup -type=MX  send.automat-ia.com.co
nslookup -type=TXT send.automat-ia.com.co
nslookup -type=TXT resend._domainkey.automat-ia.com.co
```

Si los tres devuelven algo parecido a lo que ves en Resend, vas bien.

### 3.4 Sacar la clave de la API

Esto es independiente de la verificación, puedes hacerlo mientras esperas.

1. En Resend, ve a **API Keys → Create API Key**.
2. Ponle un nombre cualquiera, por ejemplo `pagina-web`. Permiso: **Sending access**.
3. Copia la clave (empieza por `re_`). **Solo se muestra una vez.**

### 3.5 Activarlo en la página

Abre el archivo `.env` y déjalo así:

```bash
RESEND_API_KEY=re_la_clave_que_acabas_de_copiar
MAIL_TO=tu-correo@gmail.com
MAIL_FROM=Automat-IA <hola@automat-ia.com.co>
```

Sobre `MAIL_FROM`: la dirección `hola@` no tiene que existir en ningún lado. Una vez que
el dominio está verificado, Resend te deja enviar desde **cualquier** dirección de ese
dominio sin configurar nada más.

Reinicia el servidor (`Ctrl + C` y `npm start`) y envía el formulario con un correo tuyo
distinto al de `MAIL_TO`. Deben llegarte dos correos: el aviso a tu Gmail y la
confirmación a la otra dirección.

> Mientras el dominio no esté verificado, deja `MAIL_FROM=Automat-IA <onboarding@resend.dev>`.
> Funciona, pero solo puede escribirte a ti.

---

## 4. Después: DMARC (5 minutos)

Sin este registro, cualquiera puede mandar correos haciéndose pasar por tu dominio, y
algunos servidores desconfían de los dominios que no lo tienen. Resend no lo crea por ti,
ni siquiera con el botón automático.

En GoDaddy, un registro más:

| Tipo | Nombre | Valor |
|------|--------|-------|
| TXT | `_dmarc` | `v=DMARC1; p=none;` |

`p=none` significa «solo observa, no bloquees nada», que es como hay que empezar. No
puede romper tu correo. Más adelante, cuando lleves meses enviando sin problemas, se
sube a `quarantine` y luego a `reject`.

No agregues la parte de `rua=mailto:...` que verás en otros tutoriales: sirve para
recibir informes diarios y necesita un buzón en tu propio dominio, que hoy no tienes.

---

## 5. Más adelante: apuntar la página web

Esto solo se puede hacer cuando la página ya esté publicada en un hosting. Sigue el
Bloque B de `LANZAMIENTO.md`, y cuando el hosting te pida conectar el dominio:

| Tipo | Nombre | Valor |
|------|--------|-------|
| A | `@` | La dirección IP que te dé tu hosting |
| CNAME | `www` | El nombre `algo.onrender.com` que te dé tu hosting |

Usa los valores de tu panel, no los de esta guía: son distintos para cada servicio. Si
GoDaddy no te deja crear el registro A porque ya existe uno, edítalo en lugar de crear
otro: es el del «sitio en construcción» que GoDaddy pone por defecto.

---

## 6. Opcional: el buzón profesional

El día que quieras leer y escribir desde `hola@automat-ia.com.co` en vez de Gmail:

| Opción | Costo | Cuándo |
|--------|-------|--------|
| **Zoho Mail** | Gratis, 1 usuario, 5 GB | Cuando tengas los primeros clientes |
| **Google Workspace** | ~6 USD al mes | Si quieres Gmail, Drive y Calendar con tu dominio |

Te pedirán poner registros MX en la raíz (`@`). Borra antes los MX de «dominio
estacionado» que GoDaddy deja por defecto. No tocan el MX de `send`.

No corras a hacer esto. No te va a traer un solo cliente más ahora mismo.

---

## Si algo no funciona

**Resend no verifica después de una hora.** Mira el nombre de los registros en GoDaddy:
casi siempre quedó `send.automat-ia.com.co` en vez de `send`. El segundo sospechoso es el
DKIM cortado.

**No me llega ningún correo.** Revisa en este orden: que `RESEND_API_KEY` esté en `.env`,
que reiniciaste el servidor después de editarlo, que `MAIL_TO` no tenga un error de
escritura, y la carpeta de spam. En la consola del servidor verás `[MAIL] Aviso enviado`
si salió bien, o el error si falló.

**Al cliente no le llega su confirmación.** Es el síntoma clásico de seguir usando
`onboarding@resend.dev` en `MAIL_FROM`. Esa dirección solo puede escribirte a ti.

---

## Resumen: qué hacer hoy

- [ ] Agregar `automat-ia.com.co` en Resend y pulsar **Auto Configure**.
- [ ] Crear la API key y pegarla en `.env`.
- [ ] Poner tu Gmail en `MAIL_TO`.
- [ ] Esperar a que Resend diga **Verified**.
- [ ] Cambiar `MAIL_FROM` a `hola@automat-ia.com.co` y reiniciar.
- [ ] Enviar el formulario de prueba y confirmar que llegan los dos correos.
- [ ] Agregar el registro DMARC.
