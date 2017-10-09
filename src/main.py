#!/usr/bin/env python
"""Tag editor for the BGM project."""

import traceback

from frontend.repl import REPL

import lib.tag as tag

from lib.config import config

from zenlog import log


def main() -> None:
    """Start the program."""
    # TODO: add argument handling here
    # TODO: frontend loading should be conditional
    repl = REPL(config)
    repl.cmdloop()
    # db = tag.load_tagdb('taglist.xml')
    # print(tag.get_id_map(db))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.c(traceback.format_exc())
