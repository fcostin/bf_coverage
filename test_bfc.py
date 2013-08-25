import os
import subprocess
from cStringIO import StringIO
import bf2c
import tempfile

import py.test


BUFFER_SIZE = 30000


def compile_bf(source_file_name, out_dir, program_name, buffer_size=BUFFER_SIZE):
    """
    read bf from source, compile to c, then to binary via gcc
    """
    assert os.path.exists(source_file_name)
    source = bf2c.read_source(source_file_name)
    out = StringIO()
    gen = bf2c.make_master_gen(buffer_size=BUFFER_SIZE, program_size=len(source), out=out)
    bf2c.compile(source, gen)
    bfc_c_file_name = os.path.join(out_dir, program_name + '.c')
    with open(bfc_c_file_name, 'w') as f:
        f.write(out.getvalue())
    bfc_out_name = os.path.join(out_dir, program_name + '.out')

    p = subprocess.Popen(['gcc', bfc_c_file_name, '-o', bfc_out_name])
    p.communicate()
    assert p.returncode == 0

    assert os.path.exists(bfc_out_name)
    return bfc_out_name


class BfProgram:
    def __init__(self, source_file_name):
        self.source_file_name = source_file_name
        self.out_file_name = None

    def compile(self, out_dir=None, program_name='a'):
        if out_dir is None:
            out_dir = tempfile.mkdtemp()
        self.out_file_name = compile_bf(self.source_file_name, out_dir, program_name)

    def run(self, stdin):
        p = subprocess.Popen([self.out_file_name])
        out, err = p.communicate(stdin)
        return (out, err, p.returncode)

    def coverage(self):
        pass

@py.test.fixture()
def bfc(tmpdir):
    tmpdir = str(tmpdir)
    bfc_source = 'bfc_pp.bf'
    bfc = BfProgram(bfc_source)
    bfc.compile()
    return bfc

def test_bfc_compiles_empty_program(bfc):
    out, err, returncode = bfc.run('')
    assert returncode == 0

