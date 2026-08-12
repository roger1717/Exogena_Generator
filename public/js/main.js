// ============================================================================
//  main.js  ->  Toda la interactividad de la pagina
// ============================================================================
//  Que hace este archivo:
//   1) Dibuja los botones de nicho y las tarjetas de servicio (leyendo data.js).
//   2) El boton "Lo quiero" de cada tarjeta rellena el formulario y baja hasta el.
//   3) Calcula el retorno en dinero (la seccion "antes vs. despues").
//   4) Envia el formulario al servidor (/api/leads) y muestra el resultado.
//   5) Maneja el menu movil y el ano del footer.
//
//  "document.querySelector('...')" = buscar un elemento del HTML.
//  "addEventListener('click', ...)" = ejecutar algo cuando ocurre un evento.
// ============================================================================

// Esperamos a que el HTML este cargado antes de tocar sus elementos
document.addEventListener('DOMContentLoaded', () => {

  // ----- Referencias a elementos del HTML que vamos a usar -----
  const tabs = document.getElementById('tabs');
  const grid = document.getElementById('servicesGrid');
  const servicioSelect = document.getElementById('servicioSelect');
  const origenInput = document.getElementById('origenInput');
  const ahorroInput = document.getElementById('ahorroInput');
  const mensajeInput = document.getElementById('mensajeInput');
  const form = document.getElementById('leadForm');

  // NICHOS viene de data.js (la lista de sectores y servicios)
  let nichoActivo = NICHOS[0].id; // por defecto mostramos el primer nicho

  // Contadores reales del hero (asi nunca quedan desactualizados al editar data.js)
  const totalServicios = NICHOS.reduce((suma, n) => suma + n.servicios.length, 0);
  document.getElementById('statSectores').textContent = NICHOS.length;
  document.getElementById('statServicios').textContent = `${totalServicios}+`;

  // Lleva el foco al formulario y lo resalta un instante
  function irAlFormulario() {
    document.getElementById('contacto').scrollIntoView({ behavior: 'smooth' });
    form.style.transition = 'box-shadow .3s';
    form.style.boxShadow = '0 0 0 3px rgba(0,209,178,.5)';
    setTimeout(() => (form.style.boxShadow = ''), 1200);
  }

  // ==========================================================================
  //  1) DIBUJAR LOS BOTONES DE NICHO (tabs) Y LLENAR LOS SELECT
  // ==========================================================================
  const roiSector = document.getElementById('roiSector');

  NICHOS.forEach((nicho) => {
    // -- Boton de filtro (tab) --
    const btn = document.createElement('button');
    btn.className = 'tab' + (nicho.id === nichoActivo ? ' is-active' : '');
    btn.textContent = `${nicho.icono} ${nicho.nombre}`;
    btn.addEventListener('click', () => {
      nichoActivo = nicho.id;
      // Quitamos la clase activa de todos y se la ponemos al que se clico
      document.querySelectorAll('.tab').forEach((t) => t.classList.remove('is-active'));
      btn.classList.add('is-active');
      renderServicios(); // volvemos a dibujar las tarjetas del nicho elegido
    });
    tabs.appendChild(btn);

    // -- Opciones del <select> del formulario (agrupadas por nicho) --
    const group = document.createElement('optgroup');
    group.label = nicho.nombre;
    nicho.servicios.forEach((s) => {
      const opt = document.createElement('option');
      opt.value = `${nicho.nombre} - ${s.titulo}`;
      opt.textContent = s.titulo;
      group.appendChild(opt);
    });
    servicioSelect.appendChild(group);

    // -- Opciones del <select> de la calculadora --
    const optSector = document.createElement('option');
    optSector.value = nicho.id;
    optSector.textContent = `${nicho.icono} ${nicho.nombre}`;
    roiSector.appendChild(optSector);
  });

  // ==========================================================================
  //  2) DIBUJAR LAS TARJETAS DEL NICHO ACTIVO
  // ==========================================================================
  function renderServicios() {
    const nicho = NICHOS.find((n) => n.id === nichoActivo);
    grid.innerHTML = ''; // limpiamos lo anterior

    // Encabezado con el "dolor" del sector
    const header = document.createElement('div');
    header.className = 'niche-header';
    header.innerHTML = `<strong>${nicho.icono} ${nicho.nombre}:</strong> ${nicho.dolor}`;
    grid.appendChild(header);

    // Una tarjeta por cada servicio
    nicho.servicios.forEach((s) => {
      const card = document.createElement('article');
      card.className = 'service-card';
      card.innerHTML = `
        <span class="service-card__hook">${s.gancho}</span>
        <h3 class="service-card__title">${s.titulo}</h3>
        <p class="service-card__desc">${s.descripcion}</p>
        <p class="service-card__benefit">&#128161; ${s.beneficio}</p>
        <button class="service-card__btn">Lo quiero &rarr;</button>
      `;

      // Al pulsar "Lo quiero": rellenamos el formulario y bajamos hasta el.
      // Esta es la esencia del modelo "Puerta Falsa": medir interes real.
      card.querySelector('.service-card__btn').addEventListener('click', () => {
        const valor = `${nicho.nombre} - ${s.titulo}`;
        servicioSelect.value = valor;                 // marca el servicio en el select
        origenInput.value = `tarjeta:${valor}`;        // registra desde donde vino
        irAlFormulario();
      });

      grid.appendChild(card);
    });

    // Tarjeta final: invita a contar un problema que no esta en el catalogo.
    // Es la que convierte visitantes con dolores que todavia no tengo listados.
    const custom = document.createElement('article');
    custom.className = 'service-card service-card--custom';
    custom.innerHTML = `
      <span class="service-card__hook">¿Tu tarea no está aquí?</span>
      <h3 class="service-card__title">Cuéntame tu problema</h3>
      <p class="service-card__desc">
        Descríbeme qué proceso te está costando tiempo o dinero y qué necesitas que pase.
        Te digo si se puede automatizar, cómo lo haría y cuánto ahorrarías al año.
      </p>
      <p class="service-card__benefit">&#127919; La mayoría de estas soluciones nacieron justo así.</p>
      <button class="service-card__btn">Contar mi caso &rarr;</button>
    `;
    custom.querySelector('.service-card__btn').addEventListener('click', () => {
      servicioSelect.value = '';
      origenInput.value = `tarea_personalizada:${nicho.nombre}`;
      mensajeInput.focus({ preventScroll: true });
      irAlFormulario();
    });
    grid.appendChild(custom);
  }

  renderServicios(); // primera vez que se cargan las tarjetas

  // ==========================================================================
  //  3) CALCULADORA DE RETORNO ("antes vs. despues" en dinero)
  // ==========================================================================
  //  A los gerentes no los convence una lista de funciones: los convence una
  //  cifra. Aqui traducimos horas manuales a pesos y mostramos el impacto.

  // Valores por defecto de cada moneda (costo aproximado de una hora de trabajo)
  const MONEDAS = {
    COP: { locale: 'es-CO', costoHora: 25000, paso: 1000 },
    MXN: { locale: 'es-MX', costoHora: 150, paso: 10 },
    USD: { locale: 'en-US', costoHora: 18, paso: 1 },
    EUR: { locale: 'es-ES', costoHora: 17, paso: 1 }
  };

  const SEMANAS_POR_MES = 4.33;   // promedio de semanas en un mes
  const HORAS_POR_DIA = 8;        // una jornada laboral
  const HORAS_FTE_ANIO = 1920;    // 8 h x 240 dias = 1 persona de tiempo completo

  const roiPersonas = document.getElementById('roiPersonas');
  const roiHorasSemana = document.getElementById('roiHorasSemana');
  const roiMoneda = document.getElementById('roiMoneda');
  const roiCostoHora = document.getElementById('roiCostoHora');
  const roiErrores = document.getElementById('roiErrores');
  const roiPct = document.getElementById('roiPct');

  // Guardamos el ultimo calculo para poder mandarlo al formulario
  let ultimoCalculo = null;

  // Lee un campo numerico y evita valores vacios o negativos
  function num(input, minimo = 0) {
    const valor = Number(input.value);
    return Number.isFinite(valor) && valor > minimo ? valor : minimo;
  }

  function formatoDinero(valor, codigo) {
    return new Intl.NumberFormat(MONEDAS[codigo].locale, {
      style: 'currency',
      currency: codigo,
      maximumFractionDigits: 0
    }).format(Math.round(valor));
  }

  function formatoNumero(valor, codigo, decimales = 0) {
    return new Intl.NumberFormat(MONEDAS[codigo].locale, {
      minimumFractionDigits: decimales,
      maximumFractionDigits: decimales
    }).format(valor);
  }

  function calcularROI() {
    const codigo = roiMoneda.value;
    const personas = num(roiPersonas, 1);
    const horasSemana = num(roiHorasSemana, 1);
    const costoHora = num(roiCostoHora, 1);
    const errores = num(roiErrores, 0);
    const pct = num(roiPct, 1) / 100;

    // Costo del proceso HOY, hecho a mano
    const horasMes = personas * horasSemana * SEMANAS_POR_MES;
    const costoAntesMes = horasMes * costoHora + errores;

    // Lo que se recupera al automatizar la parte automatizable
    const ahorroMes = costoAntesMes * pct;
    const costoDespuesMes = costoAntesMes - ahorroMes;

    const ahorroAnio = ahorroMes * 12;
    const horasAnio = horasMes * 12 * pct;

    // ----- Pintamos el tablero -----
    document.getElementById('roiAnual').textContent = formatoDinero(ahorroAnio, codigo);
    document.getElementById('roiMensual').textContent = `${formatoDinero(ahorroMes, codigo)} cada mes`;
    document.getElementById('roiAntes').textContent = formatoDinero(costoAntesMes, codigo);
    document.getElementById('roiDespues').textContent = formatoDinero(costoDespuesMes, codigo);

    // La barra "antes" siempre ocupa el 100%; la de "despues" es proporcional
    const proporcion = costoAntesMes > 0 ? (costoDespuesMes / costoAntesMes) * 100 : 0;
    document.getElementById('roiBarAntes').style.width = '100%';
    document.getElementById('roiBarDespues').style.width = `${Math.max(proporcion, 2)}%`;

    document.getElementById('roiHorasAnio').textContent = formatoNumero(Math.round(horasAnio), codigo);
    document.getElementById('roiDias').textContent = formatoNumero(Math.round(horasAnio / HORAS_POR_DIA), codigo);
    document.getElementById('roiFte').textContent = formatoNumero(horasAnio / HORAS_FTE_ANIO, codigo, 1);

    // Guardamos el resumen para adjuntarlo al lead
    const sector = NICHOS.find((n) => n.id === roiSector.value);
    ultimoCalculo = {
      sector: sector ? sector.nombre : '',
      personas,
      horasSemana,
      pct: Math.round(pct * 100),
      ahorroMesTexto: formatoDinero(ahorroMes, codigo),
      ahorroAnioTexto: formatoDinero(ahorroAnio, codigo),
      horasAnio: Math.round(horasAnio)
    };
  }

  // Al cambiar de sector, cargamos los promedios tipicos de ese sector
  roiSector.addEventListener('change', () => {
    const sector = NICHOS.find((n) => n.id === roiSector.value);
    if (!sector) return;
    roiPersonas.value = sector.personasTipicas;
    roiHorasSemana.value = sector.horasTipicas;
    roiPct.value = sector.pctTipico;
    document.getElementById('roiPctOut').textContent = `${sector.pctTipico}%`;
    calcularROI();
  });

  // Al cambiar de moneda, ajustamos el costo por hora sugerido
  roiMoneda.addEventListener('change', () => {
    const config = MONEDAS[roiMoneda.value];
    roiCostoHora.value = config.costoHora;
    roiCostoHora.step = config.paso;
    roiErrores.step = config.paso;
    calcularROI();
  });

  // El deslizador muestra su porcentaje mientras se mueve
  roiPct.addEventListener('input', () => {
    document.getElementById('roiPctOut').textContent = `${roiPct.value}%`;
    calcularROI();
  });

  [roiPersonas, roiHorasSemana, roiCostoHora, roiErrores].forEach((campo) =>
    campo.addEventListener('input', calcularROI)
  );

  // Arrancamos con el primer sector ya seleccionado y el tablero calculado
  roiSector.value = NICHOS[0].id;
  roiSector.dispatchEvent(new Event('change'));

  // El boton del tablero lleva al formulario con el calculo ya escrito
  document.getElementById('roiCta').addEventListener('click', () => {
    if (!ultimoCalculo) calcularROI();
    const c = ultimoCalculo;
    origenInput.value = `calculadora:${c.sector}`;
    ahorroInput.value = `${c.ahorroAnioTexto}/año`;
    mensajeInput.value =
      `Sector: ${c.sector}. Hoy ${c.personas} persona(s) dedican ${c.horasSemana} h por semana ` +
      `a tareas manuales. Según la calculadora, automatizar el ${c.pct}% del proceso me ahorraría ` +
      `${c.ahorroMesTexto} al mes (${c.ahorroAnioTexto} al año) y recuperaría ${c.horasAnio} horas. ` +
      `Quiero validar esta cifra y saber por dónde empezar.`;
    irAlFormulario();
  });

  // ==========================================================================
  //  4) ENVIAR EL FORMULARIO AL SERVIDOR
  // ==========================================================================
  const feedback = document.getElementById('formFeedback');

  form.addEventListener('submit', async (e) => {
    e.preventDefault(); // evita que la pagina se recargue

    // Convertimos los campos del formulario en un objeto JavaScript
    const datos = Object.fromEntries(new FormData(form).entries());

    // Mensaje temporal mientras enviamos
    feedback.textContent = 'Enviando...';
    feedback.className = 'form__feedback';

    try {
      // Enviamos los datos al servidor (ruta POST /api/leads de server.js)
      const resp = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
      });
      const resultado = await resp.json();

      if (resultado.ok) {
        feedback.textContent = '\u2705 ¡Gracias! Recibí tu solicitud y te contactaré pronto.';
        feedback.className = 'form__feedback is-success';
        form.reset();          // limpiamos el formulario
        ahorroInput.value = ''; // y el calculo adjunto
      } else {
        feedback.textContent = '\u26A0\uFE0F ' + (resultado.error || 'Ocurrió un error. Intenta de nuevo.');
        feedback.className = 'form__feedback is-error';
      }
    } catch (err) {
      // Si el servidor no responde (por ejemplo, no esta encendido)
      feedback.textContent = '\u26A0\uFE0F No se pudo conectar. Verifica que el servidor esté encendido.';
      feedback.className = 'form__feedback is-error';
    }
  });

  // ==========================================================================
  //  5) DETALLES: menu movil y ano del footer
  // ==========================================================================
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  navToggle.addEventListener('click', () => navLinks.classList.toggle('is-open'));
  // Al hacer clic en un enlace del menu, lo cerramos (en celular)
  navLinks.querySelectorAll('a').forEach((a) =>
    a.addEventListener('click', () => navLinks.classList.remove('is-open'))
  );

  // Ano actual en el footer
  document.getElementById('year').textContent = new Date().getFullYear();
});
