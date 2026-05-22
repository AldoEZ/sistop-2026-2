'use strict';

const fs = require('fs');

const NOMBRE_FS = 'FiUnamFS';
const VERSIONES_OK = ['26-2', '24-2'];
const TAM_ENTRADA = 64;

function leerSuperbloque(buf) {
  const nombre  = buf.slice(5, 14).toString('ascii').replace(/\0/g, '');
  const version = buf.slice(14, 19).toString('ascii').replace(/\0/g, '');
  const etiqueta = buf.slice(20, 36).toString('ascii').replace(/\0/g, '').trim();

  if (nombre !== NOMBRE_FS)
    throw new Error(`La imagen no es FiUnamFS (dice: '${nombre}')`);
  if (!VERSIONES_OK.includes(version))
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

function fechaFS(date) {
  const p = n => String(n).padStart(2, '0');
  return `${date.getFullYear()}${p(date.getMonth()+1)}${p(date.getDate())}${p(date.getHours())}${p(date.getMinutes())}${p(date.getSeconds())}`;
}

function primerEntradaLibre(buf, sb) {
  const inicio = sb.tamCluster;
  const total  = Math.floor((sb.clustersDir * sb.tamCluster) / TAM_ENTRADA);
  for (let i = 0; i < total; i++) {
    if (buf[inicio + i * TAM_ENTRADA] === 0x2f) return i;
  }
  return -1;
}

function primerClusterLibre(sb, archivos, necesito) {
  const inicio = 1 + sb.clustersDir;

  const ocupados = archivos.map(a => ({
    desde: a.cluster,
    hasta: a.cluster + Math.ceil(a.tamano / sb.tamCluster) - 1
  })).sort((a, b) => a.desde - b.desde);

  let candidato = inicio;
  for (const r of ocupados) {
    if (candidato + necesito - 1 < r.desde) break;
    candidato = r.hasta + 1;
  }

  if (candidato + necesito - 1 >= sb.clustersTotal) return -1;
  return candidato;
}

class FiUnamFS {
  constructor(ruta) {
    this.ruta = ruta;
    this.buf  = null;
    this.sb   = null;
    this.archivos = null;
  }

  cargar() {
    this.buf = Buffer.from(fs.readFileSync(this.ruta));
    this.sb  = leerSuperbloque(this.buf);
    this.archivos = leerDirectorio(this.buf, this.sb);
  }

  _guardar() {
    fs.writeFileSync(this.ruta, this.buf);
    this.archivos = leerDirectorio(this.buf, this.sb);
  }

  leerArchivo(nombre) {
    const arch = this.archivos.find(a => a.nombre === nombre.trim());
    if (!arch) throw new Error(`No existe: '${nombre}'`);
    const off = arch.cluster * this.sb.tamCluster;
    return this.buf.slice(off, off + arch.tamano);
  }

  escribirArchivo(nombre, datos) {
    if (nombre.length > 15)
      throw new Error('Nombre muy largo (max 15 chars)');
    if (this.archivos.find(a => a.nombre === nombre.trim()))
      throw new Error('Ya existe un archivo con ese nombre');

    const necesito = Math.ceil(datos.length / this.sb.tamCluster);
    const clusterInicio = primerClusterLibre(this.sb, this.archivos, necesito);
    if (clusterInicio < 0) throw new Error('No hay espacio en el disco');

    const entradaIdx = primerEntradaLibre(this.buf, this.sb);
    if (entradaIdx < 0) throw new Error('No hay entradas libres en el directorio');

    datos.copy(this.buf, clusterInicio * this.sb.tamCluster);

    const ahora = fechaFS(new Date());
    const off   = this.sb.tamCluster + entradaIdx * TAM_ENTRADA;
    this.buf[off] = 0x2d;
    this.buf.write(nombre.padEnd(15, ' '), off + 1,  15, 'ascii');
    this.buf.writeUInt32LE(datos.length,   off + 16);
    this.buf.writeUInt32LE(clusterInicio,  off + 20);
    this.buf.write(ahora, off + 30, 14, 'ascii');
    this.buf.write(ahora, off + 50, 14, 'ascii');

    this._guardar();
  }

  eliminarArchivo(nombre) {
    const arch = this.archivos.find(a => a.nombre === nombre.trim());
    if (!arch) throw new Error(`No existe: '${nombre}'`);
    this.buf[arch.off] = 0x2f;
    this.buf.write('###############', arch.off + 1, 15, 'ascii');
    this._guardar();
  }
}

module.exports = { FiUnamFS, formatearFecha };
