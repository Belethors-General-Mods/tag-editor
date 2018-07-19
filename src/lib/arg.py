# argument handling, cause it looks silly if left in main.py

import argparse


def parse():
    parser = argparse.ArgumentParser(description="Use the BGM management tool from the command line, Huzzah!")

    parser.add_argument("-f", "--frontend", action="store_true",
        help="flag for using the frontend")

    parser.add_argument("-g", "--get-tag", nargs="+", default=None,
        help="prints the tag(s) under the given name or ID")

    parser.add_argument("-l", "--list", action="store_true",
        help="lists all tags")

    parser.add_argument("-a", "--add", nargs=1, default=None,
        help="creates and adds a tag to the database")

    parser.add_argument("-d", "--delete", nargs="+", default=None,
        help="deletes all the specified tags")

    parser.add_argument("-e", "--edit", nargs=1, default=None,
        help="edits a tag's properties")

    return parser.parse_args()
