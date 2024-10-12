import pytest
from lxml import etree
from causaly.src.batch_pipeline_utils import get_xlm_tree


def test_get_xlm_tree_passes():
    expected = etree._ElementTree
    actual = get_xlm_tree('data/dummy.xml')
    assert type(actual) == expected


def test_get_xlm_tree_fails_no_file():
    with pytest.raises(OSError):
        get_xlm_tree('data/does_not_exist.xml')