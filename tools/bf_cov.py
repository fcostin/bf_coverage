import argparse
import struct
from collections import namedtuple
from common import KNOWN_OPS, read_source, make_hash
import os
import logging

import coveralls


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


def make_coveralls_style_data(cov_file):
    source = read_source(cov_file.source_file_name)
    source_hash = make_hash(source)

    # check source hasnt changed from when it was compiled into
    # executable that wrote the coverage.dat file
    assert source_hash == cov_file.source_hash

    source_lines = source.split('\n')
    line_cov = figure_out_line_coverage(source_lines, cov_file.hit_ops)

    line_cov_mask = [None]*len(source_lines)
    for i, line in enumerate(source_lines):
        line_cov_mask[i] = int(i in line_cov)
    
    return (source_hash,
        {'name':cov_file.source_file_name, 'source':source, 'coverage':line_cov_mask})


def merge_data(a, b):
    out = dict(a)
    a_cov = a['coverage']
    b_cov = b['coverage']
    assert len(a_cov) == len(b_cov)
    out['coverage'] = [ai+bi for ai, bi in zip(a_cov, b_cov)]
    return out


class BfCoveralls(coveralls.Coveralls):
    def __init__(self, bf_coverage, *args, **kwargs):
        self.bf_coverage = bf_coverage
        super(BfCoveralls, self).__init__(*args, **kwargs)

    def get_coverage(self):
        """
        returns [{'name':"foo.bf", 'source':"[-]++.", 'coverage':[0,0,0,1,1,1]}, ...]
        """
        return self.bf_coverage


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('coverage_files', nargs='*', metavar='FILE')
    p.add_argument('--root', dest='root', metavar='REPO_ROOT')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()

    log = logging.getLogger('bf_cov')

    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    if args.root is None:
        root = os.getcwd()
    else:
        root = args.root
    root = os.path.abspath(root)

    data_by_key = {}
    for cov_file_name in args.coverage_files:
        cov_file = read_coverage_file(cov_file_name)
        key, data = make_coveralls_style_data(cov_file)
        if key not in data_by_key:
            data_by_key[key] = data
        else:
            data_by_key[key] = merge_data(data_by_key[key], data)

    data = data_by_key.values()
    data = sorted(data, key = lambda d : d['name'])

    # postprocess file names so they are relative to root
    for d in data:
        d['name'] = os.path.relpath(d['name'], root)
        logging.debug('got coverage data for "%s"' % d['name'])

    logging.debug('submitting coverage data via coveralls...')
    coveralls = BfCoveralls()
    coveralls.wear()
    logging.debug('fin.')

