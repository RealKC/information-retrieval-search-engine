from argparse import ArgumentParser
from collections import Counter
from trie import Trie
import os

def parse_word_file(path: str) -> Trie:
    trie = Trie()
    with open(path, 'r') as f:
        for word in f:
            if len(word) == 0 or word.startswith('#'):
                continue

            trie.insert(word)

    return trie

def main():
    parser = ArgumentParser("dindexer")
    parser.add_argument("exceptions")
    parser.add_argument("stopwords")
    parser.add_argument("directory_to_index")

    args = parser.parse_args()

    exceptions = parse_word_file(args.exeptions)
    stopwords = parse_word_file(args.stopwords)

    for file in os.listdir(os.fsencode(args.directory_to_index)):
        words = Counter()
        with open(file, 'r') as f:
            for line in file:
                for word in line.split():
                    if exceptions.contains(word):
                        words[word] += 1
                    elif stopwords.contains(word):
                        continue
                    else:
                        # TODO: Stem the word
                        pass


if __name__ == "__main__":
    main()
