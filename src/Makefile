# INCLUDE_DIRS = -I/opt/intel/compilers_and_libraries_2020.0.166/linux/mpi/intel64/include/
# LIB_DIRS = -L/opt/intel/compilers_and_libraries_2020.0.166/linux/mpi/intel64/lib/debug -L/opt/intel/compilers_and_libraries_2020.0.166/linux/mpi/intel64/lib
# MPICC = mpicc
CC = g++

CDEFS=
# CFLAGS= -g -Wall -fopenmp $(INCLUDE_DIRS) $(CDEFS)
CFLAGS= -g -Wall -fopenmp $(CDEFS)
LIBS=

PRODUCT= integrate 

HFILES= 
CFILES= integrate.cpp

SRCS= ${HFILES} ${CFILES}
OBJS= ${CFILES:.c=.o}
all:	integrate 

clean:
	-rm -f *.o *.d
	-rm -f integrate

distclean:
	-rm -f *.o *.d
	-rm -f integrate

integrate: integrate.o
	$(CC) $(LDFLAGS) $(CFLAGS) -o $@ $@.o

depend:

.c.o:
	$(CC) $(CFLAGS) -c $<