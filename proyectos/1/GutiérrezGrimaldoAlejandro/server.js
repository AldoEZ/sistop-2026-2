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

function recolectarBody(req) {
  return new Promise((resolve, reject) => {
    const partes = [];
    req.on('data', c => partes.push(c));
    req.on('end',  () => resolve(Buffer.concat(partes)));
    req.on('error', reject);
  });
}

// no quise usar multer ni nada externo, esto parsea el multipart a mano
function parsearMultipart(buf, boundary) {
  const partes = {};
  const bnd = Buffer.from('--' + boundary);

  function buscarBnd(desde) {
    for (let i = desde; i <= buf.length - bnd.length; i++) {
      let ok = true;
      for (let j = 0; j < bnd.length; j++) {
        if (buf[i+j] !== bnd[j]) { ok = false; break; }
      }
      if (ok) return i;
    }
    return -1;
  }

  function buscarSeq(seq, desde) {
    for (let i = desde; i <= buf.length - seq.length; i++) {
      let ok = true;
      for (let j = 0; j < seq.length; j++) {
        if (buf[i+j] !== seq[j]) { ok = false; break; }
      }
      if (ok) return i;
    }
    return -1;
  }

  const sep = Buffer.from('\r\n\r\n');
  let pos = 0;
  while (true) {
    const bStart = buscarBnd(pos);
    if (bStart === -1) break;
    const hStart = bStart + bnd.length + 2;
    const hEnd   = buscarSeq(sep, hStart);
    if (hEnd === -1) break;

    const header = buf.slice(hStart, hEnd).toString('ascii');
    const nameM  = header.match(/name="([^"]+)"/);
    const fileM  = header.match(/filename="([^"]+)"/);
    if (!nameM) { pos = hEnd + 4; continue; }

    const dStart = hEnd + 4;
    const dEnd   = buscarBnd(dStart) - 2;
    if (dEnd < dStart) break;

    const valor = buf.slice(dStart, dEnd);
    partes[nameM[1]] = fileM ? { filename: fileM[1], data: valor } : valor.toString('utf8');
    pos = dEnd + 2;
  }
  return partes;
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

  if (url === '/api/agregar' && req.method === 'POST') {
    const ct  = req.headers['content-type'] || '';
    const bnd = (ct.match(/boundary=(.+)/) || [])[1];
    if (!bnd) return json(res, 400, { ok: false, error: 'content-type invalido' });
    const body  = await recolectarBody(req);
    const parts = parsearMultipart(body, bnd);
    const arch  = parts['archivo'];
    const nombre = (parts['nombre'] || (arch && arch.filename) || '').trim();
    if (!arch || !nombre) return json(res, 400, { ok: false, error: 'faltan datos' });
    const tmp = path.join(os.tmpdir(), 'fiunam_up_' + Date.now());
    fs.writeFileSync(tmp, arch.data);
    const r = await correrWorker({ op: 'copiarHacia', imagePath, origen: tmp, nombre });
    fs.unlinkSync(tmp);
    return json(res, r.ok ? 200 : 500, r);
  }

  res.writeHead(404);
  res.end('not found');
});

server.listen(PUERTO, () => {
  console.log(`servidor en http://localhost:${PUERTO}`);
});
