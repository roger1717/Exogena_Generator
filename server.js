// ============================================================================
//  server.js  ->  El servidor web de Automat-IA (Node.js + Express)
// ============================================================================
//  Este archivo hace 4 cosas:
//   1. Sirve la pagina web (archivos HTML/CSS/JS de la carpeta /public).
//   2. Recibe los formularios de contacto y los guarda en la base de datos.
//   3. Te avisa por correo de cada solicitud nueva (ver mailer.js).
//   4. Ofrece una API PRIVADA para consultar los leads (tu "panel" interno).
//
//  Las claves (correo, base de datos y contrasena del panel) se leen del
//  archivo .env en tu computador, y de las "Environment Variables" del
//  panel de Vercel cuando la pagina esta publicada.
//
//  Nota sobre Vercel: en produccion este archivo NO enciende un servidor con
//  puerto propio. Vercel importa "app" (la ultima linea) y lo convierte en
//  una funcion que se despierta por cada peticion. El "app.listen" de mas
//  abajo solo corre cuando trabajas en tu computador con "npm run dev".
// ============================================================================

const express = require('express');      // Framework web que simplifica todo
const path = require('node:path');       // Para armar rutas de carpetas
const { pool, listoParaUsar } = require('./db'); // Nuestra base de datos (db.js)
const { notificarSolicitud } = require('./mailer'); // Envio de correos

const app = express();                   // Creamos la aplicacion Express
const PORT = process.env.PORT || 3000;   // Puerto donde correra (localhost:3000)

// ----------------------------------------------------------------------------
//  MIDDLEWARES  (funciones que procesan cada peticion antes de responder)
// ----------------------------------------------------------------------------

// Permite que el servidor entienda datos enviados en formato JSON (el formulario).
// El limite evita que alguien intente saturar el servidor con un envio gigante.
app.use(express.json({ limit: '32kb' }));

// Necesario para que req.ip sea la IP real cuando la pagina este publicada
// detras de un proxy (Vercel, Render, Nginx...). Sin esto, el limite de
// envios por IP contaria a todos los visitantes como si fueran uno solo.
app.set('trust proxy', 1);

// Sirve /public cuando corres el proyecto en tu computador (npm run dev).
// En Vercel esta linea se ignora: los archivos de /public los reparte
// directamente su CDN, que es mas rapido.
app.use(express.static(path.join(__dirname, 'public')));

// Antes de atender cualquier peticion a la API, nos asegura de que las
// tablas de la base de datos ya existan (ver db.js). La primera peticion
// espera un instante; el resto no nota nada porque la promesa ya esta resuelta.
app.use(async (req, res, next) => {
  try {
    await listoParaUsar;
    next();
  } catch (err) {
    next(err);
  }
});

// ============================================================================
//  SEGURIDAD
// ============================================================================

// ----------------------------------------------------------------------------
//  1) Candado del panel interno
// ----------------------------------------------------------------------------
//  Las rutas que MUESTRAN datos de clientes son solo para ti. Sin este filtro,
//  cualquiera que escriba la direccion podria descargar los nombres, correos y
//  telefonos de todos tus contactos.
//
//  La clave se define en el archivo .env (ADMIN_KEY) y se usa asi:
//    http://localhost:3000/api/leads?clave=TU_CLAVE
// ----------------------------------------------------------------------------
function soloAdmin(req, res, next) {
  const claveConfigurada = process.env.ADMIN_KEY;

  // Sin clave configurada, el panel queda cerrado a todo el mundo.
  // Preferimos que no funcione a que quede abierto por accidente.
  if (!claveConfigurada) {
    console.warn('[SEGURIDAD] Falta ADMIN_KEY en .env: el panel esta cerrado.');
    return res.status(503).json({
      ok: false,
      error: 'Panel no configurado. Define ADMIN_KEY en el archivo .env.'
    });
  }

  const claveRecibida = req.query.clave || req.get('x-admin-key');
  if (claveRecibida !== claveConfigurada) {
    console.warn(`[SEGURIDAD] Intento de acceso al panel desde ${req.ip}`);
    return res.status(401).json({ ok: false, error: 'No autorizado.' });
  }

  next();
}

// ----------------------------------------------------------------------------
//  2) Limite de envios por IP
// ----------------------------------------------------------------------------
//  Impide que un robot (o alguien molesto) mande cientos de formularios.
//  Permitimos 5 envios por hora desde la misma direccion.
//
//  Antes este conteo vivia en la memoria del servidor (un Map). En Vercel
//  cada peticion puede caer en una copia distinta de la funcion, asi que la
//  memoria no es confiable: el conteo ahora se guarda en la tabla "envios_ip"
//  de la base de datos, que es la misma para todas las copias.
// ----------------------------------------------------------------------------
const MAX_ENVIOS_POR_HORA = 5;

async function limitarEnvios(req, res, next) {
  try {
    const { rows } = await pool.query(
      `SELECT COUNT(*)::int AS total FROM envios_ip
       WHERE ip = $1 AND creado_en > now() - interval '1 hour'`,
      [req.ip]
    );

    if (rows[0].total >= MAX_ENVIOS_POR_HORA) {
      return res.status(429).json({
        ok: false,
        error: 'Recibimos varias solicitudes tuyas. Intenta de nuevo en un rato o escríbenos por correo.'
      });
    }

    await pool.query('INSERT INTO envios_ip (ip) VALUES ($1)', [req.ip]);
    next();
  } catch (err) {
    console.error('[SEGURIDAD] Error revisando el límite de envíos:', err);
    // Si la base de datos falla, dejamos pasar el envio: es preferible
    // arriesgar un poco de spam a perder un lead real por un error nuestro.
    next();
  }
}

// Recorta los textos larguisimos antes de guardarlos
function limpiar(valor, maximo = 2000) {
  if (valor === undefined || valor === null) return null;
  const texto = String(valor).trim();
  return texto ? texto.slice(0, maximo) : null;
}

// ============================================================================
//  RUTAS
// ============================================================================

// ----------------------------------------------------------------------------
//  RUTA 1 (publica): Recibir un lead del formulario
//  Metodo POST en /api/leads
// ----------------------------------------------------------------------------
app.post('/api/leads', limitarEnvios, async (req, res) => {
  // Campo trampa: es invisible en la pagina, asi que una persona real nunca lo
  // llena. Si viene con texto, es un robot. Respondemos "ok" para que no
  // reintente, pero no guardamos nada ni te enviamos correo.
  if (req.body.sitio_web) {
    console.log(`[SPAM] Envio descartado por campo trampa (${req.ip})`);
    return res.status(201).json({ ok: true });
  }

  // Sacamos los datos que envio el navegador (definidos en public/index.html)
  const nombre = limpiar(req.body.nombre, 120);
  const empresa = limpiar(req.body.empresa, 120);
  const email = limpiar(req.body.email, 160);
  const telefono = limpiar(req.body.telefono, 40);
  const tipo_solicitud = limpiar(req.body.tipo_solicitud, 80);
  const servicio_interes = limpiar(req.body.servicio_interes, 160);
  const mensaje = limpiar(req.body.mensaje, 4000);
  const origen = limpiar(req.body.origen, 160);
  const ahorro_estimado = limpiar(req.body.ahorro_estimado, 60);

  // Validacion: nombre y email son obligatorios, y el correo debe tener forma de correo
  if (!nombre || !email) {
    return res.status(400).json({ ok: false, error: 'Nombre y email son obligatorios.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Revisa el correo: no parece válido.' });
  }

  // Sin autorizacion no podemos guardar datos personales (Ley 1581 de 2012).
  // El navegador ya lo exige, pero lo revalidamos aqui por si alguien envia
  // la peticion saltandose el formulario.
  if (!req.body.consentimiento) {
    return res.status(400).json({
      ok: false,
      error: 'Necesitamos tu autorización para tratar los datos.'
    });
  }
  // Guardamos la fecha exacta en que autorizo: eso es lo que sirve como prueba
  const consentimiento = `Autorizado el ${new Date().toISOString()}`;

  try {
    // Usamos $1, $2... en vez de "?" (asi marca los parametros Postgres) para
    // evitar inyeccion de codigo (seguro), igual que antes con SQLite.
    const { rows } = await pool.query(
      `INSERT INTO leads
        (nombre, empresa, email, telefono, tipo_solicitud, servicio_interes,
         mensaje, origen, ahorro_estimado, consentimiento)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
       RETURNING id`,
      [nombre, empresa, email, telefono, tipo_solicitud, servicio_interes,
        mensaje, origen, ahorro_estimado, consentimiento]
    );
    const id = rows[0].id;

    const ahorroLog = ahorro_estimado ? ` | ahorro estimado: ${ahorro_estimado}` : '';
    console.log(
      `[NUEVO LEAD] #${id} - ${nombre} (${email}) | ` +
      `${tipo_solicitud || 'sin tipo'} | ${servicio_interes || 'general'}${ahorroLog}`
    );

    // Enviamos los correos SIN esperar a que terminen: el lead ya esta guardado
    // y el visitante recibe su "gracias" al instante. Si el correo falla, se ve
    // en la consola, pero el contacto nunca se pierde.
    notificarSolicitud({
      id, nombre, empresa, email, telefono,
      tipo_solicitud, servicio_interes, mensaje, origen, ahorro_estimado
    });

    return res.status(201).json({ ok: true, id });
  } catch (err) {
    console.error('Error guardando lead:', err);
    return res.status(500).json({ ok: false, error: 'No se pudo guardar el contacto.' });
  }
});

// ----------------------------------------------------------------------------
//  RUTA 2 (privada): Ver todos los leads (tu panel interno)
//  Abre en el navegador: http://localhost:3000/api/leads?clave=TU_ADMIN_KEY
// ----------------------------------------------------------------------------
app.get('/api/leads', soloAdmin, async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM leads ORDER BY creado_en DESC');
    return res.json({ ok: true, total: rows.length, leads: rows });
  } catch (err) {
    console.error('Error leyendo leads:', err);
    return res.status(500).json({ ok: false, error: 'No se pudieron leer los contactos.' });
  }
});

// ----------------------------------------------------------------------------
//  RUTA 3 (privada): Estadisticas rapidas (que servicio genera mas interes)
//  Esto es ORO para tu validacion: te dice que construir primero.
//  Abre en el navegador: http://localhost:3000/api/stats?clave=TU_ADMIN_KEY
// ----------------------------------------------------------------------------
app.get('/api/stats', soloAdmin, async (req, res) => {
  try {
    const porServicio = (await pool.query(`
      SELECT servicio_interes AS servicio, COUNT(*) AS total
      FROM leads
      WHERE servicio_interes IS NOT NULL
      GROUP BY servicio_interes
      ORDER BY total DESC
    `)).rows;

    const porTipo = (await pool.query(`
      SELECT tipo_solicitud AS tipo, COUNT(*) AS total
      FROM leads
      WHERE tipo_solicitud IS NOT NULL
      GROUP BY tipo_solicitud
      ORDER BY total DESC
    `)).rows;

    const totalLeads = (await pool.query('SELECT COUNT(*) AS n FROM leads')).rows[0].n;

    // Cuantos leads llegaron con una cifra de ahorro calculada: son los mas calientes,
    // porque el visitante ya se convencio solo mirando sus propios numeros.
    const conCalculo = (await pool.query(`
      SELECT COUNT(*) AS n FROM leads WHERE ahorro_estimado IS NOT NULL AND ahorro_estimado <> ''
    `)).rows[0].n;

    return res.json({
      ok: true,
      total_leads: Number(totalLeads),
      leads_con_ahorro_calculado: Number(conCalculo),
      solicitudes_por_tipo: porTipo,
      interes_por_servicio: porServicio
    });
  } catch (err) {
    console.error('Error calculando estadisticas:', err);
    return res.status(500).json({ ok: false, error: 'No se pudieron calcular las estadísticas.' });
  }
});

// ----------------------------------------------------------------------------
//  Encendemos el servidor SOLO cuando corres este archivo directamente
//  (node server.js / npm start / npm run dev). Cuando Vercel importa este
//  archivo como modulo para convertirlo en funcion, "require.main" no es
//  este archivo y por lo tanto nunca se llama app.listen: Vercel maneja el
//  ciclo de vida del servidor por su cuenta.
// ----------------------------------------------------------------------------
if (require.main === module) {
  app.listen(PORT, () => {
    const clave = process.env.ADMIN_KEY;
    const sufijo = clave ? `?clave=${clave}` : '?clave=FALTA_ADMIN_KEY_EN_.ENV';

    console.log('====================================================');
    console.log('  Automat-IA corriendo!');
    console.log(`  Abre en tu navegador: http://localhost:${PORT}`);
    console.log(`  Ver leads:            http://localhost:${PORT}/api/leads${sufijo}`);
    console.log(`  Ver estadisticas:     http://localhost:${PORT}/api/stats${sufijo}`);
    console.log('----------------------------------------------------');
    console.log(`  Base de datos:        ${process.env.DATABASE_URL ? 'Postgres (Supabase)' : 'NO CONFIGURADA (falta DATABASE_URL en .env)'}`);
    console.log(`  Panel protegido:      ${clave ? 'si' : 'NO (define ADMIN_KEY en .env)'}`);
    console.log(`  Avisos por correo:    ${process.env.RESEND_API_KEY && process.env.MAIL_TO ? 'activos -> ' + process.env.MAIL_TO : 'sin configurar (revisa .env)'}`);
    console.log('====================================================');
  });
}

module.exports = app;
