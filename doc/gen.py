#!/usr/bin/env python3
from click_skeleton.doc import gen_doc
from musicbot.cli import cli, CONTEXT_SETTINGS, PROG_NAME


if __name__ == '__main__':
    with open("doc/help.rst", "r") as main_doc:
        print(main_doc.read())
    gen_doc(cli, PROG_NAME, CONTEXT_SETTINGS)
