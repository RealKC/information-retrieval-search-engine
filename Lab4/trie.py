class Trie:
    OFFSET = ord('a')
    TERMINATOR = ord('{') - OFFSET

    def __init__(self):
        self.children = [None] * 27

    def insert(self, word: str):
        p = self

        for i, ch in enumerate(word):
            c = ord(ch) - Trie.OFFSET
            if p.children[c] is None:
                p.children[c] = Trie()
            p = p.children[c]

        if i != 0:
            p.children[Trie.TERMINATOR] = p

    def contains(self, word: str) -> bool:
        p = self
        for ch in word:
            if p is None:
                break
            p = p.children[ord(ch) - Trie.OFFSET]

        if p is None or p.children[Trie.TERMINATOR] is None:
            return False

        return True

if __name__ == '__main__':
    trie = Trie()

    trie.insert('hello')
    trie.insert('world')
    trie.insert('president')

    print(f'has "world"? {trie.contains('world')}')
    print(f'has "hell"? {trie.contains('hell')}')
