'use strict';

const http = require('http');
const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { Worker } = require('worker_threads');

const imagePath = path.resolve(process.argv[2] || '');
const PUERTO = parseInt(process.argv[3] || '8080', 10);

if (!process.argv[2]) {
  console.error('uso: node server.js <imagen.img> [puerto]');
  process.exit(1);
}
if (!fs.existsSync(imagePath)) {
  console.error(`no se encuentra la imagen: ${imagePath}`);
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

const HTML = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>FiUnamFS</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: monospace; background: #111; color: #ddd; min-height: 100vh; }

  header {
    background: #1a1a1a;
    border-bottom: 1px solid #333;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  header h1 { font-size: 1rem; color: #0f0; }
  #sb-info { margin-left: auto; font-size: 0.75rem; color: #666; }

  main { display: grid; grid-template-columns: 1fr 300px; height: calc(100vh - 49px); }

  .tabla-wrap { padding: 1.5rem; overflow: auto; border-right: 1px solid #333; }
  table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  th { text-align: left; color: #555; padding: 0 0.5rem 0.6rem; border-bottom: 1px solid #333; }
  td { padding: 0.6rem 0.5rem; border-bottom: 1px solid #222; }
  tr { cursor: pointer; }
  tr:hover td { background: #1c1c1c; }
  tr.sel td { background: #0f0f1f; color: #0f0; }
  .t-size { color: #666; text-align: right; }
  .t-cluster { color: #444; }
  .t-fecha { color: #555; font-size: 0.75rem; }

  .panel { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.2rem; overflow: auto; }
  .bloque { background: #1a1a1a; border: 1px solid #333; border-radius: 4px; padding: 1rem; }
  .bloque h3 { font-size: 0.7rem; color: #555; text-transform: uppercase; margin-bottom: 0.8rem; letter-spacing: 1px; }
  #sel-nombre { font-size: 0.85rem; color: #0f0; margin-bottom: 0.6rem; min-height: 1.2rem; }

  .fila-btns { display: flex; gap: 0.5rem; }
  button {
    font-family: monospace; font-size: 0.78rem;
    padding: 0.4rem 0.8rem;
    border: 1px solid #444; background: #222; color: #aaa;
    cursor: pointer; border-radius: 3px;
  }
  button:hover:not(:disabled) { background: #2a2a2a; color: #ddd; }
  button:disabled { opacity: 0.35; cursor: default; }
  .btn-verde { border-color: #0f0; color: #0f0; }
  .btn-rojo  { border-color: #f44; color: #f44; }

  .dropzone {
    border: 1px dashed #444; border-radius: 3px;
    padding: 1rem; text-align: center; cursor: pointer;
    font-size: 0.78rem; color: #555; position: relative;
    margin-bottom: 0.6rem; transition: border-color 0.2s;
  }
  .dropzone:hover, .dropzone.over { border-color: #0f0; color: #0f0; }
  .dropzone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  #drop-nombre { font-size: 0.75rem; color: #888; margin-bottom: 0.6rem; }

  input[type=text] {
    width: 100%; background: #111; border: 1px solid #333;
    color: #ddd; font-family: monospace; font-size: 0.8rem;
    padding: 0.4rem 0.6rem; border-radius: 3px; outline: none; margin-bottom: 0.6rem;
  }
  input[type=text]:focus { border-color: #0f0; }

  #toast {
    position: fixed; bottom: 1.5rem; left: 50%;
    transform: translateX(-50%) translateY(60px);
    background: #1a1a1a; border: 1px solid #444; color: #ddd;
    font-family: monospace; font-size: 0.78rem;
    padding: 0.5rem 1.2rem; border-radius: 3px;
    opacity: 0; transition: all 0.25s; z-index: 99;
  }
  #toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
  #toast.ok    { border-color: #0f0; color: #0f0; }
  #toast.error { border-color: #f44; color: #f44; }
</style>
</head>
<body>

<header>
  <h1>FiUnamFS</h1>
  <span id="sb-info">cargando...</span>
</header>

<main>
  <div class="tabla-wrap">
    <table>
      <thead><tr>
        <th>nombre</th><th style="text-align:right">tamaño</th>
        <th>cluster</th><th>modificado</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>

  <div class="panel">
    <div class="bloque">
      <h3>archivo seleccionado</h3>
      <div id="sel-nombre">—</div>
      <div class="fila-btns">
        <button class="btn-verde" id="btn-descargar" disabled>descargar</button>
        <button class="btn-rojo"  id="btn-eliminar"  disabled>eliminar</button>
      </div>
    </div>

    <div class="bloque">
      <h3>agregar archivo</h3>
      <div class="dropzone" id="dropzone">
        arrastra aqui o haz clic
        <input type="file" id="input-file">
      </div>
      <div id="drop-nombre"></div>
      <input type="text" id="input-nombre" placeholder="nombre (max 15 chars)" maxlength="15">
      <button id="btn-agregar" disabled style="width:100%">agregar a la imagen</button>
    </div>
  </div>
</main>

<div id="toast"></div>

<script>
let seleccionado = null;
let archivoSubir = null;
let toastTimer;

function toast(msg, tipo) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'show ' + (tipo || 'ok');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.className = '', 3000);
}

function fmtTamano(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  return (b/1048576).toFixed(2) + ' MB';
}

function fmtFecha(raw) {
  if (!raw || /^0+$/.test(raw)) return '';
  return raw.slice(0,4)+'-'+raw.slice(4,6)+'-'+raw.slice(6,8)+' '+raw.slice(8,10)+':'+raw.slice(10,12);
}

async function cargar() {
  const res  = await fetch('/api/listar');
  const data = await res.json();
  if (!data.ok) { toast(data.error, 'error'); return; }

  const sb = data.sb;
  document.getElementById('sb-info').textContent =
    sb.etiqueta + ' | cluster ' + sb.tamCluster + ' B | ' + fmtTamano(sb.clustersTotal * sb.tamCluster);

  const tbody = document.getElementById('tbody');
  tbody.innerHTML = '';
  for (const a of data.archivos) {
    const tr = document.createElement('tr');
    if (seleccionado && seleccionado.nombre === a.nombre) tr.classList.add('sel');
    tr.innerHTML =
      '<td>' + a.nombre + '</td>' +
      '<td class="t-size">' + fmtTamano(a.tamano) + '</td>' +
      '<td class="t-cluster">#' + a.cluster + '</td>' +
      '<td class="t-fecha">' + fmtFecha(a.modificado) + '</td>';
    tr.addEventListener('click', () => seleccionar(a));
    tbody.appendChild(tr);
  }
}

function seleccionar(a) {
  seleccionado = a;
  document.getElementById('sel-nombre').textContent = a.nombre + '  (' + fmtTamano(a.tamano) + ')';
  document.getElementById('btn-descargar').disabled = false;
  document.getElementById('btn-eliminar').disabled  = false;
  cargar();
}

document.getElementById('btn-descargar').addEventListener('click', async () => {
  if (!seleccionado) return;
  const res = await fetch('/api/copiar?nombre=' + encodeURIComponent(seleccionado.nombre));
  if (!res.ok) { const e = await res.json(); toast(e.error, 'error'); return; }
  const blob = await res.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = seleccionado.nombre; a.click();
  URL.revokeObjectURL(url);
  toast('descargado: ' + seleccionado.nombre);
});

document.getElementById('btn-eliminar').addEventListener('click', async () => {
  if (!seleccionado) return;
  if (!confirm('eliminar "' + seleccionado.nombre + '"?')) return;
  const res  = await fetch('/api/eliminar?nombre=' + encodeURIComponent(seleccionado.nombre), { method: 'DELETE' });
  const data = await res.json();
  if (!data.ok) { toast(data.error, 'error'); return; }
  seleccionado = null;
  document.getElementById('sel-nombre').textContent = '—';
  document.getElementById('btn-descargar').disabled = true;
  document.getElementById('btn-eliminar').disabled  = true;
  toast('eliminado');
  cargar();
});

const dropzone  = document.getElementById('dropzone');
const inputFile = document.getElementById('input-file');
const inputNom  = document.getElementById('input-nombre');
const btnAgreg  = document.getElementById('btn-agregar');

function setArchivo(f) {
  archivoSubir = f;
  document.getElementById('drop-nombre').textContent = f.name + ' (' + fmtTamano(f.size) + ')';
  inputNom.value = f.name.slice(0, 15);
  btnAgreg.disabled = false;
}

inputFile.addEventListener('change', () => { if (inputFile.files[0]) setArchivo(inputFile.files[0]); });
dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('over'); });
dropzone.addEventListener('dragleave', () => dropzone.classList.remove('over'));
dropzone.addEventListener('drop', e => {
  e.preventDefault(); dropzone.classList.remove('over');
  if (e.dataTransfer.files[0]) setArchivo(e.dataTransfer.files[0]);
});

btnAgreg.addEventListener('click', async () => {
  if (!archivoSubir) return;
  const nombre = inputNom.value.trim();
  if (!nombre) { toast('pon un nombre al archivo', 'error'); return; }
  const fd = new FormData();
  fd.append('archivo', archivoSubir);
  fd.append('nombre', nombre);
  const res  = await fetch('/api/agregar', { method: 'POST', body: fd });
  const data = await res.json();
  if (!data.ok) { toast(data.error, 'error'); return; }
  toast('agregado: ' + nombre);
  archivoSubir = null;
  inputFile.value = '';
  inputNom.value  = '';
  document.getElementById('drop-nombre').textContent = '';
  btnAgreg.disabled = true;
  cargar();
});

cargar();
</script>
</body>
</html>`;

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

  if (url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(HTML);
  }

  if (url === '/api/eliminar' && req.method === 'DELETE') {
    const nombre = params.get('nombre');
    if (!nombre) return json(res, 400, { ok: false, error: 'falta nombre' });
    const r = await correrWorker({ op: 'eliminar', imagePath, nombre });
    return json(res, r.ok ? 200 : 404, r);
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
