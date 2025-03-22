from bs4 import BeautifulSoup
from collections import Counter
from stopwords import STOPWORDS
from trie import Trie

import argparse
import requests


def main():
    parser = argparse.ArgumentParser(
        prog="StopwordCounter", description="Counts stopwords in a webpage"
    )

    parser.add_argument("url")

    args = parser.parse_args()

    r = requests.get(args.url)

    if r.status_code != 200:
        print(f"failed with status code {r.status_code}")
        return

    soup = BeautifulSoup(r.text, features="html.parser")

    noise = Counter()
    total = 0

    words = soup.get_text().split()

    for word in words:
        safe = Trie.make_safe(word)
        if STOPWORDS.contains(safe):
            noise[safe] += 1
            total += 1

    print(
        f"Webpage {soup.title.get_text()} ({args.url}) has {total} instances of noise words"
    )
    for word, count in noise.items():
        print(f"{word}: {count}")


if __name__ == "__main__":
    main()
