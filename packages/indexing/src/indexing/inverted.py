import math
from collections import Counter
from typing import Iterable

from bplustree import BPlusTree
from trie import Trie


class IndexData:
    """A data class containing info about a word within the indexed set of documents"""

    document_tfs: dict[str, float]
    """A map showing for each document, the word's term frequency(the relative frequency within a document)"""

    idf: float
    """The word's inverse document frequency, i.e. how good this word is at identifying a document"""

    def __init__(self, documents: dict[str, float], idf: float):
        self.document_tfs = documents
        self.idf = idf

    def __str__(self):
        return f"idf={self.idf} docs=[{', '.join(map(lambda item: f'{item[0]}: {item[1]}', self.document_tfs.items()))}]"

    @property
    def documents(self) -> Iterable[str]:
        """All the documents that a word was found in"""

        return self.document_tfs.keys()


def build_inverted_index(direct_index: BPlusTree[str, Counter]) -> Trie[IndexData]:
    inverted_index = Trie[IndexData]()
    document_count = 0

    for document_id, words in direct_index:
        document_count += 1

        for word, frequency in words.items():
            if (data := inverted_index.get_data_for(word)) is not None:
                data.idf += 1
                data.document_tfs[document_id] = frequency
            else:
                inverted_index.insert(word, IndexData({document_id: frequency}, 1))

    for _, index_data in inverted_index:
        index_data.idf = math.log(document_count / (1 + index_data.idf))

    return inverted_index
