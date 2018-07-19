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
    
    parser = argparse.ArgumentParser(description="Use the BGM management tool from the command line, Huzzah!")
    
    parser.add_argument("-f", "--frontend", action="store_true",
        help="flag for using the frontend")
    
    parser.add_argument("-g", "--get-tag", nargs=1, default=None,
        help="prints the tag under the given name or ID")
    
    parser.add_argument("-l", "--list", action="store_true",
        help="lists all tags")
    
    parser.add_argument("-a", "--add", nargs=1,
        help="creates and adds a tag to the database")
    
    parser.add_argument("-d", "--delete", nargs="+",
        help="deletes all the specified tags")
    
    parser.add_argument("-e", "--edit", nargs=1,
        help="edits a tag's properties")
    
    # get_tag(self, tag_name: str) -> RETV_TMP:
    # get_list(self) -> RETV_TMP:
    # tag_construct(self, beth: str, gems: str, ncategory: str, ntag: str, steam: str, name: str) -> RETV_TMP:
    # tag_add(self, tlist: Optional[list]) -> RETV_TMP:
    # tag_delete(self, tlist: Optional[list]) -> RETV_TMP:
    # tag_edit(self, tag_name: str, beth: str, gems: str, ncategory: str, ntag: str, steam: str, name: str) -> RETV_TMP:
    
    args = parser.parse_args()
    # print args for debug purposes
    print(args)
    
    # frontend loading is optional.
    if args.frontend:
        repl = REPL(config)
        repl.cmdloop()
        pass
    else:
        db = tag.DB()
        db_hist = [db]
        
        ftag = tag.FTAG(config, db, db_hist)
        ftag.db_load()
        
        
        # saving is on-hold until the bugs are sorted out
        # ftag.db_save()
        pass


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.c(traceback.format_exc())
