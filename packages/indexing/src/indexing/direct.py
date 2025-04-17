import os
import re
from collections import Counter
from io import TextIOWrapper
from typing import Generator, Iterable

from bplustree import BPlusTree
from trie.trie import Trie

from .utils import process_word_for_indexing


def build_direct_index(
    files: Iterable[TextIOWrapper],
    stopwords: Trie,
    exceptions: Trie,
) -> BPlusTree[str, Counter[str, int]]:
    direct_index = BPlusTree[str, Counter[str, int]]()

    for file in files:
        words = Counter()
        for word in _words_of_file(file):
            word = process_word_for_indexing(word, stopwords, exceptions)
            if word is not None:
                words[word] += 1
        direct_index.insert(os.path.basename(file.name.decode("utf-8")), words)

    return direct_index


def _words_of_file(file: TextIOWrapper) -> Generator[str]:
    for line in file:
        words = re.split(r"[\s—,.:;]", line)
        for word in words:
            yield word
