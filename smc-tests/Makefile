
ALL = smc-test-native smc-test-parc smc-test-parc.dump

all: $(ALL)

smc-test-native: smc-test-parc.c
	gcc -o $@ $<

smc-test-parc: smc-test-parc.c
	maven-gcc -o $@ $<

smc-test-parc.dump: smc-test-parc
	maven-objdump -dC $< > $@

clean:
	rm -f $(ALL)
