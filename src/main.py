#!/usr/bin/env python

# Tag editor for the BGM project.

import traceback

from frontend.repl import REPL

import lib.arg as arg

import lib.tag as tag

from lib.config import config

from zenlog import log


def main() -> None:
    # Start the program.
    
    args = arg.parse()
    
    # frontend loading is optional.
    if args.frontend == "repl":
        repl = REPL(config)
        repl.cmdloop()
        pass
    else:
        db = tag.DB()
        db_hist = []
        
        ftag = tag.FTAG(config, db, db_hist)
        ftag.db_load()
        ftag.db_update_mapping()
        
        if args.get_tag:
            for tag_name in args.get_tag:
                rv = ftag.get_tag(tag_name)
                log.i(rv["msg"])
        elif args.list:
            rv = ftag.get_list()
            log.i(rv["retval"])
            if rv["success"]:
                log.i("Done")
            else:
                log.e("Something went wrong!")
        elif args.add:
            if len(args.add) is 6:
                rv = ftag.tag_construct(args.add[0], args.add[1], args.add[2], args.add[3], args.add[4], args.add[5])
                print(rv["retval"])
                rv = ftag.tag_add([rv["retval"]])
                if rv["success"]:
                    log.i("Done")
                else:
                    log.e("Something went wrong!")
            else:
                log.e("how in the bloody hell did you do that")
        elif args.edit:
            if len(args.edit) >= 3:
                tag_name = args.edit[0]
                attr_name = args.edit[1]
                val = args.edit[2:]
                rv = ftag.tag_edit(tag_name, attr_name, val)
                if rv["success"]:
                    log.i("Done")
                else:
                    log.e("Something went wrong!")
            else:
                log.e("Invalid arguments, please look at -h for more info")
        elif args.delete:
            rv = ftag.tag_delete(args.delete)
            if rv["success"]:
                log.i("Done")
            else:
                log.e("Something went wrong!")
        else:
            log.e("Please invoke -h for help and usage.")
            pass
        
        rv = ftag.get_modified_state()
        if rv["success"]:
            if rv["retval"]:
                log.i("- this would be a saving message here -")
                # ftag.db_save()
        
        pass


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pylint: disable=W0703
        log.c(traceback.format_exc())
