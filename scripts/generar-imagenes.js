// ============================================================================
//  generar-imagenes.js  ->  Crea la imagen de vista previa y el icono
// ============================================================================
//  Se ejecuta con:   npm run og
//
//  Toma los moldes HTML de la carpeta assets/ y les hace una "foto" usando
//  Google Chrome en modo invisible. El resultado va a public/img/.
//
//  Ejecutalo cada vez que cambies el titular en assets/og-template.html, para
//  que la imagen que ven en WhatsApp coincida con la de la pagina.
// ============================================================================

const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const RAIZ = path.join(__dirname, '..');
const SALIDA = path.join(RAIZ, 'public', 'img');

// Ubicaciones habituales de Chrome. Si usas otro navegador basado en Chromium,
// agrega su ruta a esta lista.
const NAVEGADORES = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium'
];

const IMAGENES = [
  { molde: 'og-template.html',    archivo: 'og.png',        ancho: 1200, alto: 630, que: 'Vista previa para compartir' },
  { molde: 'icono-template.html', archivo: 'icono-180.png', ancho: 180,  alto: 180, que: 'Icono para celulares' }
];

const navegador = NAVEGADORES.find((ruta) => fs.existsSync(ruta));

if (!navegador) {
  console.error('\nNo encontre Google Chrome en este computador.');
  console.error('Instalalo desde https://google.com/chrome o agrega tu ruta');
  console.error('a la lista NAVEGADORES de este archivo.\n');
  process.exit(1);
}

fs.mkdirSync(SALIDA, { recursive: true });

for (const img of IMAGENES) {
  const molde = path.join(RAIZ, 'assets', img.molde);
  const destino = path.join(SALIDA, img.archivo);

  execFileSync(navegador, [
    '--headless',
    '--disable-gpu',
    '--hide-scrollbars',
    '--force-device-scale-factor=1',
    `--screenshot=${destino}`,
    `--window-size=${img.ancho},${img.alto}`,
    `file://${molde}`
  ], { stdio: 'ignore' });

  const kb = Math.round(fs.statSync(destino).size / 1024);
  console.log(`  ${img.que}: public/img/${img.archivo} (${img.ancho}x${img.alto}, ${kb} KB)`);
}

console.log('\nListo. Recuerda que la vista previa solo se ve cuando la pagina');
console.log('este publicada, porque las redes leen la imagen desde internet.\n');
