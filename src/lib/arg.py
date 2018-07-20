# argument handling, cause it looks silly if left in main.py

import argparse


def parse():
    parser = argparse.ArgumentParser(description="Use the BGM management tool from the command line, Huzzah!")

    parser.add_argument("-f", "--frontend", default=None, choices=["repl"],
        help="flag for using the frontend")

    parser.add_argument("-g", "--get-tag", nargs="+", default=None, metavar=("TAG_NAME"),
        help="prints the tag(s) under the given name or ID")

    parser.add_argument("-l", "--list", action="store_true",
        help="lists all tags")

    parser.add_argument("-a", "--add", nargs=6, default=None, metavar=("BETH", "GEMS", "N-CAT", "N-TAG", "STEAM", "NAME"),
        help="creates and adds a tag to the database")

    parser.add_argument("-d", "--delete", nargs="+", default=None, metavar=("TAG_NAME"),
        help="deletes all the specified tags")

    parser.add_argument("-e", "--edit", nargs=1, default=None, metavar=("TAG_NAME"),
        help="edits a tag's properties")

    return parser.parse_args()
