// ============================================================================
//  data.js  ->  El "catalogo" de servicios que se muestran en la pagina
// ============================================================================
//  Aqui esta TODO el contenido de tus servicios, separado del diseno.
//  Si quieres agregar, quitar o cambiar un servicio, SOLO editas este archivo.
//  El archivo main.js lee esta lista y dibuja las tarjetas automaticamente.
//
//  Estructura:
//   - Cada NICHO tiene: id, nombre, icono (emoji), dolor (el problema) y servicios.
//   - Cada SERVICIO tiene: titulo, gancho (frase corta), descripcion y beneficio.
//
//  Ademas, cada nicho trae dos promedios que usa la CALCULADORA DE RETORNO:
//   - personasTipicas: cuanta gente suele hacer la tarea manual en ese sector.
//   - horasTipicas:    horas por semana que le dedica cada una.
//   - pctTipico:       que porcentaje del proceso suele ser automatizable.
//  Son puntos de partida razonables; el visitante puede cambiarlos.
// ============================================================================

const NICHOS = [
  {
    id: 'rrhh',
    nombre: 'Recursos Humanos',
    icono: '\u{1F465}', // emoji personas
    dolor: 'RR. HH. pierde horas en documentos y consultas repetitivas en lugar de enfocarse en las personas.',
    personasTipicas: 2,
    horasTipicas: 8,
    pctTipico: 70,
    servicios: [
      {
        titulo: 'Clasificador Inteligente de CVs',
        gancho: 'De 100 CVs a un ranking en minutos',
        descripcion: 'Sube 100 currículums en PDF y un agente extrae habilidades, años de experiencia y genera un ranking de coincidencia (match) según la vacante.',
        beneficio: 'Reduce el filtrado inicial de días a minutos.'
      },
      {
        titulo: 'Agente de Onboarding',
        gancho: 'El nuevo empleado, listo desde el día 1',
        descripcion: 'Secuencia que envía correos de bienvenida, recolecta documentos legales y crea las cuentas corporativas del nuevo empleado de forma automática.',
        beneficio: 'Cero olvidos y una primera impresión impecable.'
      },
      {
        titulo: 'Auditor de Nómina',
        gancho: 'Detecta errores de pago antes de pagarlos',
        descripcion: 'Cruza el reporte del reloj biométrico con el archivo de nómina para detectar horas extra no pagadas o ausencias no descontadas.',
        beneficio: 'Evita multas y pagos incorrectos cada mes.'
      },
      {
        titulo: 'Chatbot Interno de Políticas',
        gancho: 'Responde dudas del personal al instante',
        descripcion: 'Un agente entrenado con el manual del empleado que contesta al momento: «¿cuántos días de vacaciones me quedan?» o «¿cómo pido una licencia?».',
        beneficio: 'Menos interrupciones al equipo de RR. HH.'
      },
      {
        titulo: 'Programador de Entrevistas',
        gancho: 'Agenda entrevistas sin cadenas de correos',
        descripcion: 'Cruza los calendarios de los gerentes y envía propuestas de horario a los candidatos, agendando la reunión cuando el candidato elige.',
        beneficio: 'Adiós al ping-pong de correos para cuadrar horarios.'
      }
    ]
  },
  {
    id: 'marketing',
    nombre: 'Marketing y Ventas',
    icono: '\u{1F4C8}', // emoji grafico
    dolor: 'Los equipos comerciales pierden velocidad en tareas manuales que retrasan cada venta.',
    personasTipicas: 3,
    horasTipicas: 7,
    pctTipico: 70,
    servicios: [
      {
        titulo: 'Enriquecimiento de Leads',
        gancho: 'Convierte una lista de correos en oportunidades',
        descripcion: 'Toma un listado de posibles clientes, busca en la web sus perfiles profesionales y devuelve cargo, empresa y un resumen de lo que hacen.',
        beneficio: 'Tus vendedores hablan con contexto, no a ciegas.'
      },
      {
        titulo: 'Calificador de Correos Entrantes',
        gancho: 'Solo ves los clientes que valen la pena',
        descripcion: 'Lee los formularios de la web y los etiqueta como «Alta prioridad», «Soporte» o «Spam», enviando alertas solo por los prospectos valiosos.',
        beneficio: 'Cero leads valiosos perdidos en la bandeja.'
      },
      {
        titulo: 'Generador de Propuestas Comerciales',
        gancho: 'De notas sueltas a una propuesta en PDF',
        descripcion: 'Toma las notas de una reunión de ventas y redacta una propuesta formal y estructurada, lista en PDF para enviar.',
        beneficio: 'Envía propuestas el mismo día de la reunión.'
      },
      {
        titulo: 'Auditor de Presupuesto Publicitario',
        gancho: 'Frena el gasto descontrolado en anuncios',
        descripcion: 'Revisa a diario el gasto en Meta/Google Ads y avisa por Slack o WhatsApp si una campaña está gastando más de lo previsto.',
        beneficio: 'Protege tu presupuesto en tiempo real.'
      },
      {
        titulo: 'Monitor de Competencia',
        gancho: 'Entérate de los movimientos del rival',
        descripcion: 'Un bot que revisa cada semana los sitios de la competencia y genera un resumen de cambios: nuevos precios, servicios o promociones.',
        beneficio: 'Decisiones basadas en el mercado, no en suposiciones.'
      }
    ]
  },
  {
    id: 'logistica',
    nombre: 'Logística e Inventarios',
    icono: '\u{1F4E6}', // emoji caja
    dolor: 'La información llega fragmentada, en mil formatos y de muchos proveedores distintos.',
    personasTipicas: 3,
    horasTipicas: 10,
    pctTipico: 75,
    servicios: [
      {
        titulo: 'Extractor de Órdenes de Compra (OCR + IA)',
        gancho: 'Facturas en PDF convertidas en datos limpios',
        descripcion: 'Recibe facturas y órdenes de compra en PDF de distintos proveedores (cada uno con su diseño) y entrega los datos clave en CSV o Excel.',
        beneficio: 'Elimina la digitación manual y sus errores.'
      },
      {
        titulo: 'Trazabilidad Centralizada de Envíos',
        gancho: 'Todos tus paquetes en una sola pantalla',
        descripcion: 'Un panel conectado a las APIs de varias transportadoras que muestra el estado de todos los envíos de la empresa en un solo lugar.',
        beneficio: 'Respondes «¿dónde va mi pedido?» al instante.'
      },
      {
        titulo: 'Comparador de Cotizaciones',
        gancho: 'La mejor oferta, resaltada para ti',
        descripcion: 'Sube 3 cotizaciones en PDF y el agente arma una tabla comparativa con precio por unidad, tiempos de entrega y condiciones de pago.',
        beneficio: 'Decides el mejor proveedor en segundos.'
      },
      {
        titulo: 'Alertas Predictivas de Stock',
        gancho: 'Nunca más te quedes sin producto',
        descripcion: 'Analiza el historial de ventas y avisa cuándo pedir más producto antes de agotarlo, considerando los tiempos de entrega del proveedor.',
        beneficio: 'Menos quiebres de stock y menos capital detenido.'
      },
      {
        titulo: 'Clasificador de Devoluciones',
        gancho: 'Aprueba garantías con una foto',
        descripcion: 'El cliente sube una foto del producto dañado y la IA evalúa la imagen para aprobar o rechazar preliminarmente la garantía.',
        beneficio: 'Agiliza devoluciones y descongestiona soporte.'
      }
    ]
  },
  {
    id: 'inmobiliario',
    nombre: 'Sector Inmobiliario',
    icono: '\u{1F3E0}', // emoji casa
    dolor: 'En bienes raíces, la velocidad de respuesta es la diferencia entre ganar o perder la comisión.',
    personasTipicas: 2,
    horasTipicas: 6,
    pctTipico: 65,
    servicios: [
      {
        titulo: 'Matchmaker Inmobiliario',
        gancho: 'Sabe a qué cliente llamar hoy',
        descripcion: 'Cruza las propiedades disponibles con las preferencias de cada cliente (presupuesto, zona, habitaciones) y sugiere a quién contactar.',
        beneficio: 'Cierras más rápido conectando oferta y demanda.'
      },
      {
        titulo: 'Redactor Inmobiliario',
        gancho: 'Anuncios que venden, en segundos',
        descripcion: 'A partir de fotos y 5 datos clave de una propiedad, redacta un texto persuasivo listo para publicar en portales.',
        beneficio: 'Publica más propiedades con textos de calidad.'
      },
      {
        titulo: 'Filtro de Inquilinos',
        gancho: 'Solo asesoras a inquilinos calificados',
        descripcion: 'Recolecta los documentos financieros de los interesados, verifica que estén completos y calcula su capacidad de pago antes de pasarlos al asesor.',
        beneficio: 'Ahorras tiempo y reduces el riesgo de impago.'
      },
      {
        titulo: 'Sincronizador de Portales',
        gancho: 'Marca «Vendida» una vez, se actualiza en todos',
        descripcion: 'Al marcar una propiedad como vendida en una hoja de cálculo, actualiza su estado automáticamente en todos los portales inmobiliarios.',
        beneficio: 'Cero anuncios desactualizados o vergonzosos.'
      },
      {
        titulo: 'Agendador de Recorridos por WhatsApp',
        gancho: 'Un asistente que agenda visitas por ti',
        descripcion: 'Responde por WhatsApp preguntas básicas de la propiedad y permite al interesado agendar una visita en los horarios libres del agente.',
        beneficio: 'Captas interesados incluso fuera de horario.'
      }
    ]
  },
  {
    id: 'salud',
    nombre: 'Clínicas y Salud',
    icono: '\u{1FA7A}', // emoji estetoscopio
    dolor: 'Los profesionales de la salud pierden tiempo valioso en tareas administrativas y gestión de pacientes.',
    personasTipicas: 3,
    horasTipicas: 9,
    pctTipico: 65,
    servicios: [
      {
        titulo: 'Confirmador de Citas Inteligente',
        gancho: 'Llena los espacios de las cancelaciones',
        descripcion: 'Un bot de WhatsApp confirma la cita un día antes; si el paciente cancela, ofrece el espacio al siguiente en la lista de espera.',
        beneficio: 'Menos huecos en la agenda, más ingresos.'
      },
      {
        titulo: 'Estructurador de Historias Clínicas',
        gancho: 'El médico revisa, no transcribe',
        descripcion: 'Graba (con consentimiento) la consulta y genera un borrador estructurado de la historia clínica para que el médico solo revise y apruebe.',
        beneficio: 'Devuelve horas de escritura a cada profesional.'
      },
      {
        titulo: 'Clasificador de Resultados de Laboratorio',
        gancho: 'Los valores críticos, resaltados en rojo',
        descripcion: 'Lee los PDF de laboratorio entrantes y resalta los valores fuera de rango para la revisión prioritaria del médico.',
        beneficio: 'Prioriza casos urgentes sin leerlo todo.'
      },
      {
        titulo: 'Automatización de Facturación a Seguros',
        gancho: 'Menos facturas rechazadas por aseguradoras',
        descripcion: 'Cruza los servicios prestados con las reglas de cobro de cada aseguradora para evitar rechazos en las facturas.',
        beneficio: 'Cobras más rápido y con menos errores.'
      },
      {
        titulo: 'Seguimiento Post-Consulta',
        gancho: 'Tus pacientes se sienten acompañados',
        descripcion: 'Contacta al paciente 3 días después de la cita para preguntar cómo sigue y alerta al médico si hay complicaciones.',
        beneficio: 'Mejor experiencia y detección temprana de riesgos.'
      }
    ]
  },
  {
    id: 'contabilidad',
    nombre: 'Contabilidad y Finanzas',
    icono: '\u{1F9FE}', // emoji recibo
    dolor: 'Los equipos contables pierden días en digitación, conciliaciones y reportes manuales llenos de riesgo de error.',
    personasTipicas: 3,
    horasTipicas: 12,
    pctTipico: 80,
    servicios: [
      {
        titulo: 'Lector Automático de Facturas y Recibos',
        gancho: 'Del PDF o la foto al asiento contable',
        descripcion: 'Recibe facturas y recibos en PDF o imagen, extrae proveedor, fecha, montos e impuestos, y los entrega listos para el sistema contable.',
        beneficio: 'Elimina horas de digitación y errores de tipeo.'
      },
      {
        titulo: 'Conciliación Bancaria Automática',
        gancho: 'Cuadra el banco con tus libros solo',
        descripcion: 'Cruza el extracto bancario con los registros contables, empareja los movimientos y resalta las diferencias que requieren revisión.',
        beneficio: 'Cierra el mes en horas, no en días.'
      },
      {
        titulo: 'Clasificador de Gastos',
        gancho: 'Cada gasto en su categoría correcta',
        descripcion: 'Analiza los movimientos y los clasifica automáticamente por categoría contable, aprendiendo de tus reglas y correcciones.',
        beneficio: 'Reportes limpios sin clasificar a mano.'
      },
      {
        titulo: 'Alertas y Calendario Tributario',
        gancho: 'Nunca más una multa por vencimiento',
        descripcion: 'Un agente que vigila fechas de impuestos y obligaciones, y envía recordatorios antes de cada vencimiento por correo o WhatsApp.',
        beneficio: 'Evita sanciones y sobrecostos por olvidos.'
      },
      {
        titulo: 'Generador de Reportes Financieros',
        gancho: 'Tus números clave, listos cada mes',
        descripcion: 'Toma los datos contables y arma automáticamente reportes de flujo de caja, ingresos frente a gastos y estado de resultados en un formato claro.',
        beneficio: 'Decisiones basadas en datos, sin armar Excel a mano.'
      }
    ]
  },
  {
    id: 'atencion',
    nombre: 'Atención al Cliente',
    icono: '\u{1F4AC}', // emoji globo de dialogo
    dolor: 'El soporte se satura respondiendo las mismas preguntas una y otra vez, y los clientes esperan demasiado.',
    personasTipicas: 4,
    horasTipicas: 14,
    pctTipico: 75,
    servicios: [
      {
        titulo: 'Chatbot de Soporte 24/7',
        gancho: 'Responde a tus clientes incluso de madrugada',
        descripcion: 'Un agente entrenado con tu información (productos, políticas, preguntas frecuentes) que responde al instante por web o WhatsApp y escala al humano si hace falta.',
        beneficio: 'Atiendes más clientes sin ampliar el equipo.'
      },
      {
        titulo: 'Clasificador y Enrutador de Tickets',
        gancho: 'Cada consulta llega a quien debe',
        descripcion: 'Lee los mensajes entrantes, detecta el tema y la urgencia, y los asigna al área o persona correcta con la prioridad adecuada.',
        beneficio: 'Menos tiempos de respuesta y nada se pierde.'
      },
      {
        titulo: 'Resumidor de Conversaciones',
        gancho: 'El contexto del cliente en 3 líneas',
        descripcion: 'Resume hilos largos de correo o chat para que el agente entienda el caso en segundos, sin leer todo el historial.',
        beneficio: 'Respuestas más rápidas y con contexto.'
      },
      {
        titulo: 'Analizador de Satisfacción (Sentimiento)',
        gancho: 'Detecta al cliente molesto a tiempo',
        descripcion: 'Analiza mensajes y encuestas para medir el ánimo del cliente y alerta cuando alguien está a punto de irse o quejarse.',
        beneficio: 'Actúas antes de perder al cliente.'
      },
      {
        titulo: 'Base de Conocimiento Automática',
        gancho: 'Convierte tus respuestas en artículos de ayuda',
        descripcion: 'A partir de las consultas más frecuentes, genera y mantiene una sección de preguntas frecuentes y guías de ayuda actualizadas.',
        beneficio: 'Los clientes se autoatienden y bajan los tickets.'
      }
    ]
  },
  {
    id: 'ecommerce',
    nombre: 'E-commerce y Retail',
    icono: '\u{1F6D2}', // emoji carrito
    dolor: 'Las tiendas en línea manejan cientos de productos, pedidos y mensajes que consumen tiempo y generan errores.',
    personasTipicas: 3,
    horasTipicas: 10,
    pctTipico: 75,
    servicios: [
      {
        titulo: 'Generador de Descripciones de Producto',
        gancho: 'Fichas que venden, en masa',
        descripcion: 'A partir de los datos y fotos de un producto, redacta descripciones persuasivas y optimizadas para buscadores, en lote.',
        beneficio: 'Publica cientos de productos sin escribir uno a uno.'
      },
      {
        titulo: 'Monitor de Precios de la Competencia',
        gancho: 'Siempre con el precio justo',
        descripcion: 'Revisa los precios de la competencia y te avisa cuándo debes ajustar para no perder ventas ni margen.',
        beneficio: 'Compites informado, no a ciegas.'
      },
      {
        titulo: 'Gestor Automático de Pedidos',
        gancho: 'Del pedido al envío sin tocar nada',
        descripcion: 'Procesa pedidos entrantes, actualiza inventario, genera la guía de envío y notifica al cliente automáticamente.',
        beneficio: 'Menos errores y despachos más rápidos.'
      },
      {
        titulo: 'Recuperador de Carritos Abandonados',
        gancho: 'Rescata las ventas que se iban a perder',
        descripcion: 'Detecta carritos abandonados y envía mensajes automáticos por correo o WhatsApp con un recordatorio o incentivo para cerrar la compra.',
        beneficio: 'Recuperas ingresos que ya dabas por perdidos.'
      },
      {
        titulo: 'Analizador de Reseñas',
        gancho: 'Escucha lo que dicen tus compradores',
        descripcion: 'Recopila y resume las reseñas de tus productos, detecta quejas recurrentes y destaca lo que más valoran los clientes.',
        beneficio: 'Mejoras producto y servicio con datos reales.'
      }
    ]
  },
  {
    id: 'legal',
    nombre: 'Servicios Legales',
    icono: '\u{2696}', // emoji balanza
    dolor: 'Los despachos legales invierten horas caras revisando documentos extensos y tareas administrativas repetitivas.',
    personasTipicas: 2,
    horasTipicas: 8,
    pctTipico: 70,
    servicios: [
      {
        titulo: 'Analizador de Contratos',
        gancho: 'Revisa cláusulas de riesgo en minutos',
        descripcion: 'Lee contratos largos, resume los puntos clave y resalta cláusulas de riesgo o poco habituales para la revisión del abogado.',
        beneficio: 'Revisiones más rápidas sin perder detalle.'
      },
      {
        titulo: 'Generador de Documentos Legales',
        gancho: 'Borradores listos a partir de plantillas',
        descripcion: 'A partir de unos pocos datos del caso, genera borradores de contratos, cartas o demandas usando tus plantillas.',
        beneficio: 'Produce documentos en minutos, no horas.'
      },
      {
        titulo: 'Buscador en Expedientes',
        gancho: 'Encuentra ese dato entre miles de páginas',
        descripcion: 'Un agente que busca dentro de expedientes y documentos extensos y responde preguntas concretas citando la fuente.',
        beneficio: 'Deja de hojear carpetas enteras.'
      },
      {
        titulo: 'Seguimiento de Plazos y Vencimientos',
        gancho: 'Ningún término se te vuelve a pasar',
        descripcion: 'Vigila fechas de audiencias, términos y vencimientos, y envía alertas anticipadas al responsable de cada caso.',
        beneficio: 'Evita sanciones y pérdidas por olvidos.'
      },
      {
        titulo: 'Asistente de Admisión de Clientes',
        gancho: 'Filtra y organiza cada consulta nueva',
        descripcion: 'Recolecta la información inicial del cliente, organiza los documentos y prepara un resumen del caso antes de la primera reunión.',
        beneficio: 'Llegas a la reunión con todo listo.'
      }
    ]
  }
];

// Hacemos la lista disponible para main.js
window.NICHOS = NICHOS;
