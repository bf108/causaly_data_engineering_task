from lxml import etree


def get_xlm_tree(file_path: str) -> etree._ElementTree:
    tree = etree.parse(file_path)
    return tree


def get_root_element(tree: etree._ElementTree) -> etree._Element:
    root = tree.getroot()
    return root

