import os
from collections import Counter
from io import TextIOWrapper
from typing import Iterable

import stemmer
from bplustree import BPlusTree
from trie.trie import Trie

from .utils import is_exception, remove_special_characters


def build_direct_index(
    files: Iterable[TextIOWrapper],
    stopwords: Trie,
    exceptions: Trie,
) -> BPlusTree[str, Counter]:
    direct_index = BPlusTree()

    for file in files:
        words = Counter()
        for line in file:
            for word in line.split():
                word = remove_special_characters(word)
                if len(word) == 0:
                    continue
                elif is_exception(exceptions, word):
                    words[word] += 1
                elif stopwords.contains(word):
                    continue
                else:
                    stem = stemmer.stem(word)
                    words[stem] += 1
        direct_index.insert(os.path.basename(file.name.decode("utf-8")), words)

    return direct_index
