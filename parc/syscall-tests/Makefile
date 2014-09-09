#=========================================================================
# Makefile
#=========================================================================

TESTS = read-test.c \
				stat-test.c \

# TODO: create objects first?

NATIVE_TARGETS = $(patsubst %.c, %-native, $(TESTS))
MAVEN_TARGETS  = $(patsubst %.c, %-maven,  $(TESTS))

all : $(NATIVE_TARGETS) $(MAVEN_TARGETS)

$(NATIVE_TARGETS) : %-native : %.c
	gcc -o $@ $<

$(MAVEN_TARGETS) : %-maven : %.c
	maven-gcc -o $@ $<

clean :
	rm $(NATIVE_TARGETS) $(MAVEN_TARGETS)

