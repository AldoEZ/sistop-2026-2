'use strict';

const { workerData, parentPort } = require('worker_threads');
const fs = require('fs');
const { FiUnamFS } = require('./fiunamfs');

const { op, imagePath } = workerData;

function responder(ok, datos) {
  parentPort.postMessage({ ok, ...datos });
}

try {
  const disco = new FiUnamFS(imagePath);
  disco.cargar();

  if (op === 'listar') {
    responder(true, { sb: disco.sb, archivos: disco.archivos });

  } else if (op === 'copiarDesde') {
    const datos = disco.leerArchivo(workerData.nombre);
    fs.writeFileSync(workerData.destino, datos);
    responder(true, { bytes: datos.length, destino: workerData.destino });

  } else if (op === 'copiarHacia') {
    const datos = fs.readFileSync(workerData.origen);
    disco.escribirArchivo(workerData.nombre, datos);
    responder(true, { bytes: datos.length });

  } else if (op === 'eliminar') {
    disco.eliminarArchivo(workerData.nombre);
    responder(true, {});

  } else {
    responder(false, { error: 'operacion desconocida' });
  }

} catch (err) {
  responder(false, { error: err.message });
}
