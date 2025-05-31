import os
from argparse import ArgumentParser
import traceback

import searchfuncs
from indexing.direct import build_direct_index
from indexing.inverted import build_inverted_index
from indexing.utils import parse_word_file


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
    inverted_index = build_inverted_index(direct_index)

    query = "abroad adam add abyss"
    print(
        f"boolean: {searchfuncs.boolean.search(query, inverted_index, stopwords, exceptions)}"
    )
    print(
        f"vector: {searchfuncs.vector.search(query, inverted_index, stopwords, exceptions)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"got exception {e}:\n {traceback.format_exc()}")
