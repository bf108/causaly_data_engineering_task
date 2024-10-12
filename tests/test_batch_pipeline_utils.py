import pytest
from lxml import etree
from causaly.src.batch_pipeline_utils import get_xlm_tree, get_single_element, get_element_text


def test_get_xlm_tree_passes():
    expected = etree._ElementTree
    actual = get_xlm_tree('data/dummy.xml')
    assert type(actual) == expected


def test_get_xlm_tree_fails_no_file():
    with pytest.raises(OSError):
        get_xlm_tree('data/does_not_exist.xml')


def test_get_single_element_returns_correct_element_when_element_exists():
    # Given
    xml_string = "<root><child>content</child></root>"
    tree = etree.ElementTree(etree.fromstring(xml_string))
    expected_element = etree.Element("child")
    expected_element.text = "content"

    # When
    actual_element = get_single_element(tree, "child")

    # Then
    assert actual_element.tag == expected_element.tag
    assert actual_element.text == expected_element.text

def test_get_single_element_returns_none_when_element_does_not_exist():
    # Given
    xml_string = "<root><child>content</child></root>"
    tree = etree.ElementTree(etree.fromstring(xml_string))

    # When
    actual_element = get_single_element(tree, "nonexistent")

    # Then
    assert actual_element is None

def test_get_single_element_raises_error_when_tree_is_none():
    # Given
    tree = None

    # When/Then
    with pytest.raises(AttributeError):
        get_single_element(tree, "child")