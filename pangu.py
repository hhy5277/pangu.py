#!/usr/bin/env python
# coding: utf-8
"""
Paranoid text spacing for good readability, to automatically insert whitespace
between CJK (Chinese, Japanese, Korean) and half-width characters (alphabetical
letters, numerical digits and symbols).

>>> import pangu
>>> pangu.spacing_text('當你凝視著bug，bug也凝視著你')
>>> # output: '當你凝視著 bug，bug 也凝視著你'
>>> pangu.spacing_file('path/to/file.txt')
>>> # output: '與 PM 戰鬥的人，應當小心自己不要成為 PM'
"""

from __future__ import print_function

import argparse
import os
import re
import sys


__version__ = '3.3.1'
__all__ = ['spacing', 'spacing_text', 'spacing_file', 'PanguCLI']

IS_PY2 = (sys.version_info[0] == 2)

if IS_PY2:
    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'), 'unicode_escape')  # noqa: F821
else:
    def u(s):
        return s

CJK_QUOTE_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(["\'])'))
QUOTE_CJK_RE = re.compile(u(r'(["\'])([\u3040-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
FIX_QUOTE_RE = re.compile(u(r'(["\'\(\[\{<\u201c]+)(\s*)(.+?)(\s*)(["\'\)\]\}>\u201d]+)'))
FIX_SINGLE_QUOTE_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])( )(\')([A-Za-z])'))

CJK_HASH_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])(#(\S+))'))
HASH_CJK_RE = re.compile(u(r'((\S+)#)([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))

CJK_OPERATOR_ANS_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\+\-\*\/=&\\|<>])([A-Za-z0-9])'))
ANS_OPERATOR_CJK_RE = re.compile(u(r'([A-Za-z0-9])([\+\-\*\/=&\\|<>])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))

CJK_BRACKET_CJK_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\(\[\{<\u201c]+(.*?)[\)\]\}>\u201d]+)([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
CJK_BRACKET_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([\(\[\{<\u201c>])'))
BRACKET_CJK_RE = re.compile(u(r'([\)\]\}>\u201d<])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))
FIX_BRACKET_RE = re.compile(u(r'([\(\[\{<\u201c]+)(\s*)(.+?)(\s*)([\)\]\}>\u201d]+)'))

FIX_SYMBOL_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([~!;:,\.\?\u2026])([A-Za-z0-9])'))

CJK_ANS_RE = re.compile(u(r'([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])([A-Za-z0-9`\$%\^&\*\-=\+\\\|/@\u00a1-\u00ff\u2022\u2027\u2150-\u218f])'))
ANS_CJK_RE = re.compile(u(r'([A-Za-z0-9`~\$%\^&\*\-=\+\\\|/!;:,\.\?\u00a1-\u00ff\u2022\u2026\u2027\u2150-\u218f])([\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])'))


def spacing_text(text):
    """
    Perform paranoid text spacing on text.
    """
    new_text = text

    # always use unicode
    if IS_PY2 and isinstance(new_text, str):
        new_text = new_text.decode('utf-8')

    if len(new_text) < 2:
        return new_text

    new_text = CJK_QUOTE_RE.sub(r'\1 \2', new_text)
    new_text = QUOTE_CJK_RE.sub(r'\1 \2', new_text)
    new_text = FIX_QUOTE_RE.sub(r'\1\3\5', new_text)
    new_text = FIX_SINGLE_QUOTE_RE.sub(r'\1\3\4', new_text)

    new_text = CJK_HASH_RE.sub(r'\1 \2', new_text)
    new_text = HASH_CJK_RE.sub(r'\1 \3', new_text)

    new_text = CJK_OPERATOR_ANS_RE.sub(r'\1 \2 \3', new_text)
    new_text = ANS_OPERATOR_CJK_RE.sub(r'\1 \2 \3', new_text)

    old_text = new_text
    tmp_text = CJK_BRACKET_CJK_RE.sub(r'\1 \2 \4', new_text)
    new_text = tmp_text
    if old_text == tmp_text:
        new_text = CJK_BRACKET_RE.sub(r'\1 \2', new_text)
        new_text = BRACKET_CJK_RE.sub(r'\1 \2', new_text)
    new_text = FIX_BRACKET_RE.sub(r'\1\3\5', new_text)

    new_text = FIX_SYMBOL_RE.sub(r'\1\2 \3', new_text)

    new_text = CJK_ANS_RE.sub(r'\1 \2', new_text)
    new_text = ANS_CJK_RE.sub(r'\1 \2', new_text)

    return new_text.strip()


def spacing_file(path):
    """
    Perform paranoid text spacing from file.
    """
    with open(os.path.abspath(path)) as f:
        fdata = f.read()
    return spacing_text(fdata)


def _is_abs_file(fpath):
    """
    Check if `fpath` is a abs path and is a file.
    """
    return os.path.isabs(fpath) and os.path.isfile(fpath)


def _detect_filepath(src):
    """
    Detect if src is a file or not, return the abs path or None.
    """
    if not src:
        return None

    if os.path.isabs(src) and os.path.isfile(src):
        return src

    if src.startswith("~"):
        abspath = os.path.expanduser(src)
        if _is_abs_file(abspath):
            return abspath
    else:
        currdir = os.path.abspath(os.path.curdir)
        abspath = os.path.join(currdir, src)
        if _is_abs_file(abspath):
            return abspath
    return None


def spacing(path_or_text):
    """
    Perform paranoid text spacing.
    """
    if _detect_filepath(path_or_text):
        greater_text = spacing_file(path_or_text)
    else:
        greater_text = spacing_text(path_or_text)
    return greater_text


class PanguCLI(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog='pangu',
            description='paranoid text spacing',
        )
        self.parser = parser
        self.parser.add_argument('-v', '--version', action='version', version=__version__)
        self.parser.add_argument('text_or_path', action='store', type=str)

        # TODO: be explicit
        # pangu "text"
        # pangu -f path/to/file.txt

    def parse(self):
        if not sys.stdin.isatty():
            print(spacing_text(sys.stdin.read()))  # noqa: T003
        elif len(sys.argv) > 1:
            namespace = self.parser.parse_args()
            print(spacing(namespace.text_or_path))  # noqa: T003
        else:
            self.parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    PanguCLI().parse()
