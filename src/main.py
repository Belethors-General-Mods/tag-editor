#!/usr/bin/env python

# Tag editor for the BGM project.

import traceback

import argparse

from frontend.repl import REPL

import lib.tag as tag

from lib.config import config

from zenlog import log


def main() -> None:
    # Start the program.
    
    parser = argparse.ArgumentParser(description='Use the BGM management tool from the command line, Huzzah!')
    parser.add_argument("-f", "--frontend", action="store_true",
        help='flag for using the frontend')
    
    
    args = parser.parse_args()
    # print args for debug purposes
    print(args)
    
    db = tag.DB()
    db_hist = [db]
    
    ftag = tag.FTAG(config, db, db_hist)
    ftag.load_database()
    
    # frontend loading is optional.
    if args.frontend:
        repl = REPL(config)
        repl.cmdloop()
        pass
    
    # TODO: add more arguments and make this thing useable with only arguments through the command line
    # the whole repl thing is way more complicated than it really needs to be


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.c(traceback.format_exc())
