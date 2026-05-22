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

// prueba rapida
const buf = Buffer.from(fs.readFileSync(process.argv[2]));
const sb  = leerSuperbloque(buf);
console.log('superbloque:', sb);
