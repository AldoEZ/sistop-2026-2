'use strict';

const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { Worker } = require('worker_threads');

const imagePath = process.argv[2];
const PUERTO = parseInt(process.argv[3] || '8080', 10);

if (!imagePath || !fs.existsSync(imagePath)) {
  console.error('uso: node server.js <imagen.img> [puerto]');
  process.exit(1);
}

function correrWorker(datos) {
  return new Promise((resolve, reject) => {
    const w = new Worker(path.join(__dirname, 'worker.js'), { workerData: datos });
    w.on('message', msg => resolve(msg));
    w.on('error', reject);
    w.on('exit', c => { if (c !== 0) reject(new Error(`worker salio: ${c}`)); });
  });
}

function json(res, status, datos) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(datos));
}

const MIMES = {
  '.png': 'image/png', '.jpg': 'image/jpeg',
  '.txt': 'text/plain', '.pdf': 'application/pdf',
};

const server = http.createServer(async (req, res) => {
  const url    = req.url.split('?')[0];
  const params = new URL(req.url, 'http://localhost').searchParams;

  if (url === '/api/listar') {
    const r = await correrWorker({ op: 'listar', imagePath });
    return json(res, r.ok ? 200 : 500, r);
  }

  if (url === '/api/copiar') {
    const nombre = params.get('nombre');
    if (!nombre) return json(res, 400, { ok: false, error: 'falta nombre' });
    const tmp = path.join(os.tmpdir(), 'fiunam_' + Date.now() + '_' + nombre);
    const r   = await correrWorker({ op: 'copiarDesde', imagePath, nombre, destino: tmp });
    if (!r.ok) return json(res, 404, r);
    const datos = fs.readFileSync(tmp);
    fs.unlinkSync(tmp);
    const mime = MIMES[path.extname(nombre).toLowerCase()] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': mime, 'Content-Disposition': `attachment; filename="${nombre}"` });
    return res.end(datos);
  }

  res.writeHead(404);
  res.end('not found');
});

server.listen(PUERTO, () => {
  console.log(`servidor en http://localhost:${PUERTO}`);
});
