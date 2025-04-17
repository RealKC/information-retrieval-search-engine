import re
from functools import reduce

import stemmer
from trie.trie import Trie


def remove_special_characters(word: str) -> str:
    word = Trie.make_safe(word.lower())

    return re.sub(r"[\#\$\[\]\(\)\{\}\*\.\,%&_=;:\-\?!]*", "", word)


def is_exception(exceptions: Trie, word: str) -> bool:
    if len(word) == 0:
        return False

    if exceptions.contains(word):
        return True

    return reduce(lambda acc, ch: acc or ch.isdigit(), word, False)


def parse_word_file(path: str) -> Trie:
    trie = Trie()
    with open(path, "r") as f:
        for word in f:
            word = word.strip()

            if len(word) == 0 or word.startswith("#"):
                continue

            word = word.lower()
            trie.insert(word)
            if "'" in word:
                trie.insert(re.sub("'", "", word))

    return trie


def process_word_for_indexing(
    word: str,
    stopwords: Trie,
    exceptions: Trie,
) -> str | None:
    word = remove_special_characters(word)
    stem = stemmer.stem(word)

    if len(word) == 0 or len(stem) == 0:
        return None
    elif is_exception(exceptions, word):
        return word
    elif is_exception(exceptions, stem):
        return stem
    elif stopwords.contains(word) or stopwords.contains(stem):
        return None
    else:
        return stem
