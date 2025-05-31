import os
import re
from argparse import ArgumentParser
from functools import reduce

from indexing.direct import build_direct_index
from indexing.utils import parse_word_file
from trie import Trie


def remove_special_characters(word: str) -> str:
    word = Trie.make_safe(word.lower())

    return re.sub(r"[\#\$\[\]\(\)\{\}\*\.\,%&_=;:\-\?!]*", "", word)


def is_exception(exceptions: Trie, word: str) -> bool:
    if exceptions.contains(word):
        return True

    return reduce(lambda acc, ch: acc or ch.isdigit(), word, False)


def main():
    parser = ArgumentParser("dindexer")
    parser.add_argument("exceptions")
    parser.add_argument("stopwords")
    parser.add_argument("directory_to_index")

    args = parser.parse_args()

    exceptions = parse_word_file(args.exceptions)
    stopwords = parse_word_file(args.stopwords)

    files = []
    directory = os.fsencode(args.directory_to_index)
    for file in os.listdir(directory):
        if not file.endswith(b".book.txt"):
            continue
        files.append(open(os.path.join(directory, file), "r"))
    direct_index = build_direct_index(files, stopwords, exceptions)

    print(f"{direct_index.find('HayFever.book.txt')}")


if __name__ == "__main__":
    main()
