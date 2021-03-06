"""
bf to c compiler

resulting program will be built to collect coverage data
when run. (coverage data measures which ops in the bf
source get run)
"""

import argparse
from cStringIO import StringIO
from string import Template as T
import os

from common import KNOWN_OPS, read_source, make_hash


BF_BASE = {
    'program_begin' : T(r"""
int main() {
    """),
    'program_end' : T(r"""
return 0;
}
    """),
}


BF_INTERP = {
    'include' : T(r"""
#include <string.h>
#include <unistd.h>
    """),
    'program_begin' : T(r"""
unsigned char buffer[${buffer_size}];
memset((void*)buffer, 0, (size_t)${buffer_size});
int dp = 0;
    """),

    '.' : T(r"""
write(STDOUT_FILENO, &(buffer[dp]), 1);
    """),

    ',' : T(r"""
read(STDIN_FILENO, &(buffer[dp]), 1);
    """),

    '>' : T(r"""
++dp;
    """),

    '<' : T(r"""
--dp;
    """),

    '+' : T(r"""
++buffer[dp];
    """),

    '-' : T(r"""
--buffer[dp];
    """),

    '[' : T(r"""
while (buffer[dp]) {
    """),

    ']' : T(r"""
}
    """),

    'program_end' : T(r"""
    """),
}


BF_COV = {
    'include' : T(r"""
#include <string.h>
#include <stdio.h>
    """),
    'program_begin' : T(r"""
unsigned char cov_mask[${program_size}];
memset((void*)cov_mask, 0, (size_t)${program_size});
    """),

    'default' : T(r"""
cov_mask[${src_line}] = 1;
    """),

    'program_end' : T(r"""
FILE *cov_f = fopen("coverage.dat", "w");
fprintf(cov_f, "%s\n", "${source_file_name}");
fprintf(cov_f, "%s\n", "${source_file_hash}");
fprintf(cov_f, "%d\n", ${program_size});
fwrite((void*)cov_mask, (size_t)1, (size_t)${program_size}, cov_f);
fclose(cov_f);
    """),
}


class Gen():
    def __init__(self, buffer_size, program_size, source_file_name, source_file_hash, templates, out):
        self.buffer_size = buffer_size
        self.program_size = program_size
        self.source_file_name = source_file_name
        self.source_file_hash = source_file_hash
        self.templates = templates
        self.out = out

    def _emit(self, op, t):
        if op in self.templates:
            self.out.write(self.templates[op].substitute(t))

    def emit_op(self, op, src_line=None):
        t = {
            'program_size' : self.program_size,
            'buffer_size' : self.buffer_size,
            'source_file_name' : self.source_file_name,
            'source_file_hash' : self.source_file_hash,
        }
        if src_line is not None:
            t['src_line'] = str(src_line)
        if op not in self.templates:
            op = 'default'
        self._emit(op, t)

class GenGen():
    def __init__(self, subgens):
        self.subgens = subgens

    def emit_op(self, op, src_line=None):
        gen_order = self.subgens
        if op in ('program_end', ']'):
            gen_order = reversed(gen_order)
        for g in gen_order:
            g.emit_op(op, src_line)


def make_master_gen(buffer_size, program_size, source_file_name, source_file_hash, out):
    ts = [BF_BASE, BF_INTERP, BF_COV]
    gens = []
    for t in ts:
        gen = Gen(buffer_size, program_size, source_file_name, source_file_hash, t, out)
        gens.append(gen)
    return GenGen(gens)


def compile(s, g):
    g.emit_op('include')
    g.emit_op('program_begin')
    for i, c in enumerate(s):
        if c in KNOWN_OPS:
            g.emit_op(c, i)
        else:
            pass # ignore unrecognised characters
    g.emit_op('program_end')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('source', metavar='FILE')
    p.add_argument('-b', '--buffer-size', dest='buffer_size', metavar='N', type=int, default=30000)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    source = read_source(args.source)
    out = StringIO()
    gen = make_master_gen(
        buffer_size=args.buffer_size,
        program_size=len(source),
        source_file_name=os.path.abspath(args.source),
        source_file_hash=make_hash(source),
        out=out)
    compile(source, gen)
    print out.getvalue()

