"""Functions for manipulating the tag database."""

from copy import copy

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
        taginf = copy(TAG_TEMPLATE)  # dear python: why is deepcopy not default
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


def save_tagdb(path: str, tagdb: dict) -> None:
    """Save the tag database to disk."""
    # TODO: implement database saving
    pass


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
