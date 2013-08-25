import os.path
import glob
import subprocess

import py.test


TEST_DIR_PREFIX = 'test_'


def here():
    return os.path.abspath(os.path.join(os.path.dirname(__file__)))

def bfc():
    return os.path.join(here(), 'bfc', 'bfc.out')

def scenario_dirs():
    m = glob.glob(os.path.join(here(), TEST_DIR_PREFIX + '*'))
    return [x for x in m if os.path.isdir(x)]

def get_scenario_name(scenario_dir):
    # figure out scenario name
    scenario_name = os.path.basename(scenario_dir)
    assert scenario_name.startswith(TEST_DIR_PREFIX)
    return scenario_name[len(TEST_DIR_PREFIX):]


@py.test.mark.parametrize(('scenario_dir', ), [(x, ) for x in scenario_dirs()])
def test_scenario(scenario_dir):
    name = get_scenario_name(scenario_dir)
    bf_name = os.path.join(scenario_dir, name + '.bf')
    s_name = os.path.join(scenario_dir, name + '.s')
    out_name = os.path.join(scenario_dir, name + '.out')

    cc_opts = '-nostdlib -Wl,--build-id=none'

    cmds = [
        ('cat %s | %s > %s' % (bf_name, bfc(), s_name)),
        ('gcc %s %s -o %s' % (s_name, cc_opts, out_name)),
        ('cat input.txt | %s > output.txt' % out_name),
        'diff -q output.txt expected_output.txt',
    ]

    huge_cmd = '&&'.join('(' + cmd + ')' for cmd in cmds)

    print huge_cmd

    p = subprocess.Popen(huge_cmd, shell=True, cwd=scenario_dir)
    p.communicate()
    assert p.returncode == 0

