import pytest
from causaly.src.batch_pipeline_utils import get_all_elements
from causaly.src.batch_pipeline_utils import get_lowercase_of_string
from causaly.src.batch_pipeline_utils import get_permutations_of_size_n
from causaly.src.batch_pipeline_utils import get_single_element
from causaly.src.batch_pipeline_utils import get_xlm_tree
from causaly.src.batch_pipeline_utils import replace_comma_space_with_underscore
from lxml import etree


def test_get_xlm_tree_passes():
    expected = etree._ElementTree
    actual = get_xlm_tree("data/dummy.xml")
    assert type(actual) == expected


def test_get_xlm_tree_fails_no_file():
    with pytest.raises(OSError):
        get_xlm_tree("data/does_not_exist.xml")


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


def test_get_all_elements():
    # Given
    tree = get_xlm_tree("data/dummy.xml")

    # When
    actual_ids_elms = get_all_elements(tree, "OtherID")
    actual_ids_elms_str = sorted([el.text for el in actual_ids_elms])

    # Then
    expected = sorted(["20600308", "NASA/00024699"])

    assert actual_ids_elms_str == expected


def test_get_all_elements_no_matches():
    # Given
    tree = get_xlm_tree("data/dummy.xml")

    # When
    actual_ids_elms = get_all_elements(tree, "OtherIDNotPresent")

    # Then
    assert actual_ids_elms == []


def test_get_lowercase_of_string():
    assert get_lowercase_of_string("HELLO") == "hello"
    assert get_lowercase_of_string("Hello") == "hello"
    assert get_lowercase_of_string("hello") == "hello"


def test_replace_comma_space_with_underscore():
    assert replace_comma_space_with_underscore("hello, world") == "hello_world"
    assert replace_comma_space_with_underscore("hello,world") == "hello,world"
    assert replace_comma_space_with_underscore("hello world") == "hello_world"
    assert replace_comma_space_with_underscore("hello,    world") == "hello_world"


def test_get_permutations_of_size_n():
    values = ["a", "b", "c"]
    n = 2
    result = get_permutations_of_size_n(values, n)
    expected_result = [
        ("a", "b"),
        ("a", "c"),
        ("b", "a"),
        ("b", "c"),
        ("c", "a"),
        ("c", "b"),
    ]
    assert result == expected_result
