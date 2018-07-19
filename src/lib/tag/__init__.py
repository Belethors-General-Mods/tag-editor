# functional layer on top of tag.py, functins should be used in frontend implementations

import os

from zenlog import log

from copy import deepcopy

from typing import Dict, List, Union, Tuple, Optional

from lib import color

from lib.tag import tag

TAG_TEMPLATE: Dict[str, Union[str, List[str], Dict[str, List[str]]]] = {
    'beth': [],
    'gems': [],
    'nexus': {'category': [], 'tag': []},
    'steam': [],
    'name': '',
}

# Uniform return value for the entire wrapper / functional layer
RETV_TMP: Dict[str, Union[bool, str, object]] = {
    "success": bool,  # ALWAYS tells if the fuction you asked for could run successfully.
    "msg": str,  # String message - can contain error messages or general information (!) Not used in every case
    "retval": object  # If a function has a return value other than its success and message, it goes in this field
    # "retval" is NOT used in every case
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
        # and now... DANCE

    def db_load(self) -> RETV_TMP:
        # Load the database.
        retval = deepcopy(RETV_TMP)
        log.d("loading the database")
        try:
            self.database = tag.load_tagdb(self.path)
            retval["success"] = True  # It's that easy. ¯\_(ツ)_/¯
        except Exception as exc:
            retval["msg"] = "An error occurred while loading the database!\n" + f"└> {color.BOLD}{exc}{color.UNBOLD}"
            retval["success"] = False
            log.e(retval["msg"])
        return retval

    def db_save(self) -> None:
        # Save changes to the database.
        retval = deepcopy(RETV_TMP)
        log.d("saving the database")
        retval = self.db_check()
        if retval["success"]:
            try:
                tag.save_tagdb(self.path, self.database)
                self.db_history.append(self.database)  # TODO fix
                self.db_update_mapping()
            except Exception as exc:
                retval["msg"] = "An error occurred while saving the database!\n" + f"└> {color.BOLD}{exc}{color.UNBOLD}"
                retval["success"] = False
                log.e(retval["msg"])
        return retval

    def db_unload(self) -> RETV_TMP:
        # Unload the database without saving.
        retval = deepcopy(RETV_TMP)
        retval["success"] = True
        self.database = None
        return retval

    def db_update_mapping(self) -> RETV_TMP:
        # Update the mapping.
        retval = deepcopy(RETV_TMP)
        log.d("building id mapping")
        retval = self.db_check()
        if retval["success"]:
            self.mapping = tag.get_id_map(self.database)
        return retval

    def db_update(self) -> RETV_TMP:
        # Update the database.
        retval = deepcopy(RETV_TMP)
        try:
            self.db_history.append(self.database)  # TODO fix
            retval = self.db_load()
            retval = self.db_update_mapping()
        except Exception as exc:
            retval["msg"] = "Oops! Something went wrong!\n" + f"└> {color.BOLD}{exc}{color.UNBOLD}"
            retval["success"] = False
            log.e(retval["msg"])
        return retval

    def db_check(self) -> RETV_TMP:
        # Check if the database(s) exist (aka. loaded into memory)
        retval = deepcopy(RETV_TMP)
        retval["msg"] = "The database is loaded!"  # we hope.
        retval["success"] = True
        if self.database is None:
            retval["msg"] = "The database is not loaded!"  # no u
            retval["success"] = False
            log.e(retval["msg"])
            return retval
        if self.db_history is None:
            retval["msg"] = "The database history is not loaded!"  # wtf??
            retval["success"] = False
            log.e(retval["msg"])
            return retval
        return retval

    def get_tag(self, tag_name: str) -> RETV_TMP:
        # Throw back the raw tag data - for printing or what
        retval = deepcopy(RETV_TMP)
        retval = self.db_check()
        if retval["success"]:
            if tag_name not in self.database:
                if tag_name in self.mapping:
                    tag_name = self.mapping[tag_name]
                if tag_name not in self.database:
                    retval["msg"] = f"No such tag \"{tag_name}\""
                    retval["success"] = False
                    log.e(retval["msg"])
                    return retval
            # we are okay ᕙ( ͠°‿ °)ᕗ
            retval["msg"] = str(self.database[tag_name])
            retval["success"] = True
            retval["retval"] = self.database[tag_name]
            # HASHTAG YOLO
        return retval
    
    def get_modified_state(self) -> RETV_TMP:
        # See if the last two states of the database are the same. (Aka. DID YOU FUCKING SAVE??)
        retval = deepcopy(RETV_TMP)
        retval = self.db_check()
        if retval["success"]:
            if self.database == self.db_history[len(self.db_history)]:  # TODO: test this, it might break stuff
                retval["msg"] = "Not changed"
                retval["success"] = True
                retval["retval"] = False
                log.e(retval["msg"])
            else:
                retval["msg"] = "Changed"
                retval["success"] = True
                retval["retval"] = True
                log.e(retval["msg"])
        return retval

    def get_list(self) -> RETV_TMP:
        # List all tags.
        retval = deepcopy(RETV_TMP)
        retval = self.db_check()
        if retval["success"]:
            retval["retval"] = []
            for tag_data in self.database.values():
                retval["retval"].append(tag_data["name"])
        return retval

    def get_next_free_id(self) -> RETV_TMP:
        # finds out the biggest ID currently used (n), and returns n+1
        retval = deepcopy(RETV_TMP)
        retval = self.db_update_mapping()
        retval["retval"] = 0
        if retval["success"]:
            for id in self.mapping.values():
                if retval["retval"] < id:
                    retval["retval"] = id
            retval["retval"] += 1
        return retval

    def tag_construct(self, beth: str, gems: str, ncategory: str, ntag: str, steam: str, name: str) -> RETV_TMP:
        # Construct a new tag.
        retval = deepcopy(RETV_TMP)
        retval["success"] = True
        
        new_tag = deepcopy(TAG_TEMPLATE)
        new_tag["beth"] = beth
        new_tag["gems"] = gems
        new_tag["nexus"]["category"] = ncategory
        new_tag["nexus"]["tag"] = ntag
        new_tag["steam"] = steam
        new_tag["name"] = name
        
        retval["msg"] = str(new_tag)
        retval["retval"] = new_tag
        return retval

    def tag_add(self, tlist: Optional[list]) -> RETV_TMP:
        # Add new tags. Or just one.
        retval = deepcopy(RETV_TMP)
        retval = self.get_next_free_id()
        if retval["success"]:  # Ok
            cid = retval["retval"]  # getting first current ID
            for ntag in tlist:
                if len(ntag) != 6:  # are you stupid?
                    retval["msg"] = "Invalid format for new tag."
                    retval["success"] = False
                    log.e(retval["msg"])
                    return retval  # guess you are
                
                new_tag = deepcopy(TAG_TEMPLATE)  # sofar so good
                new_tag["beth"] = ntag[0]
                new_tag["gems"] = ntag[1]
                new_tag["nexus"]["category"] = ntag[2]
                new_tag["nexus"]["tag"] = ntag[3]
                new_tag["steam"] = ntag[4]
                new_tag["name"] = ntag[5]
                
                self.database[new_tag["name"]] = new_tag  # let's hope these work this way
                self.mapping[new_tag["name"]] = cid
                cid += 1  # increase current ID tracker
        return retval

    def tag_delete(self, tlist: Optional[list]) -> RETV_TMP:
        # Delete tags. Or just one.
        retval = deepcopy(RETV_TMP)
        retval = self.db_check()
        if retval["success"]:
            for tag_name in tlist:
                if tag_name not in self.database:
                    if tag_name in self.mapping:
                        tag_name = self.mapping[tag_name]
                if tag_name not in self.database:
                    retval["msg"] = f"No such tag \"{tag_name}\""
                    retval["success"] = False
                    log.e(retval["msg"])
                    return retval
                self.database.pop(tag_name, None)
        return retval


    def tag_edit(self, tag_name: str) -> None:  # TODO
        # Edit a tag.
        retval = deepcopy(RETV_TMP)
        retval = self.db_check()
        if retval["success"]:  # TODO here on out
            if tag_name not in self.database:
                if tag_name in self.mapping:
                    tag_name = self.mapping[tag_name]
                if tag_name not in self.database:
                    log.e(f"No such tag \"{tag_name}\"")
                    return


    def db_sort(self, _: str) -> bool:  # TODO
        return


    def get_unused(self, _: str) -> None:  # TODO ??
        # List unused tag IDs.
        return
