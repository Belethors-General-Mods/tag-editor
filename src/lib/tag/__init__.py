# functional layer on top of tag.py, functins should be used in frontend implementations

import os

from zenlog import log

from copy import deepcopy

from typing import Dict, List, Union, Tuple, Optional

from lib import color

from lib.tag import tag


RETV_TMP: Dict[str, Union[bool, str, object]] = {
    "success": bool,
    "msg": str,
    "retval": object
}

# log.c("this is critical")
# log.d("this is debug")
# log.e("this is error")
# log.i("this is information")
# log.w("this is warning")
print("this is print")
print(RETV_TMP)


class DB(object):
    # The database itself
    def __init__(self):
        super(DB, self).__init__()
        self.database: Optional[dict] = None


class FTAG(object):
    # The worker unit
    def __init__(self, config: dict, database: dict, dbhistory: list):
        super(FTAG, self).__init__()
        print("Current working dir: " + os.getcwd())
        self.config = config
        self.path = config["tag_db_path"]
        self.database = database
        self.db_history = dbhistory
        self.mapping: dict = {}

    def load_database(self) -> None:
        # Load the database.
        retval = deepcopy(RETV_TMP)
        log.d("loading the database")
        try:
            self.database = tag.load_tagdb(self.path)
            retval["success"] = True
        except Exception as exc:
            retval["msg"] = "An error occurred while loading the database!\n" + f"└> {color.BOLD}{exc}{color.UNBOLD}"
            retval["success"] = False
            log.e(retval["msg"])
        return retval

    def update_mapping(self) -> None:
        # Update the mapping.
        retval = deepcopy(RETV_TMP)
        log.d("building id mapping")
        if self.database is None:
            retval["msg"] = "The database is not loaded!"
            retval["success"] = False
            log.e(retval["msg"])
            return retval
        self.mapping = tag.get_id_map(self.database)
        retval["success"] = True
        return retval

    def update_database(self) -> None:
        # Update the database.
        retval = deepcopy(RETV_TMP)
        try:
            self.db_history.append(self.database)
            retval = self.load_database()
            retval = self.update_mapping()
        except Exception as exc:
            retval["msg"] = "Oops! Something went wrong!\n" + f"└> {color.BOLD}{exc}{color.UNBOLD}"
            retval["success"] = False
            log.e(retval["msg"])
        return retval

    def postcmd(self, stop: Optional[bool], line: str) -> bool:
        # Update internal state after each command.
        self.changed = self.database == self.__orig_database
        return bool(stop)

    # ---------------------------------------------------------------------- #

    # disable warnings about methods which could be functions since not
    #  all repl commands need `self`
    # pylint: disable=R0201


    def do_printtag(self, tag_name: str) -> None:
        # Print the raw tag data.
        if self.database is None:
            log.e("The database is not loaded!")
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f"No such tag \"{tag_name}\"")
                return
        print(self.database[tag_name])


    def do_exit(self, _: str) -> bool:
        # Exit the command interpreter.
        confirmed = not self.changed
        if self.changed:
            log.w("You have unsaved changes!")
            confirmed = confirm()
        if confirmed:
            log.i("Bye!")
            return True
        else:
            log.i("Canceled.")
        return False


    def do_load(self, _: str) -> None:
        # Load the tag database into memory.
        if self.database is not None:
            log.e("The database is already loaded!")
            return

        self.load_database()


    def do_unload(self, _: str) -> None:
        # Unload the database without saving.
        if self.database is None:
            log.e("The database is not loaded!")
            return

        confirmed = not self.changed
        if self.changed:
            log.w("You have unsaved changes!")
            confirmed = confirm()
        if confirmed:
            self.database = None
        else:
            log.i("Canceled.")


    def do_list(self, _: str) -> None:
        # List all tags.
        if self.database is None:
            log.e("The database is not loaded!")
            return

        for tag_data in self.database.values():
            print(tag_data["name"])

    # def do_add(self, tag_name: str) -> None:
    #     # Add a new tag.
    #     if self.database is None:
    #         log.e("The database is not loaded!")
    #         return
    #
    #     name = tag_name
    #     # tag_name = tag.next_free_id(self.database)
    #
    #     new_tag = tag.TAG_TEMPLATE
    #     while True:
    #         options = ["Gems", "Nexus", "Steam", "Bethesda"]
    #         choice = choices(options)
    #
    #     self.database[tag_name] = new_tag


    def do_delete(self, tag_name: str) -> None:
        # Delete a tag.
        if self.database is None:
            log.e("The database is not loaded!")
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f"No such tag \"{tag_name}\"")
                return

        result = self.database.pop(tag_name, None)
        if result is None:
            log.e("No such tag")
        else:
            log.i("Done.")


    def do_edit(self, tag_name: str) -> None:
        # Edit a tag.
        if self.database is None:
            log.e("The database is not loaded!")
            return
        if tag_name not in self.database:
            if tag_name in self.mapping:
                tag_name = self.mapping[tag_name]
            if tag_name not in self.database:
                log.e(f"No such tag \"{tag_name}\"")
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
        m1_options.append("id")
        choice = choices(m1_options).lower()
        if choice in ["id", "name"]:
            value = ask(f"New value for {choice}:")
            self.database[tag_name][choice] = value
            self.update_mapping()
            return
        if choice == "Cancel":
            return
        else:
            log.d("NOTE: GENERIC PROPERTY")
            old_val = self.database[tag_name][choice]
            if old_val is not None:
                if isinstance(old_val, list):
                    # append or remove entries
                    print("IT WAS A LIST")
                else:
                    print(color.colorize(
                        color.FGYELLOW,
                        f"This property already has a value of {old_val}."
                        "Are you sure you want to overwrite it?"
                    ))
                    yn = choices(["Overwrite"])
                    print(yn)
            else:
                print("NO PREVIOUS VALUE")

    # def do_sort(self, _: str) -> bool:

    # def do_unused(self, _: str) -> None:
    #     # List unused tag IDs.
    #     pass


    def do_save(self, _: str) -> None:
        # Save changes to the database.
        if self.database is None:
            log.e("The database is not loaded!")
            return
        tag.save_tagdb(self.path, self.database)
        self.__orig_database = deepcopy(self.database)
        self.update_mapping()
