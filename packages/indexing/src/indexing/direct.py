import os
import re
from collections import Counter
from io import TextIOWrapper
from typing import Generator, Iterable

import stemmer
from bplustree import BPlusTree
from trie.trie import Trie

from .utils import is_exception, remove_special_characters


def build_direct_index(
    files: Iterable[TextIOWrapper],
    stopwords: Trie,
    exceptions: Trie,
) -> BPlusTree[str, Counter[str, int]]:
    direct_index = BPlusTree[str, Counter[str, int]]()

    for file in files:
        words = Counter()
        for word in _words_of_file(file):
            word = remove_special_characters(word)
            stem = stemmer.stem(word)

            if len(word) == 0 or len(stem) == 0:
                continue
            elif is_exception(exceptions, word):
                words[word] += 1
            elif is_exception(exceptions, stem):
                words[stem] += 1
            elif stopwords.contains(word) or stopwords.contains(stem):
                continue
            else:
                words[stem] += 1
        direct_index.insert(os.path.basename(file.name.decode("utf-8")), words)

    return direct_index


def _words_of_file(file: TextIOWrapper) -> Generator[str]:
    for line in file:
        words = re.split(r"[\s—,.:;]", line)
        for word in words:
            yield word
