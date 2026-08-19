# Automat-IA — Landing page de servicios de automatización

Página web profesional para ofrecer servicios de desarrollo de agentes de IA que
automatizan tareas en 9 sectores (RR. HH., Marketing/Ventas, Logística, Inmobiliaria,
Salud, Contabilidad, Atención al Cliente, E-commerce y Legal). Funciona con el modelo
**"Puerta Falsa" / Validación Lean**: primero mides el interés real de los clientes y
luego construyes lo que más piden.

> Para arrancar la página paso a paso, lee **`docs/EJECUTAR-PAGINA.md`**.
> Para publicarla en internet, **`docs/LANZAMIENTO.md`**.
> Para conseguir clientes, **`docs/GUIA-CLIENTES.md`**.

---

## 1. ¿Qué tecnología usa y por qué?

| Pieza | Tecnología | Para qué sirve |
|-------|-----------|----------------|
| Servidor | **Node.js + Express** | Sirve la página y recibe los formularios |
| Base de datos | **SQLite** (integrado en Node) | Guarda los contactos interesados (leads) |
| Correo | **Resend** | Te avisa por email de cada solicitud nueva |
| Frontend | **HTML + CSS + JavaScript** | Lo que ve y usa el visitante |

**Ventaja clave:** SQLite viene incluido en tu versión de Node, así que solo se
instalan dos dependencias: Express y Resend. Cero problemas de compilación.

---

## 2. Estructura del proyecto (qué hace cada archivo)

```
RH-AUTOM/
├── package.json          → Lista de dependencias y comandos (npm start)
├── .env                  → Claves privadas: correo y panel (NO se sube a git)
├── .env.example          → Plantilla de .env, para instalar en otro computador
├── server.js             → El servidor: sirve la web, guarda leads y protege el panel
├── db.js                 → Crea y configura la base de datos SQLite
├── mailer.js             → Envía el aviso a tu correo y la confirmación al cliente
├── data/
│   └── leads.db          → Archivo con los contactos (se crea solo al arrancar)
├── assets/               → Moldes de las imágenes (no se publican)
│   ├── og-template.html  → Diseño de la vista previa al compartir el enlace
│   └── icono-template.html → Diseño del icono para celulares
├── scripts/
│   └── generar-imagenes.js → Convierte esos moldes en imágenes (npm run og)
├── public/               → TODO lo que ve el visitante
│   ├── index.html        → Estructura de la página (secciones y textos fijos)
│   ├── privacidad.html   → Política de tratamiento de datos
│   ├── favicon.svg       → Icono de la pestaña del navegador
│   ├── img/              → Vista previa e icono generados
│   ├── css/styles.css    → Diseño: colores, tamaños, responsive
│   └── js/
│       ├── data.js       → El CATÁLOGO de servicios (aquí editas tus servicios)
│       └── main.js       → Interactividad: tarjetas, calculadora y formulario
├── README.md             → Este archivo (guía técnica)
└── docs/
    ├── EJECUTAR-PAGINA.md  → Cómo arrancar la página paso a paso
    ├── LANZAMIENTO.md      → Qué falta para publicarla y empezar a promocionar
    ├── CONECTAR-DOMINIO.md → Configurar el dominio de GoDaddy (correo y web)
    └── GUIA-CLIENTES.md    → Estrategia para conseguir clientes
```

**Regla mental sencilla:**
- ¿Quiero cambiar un **servicio o su texto**? → `public/js/data.js`
- ¿Quiero cambiar **colores o diseño**? → `public/css/styles.css`
- ¿Quiero cambiar **secciones fijas** (hero, calculadora, proceso)? → `public/index.html`
- ¿Quiero cambiar **cómo se guardan los datos**? → `server.js` y `db.js`
- ¿Quiero cambiar **el texto de los correos**? → `mailer.js`
- ¿Quiero cambiar **una clave**? → `.env`
- ¿Cambié el titular y quiero **actualizar la imagen de vista previa**? → edita
  `assets/og-template.html` y ejecuta `npm run og`

---

## 3. Cómo poner la página a funcionar (paso a paso)

### Paso 1 — Instalar Node.js (solo la primera vez)
Ya lo tienes instalado (Node v25). Para verificarlo, en la terminal:

```bash
node --version
```

### Paso 2 — Instalar las dependencias (solo la primera vez)
Desde la carpeta del proyecto:

```bash
npm install
```

Esto crea la carpeta `node_modules/` con Express.

### Paso 3 — Arrancar el servidor
```bash
npm start
```

Verás un mensaje como este:

```
  Automat-IA corriendo!
  Abre en tu navegador: http://localhost:3000
```

### Paso 4 — Abrir la página
Abre tu navegador en: **http://localhost:3000**

### Paso 5 — Detener el servidor
En la terminal donde está corriendo, pulsa `Ctrl + C`.

> **Consejo:** mientras desarrollas, usa `npm run dev`. Reinicia el servidor
> automáticamente cada vez que guardas un cambio en el código.

---

## 4. Qué pasa cuando alguien envía el formulario

1. El lead se guarda en `data/leads.db`.
2. Te llega un **correo con sus datos y su problema**. Si pidió un MVP, el asunto
   empieza con `[MVP]` para que lo veas de inmediato. Al pulsar «Responder», tu
   respuesta le llega directamente al cliente.
3. El cliente recibe una **confirmación automática** de que lo recibiste.

Si el correo no está configurado o falla, **el lead se guarda igual**: nunca se pierde
un contacto por un problema de email.

### Configurar el correo (una sola vez)

1. Crea una cuenta en [resend.com](https://resend.com) y genera una **API Key**.
2. En **Domains**, agrega tu dominio y pega los registros DNS que te da (SPF y DKIM).
   Esto es lo que evita que tus correos caigan en spam.
3. Abre el archivo `.env` y rellena `RESEND_API_KEY`, `MAIL_TO` y `MAIL_FROM`.
4. Reinicia el servidor.

> Mientras verificas el dominio puedes dejar `onboarding@resend.dev` en `MAIL_FROM`,
> pero esa dirección de prueba **solo puede escribirte a ti**: la confirmación al
> cliente no le llegará hasta que pongas tu propio dominio.

### Ver los contactos (panel privado)

Estas rutas muestran datos personales de tus clientes, así que están **protegidas
con la clave `ADMIN_KEY`** de tu archivo `.env`:

- **Lista completa:** `http://localhost:3000/api/leads?clave=TU_ADMIN_KEY`
- **Estadísticas:** `http://localhost:3000/api/stats?clave=TU_ADMIN_KEY`

Al arrancar el servidor, la consola imprime las dos direcciones ya con la clave
puesta: solo tienes que copiarlas.

`/api/stats` es tu herramienta de validación: te dice **qué construir primero** según
lo que la gente más pide, cuántos pidieron un MVP y cuántos llegaron con una cifra de
ahorro calculada (esos son los leads más calientes).

---

## 4.1. Qué protege la página

| Medida | Qué evita |
|--------|-----------|
| Clave en `/api/leads` y `/api/stats` | Que cualquiera descargue los datos de tus clientes |
| Campo trampa invisible en el formulario | Envíos automáticos de robots |
| Límite de 5 envíos por hora y por IP | Que alguien sature el formulario |
| Validación de correo y recorte de textos | Datos basura en la base de datos |
| Claves en `.env`, fuera del código | Que se filtren al subir el proyecto a git |

Si alguna vez crees que la `ADMIN_KEY` se filtró, genera otra y reinicia:

```bash
node -e "console.log(require('crypto').randomBytes(24).toString('base64url'))"
```

---

## 5. Cómo personalizar (lo más común)

### Cambiar los colores del tema
Abre `public/css/styles.css` y edita las variables del inicio (bloque `:root`):

```css
--accent:   #6c5ce7;   /* color principal (morado) */
--accent-2: #00d1b2;   /* color secundario (turquesa) */
```

Cambia esos dos valores y toda la página se re-colorea.

### Agregar, quitar o editar un servicio
Abre `public/js/data.js`. Cada servicio es un bloque así:

```js
{
  titulo: 'Nombre del servicio',
  gancho: 'Frase corta y llamativa',
  descripcion: 'Qué hace, explicado simple.',
  beneficio: 'El resultado que obtiene el cliente.'
}
```

Copia uno, cámbialo y guarda. La tarjeta aparece sola.

### Cambiar textos del hero o del proceso
Están en `public/index.html`, dentro de las secciones `<section class="hero">` y
`<section class="process">`.

---

## 6. Preguntas frecuentes

**¿Se pierde la información si apago el computador?**
No. Los leads quedan guardados en el archivo `data/leads.db`.

**¿Otros pueden ver mi página?**
Por ahora solo tú, en tu computador (`localhost`). Para que sea pública hay que
"desplegarla" en un hosting: lee la sección 7.

**¿Es seguro?**
El panel de leads está protegido con clave, el formulario tiene defensas contra
robots y las claves viven fuera del código. Al publicar en internet falta un solo
paso: usar **HTTPS** (los hostings de la sección 7 lo dan gratis y automático).

**¿Y si no configuro el correo?**
La página funciona igual y los leads se guardan. Solo tendrás que revisarlos a mano
entrando al panel.

---

## 7. Publicar la página en internet

La decisión importante es **dónde**, porque de eso depende si SQLite te sirve.

### Opción A — Servidor con disco propio (Railway, Render, Fly.io, un VPS)

**Recomendada. SQLite funciona tal como está.** Solo necesitas:

- Montar un **disco persistente** en la carpeta `data/`, para que `leads.db` sobreviva
  a los reinicios y despliegues.
- Cargar las variables del `.env` en el panel del proveedor (el archivo no se sube al
  repositorio, así que hay que copiarlas ahí a mano).

Aguanta miles de leads sin problema.

### Opción B — Vercel, Netlify o similares

**SQLite no funciona ahí.** Esos servicios no guardan archivos entre ejecuciones: cada
despliegue borraría todos tus contactos. Habría que migrar a una base administrada,
y **Supabase** (Postgres gratuito) es la más directa:

```sql
create table public.leads (
  id               bigint generated always as identity primary key,
  nombre           text not null,
  empresa          text,
  email            text not null,
  telefono         text,
  tipo_solicitud   text,
  servicio_interes text,
  mensaje          text,
  origen           text,
  ahorro_estimado  text,
  creado_en        timestamptz not null default now()
);

-- Con RLS activo y sin politicas, la tabla queda cerrada al publico:
-- solo el servidor, usando la clave service_role, puede leer y escribir.
alter table public.leads enable row level security;
```

Dos advertencias: la clave `service_role` **solo puede vivir en el servidor**, nunca
en el JavaScript del navegador, porque salta todas las reglas de seguridad. Y deja RLS
activado. El resto del código casi no cambia: se reemplazan las llamadas de `db.js` por
las de Supabase y el formulario queda igual.

### Respaldos

Con SQLite, copia `data/leads.db` a otro lado cada semana; es un solo archivo. Con
Supabase, los respaldos automáticos vienen incluidos.

---

## 8. Próximos pasos sugeridos (cuando validemos demanda)
1. Verificar tu dominio en Resend para que los correos no caigan en spam.
2. Publicar la página en internet (sección 7) y conectar un dominio propio.
3. Añadir aviso por WhatsApp para las solicitudes de MVP.
4. Crear un panel visual de leads con login, en vez de leer JSON.
5. Migrar a PostgreSQL/Supabase si el volumen crece.
