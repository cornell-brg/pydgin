#=========================================================================
# Makefile
#=========================================================================

TESTS = read-test.c \
				stat-test.c \
				open-close-test.c \
				args-test.c \
				malloc-test.c \
				fcntl-test.c \

ARM_TESTS = uname-test.c \

# TODO: create objects first?

NATIVE_TARGETS = $(patsubst %.c, %-native, $(TESTS))
MAVEN_TARGETS  = $(patsubst %.c, %-maven,  $(TESTS))
ARM_TARGETS    = $(patsubst %.c, %-arm,    $(TESTS))
ARM_NL_TARGETS = $(patsubst %.c, %-arm-nl, $(TESTS))

NATIVE_TARGETS+= $(patsubst %.c, %-native, $(ARM_TESTS))
ARM_TARGETS   += $(patsubst %.c, %-arm,    $(ARM_TESTS))

all : $(NATIVE_TARGETS) $(MAVEN_TARGETS) $(ARM_TARGETS) $(ARM_NL_TARGETS)

# newlib-based arm compiler
ARM_NL_CC = /work/bits0/bi45/misc/arm-toolchain/custom/arm-unknown-eabi/x-tools2/bin/arm-none-eabi-gcc

$(NATIVE_TARGETS) : %-native : %.c
	gcc -o $@ $<

$(MAVEN_TARGETS) : %-maven : %.c
	maven-gcc -o $@ $<

$(ARM_TARGETS) : %-arm : %.c
	arm-unknown-linux-uclibcgnueabi-gcc -static -o $@ $<

$(ARM_NL_TARGETS) : %-arm-nl : %.c
	$(ARM_NL_CC) -Tbrgarm.ld -static -o $@ $<

clean :
	rm $(NATIVE_TARGETS) $(MAVEN_TARGETS) $(ARM_TARGETS) $(ARM_NL_TARGETS)

