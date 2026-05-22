'use strict';

const http = require('http');
const fs   = require('fs');
const path = require('path');
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

const server = http.createServer(async (req, res) => {
  const url = req.url.split('?')[0];

  if (url === '/api/listar') {
    const r = await correrWorker({ op: 'listar', imagePath });
    return json(res, r.ok ? 200 : 500, r);
  }

  res.writeHead(404);
  res.end('not found');
});

server.listen(PUERTO, () => {
  console.log(`servidor en http://localhost:${PUERTO}`);
});
