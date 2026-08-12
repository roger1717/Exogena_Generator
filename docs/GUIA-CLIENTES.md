# Guía para conseguir clientes — Automat-IA

Esta guía es tu plan de acción comercial. La página web es la herramienta; aquí
está la **estrategia** para que las empresas te contacten y contraten.

Modelo que estás usando: **"Puerta Falsa" / Validación Lean**. Vendes la solución
primero, mides el interés real, y construyes lo que la gente de verdad quiere pagar.

---

## 0. La mentalidad correcta (léelo primero)

- **No vendes "software" ni "IA". Vendes tiempo y dinero recuperado.** Un gerente
  no quiere "un agente que clasifica CVs"; quiere "dejar de perder 2 días al mes
  filtrando currículums".
- **Habla de dolores, no de tecnología.** Ellos no saben (ni les importa) qué es
  Node.js. Les importa: menos costos, menos errores, más velocidad.
- **Empieza con UN nicho.** Aunque la página tenga 5 sectores, tú enfócate en el
  que más conozcas o donde tengas contactos. Es más fácil venderle a un mercado
  específico que a "todos".

---

## 1. Antes de contactar a nadie (checklist de arranque)

- [ ] La página funciona en local (`npm start`).
- [ ] Publicar la página en internet (hosting) para tener un enlace que compartir.
      *(Pídeme ayuda cuando llegues aquí; es un paso guiado de ~30 min.)*
- [ ] Tener un correo profesional (ej. `tunombre@automat-ia.com` o un Gmail serio).
- [ ] Tener un WhatsApp Business con foto y descripción clara.
- [ ] Definir tu nicho #1 (ver punto 3).
- [ ] Preparar tu "pitch de 1 línea" (ver punto 4).

---

## 2. Elige tu primer nicho (empieza por uno)

Ordena estos según **dónde tienes más contactos o conocimiento**:

| Nicho | Dónde encontrarlos | Dolor más vendible |
|-------|--------------------|--------------------|
| RRHH | LinkedIn (gerentes de RRHH), agencias de empleo | Filtrar CVs, onboarding |
| Marketing/Ventas | Agencias, PYMEs con equipo comercial | Leads fríos, propuestas lentas |
| Logística | Distribuidoras, importadores | Facturas en PDF, inventario |
| Inmobiliaria | Inmobiliarias, agentes independientes | Responder rápido, publicar |
| Salud | Clínicas, consultorios privados | Citas, historias clínicas |

**Recomendación:** elige 1, consigue 1-2 clientes, y luego expandes. El foco vende.

---

## 3. Tu mensaje: la fórmula del "pitch"

Usa esta estructura en TODO (LinkedIn, correo, WhatsApp):

> **[Dolor específico] + [Resultado concreto] + [Invitación de bajo riesgo]**

Ejemplos por nicho:

- **RRHH:** "¿Tu equipo pierde días filtrando currículums a mano? Automatizo ese
  proceso para que veas los 5 mejores candidatos en minutos. ¿Te muestro cómo en
  una llamada de 15 min, sin costo?"
- **Logística:** "Si recibes facturas en PDF de muchos proveedores y alguien las
  digita a mano, puedo convertir eso en un Excel automático. ¿Hacemos una prueba
  gratis con 3 de tus facturas?"
- **Clínicas:** "¿Tu recepción pasa el día confirmando citas por teléfono? Tengo
  un asistente de WhatsApp que lo hace solo y llena los huecos de cancelaciones.
  ¿Te lo muestro?"

Regla de oro: **termina siempre con una pregunta de sí/no fácil.**

---

## 4. Dónde y cómo conseguir los primeros contactos

### A. Tu red actual (lo más rápido y efectivo)
Haz una lista de 20-30 personas que conozcas y trabajen en empresas. Escríbeles
directo (no vendas de una): "Estoy arrancando un servicio de automatización para
[nicho]. ¿Conoces a alguien a quien le sirva ahorrar tiempo en [tarea]?"

### B. LinkedIn (el canal principal B2B)
1. Optimiza tu perfil: titular tipo "Ayudo a [nicho] a ahorrar horas automatizando
   [tarea] | Automat-IA".
2. Busca cargos: "Gerente de RRHH", "Director de Operaciones", "Dueño" en tu ciudad.
3. Envía 5-10 invitaciones al día con una nota corta (usa tu pitch).
4. Publica 2 veces por semana sobre problemas del nicho y cómo se automatizan.

### C. Grupos y comunidades
Cámaras de comercio, grupos de WhatsApp/Telegram de emprendedores, foros del sector.

### D. Correo en frío (email)
Corto, personalizado, con tu pitch y el enlace a tu página. Máximo 5 líneas.

---

## 5. El embudo: del contacto al cliente pagado

```
1. Contacto (LinkedIn/correo/WhatsApp)
        ↓  compartes el enlace a tu página
2. Visita la página y pulsa "Lo quiero"  →  queda un LEAD en tu base
        ↓  tú lo contactas en < 24h
3. Llamada de diagnóstico (15-20 min, gratis)
        ↓  identificas la tarea y confirmas que sí se puede
4. Propuesta (precio + qué hace + tiempo de entrega)
        ↓
5. Anticipo (50%) y desarrollo
        ↓
6. Entrega + 50% restante + soporte
```

**La llamada de diagnóstico es clave.** Ahí no vendes tecnología: haces preguntas.
- ¿Cuánto tiempo les toma hoy esa tarea?
- ¿Quién la hace y cada cuánto?
- ¿Qué pasa cuando hay un error?
- ¿Cuánto valdría para ustedes recuperar ese tiempo?

Con eso justificas el precio solo.

---

## 6. Cómo poner precio (sin miedo)

No cobres por horas; **cobra por el valor que ahorras.**

- **Proyecto pequeño** (una automatización simple): rango de entrada.
- **Proyecto mediano** (varios pasos, integración): rango medio.
- **Mensualidad de mantenimiento/soporte:** ingreso recurrente (lo más valioso).

Fórmula mental: si le ahorras a la empresa $X al mes, cobrar una fracción de eso
es una ganga para ellos. Empieza con precios accesibles para conseguir tus
primeros casos de éxito y testimonios; luego sube.

> **Truco Lean:** ofrece un "piloto pagado" pequeño (una prueba real con sus datos).
> Es más fácil que digan sí a algo pequeño, y de ahí crece la relación.

---

## 7. Qué hacer con los leads que te deja la página

1. Revisa `http://localhost:3000/api/leads` (o el panel cuando lo publiques).
2. Mira `http://localhost:3000/api/stats`: **el servicio con más solicitudes es el
   que debes construir y promocionar primero.** Eso es validación pura.
3. Contacta a cada lead en menos de 24 horas. La velocidad cierra ventas.
4. Lleva un registro simple (una hoja de cálculo): nombre, servicio, estado
   (contactado / reunión / propuesta / cerrado).

---

## 8. Plan de los primeros 30 días

**Semana 1 — Preparación**
- Elige nicho #1. Publica la página en internet. Ajusta tu perfil de LinkedIn.

**Semana 2 — Alcance (outreach)**
- Lista de 30 contactos. 5-10 mensajes/invitaciones al día. Comparte tu página.

**Semana 3 — Conversaciones**
- Agenda y realiza 3-5 llamadas de diagnóstico. Escucha más de lo que hablas.

**Semana 4 — Cierre**
- Envía 2-3 propuestas. Cierra tu primer piloto pagado. Pide un testimonio al terminar.

**Meta realista del mes 1:** 1 cliente pagado (aunque sea pequeño) + 3 conversaciones
avanzadas. Con eso ya validaste el negocio.

---

## 9. Errores comunes a evitar

- ❌ Hablar de tecnología en vez de resultados.
- ❌ Intentar venderle a todos los nichos a la vez.
- ❌ Tardar días en responder un lead (se enfría).
- ❌ Cobrar muy poco por miedo (mejor un piloto pequeño que regalar el trabajo).
- ❌ Prometer plazos imposibles. Bajo promete, sobre entrega.
- ❌ No pedir testimonios. Cada cliente feliz es tu mejor vendedor.

---

## 10. Cuando tengas tu primer "sí"

Avísame y te ayudo a:
- Construir esa primera automatización concreta.
- Publicar la página en internet con dominio propio.
- Añadir testimonios reales a la sección de prueba social.
- Automatizar el aviso de nuevos leads a tu WhatsApp/correo.

**Recuerda:** la página no vende sola. Vende la conversación que tú generas. La
página te da profesionalismo y un lugar donde medir el interés. El resto es
constancia: mensajes, llamadas y seguimiento.

¡A moverse! 🚀
