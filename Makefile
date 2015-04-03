package=zData
version=$(shell git describe --abbrev=0 --tags 2>/dev/null || echo '9.9.9')
distdir=$(version).$(package)


src=$(shell find src -type f \
	-not -name '.hash' \
	-not -name 'archive.zip' \
	-not -path '*/.git/*' \
	-not -path '*/.vagrant/*' \
)

ambari_path=/var/lib/ambari-server/resources/stacks
ambari_stack=HDP

tmp_dir:=$(shell mktemp -d)

dist install uninstall clean:
	$(MAKE) -C src $@

$(distdir).tar.gz: $(filter-out $(distdir).tar.gz,$(distdir))
	cd "$(tmp_dir)" ;\
		tar cof - $(distdir) |\
			gzip -9 -c > $(shell pwd)/$(distdir).tar.gz

$(distdir): $(src)
	cp --parents $? $(tmp_dir)
	cp Makefile $(tmp_dir)/src

	cd "$(tmp_dir)"; \
		mv src $(distdir);

	# Development to production text replacements
	cd "$(tmp_dir)/$(distdir)"; \
		echo $(pwd); \
		sed -i "" "s/9\\.9\\.9/$(version)/" Makefile