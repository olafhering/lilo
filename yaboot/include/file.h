/*
    Definitions for talking to the Open Firmware PROM on
    Power Macintosh computers.

    Copyright (C) 1999 Benjamin Herrenschmidt

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

#ifndef FILE_H
#define FILE_H

#include "types.h"
#include "stddef.h"
#include "prom.h"

#define FILE_MAX_PATH		1024

/* Simple error codes */
#define FILE_ERR_OK		0
#define FILE_ERR_EOF		-1
#define FILE_ERR_NOTFOUND	-2
#define FILE_CANT_SEEK		-3
#define FILE_IOERR		-4

/* Device kind */
#define FILE_DEVICE_BLOCK	1
#define FILE_DEVICE_NET		2

struct boot_file_t {

	/* File access methods */

	int		(*read)(	struct boot_file_t*	file,
					unsigned int		size,
					void*			buffer);
				
	int		(*seek)(	struct boot_file_t*	file,
					unsigned int		newpos);
					
	int		(*close)(	struct boot_file_t*	file);

	/* Filesystem private (to be broken once we have a
	 * better malloc'ator)
	 */

	int		device_kind;
	ihandle		of_device;
	ino_t		inode;
	unsigned int	pos;
	unsigned char*	buffer;
	unsigned long	len;
//	unsigned int	dev_blk_size;
//	unsigned int	part_start;
//	unsigned int	part_count;
};

extern int open_file(	const char*		of_device,
			int			default_partition,
			const char*		default_file_name,
			struct boot_file_t*	file);

extern char *parse_device_path(
			char*			of_device,
			char**			file_spec,
			int*			partition);


#endif
