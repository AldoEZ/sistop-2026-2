'use strict';

const { Worker } = require('worker_threads');
const path = require('path');
const fs   = require('fs');
const { formatearFecha } = require('./fiunamfs');

function correrWorker(datos) {
  return new Promise((resolve, reject) => {
    const w = new Worker(path.join(__dirname, 'worker.js'), { workerData: datos });
    w.on('message', msg => resolve(msg));
    w.on('error',   reject);
    w.on('exit', codigo => {
      if (codigo !== 0) reject(new Error(`Worker salio con codigo ${codigo}`));
    });
  });
}

function fmtTamano(b) {
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1024 / 1024).toFixed(2) + ' MB';
}

const args      = process.argv.slice(2);
const comando   = args[0];
const imagePath = args[1] ? path.resolve(args[1]) : null;

if (!comando || !imagePath) {
  console.log('uso: node index.js <listar|copiar|agregar|eliminar> <imagen> [args]');
  process.exit(1);
}

if (!fs.existsSync(imagePath)) {
  console.error('No se encuentra la imagen:', imagePath);
  process.exit(1);
}

async function main() {
  if (comando === 'listar') {
    const res = await correrWorker({ op: 'listar', imagePath });
    if (!res.ok) { console.error(res.error); process.exit(1); }

    const { sb, archivos } = res;
    console.log(`\n${sb.nombre} | ${sb.etiqueta} | ${sb.version}`);
    console.log(`cluster: ${sb.tamCluster} bytes | total: ${fmtTamano(sb.clustersTotal * sb.tamCluster)}\n`);

    if (archivos.length === 0) {
      console.log('(directorio vacio)');
    } else {
      for (const a of archivos) {
        console.log(`  ${a.nombre.padEnd(15)}  ${fmtTamano(a.tamano).padStart(9)}  cluster ${a.cluster}  ${formatearFecha(a.creado)}`);
      }
    }
    console.log();

  } else if (comando === 'copiar') {
    const nombre  = args[2];
    const destino = args[3];
    if (!nombre || !destino) {
      console.error('uso: node index.js copiar <imagen> <nombre> <destino>');
      process.exit(1);
    }
    const res = await correrWorker({ op: 'copiarDesde', imagePath, nombre, destino });
    if (!res.ok) { console.error(res.error); process.exit(1); }
    console.log(`copiado: ${nombre} -> ${destino} (${fmtTamano(res.bytes)})`);

  } else if (comando === 'agregar') {
    const origen = args[2];
    const nombre = args[3] || path.basename(origen);
    if (!origen || !fs.existsSync(origen)) {
      console.error('archivo no encontrado:', origen);
      process.exit(1);
    }
    const res = await correrWorker({ op: 'copiarHacia', imagePath, origen, nombre });
    if (!res.ok) { console.error(res.error); process.exit(1); }
    console.log(`agregado: ${nombre} (${fmtTamano(res.bytes)})`);

  } else if (comando === 'eliminar') {
    const nombre = args[2];
    if (!nombre) { console.error('falta el nombre del archivo'); process.exit(1); }
    const res = await correrWorker({ op: 'eliminar', imagePath, nombre });
    if (!res.ok) { console.error(res.error); process.exit(1); }
    console.log(`eliminado: ${nombre}`);

  } else {
    console.error('comando no reconocido:', comando);
    process.exit(1);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
