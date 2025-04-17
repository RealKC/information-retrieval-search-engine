import math
from collections import Counter
from collections.abc import Iterable
from functools import reduce

import stemmer
from indexing.inverted import IndexData
from indexing.utils import is_exception
from trie.trie import Trie


def cosine_similarity(doc1: dict[str, float], doc2: dict[str, float]) -> float:
    dot = 0

    if not doc1:
        raise RuntimeError("doc1 has no keys")

    if not doc2:
        raise RuntimeError("doc2 has no keys")

    for key, score in doc1.items():
        try:
            dot += score * doc2[key]
        except KeyError:
            continue

    def magnitude(doc: Iterable[float]):
        return math.sqrt(
            reduce(lambda acc, val: acc + val, map(lambda score: score * score, doc))
        )

    doc1m = magnitude(doc1.values())
    doc2m = magnitude(doc2.values())

    if doc1m == 0 or doc2m == 0:
        return 0

    return dot / (doc1m * doc2m)


def _parse_query(
    query: str, inverted_index: Trie[IndexData], exceptions: Trie
) -> dict[str, float]:
    tf = Counter()

    stems = []

    for word in query.split():
        stem = stemmer.stem(word)
        if is_exception(exceptions, word):
            stems.append(word)
        else:
            stems.append(stem)

    for word in stems:
        tf[word] += 1

    result = {}
    for word in stems:
        data = inverted_index.get_data_for(word)
        if data is not None:
            result[word] = tf[word] * data.idf

    return result


def search(query, inverted_index: Trie[IndexData], exceptions: Trie) -> set[str]:
    parsed = _parse_query(query, inverted_index, exceptions)

    interest_set = set()

    for word in parsed.keys():
        index_data = inverted_index.get_data_for(word)

        for doc in index_data.documents:
            interest_set.add(doc)

    # doc_id -> {key: score}
    document_vectors: dict[str, dict[str, float]] = {}

    for word, data in inverted_index:
        for doc, tf in data.document_tfs.items():
            if doc not in interest_set:
                continue

            if doc in document_vectors:
                document_vectors[doc][word] = data.idf * tf
            else:
                document_vectors[doc] = {word: data.idf * tf}

    scores = []
    for doc_id, vector in document_vectors.items():
        scores.append((doc_id, cosine_similarity(parsed, vector)))

    return set(
        map(
            lambda doc: doc[0],
            sorted(filter(lambda doc: doc[1] > 0, scores), key=lambda doc: doc[1]),
        )
    )
