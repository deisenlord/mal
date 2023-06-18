SOURCES_BASE = lisptypes.py reader.py printer.py lisp_input.py
SOURCES_LISP = env.py core.py stepA_mal.py
SOURCES = $(SOURCES_BASE) $(SOURCES_LISP)

all:
	true

dist: mal.pyz mal

SHELL := bash
mal.pyz: $(SOURCES)
	cp stepA_mal.py __main__.py
	zip -q - __main__.py $+ > $@
	rm __main__.py

mal: mal.pyz
	echo '#!/usr/bin/env python3' > $@
	cat $< >> $@
	chmod +x $@

install:
	sudo cp mal /usr/local/bin
	sudo cp bootstrap.mal core.mal lists.mal stats.mal csv.mal sets.mal vec.mal  /usr/local/lib/mal
clean:
	rm -f mal.pyz mal
