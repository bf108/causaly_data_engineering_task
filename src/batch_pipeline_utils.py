from lxml import etree


def get_xlm_tree(file_path: str) -> etree._ElementTree:
    tree = etree.parse(file_path)
    return tree


def get_root_element(tree: etree._ElementTree) -> etree._Element:
    root = tree.getroot()
    return root


def get_single_element(tree: etree._ElementTree, element: str) -> etree._Element | None:
    element = tree.find(element)
    return element


def get_element_text(element: str) -> str:
    element_str = element.text
    return element_str


def get_all_elements(
        tree: etree.ElementTree,
        element: str,
        *,
        attribute_value: str | None = None,
) -> list[etree._Element]:
    search_string = f".//{element}"
    if isinstance(attribute_value, str):
        search_string += f"[@{attribute_value}]"
    elements = tree.findall(search_string)
    return elements