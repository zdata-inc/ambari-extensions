package=zData
version=$(shell git describe --abbrev=0 --tags 2>/dev/null || echo 'old-vagrant')
distdir=$(version).$(package)

src=$(shell find . -type f \
	-not -name '$(distdir).tar.gz' \
	-not -name '.hash' \
	-not -name 'archive.zip' \
	-not -path '*/.git/*' \
	-not -path '*/.vagrant/*' \
)

ambari_path=/var/lib/ambari-server/resources/stacks
ambari_stack=HDP

tmp_dir:=$(shell mktemp -d)

dist: $(distdir).tar.gz

install: $(distdir)
	cd $(ambari_path)/$(ambari_stack); \
		cp -r $(tmp_dir)/$(distdir) .;

uninstall:
	rm -rf $(ambari_path)/$(ambari_stack)/$(distdir);

clean:
	rm -rf $(tmp_dir);

$(distdir).tar.gz: $(distdir)
	cd "$(tmp_dir)" ;\
		tar cof - $(distdir) |\
			gzip -9 -c > $(shell pwd)/../$(distdir).tar.gz

$(distdir): $(src)
	mkdir $(tmp_dir)/$(distdir)
	cp --parents $? $(tmp_dir)/$(distdir)

	# Development to production text replacements
	cd "$(tmp_dir)/$(distdir)"; \
		sed -i "" "s/9\\.9\\.9/$(version)/" Makefile

.PHONY: $(distdir) dist install uninstall clean
