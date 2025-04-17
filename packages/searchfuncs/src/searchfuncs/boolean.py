import itertools
from typing import TypedDict

from indexing.inverted import IndexData
from indexing.utils import process_word_for_indexing
from trie.trie import Trie


class _Query(TypedDict):
    AND: set[str]
    OR: set[str]
    NOT: set[str]


def _parse_query(query: str, stopwords: Trie, exceptions: Trie) -> _Query:
    words = query.split()

    and_ = set()
    or_ = set()
    not_ = set()

    for word in words:
        if word.startswith('"') and word.endswith('"'):
            word = process_word_for_indexing(word, stopwords, exceptions)
            if word is not None:
                and_.add(word)
        elif word.startswith("-"):
            word = process_word_for_indexing(word[1:], stopwords, exceptions)
            if word is not None:
                not_.add(word)
        else:
            word = process_word_for_indexing(word, stopwords, exceptions)
            if word is not None:
                or_.add(word)

    return {"AND": and_, "NOT": not_, "OR": or_}


def search(
    query, inverted_index: Trie[IndexData], stopwords: Trie, exceptions: Trie
) -> set[str]:
    parsed = _parse_query(query, stopwords, exceptions)

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
        try:
            result.update(interest_set[word])
        except KeyError:
            continue

    for word in parsed["NOT"]:
        try:
            result.difference_update(interest_set[word])
        except KeyError:
            continue

    must_have_docs = set()
    for word in parsed["AND"]:
        try:
            must_have_docs.update(interest_set[word])
        except KeyError:
            continue

    return result if not must_have_docs else result.intersection(must_have_docs)
