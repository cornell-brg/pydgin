#=========================================================================
# Makefile
#=========================================================================

TESTS = read-test.c \
				stat-test.c \
				open-close-test.c \
				args-test.c \

# TODO: create objects first?

NATIVE_TARGETS = $(patsubst %.c, %-native, $(TESTS))
MAVEN_TARGETS  = $(patsubst %.c, %-maven,  $(TESTS))
ARM_TARGETS    = $(patsubst %.c, %-arm,    $(TESTS))

all : $(NATIVE_TARGETS) $(MAVEN_TARGETS) $(ARM_TARGETS)

$(NATIVE_TARGETS) : %-native : %.c
	gcc -o $@ $<

$(MAVEN_TARGETS) : %-maven : %.c
	maven-gcc -o $@ $<

$(ARM_TARGETS) : %-arm : %.c
	arm-unknown-linux-uclibcgnueabi-gcc -static -o $@ $<

clean :
	rm $(NATIVE_TARGETS) $(MAVEN_TARGETS) $(ARM_TARGETS)

