# sensor_diag/Makefile
CC_X86  = gcc
CC_ARM  = arm-linux-gnueabihf-gcc
CC_MIPS = mips-linux-gnu-gcc
CFLAGS  = -O2 -Wall -Wextra -std=c99 -pedantic
SRCS    = main.c diagnostics.c

all: x86

x86:
	$(CC_X86) $(CFLAGS) -o sensor_diag_x86 $(SRCS) -lm

arm:
	$(CC_ARM) $(CFLAGS) -o sensor_diag_arm $(SRCS) -lm

mips:
	$(CC_MIPS) $(CFLAGS) -o sensor_diag_mips $(SRCS) -lm

test:
	$(CC_X86) $(CFLAGS) -o run_tests test_diagnostics.c diagnostics.c -lm
	./run_tests

clean:
	rm -f sensor_diag_x86 sensor_diag_arm sensor_diag_mips run_tests
