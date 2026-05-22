'use strict';

const fs = require('fs');

const NOMBRE_FS = 'FiUnamFS';
const VERSION_OK = '26-2';
const TAM_ENTRADA = 64;

function leerSuperbloque(buf) {
  const nombre  = buf.slice(5, 14).toString('ascii').replace(/\0/g, '');
  const version = buf.slice(14, 19).toString('ascii').replace(/\0/g, '');
  const etiqueta = buf.slice(20, 36).toString('ascii').replace(/\0/g, '').trim();

  if (nombre !== NOMBRE_FS)
    throw new Error(`La imagen no es FiUnamFS (dice: '${nombre}')`);
  if (version !== VERSION_OK)
    throw new Error(`Version no soportada: ${version}`);

  return {
    nombre,
    version,
    etiqueta,
    tamCluster:    buf.readUInt32LE(40),
    clustersDir:   buf.readUInt32LE(50),
    clustersTotal: buf.readUInt32LE(60),
  };
}

function leerDirectorio(buf, sb) {
  const inicio = sb.tamCluster;
  const total  = Math.floor((sb.clustersDir * sb.tamCluster) / TAM_ENTRADA);
  const archivos = [];

  for (let i = 0; i < total; i++) {
    const off  = inicio + i * TAM_ENTRADA;
    const tipo = buf[off];

    if (tipo !== 0x2d) continue;

    const nombre     = buf.slice(off + 1,  off + 16).toString('ascii').replace(/\0/g, '').trim();
    const tamano     = buf.readUInt32LE(off + 16);
    const cluster    = buf.readUInt32LE(off + 20);
    const creado     = buf.slice(off + 30, off + 44).toString('ascii');
    const modificado = buf.slice(off + 50, off + 64).toString('ascii');

    archivos.push({ i, nombre, tamano, cluster, creado, modificado, off });
  }

  return archivos;
}

function formatearFecha(raw) {
  if (!raw || /^0+$/.test(raw.trim())) return '(sin fecha)';
  return `${raw.slice(0,4)}-${raw.slice(4,6)}-${raw.slice(6,8)} ${raw.slice(8,10)}:${raw.slice(10,12)}:${raw.slice(12,14)}`;
}

// prueba rapida
const buf = Buffer.from(fs.readFileSync(process.argv[2]));
const sb  = leerSuperbloque(buf);
const archivos = leerDirectorio(buf, sb);
console.log(`\n${sb.nombre} | ${sb.etiqueta} | ${sb.version}`);
for (const a of archivos) {
  console.log(`  ${a.nombre.padEnd(15)} ${a.tamano} bytes  cluster ${a.cluster}  ${formatearFecha(a.creado)}`);
}
