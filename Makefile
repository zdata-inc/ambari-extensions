export pwd=$(shell pwd)

dist install uninstall clean:
	$(MAKE) -C src $@

.PHONY: install uninstall clean dist
