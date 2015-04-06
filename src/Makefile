package=zData
version=$(shell git describe --abbrev=0 --tags 2>/dev/null | echo '9.9.9')
distdir=$(version).$(package)

tmp_dir:=$(shell mktemp -d)

ambari_path="/var/lib/ambari-server/resources/stacks"
ambari_stack="HDP"

export pwd ?= $(shell pwd)

src=$(shell find . -type f \
	-not -name '.hash' \
	-not -name 'archive.zip' \
	-not -path '*/.git/*' \
	-not -path '*/.*' \
	-not -path '*/.vagrant/*' \
)

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
			gzip -9 -c > $(pwd)/$(distdir).tar.gz

$(distdir): $(src)
	mkdir -p $(tmp_dir)/$(distdir)
	cp --parents $? $(tmp_dir)/$(distdir)

	# Development to production text replacements
	cd "$(tmp_dir)/$(distdir)"; \
		sed -i"" "s/9\\.9\\.9/$(version)/" Makefile

.PHONY: dist install uninstall clean
