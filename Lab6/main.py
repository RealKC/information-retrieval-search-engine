from argparse import ArgumentParser
import os
from indexing.utils import parse_word_file
from indexing.direct import build_direct_index
from indexing.inverted import build_inverted_index


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
    print(direct_index)
    inverted_index = build_inverted_index(direct_index)

    for word, data in inverted_index:
        print(f"{word} -> {data}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{e}")
