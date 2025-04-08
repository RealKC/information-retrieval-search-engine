import re
from functools import reduce

from trie.trie import Trie


def remove_special_characters(word: str) -> str:
    word = Trie.make_safe(word.lower())

    return re.sub(r"[\#\$\[\]\(\)\{\}\*\.\,%&_=;:\-\?!]*", "", word)


def is_exception(exceptions: Trie, word: str) -> bool:
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
