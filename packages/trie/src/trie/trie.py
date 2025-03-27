from typing import Self


class Trie:
    TERMINATOR = ord("\0")

    def __init__(self):
        self.children = [None] * 128

    def insert(self, word: str):
        p = self

        for ch in word:
            c = ord(ch)
            if p.children[c] is None:
                p.children[c] = Trie()
            p = p.children[c]

        if len(word) != 0:
            p.children[Trie.TERMINATOR] = p

    def contains(self, word: str) -> bool:
        word = Trie.make_safe(word)
        p = self
        for ch in word:
            if p is None:
                break
            p = p.children[ord(ch)]

        if p is None or p.children[Trie.TERMINATOR] is None:
            return False

        return True

    @staticmethod
    def partial_search(ch: str, node: Self | None):
        if node is None:
            return None

        return node.children[ord(ch)]

    @staticmethod
    def make_safe(word: str) -> str:
        return "".join(ch for ch in word if ord(ch) < 128)


if __name__ == "__main__":
    trie = Trie()

    trie.insert("hello")
    trie.insert("world")
    trie.insert("president")

    print(f'has "world"? {trie.contains("world")}')
    print(f'has "hell"? {trie.contains("hell")}')
