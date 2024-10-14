import itertools
import re
from typing import Optional

import pandas as pd
from lxml import etree
from lxml.etree import _Element
from lxml.etree import _ElementTree

from keyword_pair_dataclass import KeywordPair


def get_xlm_tree(file_path: str) -> _ElementTree:
    tree = etree.parse(file_path)
    return tree


def get_single_element(
    tree: _Element | _ElementTree, element_name: str
) -> Optional[_Element]:
    element = tree.find(f".//{element_name}")
    return element


def get_all_elements(
    tree: _ElementTree | _Element,
    element: str,
    *,
    attribute_value: str | None = None,
) -> list[_Element]:
    search_string = f".//{element}"
    if isinstance(attribute_value, str):
        search_string += f"[@{attribute_value}]"
    elements = tree.findall(search_string)
    return elements


def get_lowercase_of_string(s: str) -> str:
    return s.lower()


def replace_comma_space_with_underscore(s: str) -> str:
    return re.sub(r",?\s+", "_", s)


def get_permutations_of_size_n(values: list[str], n: int) -> list[tuple[str, ...]]:
    return list(itertools.permutations(values, n))


def standardize_string(s: str) -> str:
    s = get_lowercase_of_string(s)
    s = replace_comma_space_with_underscore(s)
    return s


def parse_single_meeting_abstract(
    meeting_abstract: _Element,
) -> list[KeywordPair] | list:
    articles = []
    nlm_dcms_id_element = get_single_element(meeting_abstract, "NlmDcmsID")
    if isinstance(nlm_dcms_id_element, _Element) and nlm_dcms_id_element.text:
        nlm_dcms_id = nlm_dcms_id_element.text
        # Find all KeywordList elements and extract Keyword elements
        keyword_lists = get_all_elements(
            meeting_abstract,
            "KeywordList",
            attribute_value='Owner="NLM-AUTO"',
        )
        keywords = [
            keyword
            for keyword_list in keyword_lists
            for keyword in get_all_elements(keyword_list, "Keyword")
        ]
        # Handle for any duplicate keywords referenced on articles
        keywords_strings = set()
        for keyword in keywords:
            keyword_string = keyword.text
            if keyword_string:
                keywords_strings.add(keyword_string)

        if len(keywords_strings) >= 2:
            keywords_strings_processed = sorted(
                [standardize_string(keyword) for keyword in list(keywords_strings)]
            )
            keyword_pairs = get_permutations_of_size_n(keywords_strings_processed, 2)
            for kw1, kw2 in keyword_pairs:
                article = KeywordPair(
                    nlm_dcms_id=nlm_dcms_id, keyword_1=kw1, keyword_2=kw2
                )
                articles.append(article)
    return articles


def parse_all_meeting_abstracts(file_path: str) -> pd.DataFrame:
    tree = get_xlm_tree(file_path)
    meeting_abstracts = get_all_elements(tree, "MeetingAbstract")
    articles = []

    # Loop over all MeetingAbstract elements and extract the required data
    for meeting_abstract in meeting_abstracts:
        keyword_pairs_from_article = parse_single_meeting_abstract(meeting_abstract)
        articles.extend(keyword_pairs_from_article)
    return pd.DataFrame(articles)


def groupby_keyword_count_unique_ids(df: pd.DataFrame) -> pd.DataFrame:
    df_output = (
        df.groupby(by=["keyword_1", "keyword_2"])["nlm_dcms_id"]
        .nunique()
        .reset_index()
        .sort_values(by="nlm_dcms_id", ascending=False)
        .reset_index(drop=True)
    )
    df_output.rename(columns={"nlm_dcms_id": "frequency"}, inplace=True)
    return df_output


def get_keyword_pairs_from_meeting_abstract(meeting_abstract: str) -> list[KeywordPair]:
    meeting_abstract_xlm = etree.fromstring(meeting_abstract)
    keyword_pairs = parse_single_meeting_abstract(meeting_abstract_xlm)
    return keyword_pairs
