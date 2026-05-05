#define FUSE_USE_VERSION 31
#include <fuse.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <assert.h>

struct __attribute__((packed)) fiunamfs_entry {
	char type;                 
	char name[15];            
	uint32_t size;            
	uint32_t start_cluster;    
	char ctime[14];            
	char mtime[14];            
	char reserved[12];        
};

static pthread_mutex_t fs_mutex = PTHREAD_MUTEX_INITIALIZER;

static int fiunamfs_getattr(const char *path, struct stat *stbuf, struct fuse_file_info *fi) {
	memset(stbuf, 0, sizeof(struct stat));
	if (strcmp(path, "/") == 0) {
		stbuf->st_mode = S_IFDIR | 0755;
		stbuf->st_nlink = 2;
		return 0;
	}


	return -ENOENT;
	}
}

static int fiunamfs_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
							off_t offset, struct fuse_file_info *fi, enum fuse_readdir_flags flags) {
	filler(buf, ".", NULL, 0, 0);
	filler(buf, "..", NULL, 0, 0);

	pthread_mutex_lock(&fs_mutex);

	pthread_mutex_unlock(&fs_mutex);

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

