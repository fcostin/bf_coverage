import argparse
import struct
from collections import namedtuple

from common import KNOWN_OPS, read_source, make_hash


CovFile = namedtuple('CovFile', ['source_file_name', 'source_hash', 'n_ops', 'hit_ops'])


def gen_source_by_lines(lines):
    j0 = 0
    for i, line in enumerate(lines):
        n = len(line)
        for j, c in enumerate(line):
            yield i, j + j0, c
        # hack: add 1 here as we ate 1 newline to split earlier
        j0 += n + 1

def figure_out_line_coverage(lines, op_cov):
    line_cov = set()
    for i_line, j_op, c in gen_source_by_lines(lines):
        if c in KNOWN_OPS:
            if j_op in op_cov:
                line_cov.add(i_line)
        else:
            pass
    return line_cov

def read_coverage_file(file_name):
    with open(file_name, 'rb') as f:
        src_file_name = f.readline().strip()
        src_hash = f.readline().strip()
        n = int(f.readline().strip())
        data = f.read()

    assert n == len(data)
    op_mask = struct.unpack('%db' % n, data)
    hit_op_indices = set(i for (i, bit) in enumerate(op_mask) if bit)

    return CovFile(src_file_name, src_hash, n, hit_op_indices)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('coverage_files', nargs='*', metavar='FILE')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()

    for cov_file_name in args.coverage_files:
        cov_file = read_coverage_file(cov_file_name)

        source = read_source(cov_file.source_file_name)
        source_hash = make_hash(source)
        assert source_hash == cov_file.source_hash

        source_lines = source.split('\n')
        line_cov = figure_out_line_coverage(source_lines, cov_file.hit_ops)

        print '*** "%s"' % cov_file.source_file_name
        for i, line in enumerate(source_lines):
            margin = 'HIT' if i in line_cov else 'MISS'
            print '%s\t%s' % (margin, line)

