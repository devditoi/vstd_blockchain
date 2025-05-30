import hashlib

def keccak(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()  # Dùng SHA256 thay vì Keccak256 cho đơn giản

class TrieNode:
    def __init__(self):
        self.children = {}  # Map hex char (0-9a-f) → TrieNode
        self.value = None

    def is_leaf(self):
        return self.value is not None


class PatriciaTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key: str, value: str):
        key = self._hex_key(key)
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.value = value

    def get(self, key: str):
        key = self._hex_key(key)
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.value

    def _hex_key(self, key: str):
        key = key.lower().replace('0x', '')
        return list(key)

    def hash_node(self, node=None):
        if node is None:
            node = self.root

        if node.is_leaf():
            return keccak("value:" + str(node.value))

        items = []
        for k in sorted(node.children.keys()):
            child_hash = self.hash_node(node.children[k])
            items.append(f"{k}:{child_hash}")
        combined = "|".join(items)
        return keccak(combined)


if __name__ == "__main__":
    trie = PatriciaTrie()
    trie.insert("0xabc", "100")
    trie.insert("0xabd", "200")
    trie.insert("0xade", "300")

    print("Get 0xabc:", trie.get("0xabc"))
    print("Get 0xade:", trie.get("0xade"))
    print("Root Hash:", trie.hash_node())
