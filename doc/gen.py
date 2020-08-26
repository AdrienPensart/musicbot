#!/usr/bin/env python3
from click_skeleton.doc import gen_doc
from musicbot.cli import cli, CONTEXT_SETTINGS, prog_name


if __name__ == '__main__':
    with open("doc/help.rst", "r") as main_doc:
        print(main_doc.read())
    gen_doc(cli, prog_name, CONTEXT_SETTINGS)
