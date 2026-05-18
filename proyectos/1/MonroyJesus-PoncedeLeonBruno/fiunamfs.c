/*

 Proyecto Sistemas Operativos, Facultad de Ingeniería UNAM
 Versión del sistema de archivos soportada: 26-2

 fiunamfs.c — Implementación FUSE del micro sistema de archivos FiUnamFS
 
 ---- Autores ----
 - Monroy Tapia Jesús Alejandro
 - Ponce de León Reyes Bruno
 
 Compilación: Uso del comando "make" para emplear el Makefile ubicado en el mismo directorio
 Para más información acerca del uso consultar la documentación: "README.md"
*/

#define FUSE_USE_VERSION 31
#include <fuse.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <assert.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/stat.h>

// ----------- Constantes del sistema de archivos -----------
#define FS_NAME          "FiUnamFS"
#define FS_VERSION       "26-2"
#define SECTOR_SIZE      512
#define SECTORS_PER_CLUSTER 4
#define CLUSTER_SIZE     (SECTOR_SIZE * SECTORS_PER_CLUSTER)   /* 2048 bytes */
#define DISK_SIZE        (1440 * 1024)                          /* 1 440 KiB  */
#define TOTAL_CLUSTERS   (DISK_SIZE / CLUSTER_SIZE)             /* 720        */

// ----------- Superbloque (Cluster 0) -----------
#define SB_NAME_OFF      5
#define SB_NAME_LEN      9
#define SB_VER_OFF       14
#define SB_VER_LEN       5
#define SB_LABEL_OFF     20
#define SB_LABEL_LEN     16
#define SB_CLSIZE_OFF    40
#define SB_DIRSIZE_OFF   50
#define SB_TOTALCL_OFF   60

// ----------- Directorio -----------
#define DIR_START_CLUSTER 1
#define DIR_CLUSTERS      8
#define DIR_ENTRY_SIZE    64
#define DIR_ENTRIES_PER_CLUSTER (CLUSTER_SIZE / DIR_ENTRY_SIZE)
#define MAX_DIR_ENTRIES   (DIR_CLUSTERS * DIR_ENTRIES_PER_CLUSTER)
#define NAME_LEN          15
#define TIMESTAMP_LEN     14

// ----------- Marcadores de entrada -----------
#define ENTRY_FILE        '-'
#define ENTRY_EMPTY       '/'
#define ENTRY_DELETED     '#'   // Nombre "###############"

// ----------- Offsets dentro de cada entrada de directorio (64 bytes) -----------
#define DE_TYPE_OFF       0
#define DE_NAME_OFF       1
#define DE_SIZE_OFF       16   // uint32_t little-endian 
#define DE_CLUSTER_OFF    20   // uint32_t little-endian 
#define DE_CTIME_OFF      24
#define DE_MTIME_OFF      40

/*
 * - Estructuras -
*/

// Representación de una entrada de directorio
struct __attribute__((packed)) fiunamfs_entry {
	char type;                 
	char name[16];            
	uint32_t size;            
	uint32_t start_cluster;    
	char ctime[15];            
	char mtime[15];            
	char reserved[12];        
};

// Estado global del sistema de archivos montado
typedef struct {
	int fd;                        // Descriptor del archivo imagen
	uint32_t cluster_size;
	uint32_t dir_clusters;
	uint32_t total_clusters;
	char label[SB_LABEL_LEN + 1];
	fiunamfs_entry dir[MAX_DIR_ENTRIES];      // Directorio en memoria
	int dir_count;                 // Entradas en uso
	
	// Sincronización para hilo de escritura
	int dir_dirty;          // Bandera para indicar que hay cambios sin escribir
	pthread_cond_t sync_cond;
	pthread_t sync_thread;
	int shut_down;      // Señal de cierre para sync_thread
} FiUnamFS;
static FiUnamFS g_fs;

// Mutex para proteger modificaciones
static pthread_mutex_t fs_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t sync_mutex = PTHREAD_MUTEX_INITIALIZER;


// ------------------- Utilidades para bajo nivel -------------------


// Leer los bytes del disco en el offset indicado con la función pread
static int leer_disco(void *buf, size_t count, off_t offset){
	if (pread(g_fs.fd, buf, count, offset) != (ssize_t)count) {
		perror("leer_disco");
		return -EIO;
	}
	return 0;
}

// Escribir bytes al disco en el offset indicado con la función  pwrite
static int escribir_disco(const void *buf, size_t count, off_t offset){
	if (pwrite(g_fs.fd, buf, count, offset) != (ssize_t)count) {
		perror("escribir_disco");
		return -EIO;
	}
	return 0;
}

// Offset del n cluster dentro del disco
static inline off_t cluster_offset(uint32_t n){
	return (off_t)n * CLUSTER_SIZE;
}

// Leer valor uint32_t con formato Little Endian de buf[off]
static inline uint32_t leer_le32(const uint8_t *buf, int off){
	return (uint32_t)buf[off]
	| ((uint32_t)buf[off+1] << 8)
	| ((uint32_t)buf[off+2] << 16)
	| ((uint32_t)buf[off+3] << 24);
}

// Escribir valor como un uint32_t con formato Little Endian en buf[off]
static inline void escribir_le32(uint8_t *buf, int off, uint32_t val){
	buf[off]   = (uint8_t)(val & 0xff);
	buf[off+1] = (uint8_t)((val >> 8)  & 0xff);
	buf[off+2] = (uint8_t)((val >> 16) & 0xff);
	buf[off+3] = (uint8_t)((val >> 24) & 0xff);
}

// Generar cadena con el tiempo actual
// Formato: 'AAAAMMDDHHMMSS' 
static void now_timestamp(char *buf){
	time_t t = time(NULL);
	struct tm *tm = localtime(&t);
	strftime(buf, TIMESTAMP_LEN + 1, "%Y%m%d%H%M%S", tm); 
}

// Convertir cadena del timestamp a time_t
static time_t parse_timestamp(const char *ts){
	if (!ts || strlen(ts) < 14) return 0;
	struct tm t = {0};
	char tmp[5];
	// Se calculan valores considerando el diseño de tiempo en C para la estructura struct tm
	memcpy(tmp, ts,    4); tmp[4] = 0; t.tm_year = atoi(tmp) - 1900; //
	memcpy(tmp, ts+4,  2); tmp[2] = 0; t.tm_mon  = atoi(tmp) - 1;
	memcpy(tmp, ts+6,  2); tmp[2] = 0; t.tm_mday = atoi(tmp);
	memcpy(tmp, ts+8,  2); tmp[2] = 0; t.tm_hour = atoi(tmp);
	memcpy(tmp, ts+10, 2); tmp[2] = 0; t.tm_min  = atoi(tmp);
	memcpy(tmp, ts+12, 2); tmp[2] = 0; t.tm_sec  = atoi(tmp);
	t.tm_isdst = -1;
	return mktime(&t); // Considerando la época Unix
}

// ------------------- Funciones para el directorio -------------------








// ------------------- Funciones FUSE -------------------

static int fiunamfs_getattr(const char *path, struct stat *stbuf, struct fuse_file_info *fi) {
	memset(stbuf, 0, sizeof(struct stat));
	if (strcmp(path, "/") == 0) {
		stbuf->st_mode = S_IFDIR | 0755;
		stbuf->st_nlink = 2;
		return 0;
	}
	
	const char *name = path + 1;   // salta la diagonal inicial
	
	pthread_mutex_lock(&fs_mutex);
	int idx = find_entry(name);
	if (idx < 0) {
		pthread_mutex_unlock(&fs_mutex);
		return -ENOENT;
	}
	
	fiunamfs_entry e = g_fs.dir[idx];
	pthread_mutex_unlock(&fs_mutex);
	
	stbuf->st_mode  = S_IFREG | 0644;
	stbuf->st_nlink = 1;
	stbuf->st_size  = (off_t)e.size;
	stbuf->st_atime = parse_timestamp(e.mtime);
	stbuf->st_mtime = parse_timestamp(e.mtime);
	stbuf->st_ctime = parse_timestamp(e.ctime);
	return 0;
}

static int fiunamfs_readdir(const char *path, void *buf, fuse_fill_dir_t filler, off_t offset, struct fuse_file_info *fi, enum fuse_readdir_flags flags){
	filler(buf, ".", NULL, 0, 0); // Directorio actual
	filler(buf, "..", NULL, 0, 0); // Directorio anterior
	
	pthread_mutex_lock(&fs_mutex); //Adquirir mutex
	for (int i = 0; i < MAX_DIR_ENTRIES; i++) {
		if (g_fs.dir[i].type == ENTRY_FILE) {
			struct stat st = {0};
			st.st_mode  = S_IFREG | 0644;
			st.st_size  = (off_t)g_fs.dir[i].size;
			st.st_mtime = parse_timestamp(g_fs.dir[i].mtime);
			st.st_ctime = parse_timestamp(g_fs.dir[i].ctime);
			filler(buf, g_fs.dir[i].name, &st, 0, 0);
		}
	}
	
	pthread_mutex_unlock(&fs_mutex); //Libera el mutex
	return 0;
}

static void *fiunamfs_init(struct fuse_conn_info *conn, struct fuse_config *cfg){
	(void)conn;
	cfg->kernel_cache = 0;
	return NULL;
}

static void fiunamfs_destroy(void *private_data){
	(void)private_data;
	
	// Detener hilo de sincronización para modificaciones
	pthread_mutex_lock(&sync_mutex);
	g_fs.shutting_down = 1;
	pthread_cond_signal(&g_fs.sync_cond);
	pthread_mutex_unlock(&sync_mutex);
	pthread_join(g_fs.sync_thread, NULL);
	
	// Aplicar cambios pendientes
	pthread_mutex_lock(&fs_mutex);
	//flush_directory();  Función para pasar los cambios del directorio desde memoria hacia el disco (img)
	pthread_mutex_unlock(&fs_mutex);
	
	close(g_fs.fd);
}


//		--------------- Operaciones de FUSE ---------------
// Se definen las operaciones para el uso de FUSE
static const struct fuse_operations fiunamfs_oper = {
	.init = fiunamfs_init,
	.destroy = fiunamfs_destroy,
	.getattr = fiunamfs_getattr,
	.readdir = fiunamfs_readdir,
	// .read    = fiunamfs_read,
	// .unlink  = fiunamfs_unlink, (Eliminar archivo)
	// .write   = fiunamfs_write,  (Copiar hacia el FS)
};


//		--------------- Función principal ---------------

// Función para mostrar un manual del uso correcto del comando al usuario
static void uso_FUSE(const char *prog){
	fprintf(stderr,
	"Uso: %s <imagen.img> <punto_de_montaje> [opciones_fuse]\n"
	"\n"
	"Opciones de FUSE:\n"
	"  -f              Ejecutar en primer plano\n"
	"  -d              Modo debug (es necesario -f)\n"
	"  -o allow_other  Permite acceso a otros usuarios\n",
	prog);
}

// - MAIN -
int main(int argc, char *argv[]) {
	
	// Verificar que el usuario haya escrito los argumentos necesarios
	// En caso contrario, indicar los argumentos que necesita el comando
	if (argc < 3) {
		uso_FUSE(argv[0]);
		return 1;
	}
	
	const char *img_path = argv[1];
	
	// Se abre la imagen .img
	g_fs.fd = open(img_path, O_RDWR); // Abrir para lectura y escritura
	if (g_fs.fd < 0) {
		perror(img_path);
		return 1;
	}
	
	// Se valida el superbloque
	uint8_t sb[CLUSTER_SIZE];
	if (leer_disco(sb, CLUSTER_SIZE, 0) != 0) {
		fprintf(stderr, "Error al leer el superbloque\n");
		close(g_fs.fd);
		return 1;
	}
	
	// Validar nombre del FS
	char fs_name[SB_NAME_LEN + 1];
	memcpy(fs_name, sb + SB_NAME_OFF, SB_NAME_LEN);
	fs_name[SB_NAME_LEN] = '\0';
	if (strncmp(fs_name, FS_NAME, strlen(FS_NAME)) != 0) {
		fprintf(stderr, "Error: Este no es un volumen 'FiUnamFS' (Encontrado: '%s')\n", fs_name);
		close(g_fs.fd);
		return 1;
	}
	
	// Validar versión del sistema de archivos
	char fs_ver[SB_VER_LEN + 1];
	memcpy(fs_ver, sb + SB_VER_OFF, SB_VER_LEN);
	fs_ver[SB_VER_LEN] = '\0';
	if (strncmp(fs_ver, FS_VERSION, strlen(FS_VERSION)) != 0) {
		fprintf(stderr,
			"Error: Esta versión no es soportada '%s' (Se requiere: '%s')\n",
			fs_ver, FS_VERSION);
		close(g_fs.fd);
		return 1;
	}
	
	// Se leen los parámetros del superbloque para guardar características del sistema
	// Uso de leer_le32 para formato Little Endian
	g_fs.cluster_size   = leer_le32(sb, SB_CLSIZE_OFF);
	g_fs.dir_clusters   = leer_le32(sb, SB_DIRSIZE_OFF);
	g_fs.total_clusters = leer_le32(sb, SB_TOTALCL_OFF);
	memcpy(g_fs.label, sb + SB_LABEL_OFF, SB_LABEL_LEN);
	g_fs.label[SB_LABEL_LEN] = '\0';
	
	// Mostrar las características del sistema detectado
	fprintf(stdout,"FiUnamFS montando '%s'\n"
		" > Etiqueta           : %s\n"
		" > Tamaño del cluster : %u bytes\n"
		" > Clusters para Dir  : %u\n"
		" > Total de clusters  : %u\n",
		img_path, g_fs.label,
	g_fs.cluster_size, g_fs.dir_clusters, g_fs.total_clusters);
	
	// Cargar directorio en la memoria
	if (load_directory() != 0) {
		fprintf(stderr, "Error al cargar directorio\n");
		close(g_fs.fd);
		return 1;
	}
	
	// Inicialización de condición para g_fs y variables
	pthread_cond_init(&g_fs.sync_cond, NULL);
	g_fs.dir_dirty = 0;
	g_fs.shutting_down = 0;
	
	// Activar hilo para sincronización en g_fs
	if (pthread_create(&g_fs.sync_thread, NULL, sync_thread_func, NULL) != 0) {
		perror("pthread_create");
		close(g_fs.fd);
		return 1;
	}
	
	// Se construye 'argv' para FUSE 
	/* 1.Nombre del programa 
	 * 2.Punto de montaje
	 * 3.Opciones
	 */
	int fuse_argc = argc - 1; 	// Desplaza argumentos, restándole al contador
	char **fuse_argv = argv + 1;	// Desplaza argumentos a argv[1]
	fuse_argv[0] = argv[0];		// Apunta al nombre del programa

	// Se manda a llamar a la función main de FUSE con los argumentos obtenidos
	return fuse_main(fuse_argc, fuse_argv, &fiunamfs_oper, NULL);
}
