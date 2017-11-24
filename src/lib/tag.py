"""Functions for manipulating the tag database."""

from copy import deepcopy

from typing import Dict, List, Union

import untangle


TAG_TEMPLATE: Dict[str, Union[str, List[str], Dict[str, List[str]]]] = {
    'beth': [],
    'gems': [],
    'nexus': {'category': [], 'tag': []},
    'steam': [],
    'name': '',
}


def load_tagdb(path: str) -> dict:
    """Load the tag database from disk."""
    xml = untangle.parse(path)
    database = {}
    for tag in xml.taglist.children:
        if tag['id'] in database.keys():
            raise ValueError(f'Duplicate tag ID: {tag["id"]}')
        taginf = deepcopy(TAG_TEMPLATE)  # dear python: why is deepcopy not default
        taginf['name'] = tag['name']
        for url in tag.children:
            name = url._name  # pylint: disable=W0212
            link = None
            if not url['xsi:nil']:
                link = url.cdata
            if name == 'nexus' and link:
                taginf[name][url['type']].append(link)
            elif link:
                taginf[name].append(link)
        database[tag['id']] = taginf
    return database

#<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
#
#<tag-list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
#  <tag id="1" name="Animation">
#    <beth>Animations</beth>
#    <gems>160</gems>
#    <nexus type="category">Animation</nexus>
#    <nexus type="tag">Animation - Modified</nexus>
#    <nexus type="tag">Animation - New</nexus>
#    <steam xsi:nil="true" />
#  </tag>
#</tag-list>

def save_tagdb(path: str, tagdb: dict) -> None:
    """Save the tag database to disk."""
    # TODO: test and review database saving
    
    atbs = ["beth", "gems", "nexus", "steam"]
    natbs = ["category", "tag"]
    
    buffs = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n"
    buffs += "<taglist xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n"
    
    for i in tagdb:
        buffs += "\t<tag id=\"" + i + "\" name=\"" + tagdb[i]['name'] + "\">\n"
        for atb in atbs:
            nempty = True
            if (len(tagdb[i][atb]) > 0 and atb != "nexus"):
                for si in tagdb[i][atb]:
                    buffs += "\t\t<" + atb + ">" + str(si) + "<" + atb + "/>\n"
            elif (len(tagdb[i][atb]) > 0 and atb == "nexus"):
                for natb in natbs:
                    if (len(tagdb[i][atb][natb]) > 0):
                        for si in tagdb[i][atb][natb]:
                            buffs += "\t\t<" + atb + " type=\"" + natb + "\">" + str(si) + "<" + atb + "/>\n"
                        nempty = False
                if (nempty):
                    buffs += "\t\t<" + atb + " xsi:nil=\"true\" />\n"
            else:
                buffs += "\t\t<" + atb + " xsi:nil=\"true\" />\n"
        buffs += "</tag>\n"
    buffs += "</taglist>"
    
    #with open(file) as handle:
    opf = open(path, "w")
    opf.write(buffs)
    opf.close()


def get_id_map(database: dict) -> dict:
    """Make a Name to ID mapping from the database."""
    mapping = {}
    for _id in database:
        name = database[_id]['name']
        if _id in mapping.values():
            raise ValueError(f'Duplicate tag ID: {_id}')
        if name in mapping.keys():
            raise ValueError(f'Duplicate tag name: {name}')
        mapping[name] = _id
    return mapping
