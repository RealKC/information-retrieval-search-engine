from typing import Self


class Trie[V = None]:
    TERMINATOR = ord("\0")

    data: V = None

    def __init__(self):
        self.children = [None] * 128

    def insert(self, word: str, data: V = None):
        p = self

        for ch in word:
            c = ord(ch)
            if p.children[c] is None:
                p.children[c] = Trie()
            p = p.children[c]

        if len(word) != 0:
            p.children[Trie.TERMINATOR] = p
            p.data = data

    def contains(self, word: str) -> bool:
        return self._get_node(word) is not None

    def get_data_for(self, word: str) -> V | None:
        node = self._get_node(word)

        if node is None:
            return None

        return node.data

    def _get_node(self, word: str) -> Self | None:
        word = Trie.make_safe(word)
        p = self
        for ch in word:
            if p is None:
                break
            p = p.children[ord(ch)]

        if p is None or p.children[Trie.TERMINATOR] is None:
            return None

        return p

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
