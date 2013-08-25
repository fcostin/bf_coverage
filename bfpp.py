"""
brainfuck pretty-printer
"""

import sys
import argparse
from cStringIO import StringIO

OPCODES = '.,<>+-[]'
OPCODE_BEGIN = '['
OPCODE_END = ']'

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('source', metavar='FILE', help='source file')
    p.add_argument('-i', '--indent', dest='indent', type=int, default=1, help='spaces to indent')
    p.add_argument('-m', '--margin', dest='margin', type=int, default=70, help='margin width')
    return p.parse_args(args)

def clean(s):
    out = StringIO()
    for c in s:
        if not c in OPCODES:
            continue
        out.write(c)
    return out.getvalue()


class Writer:
    def __init__(self, indent, margin):
        self._indent = indent
        self._margin = margin
        self._buffer = StringIO()
        self._offset = 0
        self._line = None

    def emit_line(self):
        if self._line is not None:
            self._buffer.write(' ' * self._offset)
            self._buffer.write(self._line)
            self._buffer.write('\n')
        self._line = None

    def dedent(self):
        self._offset -= self._indent

    def indent(self):
        self._offset += self._indent

    def new_line(self, prefix=None):
        if self._line:
            self.emit_line()
        self._line = ''
        if prefix:
            self.append_to_line(prefix)

    def append_to_line(self, s):
        m = self._margin - self._offset
        while s:
            if self._line is None:
                self._line = ''
            n = m - len(self._line)
            self._line += s[:n]
            s = s[n:]
            if s:
                self.emit_line()

    def getvalue(self):
        return self._buffer.getvalue()

def layout(s, w):
    for c in s:
        if c == OPCODE_END:
            w.emit_line()
            w.dedent()
            w.new_line(c)
            w.new_line()
        elif c == OPCODE_BEGIN:
            w.emit_line()
            w.new_line(c)
            w.emit_line()
            w.indent()
            w.new_line()
        else:
            w.append_to_line(c)
    w.emit_line()
    return w.getvalue()


def main():
    args = parse_args(sys.argv[1:])
    with open(args.source, 'r') as f:
        raw_source = f.read()

    source = clean(raw_source)
    writer = Writer(args.indent, args.margin)
    output = layout(source, writer)
    sys.stdout.write(output)

if __name__ == '__main__':
    main()

