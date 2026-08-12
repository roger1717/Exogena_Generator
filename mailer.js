// ============================================================================
//  mailer.js  ->  Envia los correos cuando llega una solicitud
// ============================================================================
//  Manda dos correos por cada formulario recibido:
//    A) A TI: con los datos del cliente y el problema que escribio.
//       Lleva "replyTo" con el correo del cliente, asi respondes con el boton
//       "Responder" de tu bandeja y la respuesta le llega directo a el.
//    B) AL CLIENTE: una confirmacion de que recibiste su solicitud.
//       Sale desde MAIL_FROM (tu dominio), pero su "replyTo" apunta a MAIL_TO.
//       Gracias a eso no necesitas pagar un buzon en tu dominio: si el cliente
//       responde, su mensaje cae en el correo normal que ya lees.
//
//  Regla importante: si falta la configuracion o el envio falla, aqui NO se
//  lanza ningun error hacia arriba. El lead ya quedo guardado en la base de
//  datos y eso es lo que no se puede perder nunca.
//
//  Las claves se leen del archivo .env (nunca se escriben en el codigo).
// ============================================================================

const { Resend } = require('resend');

// ----------------------------------------------------------------------------
//  Cliente de Resend "perezoso": se crea la primera vez que se necesita.
//  Hacerlo asi es a proposito: el constructor de Resend falla si no hay clave,
//  y no queremos que el servidor se niegue a arrancar solo porque todavia no
//  has configurado el correo. Sin clave, la pagina sigue funcionando y los
//  leads se siguen guardando; simplemente no se envian avisos.
// ----------------------------------------------------------------------------
let clienteResend = null;

function obtenerCliente() {
  if (!process.env.RESEND_API_KEY || !process.env.MAIL_TO) {
    return null;
  }
  if (!clienteResend) {
    clienteResend = new Resend(process.env.RESEND_API_KEY);
  }
  return clienteResend;
}

// Avisa una sola vez en la consola si el correo no esta configurado,
// para no llenar el registro con el mismo mensaje en cada envio.
let yaAvisoFaltaConfig = false;

function correoConfigurado() {
  if (obtenerCliente()) return true;
  if (!yaAvisoFaltaConfig) {
    console.warn(
      '[MAIL] Sin configurar: falta RESEND_API_KEY o MAIL_TO en el archivo .env.\n' +
      '       Los leads se siguen guardando, pero no recibiras avisos por correo.'
    );
    yaAvisoFaltaConfig = true;
  }
  return false;
}

// ----------------------------------------------------------------------------
//  Utilidades de formato
// ----------------------------------------------------------------------------

// Evita que un texto escrito por el visitante rompa (o manipule) el HTML del correo
function escapar(texto) {
  return String(texto ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Dibuja una fila de la tabla de datos, y la omite si el campo viene vacio
function fila(etiqueta, valor) {
  if (!valor) return '';
  return `<tr>
      <td style="padding:7px 14px;color:#6b7280;white-space:nowrap;">${etiqueta}</td>
      <td style="padding:7px 14px;color:#111827;"><strong>${escapar(valor)}</strong></td>
    </tr>`;
}

// ----------------------------------------------------------------------------
//  A) EL AVISO PARA TI
// ----------------------------------------------------------------------------
async function avisarNuevoLead(lead) {
  if (!correoConfigurado()) return;

  // Las solicitudes de MVP se marcan en el asunto para que las veas de inmediato
  const esMvp = String(lead.tipo_solicitud || '').toLowerCase().includes('mvp');
  const etiquetaAhorro = lead.ahorro_estimado ? ` · ${lead.ahorro_estimado}` : '';
  const asunto = esMvp
    ? `[MVP] ${lead.nombre}${lead.empresa ? ' — ' + lead.empresa : ''}${etiquetaAhorro}`
    : `Nueva solicitud: ${lead.nombre}${etiquetaAhorro}`;

  const html = `
    <div style="font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;max-width:620px;color:#111827;">
      <h2 style="margin:0 0 2px;">Solicitud #${lead.id}${esMvp ? ' · MVP' : ''}</h2>
      <p style="color:#6b7280;margin:0 0 18px;font-size:14px;">
        Recibida el ${new Date().toLocaleString('es-CO')}
      </p>

      <table style="border-collapse:collapse;background:#f7f8fb;border-radius:10px;width:100%;font-size:15px;">
        ${fila('Nombre', lead.nombre)}
        ${fila('Empresa', lead.empresa)}
        ${fila('Email', lead.email)}
        ${fila('Teléfono', lead.telefono)}
        ${fila('Tipo', lead.tipo_solicitud)}
        ${fila('Servicio', lead.servicio_interes)}
        ${fila('Ahorro calculado', lead.ahorro_estimado)}
        ${fila('Origen', lead.origen)}
      </table>

      <h3 style="margin:22px 0 6px;">Su problema</h3>
      <p style="white-space:pre-wrap;background:#ffffff;border-left:3px solid #00d1b2;padding:12px 16px;margin:0;font-size:15px;line-height:1.6;">${escapar(lead.mensaje) || '<em style="color:#9ca3af;">No escribió mensaje.</em>'}</p>

      <p style="color:#6b7280;font-size:13px;margin-top:22px;">
        Pulsa «Responder» en este correo y tu respuesta le llega directamente a
        ${escapar(lead.email)}.
      </p>
    </div>`;

  // Ojo: el SDK devuelve { data, error } en lugar de lanzar una excepcion
  const { error } = await obtenerCliente().emails.send({
    from: process.env.MAIL_FROM || 'Automat-IA <onboarding@resend.dev>',
    to: process.env.MAIL_TO,
    replyTo: lead.email,
    subject: asunto,
    html
  });

  if (error) {
    console.error('[MAIL] No se pudo enviar el aviso interno:', error);
  } else {
    console.log(`[MAIL] Aviso enviado a ${process.env.MAIL_TO}`);
  }
}

// ----------------------------------------------------------------------------
//  B) LA CONFIRMACION PARA EL CLIENTE
// ----------------------------------------------------------------------------
//  Nota: con la direccion de pruebas onboarding@resend.dev este correo NO llega,
//  porque esa direccion solo puede escribirte a ti. Empieza a funcionar cuando
//  verifiques tu dominio en Resend y lo pongas en MAIL_FROM.
// ----------------------------------------------------------------------------
async function confirmarAlCliente(lead) {
  if (!correoConfigurado()) return;

  const esMvp = String(lead.tipo_solicitud || '').toLowerCase().includes('mvp');

  const html = `
    <div style="font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;max-width:620px;color:#111827;font-size:15px;line-height:1.6;">
      <p>Hola ${escapar(lead.nombre)},</p>
      <p>
        Recibí tu solicitud y ya la estoy revisando. Te respondo en menos de 24 horas
        ${esMvp
          ? 'con el alcance de un MVP para probar la solución con tus propios datos, el tiempo de entrega y lo que costaría.'
          : 'con una idea concreta de cómo automatizar lo que me contaste y cuánto podrías ahorrar al año.'}
      </p>
      ${lead.mensaje ? `
      <p style="color:#6b7280;margin-bottom:6px;">Esto fue lo que me escribiste:</p>
      <p style="white-space:pre-wrap;background:#f7f8fb;border-left:3px solid #6c5ce7;padding:12px 16px;margin:0 0 18px;">${escapar(lead.mensaje)}</p>` : ''}
      <p>Si quieres agregar algún detalle, responde este mismo correo.</p>
      <p style="margin-bottom:2px;">Un saludo,</p>
      <p style="margin-top:0;"><strong>Automat-IA</strong><br />
        <span style="color:#6b7280;font-size:14px;">Automatización inteligente para empresas que quieren crecer.</span>
      </p>
    </div>`;

  const { error } = await obtenerCliente().emails.send({
    from: process.env.MAIL_FROM || 'Automat-IA <onboarding@resend.dev>',
    to: lead.email,
    replyTo: process.env.MAIL_TO,
    subject: 'Recibí tu solicitud · Automat-IA',
    html
  });

  if (error) {
    console.error('[MAIL] No se pudo enviar la confirmación al cliente:', error);
  }
}

// ----------------------------------------------------------------------------
//  Envia los dos correos sin bloquear la respuesta al visitante.
//  server.js llama solo a esta funcion.
// ----------------------------------------------------------------------------
function notificarSolicitud(lead) {
  avisarNuevoLead(lead).catch((e) => console.error('[MAIL] aviso interno:', e));
  confirmarAlCliente(lead).catch((e) => console.error('[MAIL] confirmación:', e));
}

module.exports = { notificarSolicitud, avisarNuevoLead, confirmarAlCliente };
