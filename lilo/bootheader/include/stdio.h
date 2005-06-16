#ifndef _PPC_BOOT_STDIO_H_
#define _PPC_BOOT_STDIO_H_
/* $Id$ */

#include <stdarg.h>

extern int printf(const char *fmt, ...);

extern int sprintf(char *buf, const char *fmt, ...);

extern int vsprintf(char *buf, const char *fmt, va_list args);

extern int putc(int c);
extern int putchar(int c);
extern int getchar(void);

extern int fputs(char *str, void *f);

#endif				/* _PPC_BOOT_STDIO_H_ */
