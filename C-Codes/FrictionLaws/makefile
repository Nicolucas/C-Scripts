
CC = gcc
CFLAGS = -g -O0 -Wall -std=c99

LIBS = -lm

INC = -I.

SRC =	Lib_SetOfFrictionLaws.c \
	Lib_NewmarkTS.c \

OBJ = $(SRC:.c=.o)

HDR = $(SRC:.c=.h)

all:
	-@$(MAKE) fl_tester
	-@$(MAKE) stress_sandbox


fl_tester: $(OBJ) FL_Tester.o
	$(CC) $(CFLAGS) -o fl_tester FL_Tester.o $(INC) $(OBJ) $(LIBS)

stress_sandbox: $(OBJ) Stress_Sandbox.o
	$(CC) $(CFLAGS) -o stress_sandbox Stress_Sandbox.o $(INC) $(OBJ) $(LIBS)

%.o: %.c $(HDR)
	-@echo "---- Compiling $*.c -----"
	$(CC) $(CFLAGS) -c -o $*.o $*.c $(INC)


clean:
	-@rm -rf *.o
	-@rm -rf fl_tester
	-@rm -rf stress_sandbox
	-@rm -rf *.dSYM

