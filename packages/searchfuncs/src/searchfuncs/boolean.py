import itertools
from typing import TypedDict

from indexing.inverted import IndexData
from stemmer import stem
from trie.trie import Trie


class _Query(TypedDict):
    AND: set[str]
    OR: set[str]
    NOT: set[str]


def _parse_query(query: str) -> _Query:
    words = query.split()

    and_ = set()
    or_ = set()
    not_ = set()

    for word in words:
        if word.startswith("&"):
            and_.add(stem(word[1:]))
        elif word.startswith("|"):
            or_.add(stem(word[1:]))
        elif word.startswith("~"):
            not_.add(stem(word[1:]))

    return {"AND": and_, "NOT": not_, "OR": or_}


def search(query, inverted_index: Trie[IndexData]) -> set[str]:
    parsed = _parse_query(query)

    all_words = set(itertools.chain(parsed["AND"], parsed["OR"], parsed["NOT"]))

    # word -> list[doc_id]
    interest_set: dict[str, set[str]] = {}

    for word in all_words:
        index_data = inverted_index.get_data_for(word)
        if index_data is None:
            continue

        interest_set[word] = set(
            map(
                lambda doc_tf: doc_tf[0],
                filter(lambda doc_tf: doc_tf[1] > 0, index_data.document_tfs.items()),
            )
        )

    result = set()

    for word in parsed["OR"]:
        result.update(interest_set[word])

    for word in parsed["NOT"]:
        result.difference_update(interest_set[word])

    must_have_docs = set()
    for word in parsed["AND"]:
        must_have_docs.update(interest_set[word])

    return result if not must_have_docs else result.intersection(must_have_docs)
