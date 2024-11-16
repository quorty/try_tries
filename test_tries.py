from tries import VarSizeTrie

if __name__ == "__main__":
    test_trie = VarSizeTrie.create_trie(["a\0", "ab\0"])
    test_trie.insert("ac\0")
    test_trie.insert("bc\0")
    test_trie.insert("d\0")
    print("")
    #test_trie.delete("a\0")
    test_trie.insert("abc\0")
    test_trie.delete("ab\0")
    test_trie.print()

    print(test_trie.contains("d\0"))
    