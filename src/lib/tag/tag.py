# Functions for interfacing with the tag database.

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


# <?xml version="1.0" encoding="UTF-8"?>
#
# <tag-list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
#   <tag id="1" name="Animation">
#     <beth>Animations</beth>
#     <gems>160</gems>
#     <nexus type="category">Animation</nexus>
#     <nexus type="tag">Animation - Modified</nexus>
#     <nexus type="tag">Animation - New</nexus>
#     <steam xsi:nil="true" />
#   </tag>
# </tag-list>

def load_tagdb(path: str) -> dict:
    # Load the tag database from disk.
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


def save_tagdb(path: str, tagdb: list) -> None:
    # Save the tag database to disk.
    
    atbs = ['beth', 'gems', 'nexus', 'steam']
    natbs = ['category', 'tag']
    
    wbuffer = '<?xml version="1.0" encoding="UTF-8"?>\n\n'
    wbuffer += '<taglist xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
    
    for entry in tagdb:
        for key in entry:
            id = key  # this is the fastest way to get the key, since there is only one key per entry.
        
        wbuffer += f'\t<tag id="{id}" name="{entry[id]["name"]}">\n'
        for atb in atbs:
            nempty = True
            if entry[id][atb] and atb != 'nexus':
                for si in entry[id][atb]:
                    wbuffer += f'\t\t<{atb}>{si}</{atb}>\n'
            elif entry[id][atb] and atb == 'nexus':
                for natb in natbs:
                    if entry[id][atb][natb]:
                        for si in entry[id][atb][natb]:
                            wbuffer += f'\t\t<{atb} type="{natb}">{si}</{atb}>\n'
                        nempty = False
                if nempty:
                    wbuffer += f'\t\t<{atb} xsi:nil=\"true\" />\n'
            else:
                wbuffer += f'\t\t<{atb} xsi:nil=\"true\" />\n'
        wbuffer += '\t</tag>\n'
    wbuffer += '</taglist>'
    
    print(wbuffer)
    
    with open(path, 'w') as opf:
        opf.write(wbuffer)


def get_id_map(database: dict) -> dict:
    # Make a Name to ID mapping from the database.
    mapping = {}
    for _id in database:
        name = database[_id]['name']
        if _id in mapping.values():
            raise ValueError(f'Duplicate tag ID: {_id}')
        if name in mapping.keys():
            raise ValueError(f'Duplicate tag name: {name}')
        mapping[name] = _id
    return mapping
