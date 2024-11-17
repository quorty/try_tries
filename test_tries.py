from tries import VarSizeTrie, FixedSizeTrie, HashTrie
import string

if __name__ == "__main__":
    alphabet = '\0' + string.ascii_letters + string.digits
    print(chr(0))
    test_trie = FixedSizeTrie.create_trie(alphabet,["a\0", "ab\0"])# alphabet, 
    test_trie.insert("ac\0")
    test_trie.insert("bc\0")
    test_trie.insert("d\0")
    print("")
    test_trie.delete("a\0")
    test_trie.insert("abc\0")
    test_trie.delete("ab\0")
    test_trie.print()

    print(test_trie.contains("d\0"))

    
    