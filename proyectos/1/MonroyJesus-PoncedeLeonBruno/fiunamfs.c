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
  Estructuras
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

//-------------------

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

static int fiunamfs_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
							off_t offset, struct fuse_file_info *fi, enum fuse_readdir_flags flags){
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
							
static const struct fuse_operations fiunamfs_oper = {
	.getattr = fiunamfs_getattr,
	.readdir = fiunamfs_readdir,
	// .read    = fiunamfs_read,
	// .unlink  = fiunamfs_unlink, (Eliminar archivo)
	// .write   = fiunamfs_write,  (Copiar hacia el FS)
};
							
int main(int argc, char *argv[]) {
	return fuse_main(argc, argv, &fiunamfs_oper, NULL);
}
