from bs4 import BeautifulSoup
from stopwords import STOPWORDS
from trie import Trie

import requests


def main():
    url = "https://en.wikipedia.org/wiki/Arch_Linux"

    r = requests.get(url)

    if r.status_code != 200:
        print(f'failed with status code {r.status_code}')
        return

    soup = BeautifulSoup(r.text, features='html.parser')
    noise = 0

    words = soup.get_text().split()

    for word in words:
        if STOPWORDS.contains(Trie.make_safe(word)):
            noise += 1

    print(f'Webpage {soup.title.get_text()} ({url}) has {noise} instances of noise words')


if __name__ == "__main__":
    main()
