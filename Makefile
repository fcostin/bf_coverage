all:	bfc/bfc.out
.PHONY: all

bfc/bfc.c:	bfc/bfc.bf
	python tools/bf2c.py $^ > $@

bfc/bfc.out:	bfc/bfc.c
	gcc $^ -o $@

