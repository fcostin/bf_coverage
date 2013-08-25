import argparse
import struct


KNOWN_OPS = '<>+-[].,'

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

def read_source(file_name):
    with open(file_name, 'r') as f:
        source = f.read()
    return source

def read_op_cov(file_name):
    with open(file_name, 'rb') as f:
        data = f.read()
    n = len(data)
    op_mask = struct.unpack('%db' % n, data)
    hit_op_indices = set(i for (i, bit) in enumerate(op_mask) if bit)
    return hit_op_indices

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('source', metavar='FILE')
    p.add_argument('coverage_dat', metavar='FILE')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    source = read_source(args.source)
    op_cov = read_op_cov(args.coverage_dat)

    source_lines = source.split('\n')
    line_cov = figure_out_line_coverage(source_lines, op_cov)

    for i, line in enumerate(source_lines):
        margin = 'HIT' if i in line_cov else 'MISS'
        print '%s\t%s' % (margin, line)
