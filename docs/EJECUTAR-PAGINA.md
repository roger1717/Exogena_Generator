# Cómo ejecutar Automat-IA localmente

Esta guía explica cómo iniciar la página en tu computador para verla en el navegador.

## Requisitos

Necesitas tener instalado:

- **Node.js** (versión 22 o superior recomendada).
- **npm**, que se instala junto a Node.js.

Verifica que estén disponibles abriendo una terminal y ejecutando:

```bash
node --version
npm --version
```

Si ambos comandos muestran un número de versión, puedes continuar.

## Paso 1: abre una terminal en el proyecto

Ubícate dentro de la carpeta del proyecto:

```bash
cd "/Users/rh/Documents/proyectos/RH-AUTOM"
```

> En Cursor también puedes abrir la terminal integrada con ``Ctrl + ` ``.

## Paso 2: instala las dependencias

Este paso solo es necesario la primera vez, o si borras la carpeta `node_modules`:

```bash
npm install
```

Esto instala Express (el servidor que muestra la página y guarda los formularios) y Resend (el que envía los correos).

## Paso 3: inicia el servidor

Ejecuta:

```bash
npm start
```

Deberías ver un resultado similar a:

```text
Automat-IA corriendo!
Abre en tu navegador: http://localhost:3000
Ver leads:            http://localhost:3000/api/leads?clave=...
----------------------------------------------------
Panel protegido:      si
Avisos por correo:    activos -> tucorreo@gmail.com
```

Esas dos últimas líneas te dicen de un vistazo si la seguridad y el correo están bien configurados. Si dicen `sin configurar`, revisa el archivo `.env`.

No cierres esta terminal mientras estés usando la página: el servidor debe permanecer encendido.

## Paso 4: abre el frontend

En tu navegador, abre:

```text
http://localhost:3000
```

Ahí verás la landing page de Automat-IA con los nichos, servicios y formulario de contacto.

## Paso 5: prueba el formulario

1. Selecciona un servicio o pulsa el botón **“Lo quiero”** en una tarjeta.
2. Completa como mínimo tu nombre y correo.
3. Envía la solicitud.
4. Deberías ver el mensaje de confirmación.

Los datos se guardan localmente en `data/leads.db`. Si ya configuraste el correo en el archivo `.env`, además te llega un email con la solicitud; si no, en la terminal verás un aviso recordándotelo, pero el contacto queda guardado igual.

## Consultar los datos guardados

Estas rutas muestran datos personales de tus clientes, así que piden la clave `ADMIN_KEY` que está en tu archivo `.env`:

- Lista de contactos: `http://localhost:3000/api/leads?clave=TU_ADMIN_KEY`
- Estadísticas por servicio: `http://localhost:3000/api/stats?clave=TU_ADMIN_KEY`

No tienes que buscar la clave a mano: al arrancar, el servidor imprime las dos direcciones ya completas para que las copies.

Sin la clave correcta, la respuesta es `No autorizado`. No compartas estos enlaces con nadie.

## Detener la página

Vuelve a la terminal donde ejecutaste `npm start` y presiona:

```text
Ctrl + C
```

Después de eso, `http://localhost:3000` dejará de funcionar hasta que vuelvas a iniciar el servidor.

## Modo desarrollo (opcional)

Si vas a modificar `server.js` o `db.js` con frecuencia, puedes usar:

```bash
npm run dev
```

Este modo reinicia el servidor automáticamente cuando cambias archivos del backend. Después de modificar HTML, CSS o JavaScript del frontend, normalmente solo necesitas guardar y actualizar el navegador.

## Solución de problemas

### El navegador no abre la página

Confirma que la terminal siga mostrando el servidor activo y que abriste exactamente:

```text
http://localhost:3000
```

### Dice que `npm` o `node` no existen

Node.js no está instalado o la terminal no lo reconoce. Instálalo desde [nodejs.org](https://nodejs.org/) y reinicia la terminal.

### Aparece `EADDRINUSE` o “port 3000 already in use”

Ya hay otro servidor usando el puerto 3000. Cierra la otra terminal que tenga la página ejecutándose o detén el proceso con `Ctrl + C`, y vuelve a intentar `npm start`.

### El formulario no guarda los datos

Verifica que abriste la página desde `http://localhost:3000` y no haciendo doble clic en `public/index.html`. El formulario necesita que el servidor Node esté encendido para guardar los leads.
