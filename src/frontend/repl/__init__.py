"""Interactive REPL frontend for tag-editor."""

import os

from cmd import Cmd

from copy import copy

from typing import List, Union

import lib.color as color

import lib.tag as tag

from zenlog import log


def ask(question: str) -> str:
    """Ask the user to provide a value for something."""
    print(question)
    response = input()
    return response


def confirm() -> bool:
    """Ask the user for confirmation."""
    print('Are you sure you want to continue? [Y/n]')
    choice = input().lower()
    return 'yes'.startswith(choice)


def choices(items: List[str]) -> str:
    """Present the user with a list of choices."""
    items.append('Cancel')
    while True:
        count = 0
        for item in items:
            count += 1
            print(f'[{count}] {item}')
        try:
            choice = int(input()) - 1
            return items[choice]
        except (ValueError, IndexError):
            log.e('Not a valid choice!')
            continue


class REPL(Cmd):
    """A repl to execute multiple commands in a repo."""

    def __init__(self, config: dict) -> None:
        """Initialize the REPL with a config."""
        super(REPL, self).__init__()
        self.config = config
        self.path = config['tag_db_path']
        self.database: Union[None, dict] = None
        self.__orig_database: Union[None, dict] = {}
        self.mapping: dict = {}
        self.changed = False

    intro = color.colorize(
        color.FGGREEN,
        f'{color.BOLD}BGM Tag Editor\n'
        f'{color.UNBOLD}Show commands with `help`')
    path = os.getcwd()
    prompt = color.colorize(color.FGGREEN, '$ ')

    def default(self, line: str):
        """Override error output to fit with zenlog."""
        if line == 'EOF':
            print()
            return self.do_exit(line)
        log.e(f'Unknown command `{line}`')

    def update_database(self) -> None:
        """Update the database."""
        log.d('loading the database')
        self.database = tag.load_tagdb(self.path)
        self.__orig_database = copy(self.database)
        self.update_mapping()

    def update_mapping(self) -> None:
        """Update the mapping."""
        log.d('building id mapping')
        self.mapping = tag.get_id_map(self.database)

    def preloop(self) -> None:
        """Load the tag database into memory."""
        log.d('preloop')
        self.update_database()

    def postcmd(self, stop: Union[None, bool], line: str) -> bool:
        """Update internal state after each command."""
        self.changed = self.database == self.__orig_database
        return bool(stop)

    # ---------------------------------------------------------------------- #

    # disable warnings about methods which could be functions since not
    #  all repl commands need `self`
    # pylint: disable=R0201

    def do_printtag(self, tag_name: str) -> None:
        """Print the raw tag data."""
        if self.database is None:
            log.e('The database is not loaded!')
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f'No such tag \'{tag_name}\'')
                return
        print(self.database[tag_name])

    def do_exit(self, _: str) -> bool:
        """Exit the command interpreter."""
        confirmed = not self.changed
        if self.changed:
            log.w('You have unsaved changes!')
            confirmed = confirm()
        if confirmed:
            log.i('Bye!')
            return True
        else:
            log.i('Canceled.')

    def do_load(self, _: str) -> None:
        """Load the tag database into memory."""
        if self.database is not None:
            log.e('The database is already loaded!')
            return

        self.database = tag.load_tagdb(self.path)

    def do_unload(self, _: str) -> None:
        """Unload the database without saving."""
        if self.database is None:
            log.e('The database is not loaded!')
            return

        confirmed = not self.changed
        if self.changed:
            log.w('You have unsaved changes!')
            confirmed = confirm()
        if confirmed:
            self.database = None
        else:
            log.i('Canceled.')

    def do_list(self, _: str) -> None:
        """List all tags."""
        if self.database is None:
            log.e('The database is not loaded!')
            return

        for tag_data in self.database.values():
            print(tag_data['name'])

    # def do_add(self, tag_name: str) -> None:
    #     """Add a new tag."""
    #     if self.database is None:
    #         log.e('The database is not loaded!')
    #         return
    #
    #     name = tag_name
    #     # tag_name = tag.next_free_id(self.database)
    #
    #     new_tag = tag.TAG_TEMPLATE
    #     while True:
    #         options = ['Gems', 'Nexus', 'Steam', 'Bethesda']
    #         choice = choices(options)
    #
    #     self.database[tag_name] = new_tag

    def do_delete(self, tag_name: str) -> None:
        """Delete a tag."""
        if self.database is None:
            log.e('The database is not loaded!')
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f'No such tag \'{tag_name}\'')
                return

        result = self.database.pop(tag_name, None)
        if result is None:
            log.e('No such tag')
        else:
            log.i('Done.')

    def do_edit(self, tag_name: str) -> None:
        """Edit a tag."""
        if self.database is None:
            log.e('The database is not loaded!')
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f'No such tag \'{tag_name}\'')
                return

        # $ edit <tag name>
        # -> list of properties to edit
        # $ id | name
        # -> ask for new value
        # $ gems | nexus | steam | bethesda
        # ? 1+ values already
        # -> add or remove values
        # $ add
        # -> : 0 values
        # $ remove
        # -> list of values to remove + done
        # : 0 values
        # -> prompt for value
        # $ <value>
        # -> prompt again
        # $ <empty>
        # -> done

        m1_options = list(self.database[tag_name].keys())
        m1_options.append('id')
        choice = choices(m1_options).lower()
        if choice in ['id', 'name']:
            value = ask(f'New value for {choice}:')
            self.database[tag_name][choice] = value
            self.update_mapping()
            return
        if choice == 'Cancel':
            return
        else:
            log.d('NOTE: GENERIC PROPERTY')
            old_val = self.database[tag_name][choice]
            if old_val is not None:
                if isinstance(old_val, list):
                    # append or remove entries
                    print('IT WAS A LIST')
                else:
                    print(color.colorize(
                        color.FGYELLOW,
                        f'This property already has a value of {old_val}.'
                        'Are you sure you want to overwrite it?'
                    ))
                    yn = choices(['Overwrite'])
                    print(yn)
            else:
                print('NO PREVIOUS VALUE')

    # def do_sort(self, _: str) -> bool:

    # def do_unused(self, _: str) -> None:
    #     """List unused tag IDs."""
    #     pass

    def do_save(self, _: str) -> None:
        """Save changes to the database."""
        tag.save_tagdb(self.path, self.database)
        self.__orig_database = copy(self.database)
        self.update_mapping()
