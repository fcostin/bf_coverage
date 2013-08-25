all:	bfc/bfc.out
.PHONY: all

test:	bfc/bfc.out test_bfc.py
	py.test test_bfc.py
.PHONY: test

clean:
	rm -rf bfc/bfc.out
	rm -rf bfc/bfc.c
.PHONY: clean

bfc/bfc.c:	bfc/bfc.bf
	python tools/bf2c.py $^ > $@

bfc/bfc.out:	bfc/bfc.c
	gcc $^ -o $@

