from typing import Optional

from lxml import etree
from lxml.etree import _Element
from lxml.etree import _ElementTree


def get_xlm_tree(file_path: str) -> _ElementTree:
    tree = etree.parse(file_path)
    return tree


def get_root_element(tree: _ElementTree) -> _Element:
    root = tree.getroot()
    return root


def get_single_element(tree: _ElementTree, element_name: str) -> Optional[_Element]:
    element = tree.find(f".//{element_name}")
    return element


def get_element_text(element: _Element) -> str | None:
    element_str = element.text
    return element_str


def get_all_elements(
    tree: _ElementTree,
    element: str,
    *,
    attribute_value: str | None = None,
) -> list[_Element]:
    search_string = f".//{element}"
    if isinstance(attribute_value, str):
        search_string += f"[@{attribute_value}]"
    elements = tree.findall(search_string)
    return elements
