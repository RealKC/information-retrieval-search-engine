from argparse import ArgumentParser
from functools import reduce
import re
from bplustree import BPlusTree
from collections import Counter
from trie import Trie
import stemmer
import os


def parse_word_file(path: str) -> Trie:
    trie = Trie()
    with open(path, "r") as f:
        for word in f:
            word = word.strip()

            if len(word) == 0 or word.startswith("#"):
                continue

            word = word.lower()
            trie.insert(word)
            if '\'' in word:
                trie.insert(re.sub('\'', '', word))


    return trie


def remove_special_characters(word: str) -> str:
    word = Trie.make_safe(word.lower())

    return re.sub(r'[\#\$\[\]\(\)\{\}\*\.\,%&_=;:\-\?!]*', '', word)


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

    direct_index = BPlusTree()

    directory = os.fsencode(args.directory_to_index)
    for file in os.listdir(directory):
        words = Counter()
        with open(os.path.join(directory, file), "r") as f:
            for line in f:
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
        direct_index.insert(file, words)

    print(f"{direct_index.find("HayFever.book.txt")}")


if __name__ == "__main__":
    main()
