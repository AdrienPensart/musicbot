#!/usr/bin/env python3
from click_skeleton import doc
from musicbot.cli import main_cli, PROG_NAME


if __name__ == '__main__':
    with open("doc/help.rst", "r") as main_doc:
        print(main_doc.read())
    context_settings = {
        'max_content_width': 140,
        'terminal_width': 140,
        'help_option_names': ['-h', '--help'],
    }
    doc.readme(main_cli, PROG_NAME, context_settings)
