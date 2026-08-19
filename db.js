// ============================================================================
//  db.js  ->  Configuracion de la base de datos (Postgres, alojado en Supabase)
// ============================================================================
//  Antes usabamos SQLite (un archivo en el disco). En Vercel el disco no se
//  puede escribir de forma permanente, asi que la base de datos vive afuera,
//  en Supabase (Postgres administrado). El codigo que la usa en server.js
//  cambia poco: en vez de ".prepare().run()" ahora se hace "await pool.query()".
//
//  La direccion de conexion se lee de la variable DATABASE_URL en el .env
//  (o en las variables de entorno del panel de Vercel en produccion).
// ============================================================================

const { Pool } = require('pg');

if (!process.env.DATABASE_URL) {
  console.error(
    '[DB] Falta DATABASE_URL en el archivo .env. Copia la cadena de conexion ' +
    'desde Supabase (Project Settings -> Database -> Connection string -> ' +
    'modo "Transaction pooler") y pegala ahi.'
  );
}

// Un "Pool" reutiliza conexiones abiertas en vez de crear una nueva por cada
// consulta. Supabase exige SSL incluso en el plan gratis; { rejectUnauthorized: false }
// evita que Node rechace el certificado intermedio que usa su proxy de conexion.
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Crea las tablas si todavia no existen. Se llama una vez al arrancar el
// servidor (ver el final de este archivo) y tambien se puede volver a llamar
// sin riesgo: "IF NOT EXISTS" hace que sea seguro repetirlo.
async function inicializar() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS leads (
      id               SERIAL PRIMARY KEY,
      nombre           TEXT NOT NULL,
      empresa          TEXT,
      email            TEXT NOT NULL,
      telefono         TEXT,
      tipo_solicitud   TEXT,
      servicio_interes TEXT,
      mensaje          TEXT,
      origen           TEXT,
      ahorro_estimado  TEXT,
      consentimiento   TEXT,
      creado_en        TIMESTAMPTZ NOT NULL DEFAULT now()
    )
  `);

  // Tabla del limitador anti-spam (ver server.js). Antes vivia en memoria del
  // servidor; en Vercel cada peticion puede caer en una instancia distinta,
  // asi que el conteo tiene que quedar en la base de datos para ser confiable.
  await pool.query(`
    CREATE TABLE IF NOT EXISTS envios_ip (
      id        SERIAL PRIMARY KEY,
      ip        TEXT NOT NULL,
      creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
    )
  `);
  await pool.query(`
    CREATE INDEX IF NOT EXISTS envios_ip_ip_fecha_idx ON envios_ip (ip, creado_en)
  `);
}

// Se dispara al importar el modulo. Si falla (por ejemplo, DATABASE_URL mal
// copiada), lo vemos enseguida en los logs en vez de descubrirlo cuando
// alguien llene el formulario.
const listoParaUsar = inicializar().catch((err) => {
  console.error('[DB] No se pudo preparar la base de datos:', err.message);
});

module.exports = { pool, listoParaUsar };
